import uuid
import os
import xml.etree.ElementTree as ET

class Cluster(object):
    def __init__(self, name, template_domain_name, virtcon):
        self.name = name
        self.template_domain_name = template_domain_name
        self.virtcon = virtcon

    def add_domain(self):
        etree = ET.fromstring(self.template.XMLDesc())
        new_id = uuid.uuid4()
        etree.find("uuid").text = str(new_id)

        template_volume_path = etree.find('*/disk/source').attrib['file']
        

    def add_volume_to_domain(self, domain):
        # domain.attachDeviceFlags
        pass

    def detach_volume(self, domain, volume):
        pass

    @property
    def domains(self):
        return [d for d in self.virtcon.listAllDomains() if d.name().startswith(self.name)]

    def next_domain_name(self):
        return "%s-%02d" % (self.name, len(self.domains))

    @property
    def template_domain(self):
        return self.virtcon.lookupByName(self.template_domain_name)

            

