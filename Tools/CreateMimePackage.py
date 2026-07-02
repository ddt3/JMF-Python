"""
CreateMimePackage can be used to create a mime package from jmf, jdf and PDF. PDF can be added
either by reference (http) or as a file to include in the mime package
"""
import sys
import argparse
import shutil
from pathlib import Path
from urllib.parse import urlparse, unquote
from urllib.request import url2pathname
from prismasyncjmfjdf import  CreateMimePackage


#############################################################################################################
#Helper function to get tools directory                                                                     #
#                                                                                                           #
#############################################################################################################

def get_tools_dir():
    """Get the directory containing this tool, handling both script and PyInstaller execution."""
    # For PyInstaller executables, sys.argv[0] points to the actual exe location
    script_path = Path(sys.argv[0]).resolve()
    if script_path.is_file() and script_path.exists():
        return script_path.parent
    # For script execution, use __file__
    return Path(__file__).resolve().parent


#############################################################################################################
#First some defaults are set to make usage without parameters possible                                      #
#                                                                                                           #
#############################################################################################################

basepath = get_tools_dir()
configpath=basepath.joinpath(".config")

# Initialize defaults
SUBMITJMF=None
JDFFILE=None
PDFURL=None

# first check if a .config folder exists in the same folder as this script
if configpath.exists():
    jmffile=configpath.joinpath("SubmitQueueEntry.jmf")
    jdffile=configpath.joinpath("Template.jdf")
    pdffile=configpath.joinpath("Test.pdf")
    if not jmffile.exists():
        SUBMITJMF=None
    else:
        SUBMITJMF=str(jmffile)
    if not jdffile.exists():
        JDFFILE=None
    else:
        JDFFILE=str(jdffile)
    if not pdffile.exists():
        PDFURL=None
    else:
        PDFURL=pdffile.as_posix()


# The following block is used to take command line options for this tool.
parser = argparse.ArgumentParser(description='Create a mime package (mjm) from jmf, jdf and PDF'+
                                              'PDF can be added either by reference (http) or as a file to include in the mime package')
parser.add_argument('--jmf', '-j', type=str, default=SUBMITJMF,
                    help=f'Provide filename for JMF messages used for submissiuon (default: {SUBMITJMF})')
parser.add_argument('--jdf', '-t', type=str, default=JDFFILE,
                    help=f'Provide filename for JDF ticket used for submissiuon (default: {JDFFILE})')
parser.add_argument('--pdf', '-p', type=str, default=PDFURL,
                    help='Provide URL for PDF starting with either http:// or file://. (default: %(default)s)')
parser.add_argument('--output', '-o', type=str, 
                    help='Provide name for the output MIME package file. (default: filename based on timestamp)')
args = parser.parse_args()


def _fail(message, exit_code=2):
    print(f"Error: {message}")
    sys.exit(exit_code)


def _file_from_file_url(file_url):
    if not file_url.startswith("file://"):
        return None

    # Accept common non-standard relative forms like file://./path, file://.\path,
    # file://.config/path, or file://.config\path.
    # Well-formed file URLs always have an absolute path starting with '/' after the authority;
    # anything starting with '.' is a relative path used non-standardly.
    non_standard_path = file_url[len("file://"):]
    if non_standard_path.startswith("."):
        return Path(non_standard_path)

    parsed = urlparse(file_url)
    if parsed.scheme != "file":
        return None
    if parsed.netloc and parsed.netloc != "localhost":
        raw_path = f"//{parsed.netloc}{parsed.path}"
    else:
        raw_path = parsed.path
    local_path = url2pathname(unquote(raw_path))
    return Path(local_path)


# Validate that all required arguments are provided
if args.jmf is None:
    parser.error("JMF file is required. Provide --jmf argument or create a .config/SubmitQueueEntry.jmf file")
if args.jdf is None:
    parser.error("JDF file is required. Provide --jdf argument or create a .config/Template.jdf file")
if args.pdf is None:
    parser.error("PDF URL is required. Provide --pdf argument or create a .config/Test.pdf file")

# Validate files and inputs before creating the MIME package to avoid raw tracebacks.
jmf_path = Path(args.jmf)
if not jmf_path.is_file():
    _fail(f"JMF file not found: {jmf_path}")

jdf_path = Path(args.jdf)
if not jdf_path.is_file():
    _fail(f"JDF file not found: {jdf_path}")

if args.pdf.startswith("http://") or args.pdf.startswith("https://"):
    pass
elif args.pdf.startswith("file://"):
    pdf_path = _file_from_file_url(args.pdf)
    if pdf_path is None or not pdf_path.is_file():
        _fail(f"PDF file not found: {args.pdf}")
    # Resolve to an absolute path but keep the file:// prefix intact — the library
    # uses the presence of "file://" to decide whether to embed the PDF as a
    # base64 MIME part or reference it by URL.
    args.pdf = "file://" + pdf_path.resolve().as_posix()
else:
    # Support direct file paths for convenience in script and executable usage.
    pdf_direct_path = Path(args.pdf)
    if not pdf_direct_path.is_file():
        _fail("PDF must be an http(s) URL, file:// URL, or an existing local file path")
    # Convert Windows paths to forward slashes for library compatibility
    args.pdf = pdf_direct_path.as_posix()

# The jmfmessages library contains examples of how jmf can be used to send commands to PRISMAsync and obtain information from PRISMAsync
# This file is an example of how the libraries can be used to create a full mime package (including PDF)

try:
    output_file = CreateMimePackage(args.jmf, args.jdf, args.pdf)
except FileNotFoundError as err:
    _fail(f"Input file not found: {err.filename}", exit_code=1)
except PermissionError as err:
    _fail(f"Permission denied while creating MIME package: {err}", exit_code=1)
except Exception as err:
    _fail(f"Failed to create MIME package: {err}", exit_code=1)

# The library may return either str or Path; normalize for consistent handling.
output_file = Path(output_file)

if args.output:
    # Move the generated package to the requested output location.
    new_output_file = Path(args.output)
    try:
        new_output_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(output_file), str(new_output_file))
        output_file = new_output_file
        print(f"[OK] MIME package created with filename: {new_output_file}")
    except Exception as err:
        _fail(f"Failed to save MIME package to '{new_output_file}': {err}", exit_code=1)

print("Mime-package created with filename:", output_file)
