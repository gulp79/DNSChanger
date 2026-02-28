"""Build script for DNSChanger."""

import sys
import subprocess
import shutil
from pathlib import Path

def clean_build():
    """Clean build directories."""
    print("Cleaning build directories...")
    dirs_to_clean = ["build", "dist", "__pycache__"]
    
    for dir_name in dirs_to_clean:
        dir_path = Path(dir_name)
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"  Removed {dir_name}/")
    
    # Clean pycache in subdirectories
    for pycache in Path(".").rglob("__pycache__"):
        shutil.rmtree(pycache)
        print(f"  Removed {pycache}")
    
    print("✓ Clean complete\n")


def build_pyinstaller():
    """Build using PyInstaller."""
    print("Building with PyInstaller...")
    print("=" * 60)
    
    try:
        subprocess.run(
            ["pyinstaller", "DNSChanger.spec"],
            check=True
        )
        print("\n✓ PyInstaller build complete")
        print(f"  Executable: dist/DNSChanger.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ PyInstaller build failed: {e}")
        return False
    except FileNotFoundError:
        print("\n✗ PyInstaller not found. Install with: pip install pyinstaller")
        return False


def build_nuitka():
    """Build using Nuitka."""
    print("Building with Nuitka...")
    print("=" * 60)
    print("Note: This may take 10-15 minutes...")
    
    cmd = [
        "python", "-m", "nuitka",
        "--standalone",
        "--onefile",
        "--windows-console-mode=disable",
        "--enable-plugin=tk-inter",
        "--windows-uac-admin",
        "--output-filename=DNSChanger.exe",
        "dns_changer.py"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("\n✓ Nuitka build complete")
        print(f"  Executable: DNSChanger.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Nuitka build failed: {e}")
        return False
    except FileNotFoundError:
        print("\n✗ Nuitka not found. Install with: pip install nuitka ordered-set")
        return False


def create_release_package(builder_name):
    """Create release package with necessary files."""
    print(f"\nCreating release package...")
    
    release_dir = Path("release")
    release_dir.mkdir(exist_ok=True)
    
    # Copy exe
    if builder_name == "pyinstaller":
        exe_src = Path("dist/DNSChanger.exe")
    else:
        exe_src = Path("DNSChanger.exe")
    
    if exe_src.exists():
        shutil.copy2(exe_src, release_dir / "DNSChanger.exe")
        print(f"  Copied DNSChanger.exe")
    
    # Copy configuration and docs
    files_to_copy = [
        "dns_providers.yaml",
        "README.md",
        "CHANGELOG.md"
    ]
    
    for filename in files_to_copy:
        src = Path(filename)
        if src.exists():
            shutil.copy2(src, release_dir / filename)
            print(f"  Copied {filename}")
    
    print(f"\n✓ Release package created in: {release_dir.absolute()}")


def main():
    """Main build script."""
    print("DNSChanger Build Script")
    print("=" * 60)
    
    if len(sys.argv) < 2:
        print("Usage: python build.py [pyinstaller|nuitka|clean|all]")
        print("\nOptions:")
        print("  pyinstaller  - Build using PyInstaller (fast)")
        print("  nuitka       - Build using Nuitka (optimized, slower)")
        print("  clean        - Clean build directories")
        print("  all          - Clean and build with both")
        return
    
    command = sys.argv[1].lower()
    
    if command == "clean":
        clean_build()
    
    elif command == "pyinstaller":
        clean_build()
        if build_pyinstaller():
            create_release_package("pyinstaller")
    
    elif command == "nuitka":
        clean_build()
        if build_nuitka():
            create_release_package("nuitka")
    
    elif command == "all":
        clean_build()
        
        print("\n" + "=" * 60)
        print("Building with PyInstaller...")
        print("=" * 60)
        if build_pyinstaller():
            create_release_package("pyinstaller")
        
        print("\n" + "=" * 60)
        print("Building with Nuitka...")
        print("=" * 60)
        if build_nuitka():
            create_release_package("nuitka")
    
    else:
        print(f"Unknown command: {command}")
        print("Use 'python build.py' for help")


if __name__ == "__main__":
    main()
