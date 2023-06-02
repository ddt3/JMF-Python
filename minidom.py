import  xml.dom.minidom

root=xml.dom.minidom.parse("Tools\_received\signal.xml")

Entries=root.getElementsByTagName("ResourceInfo")
for resources in Entries:
    Medias=resources.getElementsByTagName("Media")
    # Only one ResourceInfo/Media is allowed, take the MediaName from that one
    MediaName=Medias[0].getAttribute("DescriptiveName")
    PartAmounts=resources.getElementsByTagName("PartAmount")
    # Media can be available in multiple trays, step through all ResourceInfo/Media/PartAmount
    for PartAmount in PartAmounts:
        Amount=PartAmount.getAttribute("ActualAmount")
        TrayNames=PartAmount.getElementsByTagName("Part")
        # Only one ResourceInfo/Media/PartAmount/Part take the Location from that one
        Trayname=TrayNames[0].getAttribute("Location")
