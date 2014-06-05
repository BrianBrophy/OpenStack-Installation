#!/usr/bin/env python

#######################################################################
# OpenStack Icehouse Control Node Setup Script
#######################################################################

import sys
import os

sys.path.append(os.path.dirname(__file__))
import openstackinstall.common as osicommon


if not os.geteuid() == 0:
  sys.exit('This script must be run as root')

print '#######################################################################'
print '# OpenStack Icehouse Control Node Setup'
print '#######################################################################'
osicommon.log('Starting installation')
print ''

# Update, Upgrade, Add Repo
osicommon.base_system_update()

# Install INI path
iniPath = os.path.join(os.path.dirname(__file__), 'icehouse-install.ini')

# Get network addresses
managementNetworkInterface = osicommon.get_config_ini(iniPath, 'control', 'network_interface_management')
managementNetworkIP = osicommon.get_network_address(managementNetworkInterface)
osicommon.set_config_ini(iniPath, 'control', 'network_address_management', managementNetworkIP)
print ''
osicommon.log('Using network addresses:')
print '    Control Node Management Network Address: ' + str(managementNetworkIP)

# Install NTP
osicommon.install_ntp(managementNetworkIP)

# Install RabbitMQ
osicommon.install_rabbitmq()

# Install MySQL
mysqlPassword = osicommon.get_config_ini(iniPath, 'mysql', 'root_password')
osicommon.install_mysql(mysqlPassword)

# Install Keystone
keystoneDatabasePassword = osicommon.get_config_ini(iniPath, 'keystone', 'database_user_password')
osicommon.install_keystone(keystoneDatabasePassword, managementNetworkIP, mysqlPassword)

# Install Glance
glanceDatabasePassword = osicommon.get_config_ini(iniPath, 'glance', 'database_user_password')
osicommon.install_glance(glanceDatabasePassword, managementNetworkIP, mysqlPassword)

# Install Neutron
neutronDatabasePassword = osicommon.get_config_ini(iniPath, 'neutron', 'database_user_password')
osicommon.install_neutron_on_control_node(neutronDatabasePassword, managementNetworkIP, mysqlPassword)

# Install Nova
novaDatabasePassword = osicommon.get_config_ini(iniPath, 'nova', 'database_user_password')
osicommon.install_nova_on_control_node(novaDatabasePassword, managementNetworkIP, mysqlPassword)

# Install Cinder
cinderDatabasePassword = osicommon.get_config_ini(iniPath, 'cinder', 'database_user_password')
osicommon.install_cinder(cinderDatabasePassword, managementNetworkIP, mysqlPassword)

# Install Dashboard
osicommon.install_horizon()

print ''
osicommon.log('Finished installation')
print ''
print '#######################################################################'
print '# OpenStack Icehouse Horizon Dashboard:'
print '#   http://' + str(managementNetworkIP) + '/horizon'
print '#   login: admin / secret'
print '#######################################################################'

