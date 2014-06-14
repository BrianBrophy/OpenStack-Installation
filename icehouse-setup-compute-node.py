#!/usr/bin/env python

#######################################################################
# OpenStack Icehouse Compute Node Setup Script
#######################################################################

import sys
import os

sys.path.append(os.path.dirname(__file__))
import openstackinstall.common as osicommon
import openstackinstall.icehouse as icehouse


if not os.geteuid() == 0:
  sys.exit('This script must be run as root')

print '#######################################################################'
print '# OpenStack Icehouse Compute Node Setup'
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
managementNetworkInterface = osicommon.get_config_ini(iniPath, 'compute', 'network_interface_management')
managementNetworkIP = osicommon.get_network_address(managementNetworkInterface)
instanceNetworkInterface = osicommon.get_config_ini(iniPath, 'compute', 'network_interface_instance')
instanceNetworkIP = osicommon.get_network_address(instanceNetworkInterface)
controlManagementNetworkIP = osicommon.get_config_ini(iniPath, 'control', 'network_address_management')
print ''
osicommon.log('Using network addresses:')
print '    Control Node Management Network Address: ' + str(controlManagementNetworkIP)
print '    Compute Node Management Network Address: ' + str(managementNetworkIP)
print '    Compute Node Instance Network Address: ' + str(instanceNetworkIP)

# Install NTP
icehouse.install_ntp(controlManagementNetworkIP)

# Install Nova
novaDatabasePassword = osicommon.get_config_ini(iniPath, 'nova', 'database_user_password')
icehouse.install_nova_on_compute_node(novaDatabasePassword, controlManagementNetworkIP, managementNetworkIP)

# Install Neutron
neutronDatabasePassword = osicommon.get_config_ini(iniPath, 'neutron', 'database_user_password')
icehouse.install_neutron_on_compute_node(neutronDatabasePassword, controlManagementNetworkIP, instanceNetworkIP)

print ''
osicommon.log('Finished installation')
print ''

