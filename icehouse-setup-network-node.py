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

# Install vlan
osicommon.install_vlan()

# Install bridge-utils
osicommon.install_bridgeutils()

# Install INI path
iniPath = os.path.join(os.path.dirname(__file__), 'icehouse-install.ini')

# Get network addresses
managementNetworkIP = osicommon.get_config_ini(iniPath, 'network', 'conrol_node_management_address')
apiNetworkIP = osicommon.get_config_ini(iniPath, 'network', 'conrol_node_api_address')
print ''
osicommon.log('Using network addresses:')
print '    Control Node Management Network Address: ' + str(managementNetworkIP)
print '    Control Node API Network Address: ' + str(apiNetworkIP)

# Install NTP
osicommon.install_ntp(managementNetworkIP)

# Install Neutron
neutronDatabasePassword = osicommon.get_config_ini(iniPath, 'neutron', 'database_user_password')
osicommon.install_neutron_on_network_node(neutronDatabasePassword, managementNetworkIP, managementNetworkIP)

print ''
osicommon.log('Finished installation')
print ''

