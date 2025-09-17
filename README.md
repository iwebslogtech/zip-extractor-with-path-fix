# zip-extractor-with-path-fix
A Python tool for robustly extracting multiple ZIP files into named folders, automatically handling and shortening long file or folder names that would otherwise fail extraction on Windows due to path length limits. Skips, truncates, and warns about problematic filenaming, making it perfect for backup, archiving, and shared drives.

# zip-extractor-with-path-fix
A Python utility for batch extracting ZIP archives into automatically created, uniquely named folders. This script handles Windows path length limitations by automatically shortening long filenames and folder names during extraction, so your files aren't lost to "Path Too Long" errors.

## Features
- Extracts all `.zip` files in a folder to their own named folders
- Detects and handles paths/names that exceed Windows path length limits
- Truncates or modifies long filenames/folders automatically, with warnings
- Skips files that can't be extracted (such as for other OS errors), but continues extracting the rest
- Clean, simple, and robust code—ideal for backup and archiving use-cases

## Usage
1. **Clone this repo** or copy the script
2. **Install Python (3.7+)**
3. **Edit the script** to set your source folder (`parent_folder = Path(...)`).
4. **Run the script**


## License
This project is released under the Creative Commons Zero v1.0 Universal license (CC0). This means you may use, modify, and distribute this code for any purpose, without asking permission. See [LICENSE](LICENSE) for details.

## Contribution
Contributions, bug reports, and improvements are welcome!
