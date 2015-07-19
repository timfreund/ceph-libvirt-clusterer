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

    def create_volume(self, name, size, pool=None):
        if not pool:
            pool = self.virtcon.listAllStoragePools()[0]
        xml = """
        <volume type='file'>
          <name>%s</name>
          <capacity unit='bytes'>%d</capacity>
          <allocation unit='bytes'>0</allocation>
          <target>
            <format type='qcow2'/>
          </target>
        </volume>
        """ % (name, size * 1024 * 1024)
        volume = pool.createXML(xml)
        return volume

    @property
    def domains(self):
        return [d for d in self.virtcon.listAllDomains() if d.name().startswith(self.name)]

    def duplicate_volume(self, volume, new_name):
        if isinstance(volume, str):
            if volume.find(os.path.sep) == 0:
                volume = self.virtcon.storageVolLookupByPath(volume)
            else:
                for pool in host.listAllStoragePools():
                    for v in pool.listAllVolumes():
                        if v.name() == volume:
                            volume = v
                            break
        template_name = volume.name()
        pool = volume.storagePoolLookupByVolume()
        new_xml = volume.XMLDesc().replace(template_name, new_name)
        new_vol = pool.createXMLFrom(new_xml, volume)
        return new_vol

    def next_domain_name(self):
        return "%s-%02d" % (self.name, len(self.domains))

    @property
    def template_domain(self):
        return self.virtcon.lookupByName(self.template_domain_name)

            

