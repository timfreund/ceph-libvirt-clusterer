# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

requires = [
    # 'libvirt' is likely already installed as a system package
    'mock',
    'nose',
]

setup(
    name='ceph-libvirt-clusterer',
    version='0.0',
    description='Just the check code for use in probe servers',
    author='Tim Freund',
    author_email='tim@freunds.net',
    license = 'MIT',
    url='https://github.com/timfreund/ceph-libvirt-clusterer',
    install_requires=requires,
    packages=['cephlvc'],
    include_package_data=True,
    entry_points = """\
    [console_scripts]
    cephlvc = cephlvc.cli:main
    """,
)
