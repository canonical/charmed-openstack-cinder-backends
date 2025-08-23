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

import unittest
from src.charm import CinderDellEMCPowerStoreCharm
from ops.model import BlockedStatus, ActiveStatus
from ops.testing import Harness


class TestCinderDellEMCPowerStoreCharm(unittest.TestCase):

    def setUp(self):
        self.harness = Harness(CinderDellEMCPowerStoreCharm)
        self.addCleanup(self.harness.cleanup)
        self.harness.begin()
        self.harness.set_leader(True)
        backend = self.harness.add_relation('storage-backend', 'cinder')
        self.harness.add_relation_unit(backend, 'cinder/0')

    def test_cinder_base(self):
        self.assertEqual(
            self.harness.framework.model.app.name,
            'cinder-dell-emc-powerstore')
        # Test that charm is blocked because of missing configurations.
        self.harness.update_config({})
        self.assertTrue(isinstance(
            self.harness.model.unit.status, BlockedStatus))

    def test_multipath_config(self):
        self.harness.update_config({'use-multipath': True})
        conf = dict(self.harness.charm.cinder_configuration(
            dict(self.harness.model.config)))
        self.assertTrue(conf.get('use_multipath_for_image_xfer'))
        self.assertTrue(conf.get('enforce_multipath_for_image_xfer'))

    def test_cinder_configuration(self):
        test_config = {
            'volume-backend-name': 'my_backend_name',
            'protocol': 'iSCSI',
            'san-ip': '192.0.2.1',
            'san-login': 'superuser',
            'san-password': 'my-password',
        }
        self.harness.update_config(test_config)
        conf = dict(self.harness.charm.cinder_configuration(
            dict(self.harness.model.config)))
        self.assertEqual(conf['volume_backend_name'], 'my_backend_name')
        self.assertEqual(conf[
            'volume_driver'],
            'cinder.volume.drivers.dell_emc.powerstore.driver.PowerStoreDriver'
        ),
        self.assertEqual(conf['storage_protocol'], 'iSCSI')
        self.assertEqual(conf['san_ip'], '192.0.2.1')
        self.assertEqual(conf['san_login'], 'superuser')
        self.assertEqual(conf['san_password'], 'my-password')
        self.assertTrue(isinstance(
            self.harness.model.unit.status, ActiveStatus))

    def test_cinder_configuration_fc(self):
        test_config = {
            'volume-backend-name': 'my_backend_name',
            'protocol': 'FC',
            'san-ip': '192.0.2.1',
            'san-login': 'superuser',
            'san-password': 'my-password',
            'powerstore-ports':
                '58:cc:f0:98:49:22:07:02,58:cc:f0:98:49:23:07:02',
        }
        self.harness.update_config(test_config)
        conf = dict(self.harness.charm.cinder_configuration(
            dict(self.harness.model.config)))
        self.assertEqual(conf['volume_backend_name'], 'my_backend_name')
        self.assertEqual(conf[
            'volume_driver'],
            'cinder.volume.drivers.dell_emc.powerstore.driver.PowerStoreDriver'
        ),
        self.assertEqual(conf['storage_protocol'], 'FC')
        self.assertEqual(conf['san_ip'], '192.0.2.1')
        self.assertEqual(conf['san_login'], 'superuser')
        self.assertEqual(conf['san_password'], 'my-password')
        self.assertEqual(conf[
            'powerstore_ports'],
            '58:cc:f0:98:49:22:07:02,58:cc:f0:98:49:23:07:02'
        )
        self.assertTrue(isinstance(
            self.harness.model.unit.status, ActiveStatus))

    def test_cinder_configuration_no_explicit_backend_name(self):
        test_config = {
            'volume-backend-name': None,
            'protocol': 'iSCSI',
            'san-ip': '192.0.2.1',
            'san-login': 'superuser',
            'san-password': 'my-password',
        }
        self.harness.update_config(test_config)
        conf = dict(self.harness.charm.cinder_configuration(
            dict(self.harness.model.config)))
        self.assertEqual(conf[
            'volume_backend_name'],
            'cinder-dell-emc-powerstore'
        )
        self.assertEqual(conf[
            'volume_driver'],
            'cinder.volume.drivers.dell_emc.powerstore.driver.PowerStoreDriver'
        ),
        self.assertEqual(conf['storage_protocol'], 'iSCSI')
        self.assertEqual(conf['san_ip'], '192.0.2.1')
        self.assertEqual(conf['san_login'], 'superuser')
        self.assertEqual(conf['san_password'], 'my-password')
        self.assertTrue(isinstance(
            self.harness.model.unit.status, ActiveStatus))
