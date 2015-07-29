from unittest import TestCase
import os
import urllib2
import libvirt

from cephlvc import Cluster

def setUpModule():
    image_name = 'cirros-0.3.4-x86_64-disk.img'
    virt = libvirt.open()
    c = Cluster('cephlvc-integration', '', virt)
    vol = c.load_volume(image_name)

    if vol is None:
        path = '/tmp/%s' % image_name
        url = 'https://download.cirros-cloud.net/0.3.4/%s' % image_name
        response = urllib2.urlopen(url)

        with open(path, 'w') as cirros_tmp:
            cirros_tmp.write(response.read())

        pool = virt.storagePoolLookupByName('default')
        vol = pool.createXML("""
        <volume type='file'>
          <name>%s</name>
          <capacity unit='bytes'>0</capacity>
          <allocation unit='bytes'>0</allocation>
          <target>
            <format type='qcow2'/>
          </target>
        </volume>
        """ % image_name)

        with open(path, 'r') as cirros_tmp:
            stream = virt.newStream(0)
            def _stream_handler(stream, nbytes, fd):
                return fd.read(nbytes)
            rc = vol.upload(stream, 0, 13287936)
            stream.sendAll(_stream_handler, cirros_tmp)

        os.remove(path)

    try:
        domain = c.template_domain
    except:
        print "domain not found..."

def tearDownModule():
    pass

class TestDomainManagement(TestCase):
    def test_add_domain(self):
        virtcon = libvirt.open()
        c = Cluster("cephlvc-integration", "cephlvc-cirros-template", virtcon)
        self.assertEquals(0, len(c.domains))
        d = c.add_domain()
        self.assertEquals(1, len(c.domains))
        self.assertEquals(0, d.undefine())
