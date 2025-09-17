import zipfile
from pathlib import Path

MAX_PATH = 220  # Safe limit for most Windows systems

def shorten_path(path: Path, max_length=MAX_PATH):
    """Shorten path components so whole path fits in max_length."""
    parts = list(path.parts)
    base_path = Path(parts[0])
    for i in range(1, len(parts)):
        new_path = base_path / Path(*parts[1:i+1])
        if len(str(new_path)) > max_length:
            # Truncate current part, keep start and end, add '_'
            shortened = parts[i][:10] + '_' + parts[i][-10:] if len(parts[i]) > 21 else parts[i][:18]
            parts[i] = shortened
    result = Path(*parts)
    # Final full path check
    if len(str(result)) > max_length:
        result = result.parent / (result.stem[:32] + result.suffix)
    return result

parent_folder = Path(r'C:\Users\CodyBaba\Main Folder')

for zip_path in parent_folder.glob('*.zip'):
    dest_folder = parent_folder / zip_path.stem
    dest_folder.mkdir(exist_ok=True)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for i, member in enumerate(zip_ref.namelist(), start=1):
            member_path = dest_folder / member
            member_path_safe = shorten_path(member_path)
            try:
                member_path_safe.parent.mkdir(parents=True, exist_ok=True)
                if not member.endswith('/'):
                    # If rename happened, warn which file was renamed
                    if member_path_safe != member_path:
                        print(f"Renamed '{member_path}' to '{member_path_safe}' due to path length.")
                    with zip_ref.open(member) as src, open(member_path_safe, "wb") as tgt:
                        tgt.write(src.read())
            except OSError as e:
                print(f"ERROR: Skipped '{member}' due to: {e}")
    print(f"Extracted '{zip_path.name}' to '{dest_folder}' (with path-shortening for long entries)")
