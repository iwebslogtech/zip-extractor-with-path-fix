# Requirements

## System Requirements

### Supported Operating Systems

- Windows 10
- Windows 11
- Windows Server 2019+
- macOS 11+
- Ubuntu 20.04+
- Most modern Linux distributions

---

## Python Requirements

This application requires:

- Python 3.9 or later
- Tkinter (usually included with Python)
- Standard Python libraries only

No external Python packages are required to run the application.

### Verify Python Installation

Open Command Prompt or Terminal and run:

```bash
python --version
```

Expected output:

```text
Python 3.9+
```

---

## If Python Is NOT Installed

### Windows

1. Download Python from:

https://www.python.org/downloads/

2. Run the installer.

3. IMPORTANT:

Enable:

```text
☑ Add Python to PATH
```

before clicking Install.

4. Verify installation:

```cmd
python --version
```

---

### macOS

Install Python via:

```bash
brew install python
```

or download from:

https://www.python.org/downloads/

Verify:

```bash
python3 --version
```

---

### Linux (Ubuntu/Debian)

Install Python:

```bash
sudo apt update
sudo apt install python3 python3-tk -y
```

Verify:

```bash
python3 --version
```

---

## Tkinter Requirement

The application uses Tkinter for its desktop graphical interface.

### Windows

Tkinter is included automatically with official Python installers.

No additional action required.

### Ubuntu / Debian

Install:

```bash
sudo apt install python3-tk -y
```

### Fedora

Install:

```bash
sudo dnf install python3-tkinter
```

### Arch Linux

Install:

```bash
sudo pacman -S tk
```

---

## Runtime Dependencies

The application uses only Python standard library modules:

```text
tkinter
zipfile
pathlib
hashlib
queue
threading
shutil
subprocess
os
sys
time
re
dataclasses
```

No third-party libraries are required.

---

## Hardware Requirements

### Minimum

- Dual-Core CPU
- 4 GB RAM
- 100 MB free disk space

### Recommended

- Quad-Core CPU
- 8 GB RAM
- SSD Storage
- 500 MB+ free disk space for temporary extraction

---

## Running the Application

### Windows

Double-click:

```text
run.bat
```

or

```cmd
python app.py
```

### Linux / macOS

```bash
python3 app.py
```

---

## Building a Standalone Windows EXE

Install PyInstaller:

```bash
pip install pyinstaller
```

Build:

```bash
build_windows.bat
```

or

```bash
pyinstaller --onefile --windowed app.py
```

Output:

```text
dist/
└── ZIP-Extractor-Path-Fix.exe
```

---

## Portable EXE Distribution

End users do NOT need:

- Python
- pip
- Tkinter
- Command Prompt

if using the generated:

```text
ZIP-Extractor-Path-Fix.exe
```

The executable contains everything required to run the application.

---

## Recommended Windows Settings

For best results when handling extremely deep folder structures:

### Enable Long Paths

Open:

```text
Local Group Policy Editor
```

Navigate to:

```text
Computer Configuration
→ Administrative Templates
→ System
→ Filesystem
→ Enable Win32 Long Paths
```

Set:

```text
Enabled
```

Although the application automatically shortens paths, enabling long paths provides additional compatibility.

---

## Security Notes

The application includes:

✅ Zip Slip protection

✅ Invalid filename sanitization

✅ Windows reserved-name protection

✅ Safe folder creation

✅ Automatic collision handling

✅ Path-length mitigation

✅ Extraction error recovery

---

## Known Limitations

- Password-protected ZIP archives are not automatically decrypted.
- Corrupted ZIP archives may partially extract.
- Extremely deep archive structures may still require shortening if filesystem limits are exceeded.
- Network drives may have stricter path limitations than local drives.

---

## Support

Before reporting issues:

1. Ensure Python 3.9+ is installed.
2. Verify Tkinter is available.
3. Confirm the ZIP file is not corrupted.
4. Check that sufficient disk space is available.
5. Try using a shorter output folder path such as:

```text
C:\Extracted
```

to maximize available filename length.
