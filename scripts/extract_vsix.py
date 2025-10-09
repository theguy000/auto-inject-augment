"""
Extract VSIX file contents for modification.

VSIX files are ZIP archives that can be extracted and repacked.
"""

import os
import sys
import zipfile
import json
from pathlib import Path
import shutil


def extract_vsix(vsix_path, output_dir="extracted"):
    """
    Extract VSIX file contents.
    
    Args:
        vsix_path: Path to VSIX file
        output_dir: Directory to extract contents
    
    Returns:
        bool: True if successful, False otherwise
    """
    vsix_file = Path(vsix_path)
    output_path = Path(output_dir)
    
    if not vsix_file.exists():
        print(f"[ERROR] VSIX file not found: {vsix_path}")
        return False
    
    # Remove existing extraction directory
    if output_path.exists():
        print(f"Removing existing extraction directory: {output_path}")
        shutil.rmtree(output_path)
    
    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Extracting VSIX: {vsix_file}")
    print(f"Output directory: {output_path}")
    
    try:
        with zipfile.ZipFile(vsix_file, 'r') as zip_ref:
            # Get list of files
            file_list = zip_ref.namelist()
            total_files = len(file_list)
            
            print(f"Total files to extract: {total_files}")
            
            # Extract all files
            for i, file in enumerate(file_list, 1):
                zip_ref.extract(file, output_path)
                if i % 100 == 0 or i == total_files:
                    print(f"\rProgress: {i}/{total_files} files", end='')
            
            print()  # New line after progress
        
        print(f"[OK] Successfully extracted to: {output_path}")
        
        # Verify extraction
        extension_dir = output_path / "extension"
        if not extension_dir.exists():
            print("[WARNING] 'extension' directory not found in extracted contents")
            print("[DEBUG] Top-level directories found:")
            for item in output_path.iterdir():
                if item.is_dir():
                    print(f"  - {item.name}/")
        else:
            print(f"[OK] Found extension directory")
            extension_js = extension_dir / "extension.js"
            if extension_js.exists():
                print(f"[OK] Found extension.js ({extension_js.stat().st_size} bytes)")
            else:
                print(f"[WARNING] extension.js not found in extension directory")
                print("[DEBUG] Files in extension/ directory:")
                for item in extension_dir.iterdir():
                    print(f"  - {item.name}")
        
        return True
        
    except zipfile.BadZipFile:
        print(f"[ERROR] Invalid VSIX file (not a valid ZIP archive)")
        return False
    except Exception as e:
        print(f"[ERROR] Error extracting VSIX: {e}")
        return False


def main():
    """Main function to extract VSIX."""
    print("=" * 60)
    print("VSIX Extractor")
    print("=" * 60)
    print()
    
    # Find VSIX file in download directory
    download_dir = Path("download")
    
    if not download_dir.exists():
        print("[ERROR] Download directory not found")
        return 1
    
    # Find VSIX file
    vsix_files = list(download_dir.glob("*.vsix"))
    
    if not vsix_files:
        print("[ERROR] No VSIX file found in download directory")
        return 1
    
    if len(vsix_files) > 1:
        print(f"[WARNING] Multiple VSIX files found, using: {vsix_files[0]}")
    
    vsix_path = vsix_files[0]
    
    # Extract
    success = extract_vsix(vsix_path)
    
    if success:
        print()
        print("=" * 60)
        print("Extraction completed successfully!")
        print("=" * 60)
        return 0
    else:
        print()
        print("=" * 60)
        print("Extraction failed!")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())

