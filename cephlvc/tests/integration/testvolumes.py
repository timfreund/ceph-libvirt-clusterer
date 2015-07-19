from unittest import TestCase
import libvirt

class TestVolumeManagement(TestCase):
    def test_dummy_test(self):
        vc = libvirt.open()
        
