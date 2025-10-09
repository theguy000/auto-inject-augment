"""
Find differences between extracted and patched extension.js files.

This script identifies the exact changes made to the extension.js file
in the patched version.
"""

import sys
from pathlib import Path
import difflib


def read_file(file_path):
    """Read file content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None


def find_differences(file1_path, file2_path, context_lines=5):
    """
    Find differences between two files.
    
    Args:
        file1_path: Path to first file (extracted)
        file2_path: Path to second file (patched)
        context_lines: Number of context lines to show
    
    Returns:
        str: Diff output
    """
    print(f"Reading {file1_path}...")
    content1 = read_file(file1_path)
    
    print(f"Reading {file2_path}...")
    content2 = read_file(file2_path)
    
    if content1 is None or content2 is None:
        return None
    
    print(f"\nFile 1 size: {len(content1):,} characters")
    print(f"File 2 size: {len(content2):,} characters")
    print(f"Difference: {len(content2) - len(content1):+,} characters")
    print()
    
    # Split into lines for diff
    lines1 = content1.splitlines(keepends=True)
    lines2 = content2.splitlines(keepends=True)
    
    print(f"File 1 lines: {len(lines1):,}")
    print(f"File 2 lines: {len(lines2):,}")
    print()
    
    # Generate unified diff
    diff = difflib.unified_diff(
        lines1,
        lines2,
        fromfile='extracted/extension.js',
        tofile='patched/extension.js',
        lineterm='',
        n=context_lines
    )
    
    return list(diff)


def analyze_diff(diff_lines):
    """
    Analyze diff to find added/removed sections.
    
    Args:
        diff_lines: List of diff lines
    
    Returns:
        dict: Analysis results
    """
    added_lines = []
    removed_lines = []
    changed_sections = []
    
    current_section = None
    
    for line in diff_lines:
        if line.startswith('@@'):
            if current_section:
                changed_sections.append(current_section)
            current_section = {
                'header': line,
                'added': [],
                'removed': [],
                'context': []
            }
        elif current_section:
            if line.startswith('+') and not line.startswith('+++'):
                current_section['added'].append(line[1:])
                added_lines.append(line[1:])
            elif line.startswith('-') and not line.startswith('---'):
                current_section['removed'].append(line[1:])
                removed_lines.append(line[1:])
            elif not line.startswith('\\'):
                current_section['context'].append(line[1:] if line.startswith(' ') else line)
    
    if current_section:
        changed_sections.append(current_section)
    
    return {
        'added_lines': added_lines,
        'removed_lines': removed_lines,
        'changed_sections': changed_sections,
        'total_added': len(added_lines),
        'total_removed': len(removed_lines),
        'total_sections': len(changed_sections)
    }


def save_diff(diff_lines, output_file):
    """Save diff to file."""
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(diff_lines)
    
    print(f"✅ Diff saved to: {output_path}")


def save_analysis(analysis, output_file):
    """Save analysis to file."""
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Extension.js Diff Analysis\n\n")
        f.write(f"## Summary\n\n")
        f.write(f"- Total changed sections: {analysis['total_sections']}\n")
        f.write(f"- Total added lines: {analysis['total_added']}\n")
        f.write(f"- Total removed lines: {analysis['total_removed']}\n")
        f.write(f"- Net change: {analysis['total_added'] - analysis['total_removed']:+} lines\n\n")
        
        f.write(f"## Changed Sections\n\n")
        for i, section in enumerate(analysis['changed_sections'], 1):
            f.write(f"### Section {i}\n\n")
            f.write(f"```\n{section['header']}\n```\n\n")
            
            if section['removed']:
                f.write(f"**Removed ({len(section['removed'])} lines)**:\n```\n")
                for line in section['removed'][:20]:  # Show first 20 lines
                    f.write(line)
                if len(section['removed']) > 20:
                    f.write(f"\n... and {len(section['removed']) - 20} more lines\n")
                f.write("```\n\n")
            
            if section['added']:
                f.write(f"**Added ({len(section['added'])} lines)**:\n```\n")
                for line in section['added'][:20]:  # Show first 20 lines
                    f.write(line)
                if len(section['added']) > 20:
                    f.write(f"\n... and {len(section['added']) - 20} more lines\n")
                f.write("```\n\n")
            
            f.write("---\n\n")
    
    print(f"✅ Analysis saved to: {output_path}")


def main():
    """Main function."""
    base_dir = Path(__file__).parent.parent.parent
    file1 = base_dir / "reference_mod" / "extracted" / "extension" / "out" / "extension.js"
    file2 = base_dir / "reference_mod" / "vscode-augment-0.561.0-patched" / "extension" / "out" / "extension.js"
    
    print("=" * 80)
    print("Extension.js Diff Finder")
    print("=" * 80)
    print()
    
    # Verify files exist
    if not file1.exists():
        print(f"❌ File not found: {file1}")
        return 1
    
    if not file2.exists():
        print(f"❌ File not found: {file2}")
        return 1
    
    # Find differences
    diff_lines = find_differences(file1, file2, context_lines=3)
    
    if diff_lines is None:
        return 1
    
    # Save full diff
    diff_output = base_dir / "auto-inject-augment" / "output" / "extension_diff.txt"
    save_diff(diff_lines, diff_output)
    
    # Analyze diff
    print("Analyzing differences...")
    analysis = analyze_diff(diff_lines)
    
    print()
    print("=" * 80)
    print("ANALYSIS RESULTS")
    print("=" * 80)
    print(f"Total changed sections: {analysis['total_sections']}")
    print(f"Total added lines: {analysis['total_added']}")
    print(f"Total removed lines: {analysis['total_removed']}")
    print(f"Net change: {analysis['total_added'] - analysis['total_removed']:+} lines")
    print()
    
    # Save analysis
    analysis_output = base_dir / "auto-inject-augment" / "output" / "extension_diff_analysis.md"
    save_analysis(analysis, analysis_output)
    
    # Show first few added lines
    if analysis['added_lines']:
        print("=" * 80)
        print("SAMPLE OF ADDED CONTENT (first 30 lines)")
        print("=" * 80)
        for line in analysis['added_lines'][:30]:
            print(line.rstrip())
        if len(analysis['added_lines']) > 30:
            print(f"\n... and {len(analysis['added_lines']) - 30} more lines")
    
    print()
    print("=" * 80)
    print("✅ DIFF ANALYSIS COMPLETED")
    print("=" * 80)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

