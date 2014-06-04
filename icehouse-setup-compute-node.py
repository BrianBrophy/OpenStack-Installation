#!/usr/bin/env python

#######################################################################
# OpenStack Icehouse Compute Node Setup Script
#######################################################################

import sys
import os

sys.path.append(os.path.dirname(__file__))
import openstackinstall.common as osicommon


if not os.geteuid() == 0:
  sys.exit('This script must be run as root')

print '#######################################################################'
print '# OpenStack Icehouse Compute Node Setup'
print '#######################################################################'
osicommon.log('Starting installation')
print ''

# Update, Upgrade, Add Repo
osicommon.base_system_update()

# sysctl
osicommon.set_sysctl('net.ipv4.ip_forward', '1')
osicommon.set_sysctl('net.ipv4.conf.all.rp_filter', '0')
osicommon.set_sysctl('net.ipv4.conf.default.rp_filter', '0')

# Install vlan
osicommon.install_vlan()

# Install bridge-utils
osicommon.install_bridgeutils()

# Install INI path
iniPath = os.path.join(os.path.dirname(__file__), 'icehouse-install.ini')

# Get network addresses
managementNetworkInterface = osicommon.get_config_ini(iniPath, 'compute', 'network_interface_management')
managementNetworkIP = osicommon.get_network_address(managementNetworkInterface)
controlManagementNetworkIP = osicommon.get_config_ini(iniPath, 'control', 'network_address_management')
controlApiNetworkIP = osicommon.get_config_ini(iniPath, 'control', 'network_address_api')
print ''
osicommon.log('Using network addresses:')
print '    Management Network Address: ' + str(managementNetworkIP)
print '    Control Node Management Network Address: ' + str(controlManagementNetworkIP)
print '    Control Node API Network Address: ' + str(controlApiNetworkIP)

# Install NTP
osicommon.install_ntp(controlManagementNetworkIP)

# Install Nova
novaDatabasePassword = osicommon.get_config_ini(iniPath, 'nova', 'database_user_password')
osicommon.install_nova_on_compute_node(novaDatabasePassword, controlManagementNetworkIP, controlManagementNetworkIP, controlApiNetworkIP, managementNetworkIP)

# Install Neutron
neutronDatabasePassword = osicommon.get_config_ini(iniPath, 'neutron', 'database_user_password')
osicommon.install_neutron_on_compute_node(neutronDatabasePassword, controlManagementNetworkIP, controlManagementNetworkIP)

print ''
osicommon.log('Finished installation')
print ''

