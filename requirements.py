import subprocess
import sys

REQUIRED_LIBS = ["colorama", "fpdf", "tqdm"]

def install_libraries():
    print("[*] Checking and installing required libraries...\n")
    for lib in REQUIRED_LIBS:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
            print(f"  ✅ {lib} is installed.")
        except subprocess.CalledProcessError:
            print(f"  ❌ Failed to install {lib}. Please check manually.")

if __name__ == "__main__":
    install_libraries()
