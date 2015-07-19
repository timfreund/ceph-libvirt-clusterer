import libvirt
import os
import string
import uuid
import xml.etree.ElementTree as ET

from cephlvc.network import ArpScraper

class Cluster(object):
    def __init__(self, name, template_domain_name, virtcon):
        self.name = name
        self.template_domain_name = template_domain_name
        self.virtcon = virtcon

    def add_domain(self, data_volume_count=0, data_volume_size=0):
        new_name = self.next_domain_name()
        new_id = uuid.uuid4()
        etree = ET.fromstring(self.template_domain.XMLDesc())

        source_volume_element = etree.find('*/disk/source')
        source_volume_path = source_volume_element.attrib['file']
        source_volume = self.virtcon.storageVolLookupByPath(source_volume_path)
        self.duplicate_volume(source_volume, "%s.img" % new_name)

        etree.find("uuid").text = str(new_id)
        etree.find("name").text = new_name
        source_volume_element.attrib['file'] = source_volume_path.replace(self.template_domain_name, new_name)

        for mac in etree.findall('*/interface/mac'):
            mac.attrib['address'] = self.next_mac_address()

        domain = self.virtcon.defineXML(ET.tostring(etree))

        for x in range(0, data_volume_count):
            vol_name = "%s-data-%02d.img" % (new_name, x)
            dev_id = "vd%s" % string.ascii_lowercase[x]
            volume = self.create_volume(vol_name, data_volume_size)
            self.add_volume_to_domain(domain, volume, dev_id)

        return domain

    def add_volume_to_domain(self, domain, volume, dev_id):
        xml = """
        <disk type='file' device='disk'>
          <driver name='qemu' type='qcow2'/>
          <source file='%s'/>
          <target dev='%s' bus='virtio'/>
        </disk>""" % (volume.path(), dev_id)

        domain.attachDeviceFlags(xml, libvirt.VIR_DOMAIN_AFFECT_CONFIG)

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

    def max_mac_address(self):
        max_mac = 0
        for d in self.virtcon.listAllDomains():
            etree = ET.fromstring(d.XMLDesc())
            for mac in etree.findall('*/interface/mac'):
                addr = int(mac.attrib['address'].replace(':', ''), 16)
                if addr > max_mac:
                    max_mac = addr
        max_mac = "%012x" % max_mac
        max_mac = ":".join(max_mac[i:i+2] for i in range(0, 12, 2))
        return max_mac

    def next_mac_address(self, mac=None):
        if mac is None:
            mac = self.max_mac_address()
        newmac = '%012x' % (int(mac.replace(':', ''), 16) + 1)
        return ":".join(newmac[i:i+2] for i in range(0, 12, 2))

    def next_domain_name(self):
        return "%s-%02d" % (self.name, len(self.domains))

    def print_ip_addresses(self):
        mac_to_domain = {}
        macs = []
        for d in self.domains:
            etree = ET.fromstring(d.XMLDesc())
            for mac in etree.findall('*/interface/mac'):
                mac_to_domain[mac.attrib['address']] = d.name()
                macs.append(mac.attrib['address'])
        arp_scraper = ArpScraper()
        addresses = arp_scraper.ip_lookup(macs)
        for mac, ip in addresses:
            print "%s %s %s" % (mac_to_domain[mac], mac, ip)

    def power_off(self):
        for d in self.domains:
            d.shutdown()

    def power_on(self):
        for d in self.domains:
            d.create()

    @property
    def template_domain(self):
        return self.virtcon.lookupByName(self.template_domain_name)

            

