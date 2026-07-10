#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Release management script for JMF-Python tools.
Extracts version from README.md and updates all version-related files.
"""

import re
import sys
import argparse
from pathlib import Path


def get_version():
    """Read the version string from README.md and return (tag, (major, minor, patch))."""
    readme = Path(__file__).resolve().parent.parent / 'README.md'
    try:
        first_line = readme.read_text(encoding='utf-8').splitlines()[0]
        match = re.search(r'R(\d+)\.(\d+)\.(\d+)', first_line)
        if match:
            return match.group(0), tuple(int(x) for x in match.groups())
    except Exception as e:
        print(f"[ERROR] Failed to read README.md: {e}")
        return None, None
    
    print("[ERROR] Could not find version in README.md (expected format: R#.#.#)")
    return None, None


def get_version_files(buildspec_dir):
    """Get list of all version-related files in buildspec."""
    version_files = []
    
    # Find all *_version_info.txt files
    for txt_file in buildspec_dir.glob('*_version_info.txt'):
        version_files.append(txt_file)
    
    return sorted(version_files)


def generate_version_info(tool, version_str, version_tuple):
    """Generate content for a PyInstaller version resource file."""
    major, minor, patch = version_tuple
    content = (
        'VSVersionInfo(\n'
        '  ffi=FixedFileInfo(\n'
        f'    filevers=({major}, {minor}, {patch}, 0),\n'
        f'    prodvers=({major}, {minor}, {patch}, 0),\n'
        '    mask=0x3f,\n'
        '    flags=0x0,\n'
        '    OS=0x4,\n'
        '    fileType=0x1,\n'
        '    subtype=0x0,\n'
        '    date=(0, 0)\n'
        '  ),\n'
        '  kids=[\n'
        '    StringFileInfo(\n'
        '      [\n'
        '      StringTable(\n'
        "        u'040904B0',\n"
        "        [StringStruct(u'CompanyName', u'Canon Production Printing'),\n"
        f"        StringStruct(u'FileDescription', u'{tool}'),\n"
        f"        StringStruct(u'FileVersion', u'{major}.{minor}.{patch}.0'),\n"
        f"        StringStruct(u'InternalName', u'{tool}'),\n"
        f"        StringStruct(u'OriginalFilename', u'{tool}.exe'),\n"
        "        StringStruct(u'ProductName', u'JMF Python Tools'),\n"
        f"        StringStruct(u'ProductVersion', u'{major}.{minor}.{patch}.0')])\n"
        '      ]),\n'
        "    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])\n"
        '  ]\n'
        ')\n'
    )
    return content


def update_readme_version(buildspec_dir, version_str, dry_run=False):
    """Update the version heading in Tools/README.md."""
    readme = buildspec_dir.parent / 'Tools' / 'README.md'
    if not readme.exists():
        print(f"[WARN] Tools/README.md not found: {readme}")
        return False

    content = readme.read_text(encoding='utf-8')
    new_content = re.sub(r'^(# JMF Tools) R\d+\.\d+\.\d+', f'\\1 {version_str}', content, count=1, flags=re.MULTILINE)

    if new_content == content:
        print(f"[WARN] Version heading not found or already up to date in Tools/README.md")
        return False

    if dry_run:
        print(f"[DRY-RUN] Would update: Tools/README.md")
    else:
        readme.write_text(new_content, encoding='utf-8')
        print(f"[OK] Updated: Tools/README.md ({version_str})")
    return True


def update_version_files(buildspec_dir, version_str, version_tuple, dry_run=False):
    """Update all version files with the new version."""
    version_files = get_version_files(buildspec_dir)
    
    if not version_files:
        print("[WARN] No version files found")
        return 0
    
    updated = 0
    
    for ver_file in version_files:
        # Extract tool name from filename (e.g., "CreateMimePackage_version_info.txt" -> "CreateMimePackage")
        tool = ver_file.stem.replace('_version_info', '')
        
        new_content = generate_version_info(tool, version_str, version_tuple)
        
        if dry_run:
            print(f"[DRY-RUN] Would update: {ver_file.name}")
            updated += 1
        else:
            try:
                ver_file.write_text(new_content, encoding='utf-8')
                print(f"[OK] Updated: {ver_file.name} ({version_str})")
                updated += 1
            except Exception as e:
                print(f"[ERROR] Failed to update {ver_file.name}: {e}")
    
    return updated


def list_version_files(buildspec_dir):
    """List all version files and their current content."""
    version_files = get_version_files(buildspec_dir)

    print("\nVersion files:")
    print("=" * 60)

    # Show Tools/README.md first as source-of-truth follower
    tools_readme = buildspec_dir.parent / 'Tools' / 'README.md'
    print(f"\n  File: Tools/README.md")
    if tools_readme.exists():
        try:
            content = tools_readme.read_text(encoding='utf-8')
            match = re.search(r'^# JMF Tools (R\d+\.\d+\.\d+)', content, re.MULTILINE)
            if match:
                print(f"  Current Version: {match.group(1)}")
            else:
                print(f"  Current Version: (not found)")
        except Exception as e:
            print(f"  Error reading: {e}")
    else:
        print(f"  (file not found)")

    if not version_files:
        print("\n[WARN] No version info files found")
    else:
        for ver_file in version_files:
            tool = ver_file.stem.replace('_version_info', '')
            print(f"\n  File: {ver_file.name}")
            print(f"  Tool: {tool}")

            try:
                content = ver_file.read_text(encoding='utf-8')
                match = re.search(r"FileVersion', u'(\d+\.\d+\.\d+)", content)
                if match:
                    print(f"  Current Version: {match.group(1)}")
            except Exception as e:
                print(f"  Error reading: {e}")

    print("\n" + "=" * 60)


def main():
    """Parse arguments and execute version update operations."""
    parser = argparse.ArgumentParser(
        description="Release management for JMF-Python tools. Updates all version information from README.md."
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all version files and their current versions'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be updated without making changes'
    )
    parser.add_argument(
        '--update',
        action='store_true',
        help='Update all version files with version from README.md'
    )
    
    args = parser.parse_args()
    
    buildspec_dir = Path(__file__).resolve().parent
    
    # If no arguments provided, show help and list current versions
    if not any([args.list, args.dry_run, args.update]):
        parser.print_help()
        print("\n")
        list_version_files(buildspec_dir)
        return 0
    
    # Read version from README.md
    version_str, version_tuple = get_version()
    if not version_str:
        return 1
    
    print(f"\nVersion from README.md: {version_str}")
    print(f"Version tuple: {version_tuple}")
    print()
    
    if args.list:
        list_version_files(buildspec_dir)
        return 0
    
    if args.dry_run or args.update:
        updated = update_version_files(buildspec_dir, version_str, version_tuple, dry_run=args.dry_run)
        update_readme_version(buildspec_dir, version_str, dry_run=args.dry_run)
        
        print()
        print("=" * 60)
        if args.dry_run:
            print(f"[DRY-RUN] Would update {updated} version file(s) and Tools/README.md")
            print("Run with --update to apply changes")
        else:
            print(f"[OK] Updated {updated} version file(s) and Tools/README.md")
        print("=" * 60)
        
        return 0
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
