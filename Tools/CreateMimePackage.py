"""
CreateMimePackage can be used to create a mime package from jmf, jdf and PDF. PDF can be added
either by reference (http) or as a file to include in the mime package
"""
import sys
import argparse
from pathlib import Path
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
        PDFURL=f'file://{str(pdffile)}'


# The following block is used to take command line options for this tool.
parser = argparse.ArgumentParser(description='Create a mime package (mjm) from jmf, jdf and PDF'+
                                              'PDF can be added either by reference (http) or as a file to include in the mime package')
parser.add_argument('--jmf', '-j', type=str, default=SUBMITJMF,
                    help=f'Provide filename for JMF messages used for submissiuon (default: {SUBMITJMF})')
parser.add_argument('--jdf', '-t', type=str, default=JDFFILE,
                    help=f'Provide filename for JDF ticket used for submissiuon (default: {JDFFILE})')
parser.add_argument('--pdf', '-p', type=str, default=PDFURL,
                    help=f'Provide URL for PDF starting with either http:// or file. (default: {PDFURL})')
args = parser.parse_args()


# Validate that all required arguments are provided
if args.jmf is None:
    parser.error("JMF file is required. Provide --jmf argument or create a .config/SubmitQueueEntry.jmf file")
if args.jdf is None:
    parser.error("JDF file is required. Provide --jdf argument or create a .config/Template.jdf file")
if args.pdf is None:
    parser.error("PDF URL is required. Provide --pdf argument or create a .config/Test.pdf file")

# The jmfmessages library contains examples of how jmf can be used to send commands to PRISMAsync and obtain information from PRISMAsync
# This file is an example of how the libraries can be used to create a full mime package (including PDF)

print("Mime-package created with filename:",CreateMimePackage(args.jmf,args.jdf, args.pdf))
