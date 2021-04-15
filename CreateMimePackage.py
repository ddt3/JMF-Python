from jmfjdf.jmfmessages import CreateMimePackage
import argparse

#############################################################################################################
#First some defaults are set to make usage without parameters possible                                      #
#                                                                                                           #
#############################################################################################################

# Which JMF file to use for submission in the examples
JMFFile="jmfjdf/SubmitQueueEntry.jmf"

# Which JdF file to use for submission in the examples
JDFFile="jmfjdf/Template.jdf"

# Which Jdf file to use for submission in the examples, either using a path to a file (file://) or to a webserver (http://)
PDFUrl="file://jmfjdf/Test.pdf"

# The following block is used to take command line options for this tool.
parser = argparse.ArgumentParser(description='Create a mime package (mjm) from jmf, jdf and PDF. PDF can be added either by reference (http) or as a file to include in the mime package')
parser.add_argument('--jmf', '-j', type=str, default=JMFFile,
                    help='Provide filename for JMF messages used for submissiuon (default: '+JMFFile+' )')
parser.add_argument('--jdf', '-t', type=str, default=JDFFile,
                    help='Provide filename for JDF ticket used for submissiuon (default: '+JDFFile+' )')
parser.add_argument('--pdf', '-p', type=str, default=PDFUrl,
                    help='Provide URL for PDF starting with either http:// or file. (default: '+PDFUrl+' )')
args = parser.parse_args()


# The jmfmessages library contains examples of how jmf can be used to send commands to PRISMAsync and obtain information from PRISMAsync
# This file is an example of how the libraries can be used to create a full mime package (including PDF)

print("Mime-package created with filename:",CreateMimePackage(args.jmf,args.jdf, args.pdf))
