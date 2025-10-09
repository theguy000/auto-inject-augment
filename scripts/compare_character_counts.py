"""
Compare character counts between extracted and patched versions.

This script compares files in reference_mod/extracted vs reference_mod/vscode-augment-0.561.0-patched
to detect where privacy injection has been applied. Files with different character counts
indicate injection points.
"""

import os
import sys
from pathlib import Path
import json


def count_characters(file_path):
    """
    Count characters in a file.
    
    Args:
        file_path: Path to file
    
    Returns:
        int: Character count or None if file cannot be read
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            return len(content)
    except Exception as e:
        # Try binary mode for non-text files
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                return len(content)
        except Exception:
            return None


def get_all_files(directory, base_path):
    """
    Get all files in directory recursively with relative paths.
    
    Args:
        directory: Directory to scan
        base_path: Base path for relative path calculation
    
    Returns:
        dict: {relative_path: absolute_path}
    """
    files = {}
    directory = Path(directory)
    base_path = Path(base_path)
    
    for file_path in directory.rglob('*'):
        if file_path.is_file():
            relative_path = file_path.relative_to(base_path)
            files[str(relative_path)] = file_path
    
    return files


def compare_directories(extracted_dir, patched_dir):
    """
    Compare character counts between extracted and patched directories.
    
    Args:
        extracted_dir: Path to extracted directory
        patched_dir: Path to patched directory
    
    Returns:
        dict: Comparison results
    """
    print("=" * 80)
    print("Character Count Comparison: Extracted vs Patched")
    print("=" * 80)
    print()
    
    # Get all files from both directories
    print("Scanning extracted directory...")
    extracted_files = get_all_files(extracted_dir, extracted_dir)
    print(f"Found {len(extracted_files)} files in extracted")
    
    print("Scanning patched directory...")
    patched_files = get_all_files(patched_dir, patched_dir)
    print(f"Found {len(patched_files)} files in patched")
    print()
    
    # Compare files
    results = {
        'identical': [],
        'different': [],
        'only_in_extracted': [],
        'only_in_patched': [],
        'read_errors': []
    }
    
    # Check files in extracted
    for rel_path, extracted_path in extracted_files.items():
        patched_path = patched_dir / rel_path
        
        if not patched_path.exists():
            results['only_in_extracted'].append(str(rel_path))
            continue
        
        # Count characters
        extracted_count = count_characters(extracted_path)
        patched_count = count_characters(patched_path)
        
        if extracted_count is None or patched_count is None:
            results['read_errors'].append({
                'file': str(rel_path),
                'extracted_readable': extracted_count is not None,
                'patched_readable': patched_count is not None
            })
            continue
        
        if extracted_count == patched_count:
            results['identical'].append({
                'file': str(rel_path),
                'count': extracted_count
            })
        else:
            results['different'].append({
                'file': str(rel_path),
                'extracted_count': extracted_count,
                'patched_count': patched_count,
                'difference': patched_count - extracted_count,
                'percentage_change': ((patched_count - extracted_count) / extracted_count * 100) if extracted_count > 0 else 0
            })
    
    # Check files only in patched
    for rel_path in patched_files.keys():
        if rel_path not in extracted_files:
            results['only_in_patched'].append(str(rel_path))
    
    return results


def print_results(results):
    """
    Print comparison results.
    
    Args:
        results: Comparison results dictionary
    """
    print("=" * 80)
    print("COMPARISON RESULTS")
    print("=" * 80)
    print()
    
    # Summary
    print("📊 SUMMARY")
    print("-" * 80)
    print(f"✅ Identical files:        {len(results['identical'])}")
    print(f"⚠️  Different files:        {len(results['different'])}")
    print(f"📁 Only in extracted:      {len(results['only_in_extracted'])}")
    print(f"📁 Only in patched:        {len(results['only_in_patched'])}")
    print(f"❌ Read errors:            {len(results['read_errors'])}")
    print()
    
    # Different files (INJECTION POINTS)
    if results['different']:
        print("=" * 80)
        print("🔍 FILES WITH DIFFERENT CHARACTER COUNTS (INJECTION POINTS)")
        print("=" * 80)
        print()
        
        # Sort by difference (largest first)
        sorted_different = sorted(results['different'], key=lambda x: abs(x['difference']), reverse=True)
        
        for item in sorted_different:
            print(f"📄 {item['file']}")
            print(f"   Extracted:  {item['extracted_count']:,} characters")
            print(f"   Patched:    {item['patched_count']:,} characters")
            print(f"   Difference: {item['difference']:+,} characters ({item['percentage_change']:+.2f}%)")
            print()
    
    # Files only in one directory
    if results['only_in_extracted']:
        print("=" * 80)
        print("📁 FILES ONLY IN EXTRACTED")
        print("=" * 80)
        for file in results['only_in_extracted'][:20]:  # Show first 20
            print(f"   {file}")
        if len(results['only_in_extracted']) > 20:
            print(f"   ... and {len(results['only_in_extracted']) - 20} more")
        print()
    
    if results['only_in_patched']:
        print("=" * 80)
        print("📁 FILES ONLY IN PATCHED")
        print("=" * 80)
        for file in results['only_in_patched'][:20]:  # Show first 20
            print(f"   {file}")
        if len(results['only_in_patched']) > 20:
            print(f"   ... and {len(results['only_in_patched']) - 20} more")
        print()
    
    # Read errors
    if results['read_errors']:
        print("=" * 80)
        print("❌ FILES WITH READ ERRORS")
        print("=" * 80)
        for item in results['read_errors'][:10]:  # Show first 10
            print(f"   {item['file']}")
        if len(results['read_errors']) > 10:
            print(f"   ... and {len(results['read_errors']) - 10} more")
        print()


def save_results_json(results, output_file):
    """
    Save results to JSON file.
    
    Args:
        results: Comparison results
        output_file: Output file path
    """
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print(f"✅ Results saved to: {output_path}")


def main():
    """Main function."""
    # Paths
    base_dir = Path(__file__).parent.parent.parent
    extracted_dir = base_dir / "reference_mod" / "extracted" / "extension"
    patched_dir = base_dir / "reference_mod" / "vscode-augment-0.561.0-patched" / "extension"
    output_file = base_dir / "auto-inject-augment" / "output" / "comparison_results.json"
    
    # Verify directories exist
    if not extracted_dir.exists():
        print(f"❌ Extracted directory not found: {extracted_dir}")
        return 1
    
    if not patched_dir.exists():
        print(f"❌ Patched directory not found: {patched_dir}")
        return 1
    
    # Compare
    results = compare_directories(extracted_dir, patched_dir)
    
    # Print results
    print_results(results)
    
    # Save to JSON
    save_results_json(results, output_file)
    
    print()
    print("=" * 80)
    print("✅ COMPARISON COMPLETED")
    print("=" * 80)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

