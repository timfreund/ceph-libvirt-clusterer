from unittest import TestCase
import libvirt

from cephlvc import Cluster

class TestDomainManagement(TestCase):
    def test_add_domain(self):
        virtcon = libvirt.open()
        c = Cluster("cephlvc-integration", "opensuse-ceph-template", virtcon)
        self.assertEquals(0, len(c.domains))
        d = c.add_domain()
        self.assertEquals(1, len(c.domains))
        self.assertEquals(0, d.undefine())
