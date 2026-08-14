Huawei Storage Backend for Cinder
-------------------------------

Overview
========

This charm provides a Huawei storage backend for use with the Cinder
charm.

To use:

    juju deploy cinder
    juju deploy cinder-huawei
    juju add-relation cinder-huawei cinder

Configuration
=============

See config.yaml for details of configuration options.

HyperMetro
==========

This charm can configure the backend to log in to a second, remote
Huawei array (paired with the local array in a HyperMetro domain) by
setting the following config options:

    hypermetro: True
    hypermetro-username: <remote array admin username>
    hypermetro-password: <remote array admin password>
    hypermetro-domain-name: <hypermetro domain name>
    hypermetro-rest-url: <remote array REST URL(s), semicolon separated>
    hypermetro-storage-pool: <remote array storage pool(s), semicolon separated>

The HyperMetro domain pairing the local and remote arrays must already
be configured on the storage arrays themselves (e.g. via
DeviceManager/ISM) before enabling this option; the charm does not
create or manage that pairing.

Enabling this option on the backend makes it *capable* of servicing
HyperMetro volumes, but it does not make every volume replicated by
itself. To get a redundant, HyperMetro-protected volume, the Cinder
volume type used to create it must also carry the extra-spec:

    openstack volume type set --property hypermetro='<is> True' <volume-type>

This is an OpenStack API level operation performed by a cloud operator
(e.g. via the OpenStack CLI or Horizon) and is outside the scope of
this charm, which has no OpenStack API credentials.
