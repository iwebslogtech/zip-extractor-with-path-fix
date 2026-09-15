# ZIP Extractor with Path Fix

A secure, user-friendly desktop application for extracting one or multiple ZIP archives while automatically handling long Windows paths, invalid filenames, duplicate names, and unsafe archive entries.

The application includes a graphical interface, batch extraction, configurable path limits, progress tracking, cancellation, activity logs, timestamp preservation, and protection against Zip Slip path traversal.

## Why This Application?

ZIP archives can contain deeply nested folders or very long filenames. On Windows, these entries may fail during extraction because the complete destination path exceeds the supported path length. Archives can also contain characters that are not permitted in Windows filenames or unsafe entries that attempt to write files outside the selected destination.

ZIP Extractor with Path Fix addresses these issues automatically by:

- Shortening paths only when required
- Retaining recognizable portions of filenames
- Adding deterministic hashes to shortened names to reduce collisions
- Replacing Windows-invalid filename characters
- Handling reserved Windows device names
- Blocking absolute paths and parent-directory traversal
- Continuing extraction when an individual entry cannot be processed

## Key Features

- Native desktop interface built with Python and Tkinter
- Add one or multiple ZIP archives
- Scan a folder for all `.zip` files
- Extract every archive into its own destination folder
- Select a custom output directory
- Configure the maximum permitted path length
- Automatically shorten long folders and filenames
- Use hash-based naming to reduce accidental collisions
- Clean invalid Windows filename characters
- Handle reserved names such as `CON`, `PRN`, `AUX`, `NUL`, `COM1`, and `LPT1`
- Protect against Zip Slip and path traversal entries
- Optionally overwrite existing files
- Preserve original file timestamps when possible
- Run extraction in a background thread so the interface remains responsive
- Show overall extraction progress
- Display renamed, skipped, completed, and failed entries in an activity log
- Cancel an extraction while it is running
- Open the output directory from the application
- Continue processing other entries when one entry fails
- Run without third-party Python packages

## Screenshots

You can add screenshots to a `screenshots` folder and display them here:

```markdown
![Main application window](screenshots/main-window.png)
![Extraction progress](screenshots/extraction-progress.png)
```

## Supported Operating Systems

The application is designed to run on:

- Windows 10
- Windows 11
- Windows Server 2019 or later
- macOS 11 or later
- Ubuntu 20.04 or later
- Other modern Linux distributions with Python and Tkinter support

Windows is the primary target because the application specifically addresses Windows path-length and filename restrictions.

## System Requirements

### Minimum requirements

- Dual-core processor
- 4 GB RAM
- Python 3.9 or later
- Tkinter support
- Sufficient free disk space for the extracted content

### Recommended requirements

- Quad-core processor
- 8 GB RAM
- SSD storage
- At least twice the compressed archive size available during extraction
- A short output location such as `C:\Extracted` when processing archives with very deep structures

## Python Requirements

The source-code version requires:

- Python 3.9 or later
- Tkinter
- Python standard library modules

No external Python package is required to run the application.

The application uses the following standard library modules:

```text
dataclasses
hashlib
os
pathlib
queue
re
shutil
subprocess
sys
threading
time
tkinter
zipfile
```

## If Python Is Not Installed

### Windows

1. Download Python from the official Python website:

   https://www.python.org/downloads/

2. Run the installer.

3. On the first installation screen, select:

   ```text
   Add Python to PATH
   ```

4. Make sure the optional Tcl/Tk and IDLE component remains selected. Tkinter is normally installed with the official Windows Python distribution.

5. Complete the installation.

6. Open Command Prompt and verify Python:

   ```cmd
   python --version
   ```

7. Verify Tkinter:

   ```cmd
   python -m tkinter
   ```

   A small Tkinter test window should open.

If the `python` command is unavailable, try:

```cmd
py --version
py -m tkinter
```

### macOS

Install a current version of Python from:

https://www.python.org/downloads/

If Homebrew is available, Python can also be installed with:

```bash
brew install python
```

Verify the installation:

```bash
python3 --version
python3 -m tkinter
```

The Python installer from python.org is generally the simplest choice when Tkinter support is required.

### Ubuntu and Debian

Install Python, Tkinter, and the virtual-environment module:

```bash
sudo apt update
sudo apt install python3 python3-tk python3-venv -y
```

Verify the installation:

```bash
python3 --version
python3 -m tkinter
```

### Fedora

```bash
sudo dnf install python3 python3-tkinter
```

### Arch Linux

```bash
sudo pacman -S python tk
```

## Download and Installation

### Option 1: Download from GitHub

1. Open the repository on GitHub.
2. Select **Code**.
3. Select **Download ZIP**.
4. Extract the downloaded repository ZIP.
5. Open the extracted project folder.

### Option 2: Clone with Git

```bash
git clone https://github.com/YOUR-USERNAME/zip-extractor-path-fix.git
cd zip-extractor-path-fix
```

Replace `YOUR-USERNAME` with your GitHub username.

## Running the Application

### Windows: simple method

Double-click:

```text
run.bat
```

### Windows: Command Prompt

```cmd
python app.py
```

If `python` is not recognized but the Python launcher is installed:

```cmd
py app.py
```

### macOS and Linux

```bash
python3 app.py
```

## How to Use

1. Start the application.
2. Select **Add ZIP files** to choose individual archives, or select **Add folder** to scan a folder for ZIP files.
3. Review the archive list.
4. Select an output directory.
5. Keep the default maximum path length of `220`, or enter another value.
6. Choose whether existing files should be overwritten.
7. Choose whether original timestamps should be preserved.
8. Select **Extract all**.
9. Monitor the progress bar and activity log.
10. Select **Open output folder** when extraction is complete.

Each ZIP archive is extracted into a separate folder based on the archive name. If that destination already exists and overwrite mode is disabled, the application creates a uniquely numbered destination folder.

## Maximum Path Length

The default maximum path length is:

```text
220 characters
```

This conservative value leaves room for filesystem and application-specific behavior on Windows.

Recommendations:

- Keep `220` for general Windows use.
- Use a short output path such as `C:\Extracted` for deeply nested archives.
- Increase the value only when the operating system and destination filesystem support longer paths.
- Do not set an unnecessarily low value because it can result in more filenames being shortened.

## Path-Shortening Method

When a path exceeds the configured limit, the application:

1. Identifies long path components.
2. Shortens the longest component first.
3. Preserves the file extension.
4. Adds a short SHA-1-based identifier.
5. Rechecks the complete destination path.
6. Continues shortening only when necessary.

A long filename may be converted into a structure similar to:

```text
quarterly_financial_archive_document__a1b2c3d4.xlsx
```

The hash makes shortened names more distinguishable than simple truncation.

## Security Features

### Zip Slip protection

The application rejects archive entries containing unsafe parent-directory paths such as:

```text
../outside.txt
```

It also rejects drive-qualified or absolute-style paths that might attempt to write outside the selected extraction folder.

### Invalid filename cleanup

Characters not allowed in Windows filenames are replaced with underscores:

```text
< > : " / \ | ? *
```

Control characters are also replaced.

### Reserved Windows names

Windows device names are adjusted automatically, including:

```text
CON
PRN
AUX
NUL
COM1 to COM9
LPT1 to LPT9
```

### Collision handling

If a file or destination already exists and overwrite mode is disabled, the application generates a numbered alternative name rather than silently replacing the existing item.

## Existing Files and Overwrite Behaviour

### Overwrite disabled

This is the safer default.

- Existing destination archive folders receive a numbered suffix.
- Existing files receive a numbered suffix.
- Existing content is not intentionally replaced.

### Overwrite enabled

- Matching files may be replaced.
- Use this option only when replacement is intended.
- Consider backing up important destination folders first.

## Password-Protected Archives

The application does not request or manage archive passwords through the graphical interface.

Password-protected entries that cannot be read are reported as skipped. Other readable entries may continue to extract.

## Building a Standalone Windows EXE

A Windows executable allows end users to run the application without separately installing Python.

### Automated build

On a Windows computer with Python installed, double-click:

```text
build_windows.bat
```

The script installs or updates PyInstaller and creates the executable.

Expected output:

```text
dist\ZIP-Extractor-Path-Fix.exe
```

### Manual build

Install PyInstaller:

```cmd
python -m pip install --upgrade pyinstaller
```

Build the executable:

```cmd
python -m PyInstaller --noconfirm --clean --onefile --windowed --name "ZIP-Extractor-Path-Fix" app.py
```

### What end users need

Users running the generated EXE do not need to install:

- Python
- pip
- Tkinter
- PyInstaller
- Any external Python package

The generated executable contains the Python runtime and application code required to launch the program.

Some antivirus products may inspect or temporarily flag newly created unsigned PyInstaller executables. For public distribution, consider code signing the Windows executable.

## Running Tests

Run the automated tests from the project folder:

### Windows

```cmd
python -m unittest -v test_app.py
```

### macOS and Linux

```bash
python3 -m unittest -v test_app.py
```

The included tests cover:

- Invalid character cleanup
- Reserved Windows filename handling
- Zip Slip rejection
- Long-path extraction and shortening
- Successful file-content extraction

## Project Structure

```text
zip-extractor-path-fix/
├── app.py
├── build_windows.bat
├── LICENSE
├── README.md
├── requirements.txt
├── run.bat
└── test_app.py
```

Optional repository directories can be added later:

```text
docs/
screenshots/
.github/ISSUE_TEMPLATE/
.github/workflows/
```

## Troubleshooting

### `python` is not recognized

Python is either not installed or was not added to the system PATH.

Try:

```cmd
py --version
```

If that also fails, reinstall Python and select **Add Python to PATH** during installation.

### Tkinter is missing

On Ubuntu or Debian:

```bash
sudo apt install python3-tk -y
```

On Fedora:

```bash
sudo dnf install python3-tkinter
```

On Windows, reinstall Python using the official installer and ensure Tcl/Tk is selected.

### The application does not open when double-clicking `run.bat`

Open Command Prompt in the project folder and run:

```cmd
python app.py
```

The command window should display any Python startup error.

### A path still cannot be extracted

Try the following:

1. Choose a shorter destination such as `C:\Extracted`.
2. Reduce the maximum path value from `220` to `200`.
3. Confirm that the destination allows file creation.
4. Avoid extracting directly into a deeply nested OneDrive, SharePoint sync, or network-drive folder.
5. Review the activity log for the exact skipped entry and error.

### Access denied

- Select an output folder where the current user has write permission.
- Avoid protected folders such as `C:\Windows` and `C:\Program Files`.
- Close files that may already be open in another application.
- Check whether security software is blocking file creation.

### Corrupted ZIP archive

Test the archive with another ZIP utility. If the archive is damaged, some or all entries may be unavailable. The application logs errors and attempts to continue where possible.

### Insufficient disk space

ZIP archives can expand to many times their compressed size. Confirm that the destination drive has enough space before extraction.

## Optional Windows Long-Path Setting

Modern Windows versions can support longer Win32 paths when the relevant operating-system policy is enabled and the application supports it.

The tool does not require this setting because it actively shortens paths. However, administrators may enable the Windows long-path policy for additional compatibility.

Group Policy location:

```text
Computer Configuration
  > Administrative Templates
  > System
  > Filesystem
  > Enable Win32 long paths
```

This setting may require administrator access and may be controlled by organizational policy.

## Known Limitations

- Password entry is not currently available in the graphical interface.
- Corrupted archives may extract only partially or fail completely.
- Available disk space is not estimated before extraction.
- Symbolic-link handling depends on how the archive was created and how Python interprets the entry.
- Destination files are not restored automatically if extraction is cancelled midway.
- Some network drives and synchronized folders enforce stricter naming or path rules.
- The program supports ZIP archives only. Other formats such as RAR, 7z, and TAR are not included.

## Privacy

The application runs locally.

- It does not upload archives.
- It does not send filenames to an external service.
- It does not require an account.
- It does not include analytics or telemetry.
- Extracted files remain in the output directory selected by the user.

## Contributing

Contributions, improvements, and bug reports are welcome.

Recommended contribution process:

1. Fork the repository.
2. Create a feature branch.
3. Make and test the changes.
4. Update documentation where required.
5. Open a pull request with a clear description.

Example:

```bash
git checkout -b feature/improved-password-support
git commit -m "Add password entry support"
git push origin feature/improved-password-support
```

## Reporting an Issue

When reporting a problem, include:

- Operating system and version
- Python version
- Whether the source-code or EXE version was used
- Maximum path-length setting
- Relevant activity-log message
- A safe sample archive structure, if possible
- Steps required to reproduce the issue

Do not upload confidential archives, private filenames, or sensitive business data to a public GitHub issue.

## Roadmap

Potential future enhancements include:

- Drag-and-drop archive selection
- Password entry for encrypted ZIP files
- Dry-run preview before extraction
- Exportable extraction reports
- Dark mode
- Destination disk-space checks
- Support for TAR and other archive formats
- Configurable filename-shortening rules
- Windows Explorer context-menu integration
- Signed Windows installer

## License

This project is released under the Creative Commons Zero v1.0 Universal dedication, also identified as `CC0-1.0`.

You may use, copy, modify, and distribute the project for personal or commercial purposes without requesting permission, subject to the terms in the `LICENSE` file.

The software is provided without warranty.

## Disclaimer

Always retain a backup of important archives and destination data. Although the application includes path safety, collision handling, and extraction error recovery, no extraction utility can guarantee recovery from corrupted archives, filesystem failures, insufficient storage, permission restrictions, or unexpected system interruption.

## Support the Project

If the application is useful:

- Star the repository
- Report reproducible issues
- Suggest improvements
- Contribute documentation or code
- Share the project with users facing Windows path-length problems

---

**Extract ZIP files safely, without path-length headaches.**
