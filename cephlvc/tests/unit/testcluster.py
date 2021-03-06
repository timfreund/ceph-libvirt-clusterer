import libvirt

from cephlvc import Cluster
from mock import MagicMock
from unittest import TestCase

class TestCluster(TestCase):
    def test_domain_name_increment(self):
        vc = libvirt.virConnect()
        d = libvirt.virDomain(vc)

        c = Cluster('unittest', 'template_domain', vc)

        vc.listAllDomains = MagicMock(return_value=[])
        self.assertEqual('unittest-00', c.next_domain_name())

        d.name = MagicMock(return_value='unittest-00')
        vc.listAllDomains = MagicMock(return_value=[d])
        self.assertEqual('unittest-01', c.next_domain_name())

    def test_next_mac_address(self):
        vc = libvirt.virConnect()
        c = Cluster('unittest', 'template_domain', vc)
        next_mac = c.next_mac_address('00:00:00:00:00:09')
        self.assertEquals('00:00:00:00:00:0a', next_mac)
