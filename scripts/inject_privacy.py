"""
Inject privacy protection (device-spoofer.js) into Augment extension HTML files.

This script:
1. Copies device-spoofer.js to extension/privacy-protection/
2. Injects script tag into all HTML webview files
3. Ensures script loads BEFORE any telemetry code
"""

import os
import sys
import re
import shutil
from pathlib import Path


# HTML files to modify in extension/common-webviews/
HTML_FILES = [
    'main-panel.html',
    'index.html',
    'settings.html',
    'secrets-home.html',
    'memories.html',
    'history.html',
    'diff-view.html',
    'rules.html',
    'preference.html',
    'remote-agent-home.html',
    'remote-agent-diff.html',
    'next-edit-suggestions.html'
]

# Script tag to inject (with nonce for CSP)
SCRIPT_TAG = '    <!-- PRIVACY PROTECTION: Load device spoofer FIRST before any telemetry -->\n    <script src="../privacy-protection/device-spoofer.js" nonce="nonce-NdJS6eXuvR9e2+J/eS0faQ=="></script>\n'


def copy_device_spoofer(extracted_dir):
    """
    Copy device-spoofer.js to extension/privacy-protection/ directory.
    
    Args:
        extracted_dir: Path to extracted VSIX contents
    
    Returns:
        bool: True if successful
    """
    source_file = Path("privacy-protection/device-spoofer.js")
    
    if not source_file.exists():
        print(f"✗ Source file not found: {source_file}")
        return False
    
    # Create privacy-protection directory in extension
    target_dir = Path(extracted_dir) / "extension" / "privacy-protection"
    target_dir.mkdir(parents=True, exist_ok=True)
    
    target_file = target_dir / "device-spoofer.js"
    
    print(f"Copying device-spoofer.js to: {target_file}")
    shutil.copy2(source_file, target_file)
    
    if target_file.exists():
        print(f"✓ device-spoofer.js copied successfully")
        return True
    else:
        print(f"✗ Failed to copy device-spoofer.js")
        return False


def inject_script_tag(html_file_path):
    """
    Inject privacy protection script tag into HTML file.
    
    Injects after <title> tag and before any other scripts.
    
    Args:
        html_file_path: Path to HTML file
    
    Returns:
        bool: True if successful
    """
    html_path = Path(html_file_path)
    
    if not html_path.exists():
        print(f"  ✗ File not found: {html_path}")
        return False
    
    # Read file content
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already injected
    if 'device-spoofer.js' in content:
        print(f"  ⚠ Already injected: {html_path.name}")
        return True
    
    # Find injection point: after </title> tag
    # Pattern: </title>\n followed by optional whitespace and then next tag
    pattern = r'(</title>\s*\n)'
    
    match = re.search(pattern, content)
    
    if not match:
        print(f"  ✗ Could not find </title> tag in: {html_path.name}")
        return False
    
    # Inject script tag after </title>
    injection_point = match.end()
    modified_content = content[:injection_point] + SCRIPT_TAG + content[injection_point:]
    
    # Write modified content
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(modified_content)
    
    print(f"  ✓ Injected: {html_path.name}")
    return True


def inject_all_html_files(extracted_dir):
    """
    Inject privacy protection into all HTML webview files.
    
    Args:
        extracted_dir: Path to extracted VSIX contents
    
    Returns:
        tuple: (success_count, total_count)
    """
    webviews_dir = Path(extracted_dir) / "extension" / "common-webviews"
    
    if not webviews_dir.exists():
        print(f"✗ Webviews directory not found: {webviews_dir}")
        return 0, 0
    
    print(f"\nInjecting privacy protection into HTML files...")
    print(f"Directory: {webviews_dir}")
    print()
    
    success_count = 0
    total_count = len(HTML_FILES)
    
    for html_file in HTML_FILES:
        html_path = webviews_dir / html_file
        if inject_script_tag(html_path):
            success_count += 1
    
    return success_count, total_count


def main():
    """Main function to inject privacy protection."""
    print("=" * 60)
    print("Privacy Protection Injector")
    print("=" * 60)
    print()
    
    extracted_dir = "extracted"
    
    if not Path(extracted_dir).exists():
        print(f"✗ Extracted directory not found: {extracted_dir}")
        return 1
    
    # Step 1: Copy device-spoofer.js
    print("[Step 1/2] Copying device-spoofer.js...")
    if not copy_device_spoofer(extracted_dir):
        return 1
    
    # Step 2: Inject into HTML files
    print("\n[Step 2/2] Injecting into HTML files...")
    success_count, total_count = inject_all_html_files(extracted_dir)
    
    print()
    print("=" * 60)
    print(f"Injection Results: {success_count}/{total_count} files modified")
    print("=" * 60)
    
    if success_count == total_count:
        print("✓ All files injected successfully!")
        return 0
    else:
        print(f"⚠ Warning: Only {success_count}/{total_count} files were modified")
        return 1


if __name__ == "__main__":
    sys.exit(main())

