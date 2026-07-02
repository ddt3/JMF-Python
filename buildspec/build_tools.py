#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Build script for JMF tools.
Builds specified tools using PyInstaller.
"""

import os
import re
import sys
import subprocess
import shutil
import argparse
import stat
from pathlib import Path

# Define the tools to build
TOOLS = [
    'ReceiveSignals',
    'CreateMimePackage',
    'JMFSubmitter',
    'RemoveQueueEntries',
    'CreateTestPDF',
    'SetupConfig',
]


def get_version():
    """Read the version string from README.md and return (tag, (major, minor, patch))."""
    readme = Path(__file__).resolve().parent.parent / 'README.md'
    try:
        first_line = readme.read_text(encoding='utf-8').splitlines()[0]
        match = re.search(r'R(\d+)\.(\d+)\.(\d+)', first_line)
        if match:
            return match.group(0), tuple(int(x) for x in match.groups())
    except Exception:
        pass
    return None, None


def generate_version_info(buildspec_dir, tool, version_str, version_tuple):
    """Write a PyInstaller version resource file for the given tool."""
    major, minor, patch = version_tuple
    ver_file = buildspec_dir / f'{tool}_version_info.txt'
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
    ver_file.write_text(content, encoding='utf-8')
    return ver_file


def _handle_remove_readonly(func, path, exc_info):
    """Retry failed delete operations after clearing read-only attributes."""
    exc = exc_info[1]
    winerror = getattr(exc, 'winerror', None)
    if isinstance(exc, PermissionError) or winerror == 5:
        os.chmod(path, stat.S_IWRITE)
        func(path)
        return
    raise exc


def _safe_rmtree(path):
    """Remove a directory tree and handle Windows permission cases."""
    try:
        shutil.rmtree(path, onerror=_handle_remove_readonly)
        return True, None
    except Exception as exc:
        return False, str(exc)

def clean_build_artifacts(tools_to_clean):
    """Remove build and dist directories for specified tools."""
    buildspec_dir = Path(__file__).resolve().parent
    
    for tool in tools_to_clean:
        # Clean dist/tool directory
        tool_dist_dir = buildspec_dir / 'dist' / tool
        if tool_dist_dir.exists():
            removed, error = _safe_rmtree(tool_dist_dir)
            if removed:
                print(f"[OK] Removed: {tool_dist_dir}")
            else:
                print(f"[WARN] Failed to remove {tool_dist_dir}: {error}")
        
        # Clean build/tool directory
        tool_build_dir = buildspec_dir / 'build' / tool
        if tool_build_dir.exists():
            removed, error = _safe_rmtree(tool_build_dir)
            if removed:
                print(f"[OK] Removed: {tool_build_dir}")
            else:
                print(f"[WARN] Failed to remove {tool_build_dir}: {error}")

def build_tools(tools_to_build):
    """Build specified tools using PyInstaller."""
    # Get the buildspec directory (where this script is located)
    buildspec_dir = Path(__file__).resolve().parent
    dist_dir = buildspec_dir / 'dist'

    version_str, version_tuple = get_version()
    if version_str:
        print(f"Version: {version_str}")
    else:
        print("[WARN] Could not determine version from README.md; exe file properties will not be set.")

    print(f"Output directory: {dist_dir}")
    
    build_results = []
    
    # Build each tool
    for tool in tools_to_build:
        spec_file = buildspec_dir / f'{tool}.spec'
        
        if not spec_file.exists():
            print(f"[ERROR] Spec file not found: {spec_file}")
            build_results.append((tool, False, f"Spec file not found"))
            continue

        if version_str:
            generate_version_info(buildspec_dir, tool, version_str, version_tuple)
        
        print(f"\n{'='*60}")
        print(f"Building {tool}...")
        print(f"{'='*60}")
        
        # Run PyInstaller
        result = subprocess.run(
            ['pyinstaller', str(spec_file)],
            cwd=str(buildspec_dir),
            capture_output=False
        )
        
        if result.returncode != 0:
            print(f"[ERROR] Build failed for {tool}")
            build_results.append((tool, False, "Build failed"))
            continue
        
        # Verify executable was created
        exe_file = dist_dir / f'{tool}.exe'
        
        if exe_file.exists():
            print(f"[OK] Built {tool}.exe")
            build_results.append((tool, True, "Success"))
        else:
            print(f"[WARN] Executable not found: {exe_file}")
            build_results.append((tool, False, "Executable not found"))
    
    # Report summary
    print(f"\n{'='*60}")
    print("Build Summary:")
    print(f"{'='*60}")
    for tool, success, message in build_results:
        status = "[OK]" if success else "[ERROR]"
        print(f"{status} {tool}: {message}")
    
    successful = sum(1 for _, success, _ in build_results if success)
    total = len(build_results)
    print(f"\n{'='*60}")
    print(f"[OK] Build complete! {successful}/{total} tools built successfully.")
    print(f"Executables are in: {dist_dir}")
    print(f"{'='*60}")

def main():
    """Parse arguments and execute build or clean operations."""
    parser = argparse.ArgumentParser(
        description="Build script for JMF tools. Builds specified tools using PyInstaller."
    )
    parser.add_argument(
        'tools',
        nargs='?',
        default='all',
        help='Tools to build/clean: "all", or specific tool name (e.g., CreateMimePackage). Default: all'
    )
    parser.add_argument(
        '--clean',
        action='store_true',
        help='Clean previous build artifacts for specified tool(s) before building'
    )
    
    args = parser.parse_args()
    
    # Determine which tools to build/clean
    if args.tools.lower() == 'all':
        tools_to_process = TOOLS
    else:
        tools_to_process = [args.tools]
    
    # Validate that spec files exist for requested tools
    buildspec_dir = Path(__file__).resolve().parent
    for tool in tools_to_process:
        spec_file = buildspec_dir / f'{tool}.spec'
        if not spec_file.exists():
            print(f"[ERROR] Spec file not found for {tool}: {spec_file}")
            sys.exit(1)
    
    # Clean if requested
    if args.clean:
        print(f"{'='*60}")
        print(f"Cleaning build artifacts for: {', '.join(tools_to_process)}")
        print(f"{'='*60}")
        clean_build_artifacts(tools_to_process)
        print("")
    
    # Build
    print(f"{'='*60}")
    print(f"Building: {', '.join(tools_to_process)}")
    print(f"{'='*60}")
    build_tools(tools_to_process)

if __name__ == '__main__':
    main()
