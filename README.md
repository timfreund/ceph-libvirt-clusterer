# Ceph Libvirt Clusterer

Build a dev/test cluster of not-yet-Ceph nodes on a hypervisor running
libvirt and KVM.

If you are planning on writing [Ceph](http://ceph.com/) code or writing applications that
use Ceph, you're going to want a small cluster for development and
testing.  If you're running Linux with [libvirt](http://libvirt.org/)
and [KVM](http://www.linux-kvm.org/page/Main_Page), this tool can help you provision such a cluster.

This tool only handles virtual machine creation.  Once the virtual machines are built,
you can use [ceph-deploy](https://github.com/ceph/ceph-deploy),
[puppet](https://github.com/stackforge/puppet-ceph),
[chef](https://github.com/stackforge/puppet-ceph), or
[ansible](https://github.com/ceph/ceph-ansible) to do the Ceph configuration.

## Installation

### Prerequisites
On Ubuntu/Debian machines:

    sudo apt-get install python-libvirt python-virtualenv

On RHEL/CentOS machines:

    # (coming soon... installing a RHEL system to test...)

On openSUSE machines:

    sudo zypper install libvirt-python python-virtualenv

### Clone the code and install:

    git clone https://github.com/timfreund/ceph-libvirt-clusterer.git
    cd ceph-libvirt-clusterer
    virtualenv venv
    . venv/bin/activate
    python setup.py develop

## Usage

Before you use cephlvc, you need a machine image that the rest of your
cluster will be built with.  I built this tool to test openSUSE's Ceph
Enterprise Storage, so I have a virtual machine named opensuse-ceph-template
with the following attributes:

- ceph user is created
- ceph user has a SSH key
- ceph user's public key is in the ceph user's authorized_keys file
- ceph user is configured for passwordless sudo
- emacs is installed (not strictly necessary :-) )

Right now there's an API.  A command line interface is planned.


    import cephlvc
    import libvirt

    cluster = cephlvc.Cluster(name='cephdemo',
        template_domain_name='opensuse-ceph-template',
        virtcon=libvirt.open())

    for x in range(0, 4):
        cluster.add_domain(data_volume_count=3, data_volume_size=8192)

    cluster.power_on()

    # at this point you're going to want to know the IP addresses of the machines:
    cluster.print_ip_addresses()
    # work, work, work, work, work
    cluster.power_off()

That code will create 4 machines:

- cephdemo-00
- cephdemo-01
- cephdemo-02
- cephdemo-03

And each machine will have three data volumes of 8GB.
