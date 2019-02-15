# -*- coding: utf-8 -*-

# Copyright: (c) 2019, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.facts.system.distribution.base import Distribution, DistributionFactCollector


class DarwinDistribution(Distribution):
    platform = 'Darwin'

    def populate(self, collected_facts=None):
        darwin_facts = {'distribution': 'MacOSX'}
        rc, out, err = self.module.run_command("/usr/bin/sw_vers -productVersion")
        data = out.split()[-1]
        if data:
            darwin_facts['distribution_major_version'] = data.split('.')[0]
            darwin_facts['distribution_version'] = data

        darwin_facts['os_family'] = self.OS_FAMILY.get(darwin_facts['distribution'], None) or darwin_facts['distribution']

        return darwin_facts


class DarwinDistributionCollector(DistributionFactCollector):
    _platform = 'Darwin'
    _fact_class = DarwinDistribution
