# ZIP Extractor with Path Fix

A desktop Python application for safely extracting one or many ZIP archives while automatically fixing Windows path-length problems, invalid filename characters, collisions, and unsafe archive paths.

A desktop Python application for batch extracting ZIP files while automatically fixing Windows path length issues, invalid filenames, unsafe archive paths, and naming conflicts.

## Highlights

- Native desktop GUI built with Tkinter, with no third-party runtime dependencies
- Add individual ZIP files or scan a folder for archives
- Extract each archive into a separate named folder
- Configurable maximum path length, defaulting to 220 characters
- Deterministic hashed shortening to reduce accidental filename collisions
- Protection against Zip Slip paths such as `../outside.txt`
- Cleans Windows-invalid names and reserved device names
- Optional overwrite behavior and timestamp preservation
- Responsive background extraction, progress indicator, activity log, and cancellation
- Works on Windows, macOS, and Linux with Python 3.9+

## Run

```bash
python app.py
```

On Windows, you can also double-click `run.bat`.

## Build a Windows EXE

```bat
build_windows.bat
```

This installs PyInstaller and creates `dist\ZIP-Extractor-Path-Fix.exe`.

## Notes

- Password-protected ZIP files are reported as skipped unless Python can read them without a password.
- Existing destination folders receive a numbered suffix by default. Enable overwrite if you want matching files replaced.
- A shorter output-folder location provides more room for filenames.

## License

Released under the CC0 1.0 Universal dedication. See `LICENSE`.
