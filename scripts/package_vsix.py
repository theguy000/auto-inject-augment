"""
Package modified extension into VSIX file.

Uses vsce (Visual Studio Code Extension Manager) to create VSIX package.
"""

import os
import sys
import subprocess
import json
import shutil
from pathlib import Path


def get_version_info():
    """
    Get version information from download metadata.
    
    Returns:
        dict: Version info or None
    """
    version_file = Path("download/version.json")
    
    if not version_file.exists():
        print("⚠ Version info not found, using default")
        return {"version": "0.585.0"}
    
    with open(version_file, 'r') as f:
        return json.load(f)


def package_with_vsce(extension_dir, output_dir, version):
    """
    Package extension using vsce.
    
    Args:
        extension_dir: Path to extension directory
        output_dir: Output directory for VSIX
        version: Version string
    
    Returns:
        str: Path to created VSIX or None
    """
    extension_path = Path(extension_dir)
    output_path = Path(output_dir)
    
    if not extension_path.exists():
        print(f"✗ Extension directory not found: {extension_path}")
        return None
    
    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Output filename
    output_filename = f"augment-privacy-protected-{version}.vsix"
    output_file = output_path / output_filename
    
    # Remove existing file
    if output_file.exists():
        print(f"Removing existing VSIX: {output_file}")
        output_file.unlink()
    
    print(f"Packaging extension...")
    print(f"Extension directory: {extension_path}")
    print(f"Output file: {output_file}")
    print()
    
    try:
        # Run vsce package command
        cmd = [
            "vsce",
            "package",
            "--no-dependencies",
            "--out",
            str(output_file)
        ]
        
        print(f"Running: {' '.join(cmd)}")
        print()
        
        # Execute in extension directory
        result = subprocess.run(
            cmd,
            cwd=extension_path,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Print output
        if result.stdout:
            print(result.stdout)
        
        if result.stderr:
            print(result.stderr)
        
        # Verify file was created
        if output_file.exists():
            file_size = output_file.stat().st_size
            file_size_mb = file_size / (1024 * 1024)
            print(f"✓ VSIX created successfully!")
            print(f"  File: {output_file}")
            print(f"  Size: {file_size_mb:.2f} MB")
            return str(output_file)
        else:
            print(f"✗ VSIX file was not created")
            return None
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Error running vsce:")
        print(f"  Exit code: {e.returncode}")
        if e.stdout:
            print(f"  Output: {e.stdout}")
        if e.stderr:
            print(f"  Error: {e.stderr}")
        return None
    except FileNotFoundError:
        print(f"✗ vsce command not found")
        print(f"  Install with: npm install -g @vscode/vsce")
        return None
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return None


def create_logs_directory():
    """Create logs directory for build logs."""
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    return logs_dir


def main():
    """Main function to package VSIX."""
    print("=" * 60)
    print("VSIX Packager")
    print("=" * 60)
    print()
    
    # Get version info
    version_info = get_version_info()
    version = version_info.get("version", "0.585.0")
    
    print(f"Version: {version}")
    print()
    
    # Create logs directory
    logs_dir = create_logs_directory()
    
    # Package extension
    extension_dir = "extracted/extension"
    output_dir = "output"
    
    result = package_with_vsce(extension_dir, output_dir, version)
    
    if result:
        print()
        print("=" * 60)
        print("Packaging completed successfully!")
        print("=" * 60)
        print()
        print("Next steps:")
        print(f"  1. Install: code --install-extension {result}")
        print(f"  2. Or use VSCode UI: Extensions → ... → Install from VSIX")
        return 0
    else:
        print()
        print("=" * 60)
        print("Packaging failed!")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())

