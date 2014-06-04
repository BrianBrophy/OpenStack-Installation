#!/usr/bin/env python

#######################################################################
# OpenStack Icehouse Network Node Setup Script
#######################################################################

import sys
import os

sys.path.append(os.path.dirname(__file__))
import openstackinstall.common as osicommon


if not os.geteuid() == 0:
  sys.exit('This script must be run as root')

print '#######################################################################'
print '# OpenStack Icehouse Network Node Setup'
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
controlManagementNetworkIP = osicommon.get_config_ini(iniPath, 'control', 'network_address_management')
controlApiNetworkIP = osicommon.get_config_ini(iniPath, 'control', 'network_address_api')
print ''
osicommon.log('Using network addresses:')
print '    Control Node Management Network Address: ' + str(controlManagementNetworkIP)
print '    Control Node API Network Address: ' + str(controlApiNetworkIP)

# Install NTP
osicommon.install_ntp(controlManagementNetworkIP)

# Install Neutron
neutronDatabasePassword = osicommon.get_config_ini(iniPath, 'neutron', 'database_user_password')
osicommon.install_neutron_on_network_node(neutronDatabasePassword, controlManagementNetworkIP, controlManagementNetworkIP)

print ''
osicommon.log('Finished installation')
print ''

