"""
Inject privacy protection into Augment extension.js file.

This script implements the injection method described in diff_summary.md:
1. Reads the privacy protection code from test.js
2. Base64 encodes it
3. Wraps it in a self-executing function with decoder
4. Injects at the beginning of extension/extension.js
5. Adds // __AUG_INIT marker comment

The injected code will:
- Spoof device fingerprints (Machine IDs, UUIDs, serial numbers)
- Intercept HTTP/HTTPS requests
- Spoof system command outputs
- Randomize session IDs
- Strip telemetry data
"""

import os
import sys
import base64
from pathlib import Path


def read_privacy_code():
    """
    Read the privacy protection code from test.js.
    
    Returns:
        str: The privacy protection JavaScript code
    """
    test_file = Path("privacy-protection/test.js")
    
    if not test_file.exists():
        print(f"[ERROR] Privacy protection code not found: {test_file}")
        return None
    
    with open(test_file, 'r', encoding='utf-8') as f:
        code = f.read()
    
    print(f"[OK] Read privacy protection code ({len(code)} bytes)")
    return code


def encode_to_base64(code):
    """
    Encode JavaScript code to Base64.
    
    Args:
        code: JavaScript code string
    
    Returns:
        str: Base64 encoded string
    """
    encoded = base64.b64encode(code.encode('utf-8')).decode('utf-8')
    print(f"[OK] Encoded to Base64 ({len(encoded)} bytes)")
    return encoded


def create_injection_code(base64_code):
    """
    Create the injection code that will be prepended to extension.js.
    
    This creates a self-executing function that:
    1. Contains the Base64-encoded payload
    2. Decodes it using Buffer.from()
    3. Executes it using eval()
    
    Args:
        base64_code: Base64 encoded privacy protection code
    
    Returns:
        str: Complete injection code with marker
    """
    injection = f"""// __AUG_INIT
(function(){{
  const cfg = '{base64_code}';
  const dec = (d) => Buffer.from(d, 'base64').toString('utf8');
  eval(dec(cfg));
}})();

"""
    return injection


def inject_into_extension_js(extracted_dir, injection_code):
    """
    Inject privacy protection code into extension/extension.js.
    
    Prepends the injection code to the beginning of the file.
    
    Args:
        extracted_dir: Path to extracted VSIX contents
        injection_code: Code to inject
    
    Returns:
        bool: True if successful
    """
    extension_js = Path(extracted_dir) / "extension" / "extension.js"
    
    if not extension_js.exists():
        print(f"[ERROR] extension.js not found: {extension_js}")
        print(f"[DEBUG] Checking extracted directory structure...")
        extracted_path = Path(extracted_dir)
        if extracted_path.exists():
            print(f"[DEBUG] Contents of {extracted_dir}:")
            for item in extracted_path.iterdir():
                print(f"  - {item.name}")
                if item.is_dir() and item.name == "extension":
                    print(f"[DEBUG] Contents of extension/:")
                    for subitem in item.iterdir():
                        print(f"    - {subitem.name}")
        return False
    
    print(f"Reading: {extension_js}")
    
    # Read original content
    with open(extension_js, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    # Check if already injected
    if '// __AUG_INIT' in original_content:
        print(f"[WARNING] Already injected (found // __AUG_INIT marker)")
        return True
    
    # Create modified content: injection + original
    modified_content = injection_code + original_content
    
    # Write modified content
    with open(extension_js, 'w', encoding='utf-8') as f:
        f.write(modified_content)
    
    # Verify injection
    with open(extension_js, 'r', encoding='utf-8') as f:
        verify_content = f.read()
    
    if not verify_content.startswith('// __AUG_INIT'):
        print(f"[ERROR] Injection verification failed")
        return False
    
    original_lines = original_content.count('\n')
    injected_lines = injection_code.count('\n')
    modified_lines = modified_content.count('\n')
    
    print(f"[OK] Injected successfully")
    print(f"  Original lines: {original_lines}")
    print(f"  Injected lines: {injected_lines}")
    print(f"  Modified lines: {modified_lines}")
    print(f"  Net change: +{injected_lines} lines")
    
    return True


def main():
    """Main function to inject privacy protection."""
    print("=" * 70)
    print("Privacy Protection Injector - extension.js Direct Injection")
    print("=" * 70)
    print()
    print("This script implements the injection method described in:")
    print("  output/diff_summary.md")
    print()
    print("Injection method:")
    print("  1. Read privacy protection code from test.js")
    print("  2. Encode to Base64")
    print("  3. Wrap in self-executing function with decoder")
    print("  4. Inject at beginning of extension/extension.js")
    print("  5. Add // __AUG_INIT marker")
    print()
    print("=" * 70)
    print()
    
    extracted_dir = "extracted"
    
    if not Path(extracted_dir).exists():
        print(f"[ERROR] Extracted directory not found: {extracted_dir}")
        print(f"  Run extract_vsix.py first")
        return 1
    
    # Step 1: Read privacy protection code
    print("[Step 1/4] Reading privacy protection code...")
    privacy_code = read_privacy_code()
    if not privacy_code:
        return 1
    print()
    
    # Step 2: Encode to Base64
    print("[Step 2/4] Encoding to Base64...")
    base64_code = encode_to_base64(privacy_code)
    print()
    
    # Step 3: Create injection code
    print("[Step 3/4] Creating injection wrapper...")
    injection_code = create_injection_code(base64_code)
    print(f"[OK] Created injection code ({len(injection_code)} bytes)")
    print(f"  Structure:")
    print(f"    - Marker comment: // __AUG_INIT")
    print(f"    - Self-executing function")
    print(f"    - Base64 decoder using Buffer.from()")
    print(f"    - eval() execution")
    print()
    
    # Step 4: Inject into extension.js
    print("[Step 4/4] Injecting into extension/extension.js...")
    if not inject_into_extension_js(extracted_dir, injection_code):
        return 1
    
    print()
    print("=" * 70)
    print("[OK] INJECTION COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print()
    print("What was injected:")
    print("  - 7 lines at the beginning of extension/extension.js")
    print("  - Marker: // __AUG_INIT")
    print("  - Base64-encoded privacy protection payload")
    print("  - Self-decoding and self-executing wrapper")
    print()
    print("Privacy features enabled:")
    print("  [OK] Session ID spoofing")
    print("  [OK] Device fingerprint spoofing (Machine IDs, UUIDs, serials)")
    print("  [OK] HTTP/HTTPS request interception")
    print("  [OK] System command output spoofing (ioreg, REG, wmic, git)")
    print("  [OK] Telemetry data stripping")
    print("  [OK] Fetch/Axios/XHR interception")
    print()
    print("Next steps:")
    print("  1. Run tests: python -m pytest tests/ -v")
    print("  2. Package: python scripts/package_vsix.py")
    print("  3. Install: code --install-extension output/*.vsix")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
