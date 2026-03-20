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

class PDF(FPDF):
    def __init__(self, title="", total_pages=0, **kwargs):
        super().__init__(**kwargs)
        self.pdf_title = title
        self.total_pages = total_pages

    def header(self):
        # Override the header method to prevent default header
        # Add title
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 10, self.pdf_title, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        self.ln(10)

    def footer(self):
        # Override the footer method to prevent default footer
                # Add page number at the bottom of the page with page size information
        self.set_y(-15)
        self.set_font("Helvetica", "I", 10)
        self.cell(0, 10, f"Page {self.page_no()} of {self.total_pages}, size : {self.w:.0f}x{self.h:.0f}(mm) / {self.w/25.4:.2f}x{self.h/25.4:.2f}(inches)", align="C")


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
    global sizes 
    if size_name.startswith("custom"):
        try:
            dimensions = size_name[len("custom"):].split('x')
            if len(dimensions) == 2:
                width = float(dimensions[0])
                height = float(dimensions[1])
                if width <= 0 or height <= 0:
                    return None
                return (width, height)
        except ValueError:
            return None
        return None
    return sizes.get(size_name)

def list_media_sizes():
    """List all available media sizes."""
    global sizes
    return list(sizes.keys())

def create_test_pdf(output_path, num_pages=1, title="Test PDF", text="Test content", blackwhite=False, pagesize='a4'):
    """
    Create a simple test PDF with text.
    
    Args:
        output_path: Path where the PDF will be saved
        num_pages: Number of pages to create
        title: Title/header for the PDF
        text: Text content for each page
    """
    page_size = get_page_size(pagesize)
    if page_size is None:
        raise ValueError(
            f"Invalid page size '{pagesize}'. Use one of: {', '.join(list_media_sizes())} or custom[width]x[height]"
        )

    pdf = PDF(title=title, total_pages=num_pages, orientation="portrait", format=page_size)
    
    for page_num in range(1, num_pages + 1):
        pdf.add_page()
        

        
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
        # find the middle of the page and start the text there
        pdf.set_xy(pdf.w / 2 - 50, pdf.h / 2 - 10)
        replaced_text = text.replace("##", str(page_num))
        pdf.multi_cell(0, 10, replaced_text)
        pdf.ln(10)
        
        #draw a border around the page for visual reference
        pdf.rect(0+5, 0+5, pdf.w-10, pdf.h-10)
    
    # Create output directory if it doesn't exist
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save PDF but make sure it is possible to write to the location, if not print an error message
    try:
        pdf.output(str(output_path))
        print(f"[OK] Created PDF: {output_path}")
    except PermissionError as e:
        raise PermissionError(
            f"Failed to create PDF at '{output_path}'. The file may be open in another program or not writable"
        ) from e
    except OSError as e:
        raise OSError(f"Failed to write PDF to '{output_path}': {e}") from e


def main():
    """Parse arguments and create test PDF."""
    def _fail(message, exit_code=2):
        print(f"Error: {message}")
        sys.exit(exit_code)

    parser = argparse.ArgumentParser(
        description="Create a simple test PDF file for use with JMF tools."
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
        help='Total number of pages of the created PDF (default: 1)'
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
        default='This is page ## of a test PDF created for JMF processing.',
        help='Content line on each page, when ## is used it  will be replaced by the current page number (default: "This is page ## of a test PDF created for JMF processing.")'
    )
    parser.add_argument(
        '--config',
        action='store_true',
        help='Save PDF to .config folder instead of current directory. Can be used to create a default PDFs for use with the other JMF tools(default: False)'
    )
    parser.add_argument(
        '--blackwhite', '-bw',
        action='store_true',
        help='Create a black and white PDF. Normally text is in a random random color. Use this option to create a PDF with black text (default: color)'
    )
    parser.add_argument(
        '--list-sizes', '-ls',
        action='store_true',
        help='Do not create a PDF, just list all available media sizes'
    )
        
    parser.add_argument(
        '--pagesize', '-ps',
        type=str,
        default='a4',
        help='Available known page sizes for the PDF (default: a4)'
    )    
    args = parser.parse_args()

    if args.pages < 1:
        _fail("Number of pages must be at least 1")
    
    # Determine output path
    if args.config:
        # Save to .config folder in the tools directory
        tools_dir = get_tools_dir()
        config_dir = tools_dir / '.config'
        output_path = config_dir / args.output
    else:
        output_path = Path(args.output)
    
    # Create the PDF
    if args.list_sizes:
        print("Available media sizes:")
        for size in list_media_sizes():
            print(f" -ps {size}")
        print("Custom media sizes:")
        print(f" -ps custom[width]x[height] (e.g. -ps custom220x310, size in mm)")
    else:
        try:
            create_test_pdf(output_path, args.pages, args.title, args.content, args.blackwhite, args.pagesize)
        except ValueError as e:
            _fail(str(e), exit_code=2)
        except PermissionError as e:
            _fail(str(e), exit_code=1)
        except OSError as e:
            _fail(str(e), exit_code=1)
        except Exception as e:
            _fail(f"Unexpected error while creating PDF: {e}", exit_code=1)


if __name__ == '__main__':
    main()
