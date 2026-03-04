#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CreateTestPDF generates simple test PDF files for use with JMF tools.
Can create PDFs with configurable text, number of pages, and layout.
"""
import sys
import argparse
from pathlib import Path
from fpdf import FPDF, XPos, YPos


def get_tools_dir():
    """Get the directory containing this tool, handling both script and PyInstaller execution."""
    # For PyInstaller executables, sys.argv[0] points to the actual exe location
    script_path = Path(sys.argv[0]).resolve()
    if script_path.is_file() and script_path.exists():
        return script_path.parent
    # For script execution, use __file__
    return Path(__file__).resolve().parent

def get_page_size(size_name):
    """Return page dimensions for a given size name."""
    sizes = {
        'a3': (297, 420),  # in mm
        'a4': (210, 297),  # in mm
        'a5': (148, 210),  # in mm
        'sra3': (320, 450),  # in mm
        'tabloid': (279, 432),  # in mm
        'legal': (216, 356),  # in mm
        'ledger': (432, 279),  # in mm
        'letter': (216, 279),  # in mm
        'tabloid-extra': (305, 457),  # in mm
    }
    return sizes.get(size_name, sizes['a4'])  # Default to a4 if unknown



def create_test_pdf(output_path, num_pages=1, title="Test PDF", text="Test content", blackwhite=False, pagesize='a4'):
    """
    Create a simple test PDF with text.
    
    Args:
        output_path: Path where the PDF will be saved
        num_pages: Number of pages to create
        title: Title/header for the PDF
        text: Text content for each page
    """
    pdf = FPDF(orientation="portrait", format=get_page_size(pagesize))
    
    for page_num in range(1, num_pages + 1):
        pdf.add_page()
        
        # Add title
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        pdf.ln(10)
        
        # Add text content
        # The text can include "##" which will be replaced with the current page number
        # Text is either black and white or color based on blackwhite parameter, when color text is cycled through a set of colors for each page
        if blackwhite:
            pdf.set_text_color(0, 0, 0)
        else:
            # Cycle through some colors for demonstration
            colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 165, 0), (128, 0, 128)]
            color = colors[(page_num - 1) % len(colors)]
            pdf.set_text_color(*color)
        pdf.set_font("Helvetica", "", 12)
        replaced_text = text.replace("##", str(page_num))
        pdf.multi_cell(0, 10, replaced_text)
        pdf.ln(10)
        
        # Add page number
        pdf.set_font("Helvetica", "I", 10)
        pdf.cell(0, 10, f"Page {page_num} of {num_pages}", align="C")
    
    # Create output directory if it doesn't exist
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save PDF
    pdf.output(str(output_path))
    print(f"✅ Created PDF: {output_path}")


def main():
    """Parse arguments and create test PDF."""
    parser = argparse.ArgumentParser(
        description="Create simple test PDF files for use with JMF tools."
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='Test.pdf',
        help='Output PDF file path (default: Test.pdf)'
    )
    parser.add_argument(
        '-p', '--pages',
        type=int,
        default=1,
        help='Number of pages to create (default: 1)'
    )
    parser.add_argument(
        '-t', '--title',
        type=str,
        default='Test PDF',
        help='PDF title/header (default: Test PDF)'
    )
    parser.add_argument(
        '-c', '--content',
        type=str,
        default='This is page ## a test PDF created for JMF processing.',
        help='Text content for each page, ## will be replaced with page number (default: "This is page ## a test PDF created for JMF processing.")'
    )
    parser.add_argument(
        '--config',
        action='store_true',
        help='Save PDF to .config folder instead of current directory'
    )
    parser.add_argument(
        '--blackwhite', '-bw',
        action='store_true',
        help='Create a black and white PDF (default: color)'
    )
    parser.add_argument(
        '--pagesize', '-ps',
        type=str,
        default='a4',
        help='Page size for the PDF (default: a4)'
    )    
    args = parser.parse_args()
    
    # Determine output path
    if args.config:
        # Save to .config folder in the tools directory
        tools_dir = get_tools_dir()
        config_dir = tools_dir / '.config'
        output_path = config_dir / args.output
    else:
        output_path = Path(args.output)
    
    # Create the PDF
    create_test_pdf(output_path, args.pages, args.title, args.content, args.blackwhite, args.pagesize)


if __name__ == '__main__':
    main()
