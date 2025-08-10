import re
import sys
from pathlib import Path
import subprocess


#===CONFIG===#
CURRENT_DIR = Path(__file__).parent
INIT_FILE = Path(CURRENT_DIR, "src/__init__.py")
MANIFEST_FILE = Path(CURRENT_DIR, "src/blender_manifest.toml")
UPDATE_INIT = True
UPDATE_MANIFEST = True


#===CODE===#
def get_init_version():
    init_text = INIT_FILE.read_text(encoding="utf-8")
    match = re.search( # "version": (0, 0, 4)
        r'["\']version["\']\s*:\s*\(\s*(\d+),\s*(\d+),\s*(\d+)\s*\)', 
        init_text) 
    if not match:
        raise ValueError("Version tuple not found in __init__.py")
    major, minor, patch = map(int, match.groups())
    return major, minor, patch


def write_init_version(major: int, minor: int, patch: int):
    new_tuple = f"({major}, {minor}, {patch})"
    init_text = INIT_FILE.read_text(encoding="utf-8")
    init_text = re.sub( # "version": (0, 0, 4)
        r'["\']version["\']\s*:\s*\(\s*(\d+),\s*(\d+),\s*(\d+)\s*\)', 
        f'"version": {new_tuple}',
        init_text
    )
    INIT_FILE.write_text(init_text, encoding="utf-8")
    return new_tuple


def get_manifest_version():
    manifest_text = MANIFEST_FILE.read_text(encoding="utf-8")
    match = re.search( # version = "0.0.5"
        r'\nversion\s*=\s*["\'](\d+)\.(\d+)\.(\d+)["\']',
        manifest_text)
    if not match:
        raise ValueError("Version str not found in blender_manifest.toml")
    major, minor, patch = map(int, match.groups())
    return major, minor, patch


def write_manifest_version(major: int, minor: int, patch: int):
    new_str = f"{major}.{minor}.{patch}"
    manifest_text = MANIFEST_FILE.read_text(encoding="utf-8")
    manifest_text = re.sub( # version = "0.0.5"
        r'\nversion\s*=\s*["\'](\d+)\.(\d+)\.(\d+)["\']',
        f'\nversion = "{new_str}"',
        manifest_text
    )
    MANIFEST_FILE.write_text(manifest_text, encoding="utf-8")
    return new_str


def main():
    # Get current max version
    if not UPDATE_INIT and not UPDATE_MANIFEST:
        raise ValueError("Please check that at least one file updates")
    init_version = (0, 0, 0)
    manifest_version = (0, 0, 0)
    if UPDATE_INIT:
        if not INIT_FILE.exists():
            raise FileNotFoundError(f"Missing __init__.py here '{INIT_FILE}'")
        init_version = get_init_version()
    if UPDATE_MANIFEST:
        if not MANIFEST_FILE.exists():
            raise FileNotFoundError(f"Missing blender_manifest.toml here '{INIT_FILE}'")
        manifest_version = get_manifest_version()
    major, minor, patch = map(max, zip(init_version, manifest_version))
    print(f"Getting version ({major}, {minor}, {patch})")

    # Bump version
    bump_type = (sys.argv[1] if len(sys.argv) > 1 else "patch").lower()
    match bump_type:
        case "patch":
            patch += 1
        case "minor":
            minor += 1
            patch = 0
        case "major":
            major += 1
            minor = 0
            patch = 0
        case _:
            raise ValueError(f"Unknown bump type: {bump_type}, must be in ['', 'patch', 'minor', 'major']")
    print(f"Bumping {bump_type}: → ({major}, {minor}, {patch})")

    # Update
    if UPDATE_INIT:
        new_ver = write_init_version(major, minor, patch)
        print(f"✅ Updated __init__.py to '{new_ver}'")
    if UPDATE_MANIFEST:
        new_ver = write_manifest_version(major, minor, patch)
        print(f"✅ Updated blender_manifest.toml to '{new_ver}'")
    
    # Git
    rel_init_file = Path.relative_to(INIT_FILE, CURRENT_DIR)
    rel_manifest_file = Path.relative_to(MANIFEST_FILE, CURRENT_DIR)
    subprocess.run(["git", "add", str(rel_init_file), str(rel_manifest_file)])
    subprocess.run(["git", "commit", "-m", f"build: version bump to {new_ver}"])


if __name__ == "__main__":
    main()