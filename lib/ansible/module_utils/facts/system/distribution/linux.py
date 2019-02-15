# -*- coding: utf-8 -*-

# Copyright: (c) 2019, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.facts.system.distribution.base import Distribution, DistributionFactCollector


class LinuxDistribution(Distribution):
    platform = 'Linux'

    def populate(self, collected_facts=None):
        return {'distribution_release': 'Linx'}


class LinuxDistributionCollector(DistributionFactCollector):
    _platform = 'Linux'
    _fact_class = LinuxDistribution
