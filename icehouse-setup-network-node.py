#!/usr/bin/env python

#######################################################################
# OpenStack Icehouse Network Node Setup Script
#######################################################################

import sys
import os

sys.path.append(os.path.dirname(__file__))
import openstackinstall.common as osicommon
import openstackinstall.icehouse as icehouse


if not os.geteuid() == 0:
  sys.exit('This script must be run as root')

print '#######################################################################'
print '# OpenStack Icehouse Network Node Setup'
print '#######################################################################'
osicommon.log('Starting installation')
print ''

# Update, Upgrade, Add Repo
icehouse.base_system_update()

# sysctl
osicommon.set_sysctl('net.ipv4.ip_forward', '1')
osicommon.set_sysctl('net.ipv4.conf.all.rp_filter', '0')
osicommon.set_sysctl('net.ipv4.conf.default.rp_filter', '0')

# Install vlan
icehouse.install_vlan()

# Install bridge-utils
icehouse.install_bridgeutils()

# Install INI path
iniPath = os.path.join(os.path.dirname(__file__), 'icehouse-install.ini')

# Get network addresses
controlManagementNetworkIP = osicommon.get_config_ini(iniPath, 'control', 'network_address_management')
instanceNetworkInterface = osicommon.get_config_ini(iniPath, 'network', 'network_interface_instance')
instanceNetworkIP = osicommon.get_network_address(instanceNetworkInterface)
externalNetworkInterface = osicommon.get_config_ini(iniPath, 'network', 'network_interface_external')
internetNetworkInterface = osicommon.get_config_ini(iniPath, 'network', 'network_interface_internet')
providerExternalNetworkCIDR = osicommon.get_config_ini(iniPath, 'network', 'openstack_external_network')

print ''
osicommon.log('Using network addresses:')
print '    Control Node Management Network Address: ' + str(controlManagementNetworkIP)
print '    Network Node Instance Network Address: ' + str(instanceNetworkIP)
print '    Network Node External Network Interface: ' + str(externalNetworkInterface)
print '    Network Node Internet Network Interface: ' + str(internetNetworkInterface)

# Install NTP
icehouse.install_ntp(controlManagementNetworkIP)

# Install Neutron
neutronDatabasePassword = osicommon.get_config_ini(iniPath, 'neutron', 'database_user_password')
icehouse.install_neutron_on_network_node(neutronDatabasePassword, controlManagementNetworkIP, instanceNetworkIP, externalNetworkInterface, internetNetworkInterface, providerExternalNetworkCIDR)

print ''
osicommon.log('Finished installation')
print ''

