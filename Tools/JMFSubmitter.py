"""
JMFSubmitter can be used to easily submit a job to PRISMAsync using JMF.
Upon exit it will return the returned QueueEntryID
"""
import sys
import argparse
from pathlib import Path
from urllib.parse import urlparse, unquote
from urllib.request import url2pathname
from prismasyncjmfjdf import SendJob, SendMime

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
#First some defaults are set to make usage easier when e.g. only one printer is used                        #
#                                                                                                           #
#############################################################################################################

# Provide a correct address for your printer: http://<hostname or ip address>:<portnumber>
# By PRISMAsync default port number is 8010. make sure to enable jmf support in the PRISMAsync settings editor

PRISMASYNCADDRESS="http://PRISMAsync.cpp.canon:8010"

basepath=get_tools_dir()
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

# # Which JMF file to use for submission in the examples
# SUBMITJMF='\"jmfjdf/SubmitQueueEntry.jmf\"'

# # Which JdF file to use for submission in the examples
# JDFFILE='\"jmfjdf/Template.jdf\"'

# # Which Jdf file to use for submission in the examples, either using a path to a file (file://) or to a webserver (http://)
# PDFURL='file:\"//jmfjdf/Test.pdf\"'

# The following block is used to take command line options for this tool.
parser = argparse.ArgumentParser(description='Submit JMF, JDF, and PDF to PRISMAsync. Create a .config folder to add defaults for: SubmitQueueEntry.jmf, Template.jdf, and Test.pdf')
parser.add_argument('--url', '-u', type=str, default=PRISMASYNCADDRESS,
                    help=f'full url to PRISMAsync jmf interface (default: {PRISMASYNCADDRESS})')
parser.add_argument('--jmf', '-j', type=str, default=SUBMITJMF,
                    help=f'Provide filename for JMF messages used for submission (default: {SUBMITJMF})')
parser.add_argument('--jdf', '-t', type=str, default=JDFFILE,
                    help=f'Provide filename for JDF ticket used for submissiuon (default: {JDFFILE})')
parser.add_argument('--pdf', '-p', type=str, default=PDFURL,
                    help='Provide URL for PDF starting with either http:// or file://. If file:// is used PDF will be part of mime pacakge (default: %(default)s)')
parser.add_argument('--silent', '-s', action='store_true',
                    help='Do not print ID just submit and stay silent')
parser.add_argument('--mime', '-m', type=str, default=None,
                    help='Mime package to send, takes priority over all other settings (default: no mime package)')
parser.add_argument('--chunksize', '--chunk-size', '-c', type=str, default=0,
                    help='Chunk size for uploading mime package in bytes (default: 0, which means no chunking)\n Sizes can be specified in bytes, kilobytes (e.g., 10k), megabytes (e.g., 5M), or gigabytes (e.g., 1G).')
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


def _is_valid_http_url(url_value):
    parsed = urlparse(url_value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)

# Validate that required arguments are provided
if args.mime is None:
    if args.jmf is None:
        parser.error("JMF file is required. Provide --jmf argument or create a .config/SubmitQueueEntry.jmf file")
    if args.jdf is None:
        parser.error("JDF file is required. Provide --jdf argument or create a .config/Template.jdf file")
    if args.pdf is None:
        parser.error("PDF URL is required. Provide --pdf argument or create a .config/Test.pdf file")

if not _is_valid_http_url(args.url):
    _fail(f"Invalid PRISMAsync URL: {args.url}. Use http://<host>:<port> or https://<host>:<port>")

if args.mime is None:
    jmf_path = Path(args.jmf)
    if not jmf_path.is_file():
        _fail(f"JMF file not found: {jmf_path}")

    jdf_path = Path(args.jdf)
    if not jdf_path.is_file():
        _fail(f"JDF file not found: {jdf_path}")

# Perform sanity checks on command line arguments
# First translate chunk size argument to an integer as it can contain K, M, or G suffixes, if it is not zero or negative, then fail
if isinstance(args.chunksize, str):
    suffix_multipliers = {"K": 1024, "M": 1048576, "G": 1073741824}
    if args.chunksize[-1].upper() in suffix_multipliers:
        args.chunksize = int(args.chunksize[:-1]) * suffix_multipliers[args.chunksize[-1].upper()]
    else:
        args.chunksize = int(args.chunksize)

if args.chunksize < 0:
    _fail("Chunk size must be a non-negative integer")

# Check if pdf argument starts with http(s):// or file://
if args.mime is None :
    if args.pdf.startswith("http://") or args.pdf.startswith("https://") :
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
        pdf_path = Path(args.pdf)
        if not pdf_path.is_file():
            _fail("PDF must be an http(s) URL, file:// URL, or an existing local file path")
        # Convert Windows paths to forward slashes for library compatibility
        args.pdf = pdf_path.as_posix()
else :
    # Check if mime filename argument does exist
    if Path(args.mime).is_file():
        pass
    else:
        _fail(f"MIME package not found: {args.mime}")
# First check if mime argument is given, if yes, send mine , else send JDF and PDF
try:
    if args.mime is None:
        QueueEntryID = SendJob(args.url, args.pdf, args.jdf)
    else:
        # If chunksize is zero do not chunk, else use the provided chunksize 
        chunk_size = args.chunksize if args.chunksize > 0 else 0
        chunked_upload = True if args.chunksize > 0 else False
        QueueEntryID = SendMime(args.url, args.mime, chunked_upload=chunked_upload, chunk_size=chunk_size)
except FileNotFoundError as err:
    _fail(f"Input file not found: {err.filename}", exit_code=1)
except PermissionError as err:
    _fail(f"Permission denied while reading input file: {err}", exit_code=1)
except ConnectionError as err:
    _fail(f"Network connection error while sending job: {err}", exit_code=1)
except TimeoutError as err:
    _fail(f"Timeout while sending job: {err}", exit_code=1)
except Exception as err:
    _fail(f"Failed to submit job: {err}", exit_code=1)
if not args.silent :
    print("Job submitted, got QueueEntryID: ", QueueEntryID)
