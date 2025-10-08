"""
Main build orchestrator for privacy-protected Augment extension.

This script coordinates the entire build process:
1. Download latest extension
2. Extract VSIX
3. Inject privacy protection
4. Run tests
5. Package modified VSIX
"""

import sys
import subprocess
from pathlib import Path


def run_script(script_path, description):
    """
    Run a Python script and handle errors.
    
    Args:
        script_path: Path to script
        description: Description for logging
    
    Returns:
        bool: True if successful
    """
    print()
    print("=" * 60)
    print(f"{description}")
    print("=" * 60)
    print()
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            check=True,
            capture_output=False
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Error: {description} failed with exit code {e.returncode}")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return False


def main():
    """Main build function."""
    print("=" * 60)
    print("Augment Privacy-Protected Extension Builder")
    print("=" * 60)
    print()
    print("This script will:")
    print("  1. Download latest Augment extension")
    print("  2. Extract VSIX contents")
    print("  3. Inject privacy protection")
    print("  4. Run verification tests")
    print("  5. Package modified VSIX")
    print()
    
    scripts_dir = Path("scripts")
    
    # Step 1: Download
    if not run_script(scripts_dir / "download_extension.py", "Step 1: Download Extension"):
        return 1
    
    # Step 2: Extract
    if not run_script(scripts_dir / "extract_vsix.py", "Step 2: Extract VSIX"):
        return 1
    
    # Step 3: Inject
    if not run_script(scripts_dir / "inject_privacy.py", "Step 3: Inject Privacy Protection"):
        return 1
    
    # Step 4: Test
    print()
    print("=" * 60)
    print("Step 4: Run Verification Tests")
    print("=" * 60)
    print()
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-v"],
            check=True
        )
    except subprocess.CalledProcessError:
        print("\n✗ Tests failed!")
        return 1
    
    # Step 5: Package
    if not run_script(scripts_dir / "package_vsix.py", "Step 5: Package VSIX"):
        return 1
    
    # Success
    print()
    print("=" * 60)
    print("✓ BUILD COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print()
    print("Output:")
    
    # List output files
    output_dir = Path("output")
    if output_dir.exists():
        vsix_files = list(output_dir.glob("*.vsix"))
        for vsix_file in vsix_files:
            file_size = vsix_file.stat().st_size / (1024 * 1024)
            print(f"  {vsix_file} ({file_size:.2f} MB)")
    
    print()
    print("Installation:")
    print("  code --install-extension output/augment-privacy-protected-*.vsix")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

