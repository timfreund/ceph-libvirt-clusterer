from unittest import TestCase
import libvirt

from cephlvc import Cluster

class TestVolumeManagement(TestCase):
    def test_duplicate_volume(self):
        virtcon = libvirt.open()
        c = Cluster("integration", None, virtcon)
        original = c.create_volume("cephlvc-test_duplicate_volume-original.img", 8)
        duplicate = c.duplicate_volume(original, "cephlvc-test_duplicate_volume-duplicate.img")

        self.assertEquals("cephlvc-test_duplicate_volume-duplicate.img", duplicate.name())
        self.assertEquals(0, original.delete())
        self.assertEquals(0, duplicate.delete())
