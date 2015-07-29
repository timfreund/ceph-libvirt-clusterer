import libvirt
import os
import string
import uuid
import xml.etree.ElementTree as ET

from cephlvc.network import ArpScraper

class Domain(object):
    def __init__(self, virDomain):
        self.domain = virDomain

    def __getattr__(self, attr_name):
        if hasattr(self.domain, attr_name):
            return getattr(self.domain, attr_name)

    def disk_count(self, bus=None):
        targets = self.etree.findall('*/disk/target')

        if not bus:
            return len(targets)

        count = 0
        for target in targets:
            if target.attrib['bus'] == bus:
                count += 1
        return count

    @property
    def etree(self):
        return ET.fromstring(self.domain.XMLDesc())

    @property
    def volume_paths(self):
        paths = []
        etree = self.etree
        for source in etree.findall('*/disk/source'):
            paths.append(source.attrib['file'])
        return paths

class Cluster(object):
    def __init__(self, name, template_domain_name, virtcon):
        self.name = name
        self.template_domain_name = template_domain_name
        self.virtcon = virtcon

    def add_domain(self, data_volume_count=0, data_volume_size=0):
        new_name = self.next_domain_name()
        etree = self.template_domain.etree

        source_volume_element = etree.find('*/disk/source')
        source_volume_path = source_volume_element.attrib['file']
        source_volume = self.virtcon.storageVolLookupByPath(source_volume_path)
        volume = self.duplicate_volume(source_volume, "%s.img" % new_name)

        domain = self.create_domain(new_name, self.template_domain.etree, volume)

        disk_offset = domain.disk_count('virtio')
        for x in range(0, data_volume_count):
            vol_name = "%s-data-%02d.img" % (new_name, x)
            dev_id = "vd%s" % string.ascii_lowercase[x + disk_offset]
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

    def create_domain(self, name, template_etree, source_volume):
        etree = template_etree

        etree.find("uuid").text = str(uuid.uuid4())
        etree.find("name").text = name

        source_volume_element = etree.find('*/disk/source')
        source_volume_element.attrib['file'] = source_volume.path()

        for mac in etree.findall('*/interface/mac'):
            mac.attrib['address'] = self.next_mac_address()

        return Domain(self.virtcon.defineXML(ET.tostring(etree)))

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

    def destroy_all(self):
        for d in self.domains:
            self.destroy_domain(d, and_volumes=True)

    def destroy_domain(self, domain, and_volumes=True):
        # preloading paths because we can't get them from the domain
        # once undefine is called
        paths = domain.volume_paths

        if domain.isActive():
            domain.destroy()
        domain.undefine()

        if and_volumes:
            for path in paths:
                self.destroy_volume(path)

    def destroy_volume(self, volume):
        volume = self.load_volume(volume)
        volume.delete()

    def detach_volume(self, domain, volume):
        pass

    @property
    def domains(self):
        return [Domain(d) for d in self.virtcon.listAllDomains() if d.name().startswith(self.name)]

    def duplicate_volume(self, volume, new_name):
        volume = self.load_volume(volume)
        template_name = volume.name()
        pool = volume.storagePoolLookupByVolume()
        new_xml = volume.XMLDesc().replace(template_name, new_name)
        new_vol = pool.createXMLFrom(new_xml, volume)
        return new_vol

    def load_volume(self, volume):
        if isinstance(volume, libvirt.virStorageVol):
            return volume
        if isinstance(volume, str):
            volume_name = volume
            volume = None

            if volume_name.find(os.path.sep) == 0:
                volume = self.virtcon.storageVolLookupByPath(volume_name)
            else:
                for pool in self.virtcon.listAllStoragePools():
                    for v in pool.listAllVolumes():
                        if v.name() == volume_name:
                            volume = v
                            break
        return volume

    def max_mac_address(self):
        max_mac = 0
        for d in [Domain(d) for d in self.virtcon.listAllDomains()]:
            etree = d.etree
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
            etree = d.etree
            for mac in etree.findall('*/interface/mac'):
                mac_to_domain[mac.attrib['address']] = d.name()
                macs.append(mac.attrib['address'])
        arp_scraper = ArpScraper()
        addresses = arp_scraper.ip_lookup(macs)
        for mac, ip in addresses:
            print "%s %s" % (ip, mac_to_domain[mac])

    def power_off(self):
        for d in self.domains:
            d.shutdown()

    def power_on(self):
        for d in self.domains:
            d.create()

    @property
    def template_domain(self):
        return Domain(self.virtcon.lookupByName(self.template_domain_name))

            

