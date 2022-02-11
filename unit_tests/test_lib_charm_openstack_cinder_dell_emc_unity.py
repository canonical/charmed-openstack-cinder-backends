# Copyright 2016 Canonical Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import
from __future__ import print_function

import charmhelpers

import charm.openstack.cinder_dell_emc_powerstore as cinder_dell_emc_powerstore

import charms_openstack.test_utils as test_utils


class TestCinderDellEMCPowerstoreCharm(test_utils.PatchHelper):
    def _patch_config_and_charm(self, config):
        self.patch_object(charmhelpers.core.hookenv, "config")

        def cf(key=None):
            if key is not None:
                return config[key]
            return config

        self.config.side_effect = cf
        c = cinder_dell_emc_powerstore.CinderDellEMCPowerstoreCharm()
        return c

    def test_cinder_base(self):
        charm = self._patch_config_and_charm({})
        self.assertEqual(charm.name, "cinder_dell_emc_powerstore")
        self.assertEqual(charm.version_package, "python3-storops")
        self.assertEqual(charm.packages, [
            "python3-storops",
            "sg3-utils",
            "multipath-tools",
            "sysfsutils"
        ])

    def test_cinder_configuration(self):
        charm = self._patch_config_and_charm(
            {
                "volume-backend-name": "my_backend_name",
                "storage-protocol": "FC",
                "san-ip": "192.0.2.1",
                "san-login": "superuser",
                "san-password": "my-password",
                "powerstore_ports": "spa_iom_0_fc0,spb_iom_0_fc0,*_iom_0_fc1",
            }
        )
        config = charm.cinder_configuration()
        self.assertEqual(
            config,
            [
                ("volume_backend_name", "my_backend_name"),
                (
                    "volume_driver",
                    "cinder.volume.drivers.dell_emc.powerstore.Driver"
                ),
                ("storage_protocol", "FC"),
                ("san_ip", "192.0.2.1"),
                ("san_login", "superuser"),
                ("san_password", "my-password"),
                ("powerstore_ports",
                 "spa_iom_0_fc0,spb_iom_0_fc0,*_iom_0_fc1"),
            ],
        )

    def test_cinder_configuration_missing_mandatory_config(self):
        self.patch_object(charmhelpers.core.hookenv, "service_name")
        self.service_name.return_value = "cinder-myapp-name"
        charm = self._patch_config_and_charm(
            {
                "volume-backend-name": "my_backend_name",
                "storage-protocol": "iSCSI",
                "san-ip": "192.0.2.1",
                "san-login": "superuser",
                "san-password": None,
                "powerstore-ports": "spa_eth2,spb_eth2,*_eth3",
            }
        )
        config = charm.cinder_configuration()
        self.assertEqual(config, [])

    def test_cinder_configuration_no_explicit_backend_name(self):
        self.patch_object(charmhelpers.core.hookenv, "service_name")
        self.service_name.return_value = "cinder-myapp-name"
        charm = self._patch_config_and_charm(
            {
                "volume-backend-name": None,
                "storage-protocol": "iSCSI",
                "san-ip": "192.0.2.1",
                "san-login": "superuser",
                "san-password": "my-password",
                "powerstore-ports": "spa_eth2,spb_eth2,*_eth3",
            }
        )
        config = charm.cinder_configuration()
        self.assertEqual(
            config,
            [
                ("volume_backend_name", "cinder-myapp-name"),
                (
                    "volume_driver",
                    "cinder.volume.drivers.dell_emc."
                    "powerstore.driver.PowerStoreDriver"
                ),
                ("storage_protocol", "iSCSI"),
                ("san_ip", "192.0.2.1"),
                ("san_login", "superuser"),
                ("san_password", "my-password"),
                ("powerstore_ports", "spa_eth2,spb_eth2,*_eth3"),
            ],
        )
