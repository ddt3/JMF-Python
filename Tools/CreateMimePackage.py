"""
CreateMimePackage can be used to create a mime package from jmf, jdf and PDF. PDF can be added
either by reference (http) or as a file to include in the mime package
"""
import argparse
from pathlib import Path
from prismasyncjmfjdf import  CreateMimePackage


#############################################################################################################
#First some defaults are set to make usage without parameters possible                                      #
#                                                                                                           #
#############################################################################################################

basepath=Path(__file__).resolve().parent
configpath=basepath.joinpath(".config")
# first check if a .config folder exists in the same folder as this script
if Path.exists(configpath) :
    jmffile=configpath.joinpath("SubmitQueueEntry.jmf")
    jdffile=configpath.joinpath("Template.jdf")
    pdffile=configpath.joinpath("Test.pdf")
    if not jmffile.exists:
        SUBMITJMF=None
    else:
        SUBMITJMF=str(jmffile)
    if not jdffile.exists:
        JDFFILE=None
    else:
        JDFFILE=str(jdffile)
    if not pdffile.exists:
        PDFURL=None
    else:
        PDFURL=f'file://{str(pdffile)}'


# The following block is used to take command line options for this tool.
parser = argparse.ArgumentParser(description='Create a mime package (mjm) from jmf, jdf and PDF'+
                                              'PDF can be added either by reference (http) or as a file to include in the mime package')
parser.add_argument('--jmf', '-j', type=str, default=SUBMITJMF,
                    help='Provide filename for JMF messages used for submissiuon (default: '+SUBMITJMF+' )')
parser.add_argument('--jdf', '-t', type=str, default=JDFFILE,
                    help='Provide filename for JDF ticket used for submissiuon (default: '+JDFFILE+' )')
parser.add_argument('--pdf', '-p', type=str, default=PDFURL,
                    help='Provide URL for PDF starting with either http:// or file. (default: '+PDFURL+' )')
args = parser.parse_args()


# The jmfmessages library contains examples of how jmf can be used to send commands to PRISMAsync and obtain information from PRISMAsync
# This file is an example of how the libraries can be used to create a full mime package (including PDF)

print("Mime-package created with filename:",CreateMimePackage(args.jmf,args.jdf, args.pdf))
