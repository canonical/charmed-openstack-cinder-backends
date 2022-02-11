import charms_openstack.charm
import charmhelpers.core.hookenv as ch_hookenv  # noqa

charms_openstack.charm.use_defaults("charm.default-select-release")



class CinderDellEMCPowerstoreCharm(
    charms_openstack.charm.CinderStoragePluginCharm
):

    # The name of the charm
    name = "cinder_dell_emc_powerstore"

    # Package to determine application version. Use "cinder-common" when
    # the driver is in-tree of Cinder upstream.
    version_package = "python3-storops"

    # Package to determine OpenStack release name
    release_pkg = "cinder-common"

    # this is the first release in which this charm works
    release = "victoria"

    stateless = True

    # https://docs.openstack.org/cinder/latest/reference/support-matrix.html#operation_active_active_ha
    # https://docs.openstack.org/cinder/latest/contributor/high_availability.html#enabling-active-active-on-drivers
    active_active_ha = False

    # Specify any config that the user *must* set.
    mandatory_config = [
        "storage-protocol",
        "san-ip",
        "san-login",
        "san-password",
        "powerstore-ports",
    ]

    def cinder_configuration(self):
        mandatory_config_values = map(self.config.get, self.mandatory_config)
        if not all(list(mandatory_config_values)):
            return []

        if self.config.get("volume-backend-name"):
            volume_backend_name = self.config.get("volume-backend-name")
        else:
            volume_backend_name = ch_hookenv.service_name()

        volume_driver = "cinder.volume.drivers.dell_emc.powerstore.driver.PowerStoreDriver"

        driver_options = [
            ("volume_backend_name", volume_backend_name),
            ("volume_driver", volume_driver),
            ("storage_protocol", self.config.get("storage-protocol")),
            ("san_ip", self.config.get("san-ip")),
            ("san_login", self.config.get("san-login")),
            ("san_password", self.config.get("san-password")),
            ("powerstore_ports", self.config.get("powerstore-ports")),
        ]

        if self.config.get("use-multipath"):
            driver_options.extend(
                [
                    ("use_multipath_for_image_xfer", True),
                    ("enforce_multipath_for_image_xfer", True),
                ]
            )

        return driver_options
