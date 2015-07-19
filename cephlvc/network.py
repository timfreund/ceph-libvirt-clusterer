import re
import subprocess

class ArpScraper(object):
    # this entire class is obviously full of peril and shame
    # ... only tested on Ubuntu 14.04...
    # A cursory search for python arp libraries returned immature
    # libraries focused on crafting arp packets rather than querying
    # known system data, so here we are.

    ip_re = re.compile('[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}')
    mac_re = re.compile('..:..:..:..:..:..')
    
    def __init__(self):
        pass

    def ip_lookup(self, mac_addresses=[]):
        arp_dict = self.parse_system_arp()
        addresses = []
        for mac in mac_addresses:
            addresses.append((mac, arp_dict.get(mac, "")))
        return addresses

    def parse_system_arp(self):
        arp_dict = {}
        arp_out = subprocess.check_output(['arp', '-a'])
        for line in arp_out.split('\n'):
            try:
                ip = self.ip_re.search(line).group(0)
                mac = self.mac_re.search(line).group(0)
                arp_dict[mac] = ip
            except:
                pass
        return arp_dict
