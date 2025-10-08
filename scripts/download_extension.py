"""
Download latest Augment VSCode extension from Visual Studio Marketplace.

This script downloads the VSIX file for automated processing.
"""

import os
import sys
import requests
from pathlib import Path
import json


def get_latest_version(publisher, extension_name):
    """
    Get the latest version of the extension from the marketplace API.
    
    Args:
        publisher: Publisher name
        extension_name: Extension name
    
    Returns:
        str: Version number or None if not found
    """
    api_url = "https://marketplace.visualstudio.com/_apis/public/gallery/extensionquery"
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json;api-version=3.0-preview.1"
    }
    
    payload = {
        "filters": [{
            "criteria": [{
                "filterType": 7,
                "value": f"{publisher}.{extension_name}"
            }],
            "pageNumber": 1,
            "pageSize": 1
        }],
        "flags": 914
    }
    
    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('results') and len(data['results']) > 0:
            extensions = data['results'][0].get('extensions', [])
            if extensions:
                version = extensions[0].get('versions', [{}])[0].get('version')
                return version
        
        return None
    except Exception as e:
        print(f"Error fetching version info: {e}")
        return None


def download_vsix(publisher, extension_name, version, output_dir="download"):
    """
    Download VSIX file from Visual Studio Marketplace.
    
    Args:
        publisher: Publisher name
        extension_name: Extension name
        version: Version to download
        output_dir: Directory to save the downloaded file
    
    Returns:
        str: Path to downloaded file or None if download failed
    """
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Construct the download URL
    download_url = f"https://marketplace.visualstudio.com/_apis/public/gallery/publishers/{publisher}/vsextensions/{extension_name}/{version}/vspackage"
    
    # Construct output filename
    output_filename = f"{publisher}.{extension_name}-{version}.vsix"
    output_file = output_path / output_filename
    
    print(f"Downloading from: {download_url}")
    print(f"Saving to: {output_file}")
    
    try:
        # Download the file with streaming
        response = requests.get(download_url, stream=True)
        response.raise_for_status()
        
        # Get total file size
        total_size = int(response.headers.get('content-length', 0))
        
        # Download with progress
        downloaded_size = 0
        chunk_size = 8192
        
        with open(output_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    
                    if total_size > 0:
                        progress = (downloaded_size / total_size) * 100
                        print(f"\rProgress: {progress:.1f}% ({downloaded_size}/{total_size} bytes)", end='')
        
        print(f"\n✓ Successfully downloaded to: {output_file}")
        
        # Save version info
        version_info = {
            "publisher": publisher,
            "extension": extension_name,
            "version": version,
            "download_url": download_url,
            "file_path": str(output_file)
        }
        
        version_file = output_path / "version.json"
        with open(version_file, 'w') as f:
            json.dump(version_info, f, indent=2)
        
        return str(output_file)
        
    except requests.exceptions.RequestException as e:
        print(f"\n✗ Error downloading file: {e}")
        return None
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return None


def main():
    """Main function to download the extension."""
    publisher = "augment"
    extension_name = "vscode-augment"
    
    print("=" * 60)
    print("Augment Extension Downloader")
    print("=" * 60)
    print()
    
    # Get latest version
    print(f"Fetching latest version for {publisher}.{extension_name}...")
    version = get_latest_version(publisher, extension_name)
    
    if not version:
        print("✗ Could not determine latest version")
        return 1
    
    print(f"Latest version: {version}")
    print()
    
    # Download the VSIX file
    result = download_vsix(publisher, extension_name, version)
    
    if result:
        print()
        print("=" * 60)
        print("Download completed successfully!")
        print("=" * 60)
        return 0
    else:
        print()
        print("=" * 60)
        print("Download failed!")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())

