# -*- coding: utf-8 -*-

# Copyright: (c) 2019, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import platform

from ansible.module_utils.facts.collector import BaseFactCollector


class Distribution:
    _platform = 'Generic'

    # keep keys in sync with Conditionals page of docs
    OS_FAMILY_MAP = {
        'RedHat': ['RedHat', 'Fedora', 'CentOS', 'Scientific', 'SLC',
                   'Ascendos', 'CloudLinux', 'PSBM', 'OracleLinux', 'OVS',
                   'OEL', 'Amazon', 'Virtuozzo', 'XenServer', 'Alibaba'],
        'Debian': ['Debian', 'Ubuntu', 'Raspbian', 'Neon', 'KDE neon',
                   'Linux Mint', 'SteamOS', 'Devuan', 'Kali'],
        'Suse': ['SuSE', 'SLES', 'SLED', 'openSUSE', 'openSUSE Tumbleweed',
                 'SLES_SAP', 'SUSE_LINUX', 'openSUSE Leap'],
        'Archlinux': ['Archlinux', 'Antergos', 'Manjaro'],
        'Mandrake': ['Mandrake', 'Mandriva'],
        'Solaris': ['Solaris', 'Nexenta', 'OmniOS', 'OpenIndiana', 'SmartOS'],
        'Slackware': ['Slackware'],
        'Altlinux': ['Altlinux'],
        'SGML': ['SGML'],
        'Gentoo': ['Gentoo', 'Funtoo'],
        'Alpine': ['Alpine'],
        'AIX': ['AIX'],
        'HP-UX': ['HPUX'],
        'Darwin': ['MacOSX'],
        'FreeBSD': ['FreeBSD', 'TrueOS'],
        'ClearLinux': ['Clear Linux OS', 'Clear Linux Mix']
    }

    OS_FAMILY = {}
    for family, names in OS_FAMILY_MAP.items():
        for name in names:
            OS_FAMILY[name] = family

    def __init__(self, module):
        self.module = module

    def populate(self, collected_facts=None):
        distribution_facts = {}
        system = platform.system()
        distribution_facts['distribution'] = system
        distribution_facts['distribution_release'] = platform.release()
        distribution_facts['distribution_version'] = platform.version()

        return distribution_facts


class DistributionFactCollector(BaseFactCollector):
    name = 'distribution'
    _fact_class = Distribution

    _fact_ids = {
        'distribution_version',
        'distribution_release',
        'distribution_major_version',
        'os_family'
    }

    def collect(self, module=None, collected_facts=None):
        collected_facts = collected_facts or {}
        if not module:
            return {}

        facts_obj = self._fact_class(module=module)

        distro_facts_dict = facts_obj.populate(collected_facts=collected_facts)

        return distro_facts_dict
