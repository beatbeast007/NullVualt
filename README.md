# NullVualt
NullVault is a professional-grade Android forensics tool designed to support lockscreen bypassing, brute-force PIN cracking, local data extraction, file system snapshotting, and PDF reporting — all from a single Python interface.

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)  
**MIT © 2025** Abhishek Bhagat

## Table of Contents 

- Introduction
- Features
- Installation
- Usage
- Options
- Examples
- Contributing
- License

---

## Introduction

**NullVault** is a Python-based forensic utility designed to bypass or brute-force Android device lockscreens in controlled environments. It is primarily intended for digital forensic analysts, penetration testers, and incident responders with authorized access to test devices.

This tool supports both rooted and non-rooted ADB-enabled Android devices and performs a range of actions such as lockscreen bypass, 4-digit PIN brute-force, full device backup, file system snapshots, and device info PDF generation.


## Features
- 🔓 **Lockscreen Bypass** (Rooted)  
- 🔢 **4-Digit PIN Brute Force** (Non-rooted, ADB Keyevent)  
- 🧠 **Auto-Detection of Android Version and Lock Type**  
- 📁 **PDF Report Generator**  
- 📷 **File System Snapshot for Offline Analysis**  
- 📶 **Wi-Fi Password & SMS/Call Log Extraction**  
- 📦 **Import `locksettings.db` for Offline Cracking**  
- 📃 **Auto-Generated Reports Named with Device Info**  
- 🔄 **Main Menu Loop – No Script Restart Needed**  
- 🛠️ **Tested on Real Devices with ADB/Root Access**

## Installation

1. Clone the repository:

```bash
  git clone https://github.com/beatbeast007/NullVault
```
2. Navigate to the project directory:
```bash
  cd NullVault
```
3. Install dependencies:
```bash
  pip install -r requirements.txt
```
**Required tools:**
-Python 3.x

- ADB (Android Debug Bridge)

- su binary (for rooted operations)

- tar & zip (on device or via toybox)

## Usage
```bash
python NullVault.py
```
***Make sure:***

- ADB is enabled on the device

- USB Debugging is turned on

- The device is connected via USB

  ## Options

**0**	- Bypass Android lockscreen (root required)

**1**	- Brute-force 4-digit PIN (no root)
 
**2**	- Import locksettings.db from device

**3** -	Extract saved Wi-Fi passwords

**4**	- Extract SMS & call logs

**5** -	Generate file system snapshot

**9**	- Exit the tool

## Examples
Main Screen:

![image](https://github.com/user-attachments/assets/b06fb8cd-7a14-4a9e-9b9d-e773e1f36ce0)

![image](https://github.com/user-attachments/assets/13226445-aeb3-4707-8603-84d41ae98d08)


**0.** Bypass lockscreen (rooted):

![image](https://github.com/user-attachments/assets/7b38e41b-d4de-4125-90fe-cf798e01b84f)


**1**	Brute-force 4-digit PIN (no root)

![image](https://github.com/user-attachments/assets/8dc72e8b-a8cc-479f-80d7-5570f344ef1e)


**2**	Import locksettings.db from device

![image](https://github.com/user-attachments/assets/a6f788a0-d882-46c1-8530-00be68f1d4eb)



**3**	Extract saved Wi-Fi passwords

![image](https://github.com/user-attachments/assets/acf1eff7-6dff-4cc5-9449-8828772c2f9b)


**4**	Extract SMS & call logs

![image](https://github.com/user-attachments/assets/e6f3c7a6-0ec4-4d99-99b9-4d5554fbc3d7)


**5**	Generate file system snapshot (rooted)

![image](https://github.com/user-attachments/assets/6c866ecf-8d0b-49c3-b7a7-ce2a0a862968)


**9**	Exit the tool

![image](https://github.com/user-attachments/assets/62653383-74a2-48f7-b5c6-d563eb286330)


## Contributing

Contributions are welcome! If you'd like to contribute to ParaMon, please follow these steps:

1. Fork the repository.

2. Create a new branch (git checkout -b feature/your-feature-name).Make your changes.

3. Commit your changes (git commit -am 'Add new feature').

4. Push to the branch (git push origin feature/your-feature-name).

5. Create a new Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/beatbeast007/ParaMon/blob/main/LICENSE) file for details
