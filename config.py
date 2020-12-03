import configparser
import argparse

config = configparser.ConfigParser(allow_no_value=True)
config.optionxform=str
config_file='config.ini'

try:
    config.read('config.ini')
    printer = config['Printer']
    jobs = config['Jobs']
except:
    print("Config file not read, creating a new one")
    if not config.has_section('Printer'):
        config.add_section('Printer')
        config.set('Printer', ';Provide the URL to the printer in the form: http://printer-ip:jmf_port')
        config.set('Printer', 'PRISMAsyncUrl', "http://PRISMAsync.network.lan:8010")
    if not config.has_section('Jobs'):
        config.add_section('Jobs')
        config.set('Jobs', 'StatusToRemove', "Completed")
        config.set('Jobs', ';Provide URL for PDF starting with either http:// or file.')
        config.set('Jobs', ';If a file url is provided the PDF will be send as part of a mime package')
        config.set('Jobs', 'UrlforPDF', "http://ubuntu-hdok.ocevenlo.oce.net/pdf/PosterFashionWomanplusTextSample.pdf")
        config.set('Jobs','RemoveMime', "Yes")
    with open('config.ini', 'w') as fp:
        config.write(fp) 
    print("Please adapt",config_file, "to your situation")
    exit(0)

# The following block is used to take command line options for this tool.
# It needs a printer address and an  opional --status. --help is automatically generated
parser = argparse.ArgumentParser(description='Delete all JMF QueueEntries that have the provided status from PRISMAsync')
parser.add_argument('--url', type=str, default=printer['PRISMAsyncUrl'],
                    help='full url to PRISMAsync jmf interface. (default: '+printer['PRISMAsyncUrl']+')')
parser.add_argument('--status', '-s', type=str, default=jobs['StatusToRemove'],
                    help='The status of the jobs that need to be removed (default:'+jobs['StatusToRemove']+')')
parser.add_argument('--pdf', '-p', type=str, default=jobs['UrlforPDF'],
                    help='Provide URL for PDF starting with either http:// or file. (default:'+jobs['UrlforPDF']+')')
parser.add_argument('--removemime', '-k', type=str, default=jobs['RemoveMime'], choices=['Yes', 'No'],
                    help='Remove mime package after sendig (default:'+jobs['RemoveMime']+')')                    
args = parser.parse_args()


url=args.url
status=args.status
pdf=args.pdf
removemime=(args.removemime == 'Yes')