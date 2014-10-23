import os
import sys
import time

import common as osicommon

#######################################################################
def base_system_update():
  print ''
  osicommon.log('Updating and Upgrading System')
  osicommon.run_command("apt-get clean" , True)
  osicommon.run_command("apt-get autoclean -y" , True)
  osicommon.run_command("apt-get update -y" , True)
  osicommon.run_command("apt-get install -y ubuntu-cloud-keyring python-setuptools python-iniparse python-psutil python-software-properties ethtool", True)
  osicommon.delete_file("/etc/apt/sources.list.d/juno.list")
  osicommon.run_command("echo deb http://ubuntu-cloud.archive.canonical.com/ubuntu trusty-updates/juno main >> /etc/apt/sources.list.d/juno.list")
  osicommon.run_command("apt-get update -y", True)
  osicommon.run_command("apt-get dist-upgrade -y", True)
#######################################################################


#######################################################################
def install_bridgeutils():
  print ''
  osicommon.log('Installing bridge-utils')
  osicommon.run_command("apt-get install -y bridge-utils" , True)
  osicommon.log('Completed bridge-utils')
#######################################################################


#######################################################################
def install_cinder(databaseUserPassword, controlNodeIP, mySQLPassword):
  if not databaseUserPassword or len(str(databaseUserPassword)) == 0:
    raise Exception("Unable to install/configure cinder, no database user password specified")
  if not mySQLPassword or len(str(mySQLPassword)) == 0:
    raise Exception("Unable to install/configure cinder, no MySQL Password specified")
  if not controlNodeIP or len(str(controlNodeIP)) == 0:
    raise Exception("Unable to install/configure cinder, no control node IP specified")
  print ''
  osicommon.log('Installing Cinder')
  osicommon.run_db_command(mySQLPassword, "CREATE DATABASE IF NOT EXISTS cinder CHARACTER SET utf8 COLLATE utf8_general_ci;")
  osicommon.run_db_command(mySQLPassword, "GRANT ALL ON cinder.* TO 'cinder'@'%' IDENTIFIED BY '" + databaseUserPassword + "';")
  # iscsitarget is not needed, can use tgt instead - which is what cinder-volume wants to use
  os.environ['DEBIAN_FRONTEND'] = 'noninteractive'
  #osicommon.run_command("apt-get update -y", True)
  #try:
  # osicommon.run_command("apt-get install -y --force-yes iscsitarget open-iscsi iscsitarget-dkms", True)
  #except:
  # # try one last time
  # osicommon.run_command("apt-get install -y --force-yes iscsitarget open-iscsi iscsitarget-dkms", True)
  osicommon.run_command("apt-get install -y open-iscsi cinder-api cinder-scheduler cinder-volume sysfsutils tgt" , True)
  osicommon.log('Configuring Cinder')
  osicommon.run_command("service tgt restart")
  #osicommon.run_command("sed -i 's/false/true/g' /etc/default/iscsitarget")
  #osicommon.run_command("service iscsitarget restart")
  osicommon.run_command("service open-iscsi restart")
  cinderConf = '/etc/cinder/cinder.conf'
  osicommon.set_config_ini(cinderConf, 'DEFAULT', 'rootwrap_config', '/etc/cinder/rootwrap.conf')
  osicommon.set_config_ini(cinderConf, 'DEFAULT', 'sql_connection', "mysql://cinder:%s@%s/cinder" %(databaseUserPassword,controlNodeIP))
  osicommon.set_config_ini(cinderConf, 'DEFAULT', 'api_paste_config', '/etc/cinder/api-paste.ini')
  osicommon.set_config_ini(cinderConf, 'DEFAULT', 'iscsi_helper', 'tgtadm')
  osicommon.set_config_ini(cinderConf, 'DEFAULT', 'volume_name_template', 'volume-%s')
  osicommon.set_config_ini(cinderConf, 'DEFAULT', 'volume_group', 'cinder-volumes')
  osicommon.set_config_ini(cinderConf, 'DEFAULT', 'verbose', 'False')
  osicommon.set_config_ini(cinderConf, 'DEFAULT', 'auth_strategy', 'keystone')
  osicommon.set_config_ini(cinderConf, 'DEFAULT', 'iscsi_ip_address', controlNodeIP)
  osicommon.set_config_ini(cinderConf, 'DEFAULT', 'glance_host', controlNodeIP)
  osicommon.set_config_ini(cinderConf, 'DEFAULT', 'rpc_backend', 'cinder.openstack.common.rpc.impl_kombu')
  osicommon.set_config_ini(cinderConf, 'DEFAULT', 'rabbit_host', controlNodeIP)
  osicommon.set_config_ini(cinderConf, 'DEFAULT', 'rabbit_port', '5672')
  osicommon.set_config_ini(cinderConf, 'database', 'connection', "mysql://cinder:%s@%s/cinder" %(databaseUserPassword,controlNodeIP))
  osicommon.set_config_ini(cinderConf, 'keystone_authtoken', 'auth_uri', "http://%s:5000/v2.0" %controlNodeIP)
  osicommon.set_config_ini(cinderConf, 'keystone_authtoken', 'identity_uri', "http://%s:35357" %controlNodeIP)
  osicommon.remove_config_ini(cinderConf, 'keystone_authtoken', 'auth_host')
  osicommon.remove_config_ini(cinderConf, 'keystone_authtoken', 'auth_port')
  osicommon.remove_config_ini(cinderConf, 'keystone_authtoken', 'auth_protocol')
  osicommon.set_config_ini(cinderConf, 'keystone_authtoken', 'admin_tenant_name', 'service')
  osicommon.set_config_ini(cinderConf, 'keystone_authtoken', 'admin_user', 'cinder')
  osicommon.set_config_ini(cinderConf, 'keystone_authtoken', 'admin_password', 'cinder')
  cinderApiPasteConf = '/etc/cinder/api-paste.ini'
  osicommon.set_config_ini(cinderApiPasteConf, 'filter:authtoken', 'service_protocol', 'http')
  osicommon.set_config_ini(cinderApiPasteConf, 'filter:authtoken', 'service_host', controlNodeIP)
  osicommon.set_config_ini(cinderApiPasteConf, 'filter:authtoken', 'service_port', '5000')
  osicommon.set_config_ini(cinderApiPasteConf, 'filter:authtoken', 'auth_host', controlNodeIP)
  osicommon.set_config_ini(cinderApiPasteConf, 'filter:authtoken', 'auth_port', '35357')
  osicommon.set_config_ini(cinderApiPasteConf, 'filter:authtoken', 'auth_protocol', 'http')
  osicommon.set_config_ini(cinderApiPasteConf, 'filter:authtoken', 'admin_tenant_name', 'service')
  osicommon.set_config_ini(cinderApiPasteConf, 'filter:authtoken', 'admin_user', 'cinder')
  osicommon.set_config_ini(cinderApiPasteConf, 'filter:authtoken', 'admin_password', 'cinder')
  osicommon.set_config_ini(cinderApiPasteConf, 'filter:authtoken', 'signing_dir', '/var/lib/cinder')
  osicommon.run_command("cinder-manage db sync", True)
  osicommon.run_command("service cinder-api restart")
  osicommon.run_command("service cinder-scheduler restart")
  osicommon.run_command("service cinder-volume restart")
  osicommon.log('Completed Cinder')
#######################################################################


#######################################################################
def install_glance(databaseUserPassword, controlNodeIP, mySQLPassword):
  if not databaseUserPassword or len(str(databaseUserPassword)) == 0:
    raise Exception("Unable to install/configure glance, no database user password specified")
  if not mySQLPassword or len(str(mySQLPassword)) == 0:
    raise Exception("Unable to install/configure glance, no MySQL Password specified")
  if not controlNodeIP or len(str(controlNodeIP)) == 0:
    raise Exception("Unable to install/configure glance, no control node IP specified")
  print ''
  osicommon.log('Installing Glance')
  osicommon.run_db_command(mySQLPassword, "CREATE DATABASE IF NOT EXISTS glance CHARACTER SET utf8 COLLATE utf8_general_ci;")
  osicommon.run_db_command(mySQLPassword, "GRANT ALL ON glance.* TO 'glance'@'%' IDENTIFIED BY '" + databaseUserPassword + "';")
  osicommon.run_command("apt-get install -y glance python-glanceclient" , True)
  osicommon.log('Configuring Glance')
  osicommon.delete_file('/var/lib/glance/glance.sqlite')
  glanceApiConf = '/etc/glance/glance-api.conf'
  osicommon.set_config_ini(glanceApiConf, 'DEFAULT', 'sql_connection', "mysql://glance:%s@%s/glance" %(databaseUserPassword,controlNodeIP))
  osicommon.set_config_ini(glanceApiConf, 'DEFAULT', 'verbose', 'false')
  osicommon.set_config_ini(glanceApiConf, 'DEFAULT', 'debug', 'false')
  osicommon.set_config_ini(glanceApiConf, 'DEFAULT', 'rpc_backend', 'rabbit')
  osicommon.set_config_ini(glanceApiConf, 'DEFAULT', 'rabbit_host', controlNodeIP)
  osicommon.set_config_ini(glanceApiConf, 'database', 'connection', "mysql://glance:%s@%s/glance" %(databaseUserPassword,controlNodeIP))
  #osicommon.set_config_ini(glanceApiConf, 'DEFAULT', 'db_enforce_mysql_charset', 'false')
  osicommon.set_config_ini(glanceApiConf, 'keystone_authtoken', 'auth_uri', "http://%s:5000/v2.0" %controlNodeIP)
  osicommon.set_config_ini(glanceApiConf, 'keystone_authtoken', 'identity_uri', "http://%s:35357" %controlNodeIP)
  osicommon.remove_config_ini(glanceApiConf, 'keystone_authtoken', 'auth_host')
  osicommon.remove_config_ini(glanceApiConf, 'keystone_authtoken', 'auth_port')
  osicommon.remove_config_ini(glanceApiConf, 'keystone_authtoken', 'auth_protocol')
  osicommon.set_config_ini(glanceApiConf, 'keystone_authtoken', 'admin_tenant_name', 'service')
  osicommon.set_config_ini(glanceApiConf, 'keystone_authtoken', 'admin_user', 'glance')
  osicommon.set_config_ini(glanceApiConf, 'keystone_authtoken', 'admin_password', 'glance')
  osicommon.set_config_ini(glanceApiConf, 'paste_deploy', 'flavor', 'keystone')
  glanceApiPasteConf = '/etc/glance/glance-api-paste.ini'
  osicommon.set_config_ini(glanceApiPasteConf, 'filter:authtoken', 'auth_host', controlNodeIP)
  osicommon.set_config_ini(glanceApiPasteConf, 'filter:authtoken', 'auth_port', '35357')
  osicommon.set_config_ini(glanceApiPasteConf, 'filter:authtoken', 'auth_protocol', 'http')
  osicommon.set_config_ini(glanceApiPasteConf, 'filter:authtoken', 'admin_tenant_name', 'service')
  osicommon.set_config_ini(glanceApiPasteConf, 'filter:authtoken', 'admin_user', 'glance')
  osicommon.set_config_ini(glanceApiPasteConf, 'filter:authtoken', 'admin_password', 'glance')
  glanceRegistryConf = '/etc/glance/glance-registry.conf'
  osicommon.set_config_ini(glanceRegistryConf, 'DEFAULT', 'sql_connection', "mysql://glance:%s@%s/glance" %(databaseUserPassword,controlNodeIP))
  osicommon.set_config_ini(glanceRegistryConf, 'DEFAULT', 'verbose', 'false')
  osicommon.set_config_ini(glanceRegistryConf, 'DEFAULT', 'debug', 'false')
  osicommon.set_config_ini(glanceRegistryConf, 'database', 'connection', "mysql://glance:%s@%s/glance" %(databaseUserPassword,controlNodeIP))
  osicommon.set_config_ini(glanceRegistryConf, 'keystone_authtoken', 'auth_uri', "http://%s:5000/v2.0" %controlNodeIP)
  osicommon.set_config_ini(glanceRegistryConf, 'keystone_authtoken', 'identity_uri', "http://%s:35357" %controlNodeIP)
  osicommon.remove_config_ini(glanceRegistryConf, 'keystone_authtoken', 'auth_host')
  osicommon.remove_config_ini(glanceRegistryConf, 'keystone_authtoken', 'auth_port')
  osicommon.remove_config_ini(glanceRegistryConf, 'keystone_authtoken', 'auth_protocol')
  osicommon.set_config_ini(glanceRegistryConf, 'keystone_authtoken', 'admin_tenant_name', 'service')
  osicommon.set_config_ini(glanceRegistryConf, 'keystone_authtoken', 'admin_user', 'glance')
  osicommon.set_config_ini(glanceRegistryConf, 'keystone_authtoken', 'admin_password', 'glance')
  osicommon.set_config_ini(glanceRegistryConf, 'paste_deploy', 'flavor', 'keystone')
  glanceRegistryPasteConf = '/etc/glance/glance-registry-paste.ini'
  osicommon.set_config_ini(glanceRegistryPasteConf, 'filter:authtoken', 'auth_host', controlNodeIP)
  osicommon.set_config_ini(glanceRegistryPasteConf, 'filter:authtoken', 'auth_port', '35357')
  osicommon.set_config_ini(glanceRegistryPasteConf, 'filter:authtoken', 'auth_protocol', 'http')
  osicommon.set_config_ini(glanceRegistryPasteConf, 'filter:authtoken', 'admin_tenant_name', 'service')
  osicommon.set_config_ini(glanceRegistryPasteConf, 'filter:authtoken', 'admin_user', 'glance')
  osicommon.set_config_ini(glanceRegistryPasteConf, 'filter:authtoken', 'admin_password', 'glance')
  osicommon.run_command("service glance-api restart", True)
  osicommon.run_command("service glance-registry restart", True)
  time.sleep(10)
  osicommon.run_command("glance-manage db_sync", True)
  osicommon.log('Completed Glance')
#######################################################################


#######################################################################
def install_heat(databaseUserPassword, controlNodeIP, mySQLPassword):
  if not databaseUserPassword or len(str(databaseUserPassword)) == 0:
    raise Exception("Unable to install/configure cinder, no database user password specified")
  if not controlNodeIP or len(str(controlNodeIP)) == 0:
    raise Exception("Unable to install/configure cinder, no control node IP specified")
  if not mySQLPassword or len(str(mySQLPassword)) == 0:
    raise Exception("Unable to install/configure cinder, no MySQL Password specified")
  print ''
  osicommon.log('Installing Heat')
  osicommon.run_db_command(mySQLPassword, "CREATE DATABASE IF NOT EXISTS heat CHARACTER SET utf8 COLLATE utf8_general_ci;")
  osicommon.run_db_command(mySQLPassword, "GRANT ALL ON heat.* TO 'heat'@'%' IDENTIFIED BY '" + databaseUserPassword + "';")
  osicommon.run_command("apt-get install -y heat-api heat-api-cfn heat-engine python-heatclient", True)
  osicommon.delete_file('Configuring Heat')
  osicommon.delete_file('/var/lib/heat/heat.sqlite')
  heatConf = '/etc/heat/heat.conf'
  osicommon.set_config_ini(heatConf, 'DEFAULT', 'log_dir', '/var/log/heat')
  osicommon.set_config_ini(heatConf, 'DEFAULT', 'verbose', 'False')
  osicommon.set_config_ini(heatConf, 'DEFAULT', 'rabbit_host', controlNodeIP)
  osicommon.set_config_ini(heatConf, 'DEFAULT', 'rabbit_port', '5672')
  osicommon.set_config_ini(heatConf, 'DEFAULT', 'heat_metadata_server_url', "http://%s:8000" %controlNodeIP)
  osicommon.set_config_ini(heatConf, 'DEFAULT', 'heat_waitcondition_server_url', "http://%s:8000/v1/waitcondition" %controlNodeIP)
  osicommon.set_config_ini(heatConf, 'DEFAULT', 'stack_domain_admin', 'heat_admin')
  osicommon.set_config_ini(heatConf, 'DEFAULT', 'stack_domain_admin_password', 'heat_password')
  osicommon.set_config_ini(heatConf, 'DEFAULT', 'heat_stack_user_role', 'heat_stack_user')
  osicommon.set_config_ini(heatConf, 'database', 'connection', "mysql://heat:%s@%s/heat" %(databaseUserPassword,controlNodeIP))
  osicommon.set_config_ini(heatConf, 'ec2authtoken', 'auth_uri', "http://%s:5000/v2.0" %controlNodeIP)
  osicommon.set_config_ini(heatConf, 'keystone_authtoken', 'auth_uri', "http://%s:5000/v2.0" %controlNodeIP)
  osicommon.set_config_ini(heatConf, 'keystone_authtoken', 'identity_uri', "http://%s:35357" %controlNodeIP)
  osicommon.remove_config_ini(heatConf, 'keystone_authtoken', 'auth_host')
  osicommon.remove_config_ini(heatConf, 'keystone_authtoken', 'auth_port')
  osicommon.remove_config_ini(heatConf, 'keystone_authtoken', 'auth_protocol')
  osicommon.set_config_ini(heatConf, 'keystone_authtoken', 'admin_tenant_name', 'service')
  osicommon.set_config_ini(heatConf, 'keystone_authtoken', 'admin_user', 'heat')
  osicommon.set_config_ini(heatConf, 'keystone_authtoken', 'admin_password', 'heat')
  osicommon.set_config_ini(heatConf, 'keystone_authtoken', 'service_host', controlNodeIP)
  osicommon.set_config_ini(heatConf, 'keystone_authtoken', 'keystone_ec2_uri', "http://%s:35357/v2.0" %controlNodeIP)
  heatApiPasteConf = '/etc/heat/api-paste.ini'
  osicommon.set_config_ini(heatApiPasteConf, 'filter:authtoken', 'auth_host', controlNodeIP)
  osicommon.set_config_ini(heatApiPasteConf, 'filter:authtoken', 'auth_port', '35357')
  osicommon.set_config_ini(heatApiPasteConf, 'filter:authtoken', 'auth_protocol', 'http')
  osicommon.set_config_ini(heatApiPasteConf, 'filter:authtoken', 'auth_uri', "http://%s:5000/v2.0" %controlNodeIP)
  osicommon.set_config_ini(heatApiPasteConf, 'filter:authtoken', 'admin_tenant_name', 'service')
  osicommon.set_config_ini(heatApiPasteConf, 'filter:authtoken', 'admin_user', 'heat')
  osicommon.set_config_ini(heatApiPasteConf, 'filter:authtoken', 'admin_password', 'heat')
  # Create the Heat Domain using Python API
  from keystoneclient.v3 import client
  import keystoneclient.exceptions as kc_exception
  USERNAME = 'admin'
  PASSWORD = 'secret'
  AUTH_URL = "http://%s:5000/v3" %controlNodeIP
  HEAT_DOMAIN = 'heat'
  HEAT_DOMAIN_ADMIN = 'heat_admin'
  HEAT_DOMAIN_PASSWORD = 'heat_password'
  HEAT_DOMAIN_NAME = 'heat'
  HEAT_DOMAIN_DESCRIPTION = 'Contains users and projects created by Heat'
  c = client.Client(debug=False, username=USERNAME, password=PASSWORD, auth_url=AUTH_URL, endpoint=AUTH_URL)
  ret = c.authenticate()
  heat_domain = c.domains.list(name=HEAT_DOMAIN_NAME)
  if not heat_domain:
    heat_domain = c.domains.create(name=HEAT_DOMAIN_NAME, description=HEAT_DOMAIN_DESCRIPTION)
  heat_domain = c.domains.list(name=HEAT_DOMAIN_NAME)[0]
  domain_admin = c.users.list(name=HEAT_DOMAIN_ADMIN)
  if not domain_admin:
    domain_admin = c.users.create(name=HEAT_DOMAIN_ADMIN, password=HEAT_DOMAIN_PASSWORD, domain=heat_domain, description="Heat domain admin")
  domain_admin = c.users.list(name=HEAT_DOMAIN_ADMIN)[0]
  roles_list = c.roles.list()
  admin_role = [r for r in roles_list
    if r.name == 'admin'][0]
  c.roles.grant(role=admin_role, user=domain_admin, domain=heat_domain)
  # Update stack_user_domain in config
  osicommon.set_config_ini(heatConf, 'DEFAULT', 'stack_user_domain', heat_domain.id)
  osicommon.run_command("service heat-api restart", True)
  osicommon.run_command("service heat-api-cfn restart", True)
  osicommon.run_command("service heat-engine restart", True)
  time.sleep(10)
  osicommon.run_command("heat-manage db_sync", True)
  # Another restart seems to be the most reliable thing after the db_sync in Heat
  # Sometimes seeing RPC timeouts if a final restart is not done
  time.sleep(10)
  osicommon.run_command("service heat-api restart", True)
  osicommon.run_command("service heat-api-cfn restart", True)
  osicommon.run_command("service heat-engine restart", True)
  time.sleep(10)
  osicommon.log('Completed Heat')
#######################################################################


#######################################################################
def install_horizon():
  print ''
  osicommon.log('Installing Horizon')
  osicommon.run_command("apt-get install -y apache2 openstack-dashboard memcached", True)
  # Enable LBaaS within dashboard
  enableLBaaSCmd = "sed -i " + '"' + "s/'enable_lb'\:\s*False/'enable_lb'\: True/" + '"' + " /etc/openstack-dashboard/local_settings.py"
  osicommon.run_command(enableLBaaSCmd)
  osicommon.run_command("service apache2 restart", True)
  osicommon.run_command("service memcached restart", True)
  osicommon.log('Completed Horizon')
#######################################################################


#######################################################################
def install_keystone(databaseUserPassword, controlNodeIP, mySQLPassword):
  if not databaseUserPassword or len(str(databaseUserPassword)) == 0:
    raise Exception("Unable to install/configure keystone, no database user password specified")
  if not mySQLPassword or len(str(mySQLPassword)) == 0:
    raise Exception("Unable to install/configure keystone, no MySQL Password specified")
  if not controlNodeIP or len(str(controlNodeIP)) == 0:
    raise Exception("Unable to install/configure keystone, no control node IP specified")
  print ''
  osicommon.log('Installing Keystone')
  osicommon.run_db_command(mySQLPassword, "CREATE DATABASE IF NOT EXISTS keystone CHARACTER SET utf8 COLLATE utf8_general_ci;")
  osicommon.run_db_command(mySQLPassword, "GRANT ALL ON keystone.* TO 'keystone'@'%' IDENTIFIED BY '" + databaseUserPassword + "';")
  osicommon.run_command("apt-get install -y python-six python-babel keystone" , True)
  osicommon.log('Configuring Keystone')
  osicommon.delete_file('/var/lib/keystone/keystone.db')
  keystoneConf = '/etc/keystone/keystone.conf'
  osicommon.set_config_ini(keystoneConf, 'DEFAULT', 'admin_token', 'ADMINTOKEN')
  osicommon.set_config_ini(keystoneConf, 'DEFAULT', 'admin_port', 35357)
  osicommon.set_config_ini(keystoneConf, 'DEFAULT', 'log_dir', '/var/log/keystone')
  osicommon.set_config_ini(keystoneConf, 'database', 'connection', "mysql://keystone:%s@%s/keystone" %(databaseUserPassword,controlNodeIP))
  osicommon.set_config_ini(keystoneConf, 'signing', 'token_format', 'UUID')
  osicommon.run_command("service keystone restart" , True)
  time.sleep(10)
  osicommon.run_command("keystone-manage db_sync" , True)

  # Configure users/endpoints/etc
  os.environ['SERVICE_TOKEN'] = 'ADMINTOKEN'
  os.environ['SERVICE_ENDPOINT'] = 'http://%s:35357/v2.0'% controlNodeIP
  os.environ['no_proxy'] = "localhost,127.0.0.1,%s" % controlNodeIP

  # Little bit of dancing to handle if the admin user already exists or maybe does not yet
  adminrc = '/root/openstack-admin.rc'
  adminAuthArg = ''
  adminUserExists = os.path.exists(adminrc) and os.path.isfile(adminrc)
  if adminUserExists:
    adminAuthArg = " --os-username admin --os-password secret --os-auth-url http://%s:5000/v2.0 " % controlNodeIP

  admin_tenant = osicommon.run_command("keystone " + adminAuthArg + " tenant-list | grep admin | awk '{print $2}'")
  if not admin_tenant or not len(str(admin_tenant)) > 0:
    admin_tenant = osicommon.run_command("keystone " + adminAuthArg + " tenant-create --name admin --description 'Admin Tenant' --enabled true |grep ' id '|awk '{print $4}'")

  admin_user = osicommon.run_command("keystone " + adminAuthArg + " user-list | grep admin | awk '{print $2}'")
  if not admin_user or not len(str(admin_user)) > 0:
    admin_user = osicommon.run_command("keystone " + adminAuthArg + " user-create --tenant_id %s --name admin --pass secret --enabled true|grep ' id '|awk '{print $4}'" % admin_tenant)

  # Now that the admin user definitely exists, setup auth for remaining commands
  osicommon.run_command("echo 'export OS_USERNAME=admin' >%s" %adminrc)
  osicommon.run_command("echo 'export OS_PASSWORD=secret' >>%s" %adminrc)
  osicommon.run_command("echo 'export OS_TENANT_NAME=admin' >>%s" %adminrc)
  osicommon.run_command("echo 'export OS_AUTH_URL=http://%s:5000/v2.0' >>%s" % (controlNodeIP,adminrc))
  adminAuthArg = " --os-username admin --os-password secret --os-auth-url http://%s:5000/v2.0 " % controlNodeIP

  admin_role = osicommon.run_command("keystone " + adminAuthArg + " role-list| grep admin | awk '{print $2}'")
  if not admin_role or not len(str(admin_user)) > 0:
    admin_role = osicommon.run_command("keystone " + adminAuthArg + " role-create --name admin|grep ' id '|awk '{print $4}'")

  heat_role = osicommon.run_command("keystone " + adminAuthArg + " role-list| grep 'heat_stack_user' | awk '{print $2}'")
  if not heat_role or not len(str(heat_role)) > 0:
    heat_role = osicommon.run_command("keystone " + adminAuthArg + " role-create --name heat_stack_user|grep ' id '|awk '{print $4}'")

  admin_role_mapped = osicommon.run_command("keystone " + adminAuthArg + " user-role-list --user_id %s --tenant_id %s | grep %s | awk '{print $2}'" % (admin_user,admin_tenant,admin_role))
  if not admin_role_mapped or not len(str(admin_role_mapped)) > 0:
    osicommon.run_command("keystone " + adminAuthArg + " user-role-add --user_id %s --tenant_id %s --role_id %s" % (admin_user, admin_tenant, admin_role))

  service_tenant = osicommon.run_command("keystone " + adminAuthArg + " tenant-list | grep service | awk '{print $2}'")
  if not service_tenant or not len(str(service_tenant)) > 0:
    service_tenant = osicommon.run_command("keystone " + adminAuthArg + " tenant-create --name service --description 'Service Tenant' --enabled true |grep ' id '|awk '{print $4}'")

  keystone_service = osicommon.run_command("keystone " + adminAuthArg + " service-list| grep keystone | awk '{print $2}'")
  if not keystone_service or not len(str(keystone_service)) > 0:
    keystone_service = osicommon.run_command("keystone " + adminAuthArg + " service-create --name=keystone --type=identity --description='Keystone Identity Service'|grep ' id '|awk '{print $4}'")

  keystone_endpoint = osicommon.run_command("keystone " + adminAuthArg + " endpoint-list | grep %s | awk '{print $2}'" % keystone_service)
  if keystone_endpoint and len(str(keystone_endpoint)) > 0:
    osicommon.run_command("keystone " + adminAuthArg + " endpoint-delete %s" % keystone_service)
  osicommon.run_command("keystone " + adminAuthArg + " endpoint-create --region region --service_id=%s --publicurl=http://%s:5000/v2.0 --internalurl=http://%s:5000/v2.0 --adminurl=http://%s:35357/v2.0" % (keystone_service,controlNodeIP,controlNodeIP,controlNodeIP))

  glance_user = osicommon.run_command("keystone " + adminAuthArg + " user-list | grep glance | awk '{print $2}'")
  if not glance_user or not len(str(glance_user)) > 0:
    glance_user = osicommon.run_command("keystone " + adminAuthArg + " user-create --tenant_id %s --name glance --pass glance --enabled true|grep ' id '|awk '{print $4}'" % service_tenant)

  glance_role_mapped = osicommon.run_command("keystone " + adminAuthArg + " user-role-list --user_id %s --tenant_id %s | grep %s | awk '{print $2}'" % (glance_user, service_tenant, admin_role))
  if not glance_role_mapped or not len(str(glance_role_mapped)) > 0:
    osicommon.run_command("keystone " + adminAuthArg + " user-role-add --user_id %s --tenant_id %s --role_id %s" % (glance_user, service_tenant, admin_role))

  glance_service = osicommon.run_command("keystone " + adminAuthArg + " service-list| grep glance | awk '{print $2}'")
  if not glance_service or not len(str(glance_service)) > 0:
    glance_service = osicommon.run_command("keystone " + adminAuthArg + " service-create --name=glance --type=image --description='Glance Image Service'|grep ' id '|awk '{print $4}'")

  glance_endpoint = osicommon.run_command("keystone " + adminAuthArg + " endpoint-list | grep %s | awk '{print $2}'" % glance_service)
  if glance_endpoint and len(str(glance_endpoint)) > 0:
    osicommon.run_command("keystone " + adminAuthArg + " endpoint-delete %s" % glance_service)
  osicommon.run_command("keystone " + adminAuthArg + " endpoint-create --region region --service_id=%s --publicurl=http://%s:9292/v2 --internalurl=http://%s:9292/v2 --adminurl=http://%s:9292/v2" % (glance_service,controlNodeIP,controlNodeIP,controlNodeIP))

  nova_user = osicommon.run_command("keystone " + adminAuthArg + " user-list | grep nova | awk '{print $2}'")
  if not nova_user or not len(str(nova_user)) > 0:
    nova_user = osicommon.run_command("keystone " + adminAuthArg + " user-create --tenant_id %s --name nova --pass nova --enabled true|grep ' id '|awk '{print $4}'" % service_tenant)

  nova_role_mapped = osicommon.run_command("keystone " + adminAuthArg + " user-role-list --user_id %s --tenant_id %s | grep %s | awk '{print $2}'" % (nova_user, service_tenant, admin_role))
  if not nova_role_mapped or not len(str(nova_role_mapped)) > 0:
    osicommon.run_command("keystone " + adminAuthArg + " user-role-add --user_id %s --tenant_id %s --role_id %s" % (nova_user, service_tenant, admin_role))

  nova_service = osicommon.run_command("keystone " + adminAuthArg + " service-list| grep nova | awk '{print $2}'")
  if not nova_service or not len(str(nova_service)) > 0:
    nova_service = osicommon.run_command("keystone " + adminAuthArg + " service-create --name=nova --type=compute --description='Nova Compute Service'|grep ' id '|awk '{print $4}'")

  nova_endpoint = osicommon.run_command("keystone " + adminAuthArg + " endpoint-list | grep %s | awk '{print $2}'" % nova_service)
  if nova_endpoint and len(str(nova_endpoint)) > 0:
    osicommon.run_command("keystone " + adminAuthArg + " endpoint-delete %s" % nova_service)
  osicommon.run_command("keystone " + adminAuthArg + " endpoint-create --region region --service_id=%s --publicurl='http://%s:8774/v2/$(tenant_id)s' --internalurl='http://%s:8774/v2/$(tenant_id)s' --adminurl='http://%s:8774/v2/$(tenant_id)s'" % (nova_service,controlNodeIP,controlNodeIP,controlNodeIP))

  neutron_user = osicommon.run_command("keystone " + adminAuthArg + " user-list | grep neutron | awk '{print $2}'")
  if not neutron_user or not len(str(neutron_user)) > 0:
    neutron_user = osicommon.run_command("keystone " + adminAuthArg + " user-create --tenant_id %s --name neutron --pass neutron --enabled true|grep ' id '|awk '{print $4}'" % service_tenant)

  neutron_role_mapped = osicommon.run_command("keystone " + adminAuthArg + " user-role-list --user_id %s --tenant_id %s | grep %s | awk '{print $2}'" % (neutron_user, service_tenant, admin_role))
  if not neutron_role_mapped or not len(str(neutron_role_mapped)) > 0:
    osicommon.run_command("keystone " + adminAuthArg + " user-role-add --user_id %s --tenant_id %s --role_id %s" % (neutron_user, service_tenant, admin_role))

  neutron_service = osicommon.run_command("keystone " + adminAuthArg + " service-list| grep neutron | awk '{print $2}'")
  if not neutron_service or not len(str(neutron_service)) > 0:
    neutron_service = osicommon.run_command("keystone " + adminAuthArg + " service-create --name=neutron --type=network --description='Neutron Networking Service'|grep ' id '|awk '{print $4}'")

  neutron_endpoint = osicommon.run_command("keystone " + adminAuthArg + " endpoint-list | grep %s | awk '{print $2}'" % neutron_service)
  if neutron_endpoint and len(str(neutron_endpoint)) > 0:
    osicommon.run_command("keystone " + adminAuthArg + " endpoint-delete %s" % neutron_service)
  osicommon.run_command("keystone " + adminAuthArg + " endpoint-create --region region --service_id=%s --publicurl=http://%s:9696/ --internalurl=http://%s:9696/ --adminurl=http://%s:9696/" % (neutron_service,controlNodeIP,controlNodeIP,controlNodeIP))

  cinder_user = osicommon.run_command("keystone " + adminAuthArg + " user-list| grep cinder | awk '{print $2}'")
  if not cinder_user or not len(str(cinder_user)) > 0:
    cinder_user = osicommon.run_command("keystone " + adminAuthArg + " user-create --tenant_id %s --name cinder --pass cinder --enabled true|grep ' id '|awk '{print $4}'" % service_tenant)

  cinder_role_mapped = osicommon.run_command("keystone " + adminAuthArg + " user-role-list --user_id %s --tenant_id %s | grep %s | awk '{print $2}'" % (cinder_user, service_tenant, admin_role))
  if not cinder_role_mapped or not len(str(cinder_role_mapped)) > 0:
    osicommon.run_command("keystone " + adminAuthArg + " user-role-add --user_id %s --tenant_id %s --role_id %s" % (cinder_user, service_tenant, admin_role))

  cinder_service = osicommon.run_command("keystone " + adminAuthArg + " service-list| grep cinder | awk '{print $2}'")
  if not cinder_service or not len(str(cinder_service)) > 0:
    cinder_service = osicommon.run_command("keystone " + adminAuthArg + " service-create --name=cinder --type=volume --description='Cinder Volume Service'|grep ' id '|awk '{print $4}'")

  cinder_endpoint = osicommon.run_command("keystone " + adminAuthArg + " endpoint-list | grep %s | awk '{print $2}'" % cinder_service)
  if cinder_endpoint and len(str(cinder_endpoint)) > 0:
    osicommon.run_command("keystone " + adminAuthArg + " endpoint-delete %s" % cinder_service)
  osicommon.run_command("keystone " + adminAuthArg + " endpoint-create --region region --service_id=%s --publicurl 'http://%s:8776/v1/$(tenant_id)s' --internalurl='http://%s:8776/v1/$(tenant_id)s' --adminurl='http://%s:8776/v1/$(tenant_id)s'" % (cinder_service,controlNodeIP,controlNodeIP,controlNodeIP))

  heat_user = osicommon.run_command("keystone " + adminAuthArg + " user-list| grep heat | awk '{print $2}'")
  if not heat_user or not len(str(heat_user)) > 0:
    heat_user = osicommon.run_command("keystone " + adminAuthArg + " user-create --tenant_id %s --name heat --pass heat --enabled true|grep ' id '|awk '{print $4}'" % service_tenant)

  heatrole_mapped = osicommon.run_command("keystone " + adminAuthArg + " user-role-list --user_id %s --tenant_id %s | grep %s | awk '{print $2}'" % (heat_user, service_tenant, admin_role))
  if not heatrole_mapped or not len(str(heatrole_mapped)) > 0:
    osicommon.run_command("keystone " + adminAuthArg + " user-role-add --user_id %s --tenant_id %s --role_id %s" % (heat_user, service_tenant, admin_role))

  heat_service = osicommon.run_command("keystone " + adminAuthArg + " service-list| grep 'heat ' | awk '{print $2}'")
  if not heat_service or not len(str(heat_service)) > 0:
    heat_service = osicommon.run_command("keystone " + adminAuthArg + " service-create --name=heat --type=orchestration --description='Heat Orchestration Service'|grep ' id '|awk '{print $4}'")

  heat_endpoint = osicommon.run_command("keystone " + adminAuthArg + " endpoint-list | grep %s | awk '{print $2}'" % heat_service)
  if heat_endpoint and len(str(heat_endpoint)) > 0:
    osicommon.run_command("keystone " + adminAuthArg + " endpoint-delete %s" % heat_service)
  osicommon.run_command("keystone " + adminAuthArg + " endpoint-create --region region --service_id=%s --publicurl 'http://%s:8004/v1/$(tenant_id)s' --internalurl='http://%s:8004/v1/$(tenant_id)s' --adminurl='http://%s:8004/v1/$(tenant_id)s'" % (heat_service,controlNodeIP,controlNodeIP,controlNodeIP))

  heat_cfn_service = osicommon.run_command("keystone " + adminAuthArg + " service-list| grep 'heat-cfn' | awk '{print $2}'")
  if not heat_cfn_service or not len(str(heat_cfn_service)) > 0:
    heat_cfn_service = osicommon.run_command("keystone " + adminAuthArg + " service-create --name=heat-cfn --type=cloudformation --description='Heat CloudFormation Orchestration Service'|grep ' id '|awk '{print $4}'")

  heat_cfn_endpoint = osicommon.run_command("keystone " + adminAuthArg + " endpoint-list | grep %s | awk '{print $2}'" % heat_cfn_service)
  if heat_cfn_endpoint and len(str(heat_cfn_endpoint)) > 0:
    osicommon.run_command("keystone " + adminAuthArg + " endpoint-delete %s" % heat_cfn_service)
  osicommon.run_command("keystone " + adminAuthArg + " endpoint-create --region region --service_id=%s --publicurl 'http://%s:8000/v1' --internalurl='http://%s:8000/v1' --adminurl='http://%s:8000/v1'" % (heat_cfn_service,controlNodeIP,controlNodeIP,controlNodeIP))

  osicommon.log('Completed Keystone')
#######################################################################


#######################################################################
def install_mysql(rootPassword):
  if not rootPassword or len(str(rootPassword)) == 0:
    raise Exception("Unable to install/configure MySQL, no root password specified")
  print ''
  osicommon.log('Installing MySQL')
  mySqlConf = '/etc/mysql/my.cnf'
  mySqlConfOpenStackBackup = '/etc/mysql/my.cnf.orig.preOpenStack'
  mySqlConfExistsBeforeInstall = os.path.exists(mySqlConf)
  preOpenStackBackupExistsBeforeInstall = os.path.exists(mySqlConfOpenStackBackup)
  os.environ['DEBIAN_FRONTEND'] = 'noninteractive'
  osicommon.run_command("apt-get install -y mysql-server python-mysqldb" , True)
  osicommon.log('Configuring MySQL')
  osicommon.run_command("service mysql stop || true", True)
  time.sleep(10)
  if mySqlConfExistsBeforeInstall and not preOpenStackBackupExistsBeforeInstall:
    osicommon.run_command("cp " + mySqlConf + " " + mySqlConfOpenStackBackup)
  ourConfigFile = os.path.join(os.path.dirname(__file__), '../juno.mysql.my.cnf')
  osicommon.run_command("cp -f " + ourConfigFile + " " + mySqlConf)
  osicommon.run_command("service mysql restart", True)
  time.sleep(10)
  try:
    osicommon.run_command("mysqladmin -u root password %s" %rootPassword)
  except:
    # password may already be set, pass
    osicommon.log('MySQL root password was already set ... verifying')
  # verify database connectivity
  osicommon.run_db_command(rootPassword, 'show databases;')
  osicommon.log('Verified MySQL root password')
  osicommon.log('Completed MySQL')
#######################################################################


#######################################################################
def install_neutron_on_compute_node(databaseUserPassword, controlNodeIP, computeNodeInstanceIP):
  if not databaseUserPassword or len(str(databaseUserPassword)) == 0:
    raise Exception("Unable to install/configure neutron, no database user password specified")
  if not controlNodeIP or len(str(controlNodeIP)) == 0:
    raise Exception("Unable to install/configure neutron, no control node IP specified")
  if not computeNodeInstanceIP or len(str(computeNodeInstanceIP)) == 0:
    raise Exception("Unable to install/configure neutron, no compute node instance IP specified")
  print ''
  osicommon.log('Installing Neutron')
  osicommon.run_command("apt-get install -y openvswitch-switch openvswitch-datapath-dkms" , True)
  osicommon.run_command("ovs-vsctl --may-exist add-br br-int" , True)
  #osicommon.run_command("ovs-vsctl --may-exist add-br br-eth1" , True)
  #osicommon.run_command("ovs-vsctl --may-exist add-port br-eth1 eth1" , True)
  osicommon.run_command("apt-get install -y neutron-plugin-openvswitch-agent" , True)
  osicommon.log('Configuring Neutron')
  neutronConf = '/etc/neutron/neutron.conf'
  osicommon.set_config_ini(neutronConf, 'DEFAULT', 'core_plugin', 'ml2')
  osicommon.set_config_ini(neutronConf, 'DEFAULT', 'service_plugins', 'router')
  osicommon.set_config_ini(neutronConf, 'DEFAULT', 'verbose', 'False')
  osicommon.set_config_ini(neutronConf, 'DEFAULT', 'debug', 'False')
  osicommon.set_config_ini(neutronConf, 'DEFAULT', 'auth_strategy', 'keystone')
  osicommon.set_config_ini(neutronConf, 'DEFAULT', 'rpc_backend', 'neutron.openstack.common.rpc.impl_kombu')
  osicommon.set_config_ini(neutronConf, 'DEFAULT', 'rabbit_host', controlNodeIP)
  osicommon.set_config_ini(neutronConf, 'DEFAULT', 'rabbit_port', '5672')
  osicommon.set_config_ini(neutronConf, 'DEFAULT', 'allow_overlapping_ips', 'False')
  osicommon.set_config_ini(neutronConf, 'DEFAULT', 'root_helper', 'sudo neutron-rootwrap /etc/neutron/rootwrap.conf')
  osicommon.set_config_ini(neutronConf, 'keystone_authtoken', 'auth_uri', "http://" + controlNodeIP + ":5000/v2.0")
  osicommon.set_config_ini(neutronConf, 'keystone_authtoken', 'identity_uri', "http://" + controlNodeIP + ":35357")
  osicommon.remove_config_ini(neutronConf, 'keystone_authtoken', 'auth_host')
  osicommon.remove_config_ini(neutronConf, 'keystone_authtoken', 'auth_protocol')
  osicommon.remove_config_ini(neutronConf, 'keystone_authtoken', 'auth_port')
  osicommon.set_config_ini(neutronConf, 'keystone_authtoken', 'admin_tenant_name', 'service')
  osicommon.set_config_ini(neutronConf, 'keystone_authtoken', 'admin_user', 'neutron')
  osicommon.set_config_ini(neutronConf, 'keystone_authtoken', 'admin_password', 'neutron')
  neutronPasteConf = '/etc/neutron/api-paste.ini'
  osicommon.set_config_ini(neutronPasteConf, 'filter:authtoken', 'auth_host', controlNodeIP)
  osicommon.set_config_ini(neutronPasteConf, 'filter:authtoken', 'auth_port', '35357')
  osicommon.set_config_ini(neutronPasteConf, 'filter:authtoken', 'auth_protocol', 'http')
  osicommon.set_config_ini(neutronPasteConf, 'filter:authtoken', 'admin_tenant_name', 'service')
  osicommon.set_config_ini(neutronPasteConf, 'filter:authtoken', 'admin_user', 'neutron')
  osicommon.set_config_ini(neutronPasteConf, 'filter:authtoken', 'admin_password', 'neutron')
  neutronPluginConf = '/etc/neutron/plugins/ml2/ml2_conf.ini'
  osicommon.set_config_ini(neutronPluginConf, 'database', 'sql_connection', "mysql://neutron:%s@%s/neutron" %(databaseUserPassword,controlNodeIP))
  osicommon.set_config_ini(neutronPluginConf, 'ml2', 'type_drivers', 'gre')
  osicommon.set_config_ini(neutronPluginConf, 'ml2', 'tenant_network_types', 'gre')
  osicommon.set_config_ini(neutronPluginConf, 'ml2', 'mechanism_drivers', 'openvswitch')
  osicommon.set_config_ini(neutronPluginConf, 'ml2_type_gre', 'tunnel_id_ranges', '1:1000')
  osicommon.set_config_ini(neutronPluginConf, 'ovs', 'local_ip', computeNodeInstanceIP)
  osicommon.set_config_ini(neutronPluginConf, 'ovs', 'tunnel_type', 'gre')
  osicommon.set_config_ini(neutronPluginConf, 'ovs', 'enable_tunneling', 'True')
  #osicommon.set_config_ini(neutronPluginConf, 'OVS', 'bridge_mappings', 'physnet1:br-eth1')
  #osicommon.set_config_ini(neutronPluginConf, 'OVS', 'tenant_network_type', 'vlan')
  #osicommon.set_config_ini(neutronPluginConf, 'OVS', 'network_vlan_ranges', 'physnet1:1000:2999')
  #osicommon.set_config_ini(neutronPluginConf, 'OVS', 'integration_bridge', 'br-int')
  osicommon.set_config_ini(neutronPluginConf, 'securitygroup', 'firewall_driver', 'neutron.agent.linux.iptables_firewall.OVSHybridIptablesFirewallDriver')
  osicommon.set_config_ini(neutronPluginConf, 'securitygroup', 'enable_security_group', 'True')
  osicommon.run_command("service openvswitch-switch restart", True)
  osicommon.run_command("service neutron-plugin-openvswitch-agent restart", True)
  osicommon.log('Completed Neutron')
#######################################################################


#######################################################################
def install_neutron_on_control_node(databaseUserPassword, controlNodeIP, mySQLPassword):
  if not databaseUserPassword or len(str(databaseUserPassword)) == 0:
    raise Exception("Unable to install/configure neutron, no database user password specified")
  if not mySQLPassword or len(str(mySQLPassword)) == 0:
    raise Exception("Unable to install/configure neutron, no MySQL Password specified")
  if not controlNodeIP or len(str(controlNodeIP)) == 0:
    raise Exception("Unable to install/configure neutron, no control node IP specified")
  print ''
  osicommon.log('Installing Neutron')
  osicommon.run_db_command(mySQLPassword, "CREATE DATABASE IF NOT EXISTS neutron CHARACTER SET utf8 COLLATE utf8_general_ci;")
  osicommon.run_db_command(mySQLPassword, "GRANT ALL ON neutron.* TO 'neutron'@'%' IDENTIFIED BY '" + databaseUserPassword + "';")
  osicommon.run_command("apt-get install -y neutron-server" , True)
  osicommon.run_command("apt-get install -y neutron-plugin-ml2" , True)
  osicommon.log('Configuring Neutron')
  service_tenant = osicommon.run_command("keystone tenant-list | grep service | awk '{print $2}'")
  neutronConf = '/etc/neutron/neutron.conf'
  osicommon.set_config_ini(neutronConf, 'DEFAULT', 'core_plugin', 'ml2')
  osicommon.set_config_ini(neutronConf, 'DEFAULT', 'service_plugins', 'router,lbaas')
  osicommon.set_config_ini(neutronConf, 'DEFAULT', 'verbose', 'False')
  osicommon.set_config_ini(neutronConf, 'DEFAULT', 'debug', 'False')
  osicommon.set_config_ini(neutronConf, 'DEFAULT', 'auth_strategy', 'keystone')
  osicommon.set_config_ini(neutronConf, 'DEFAULT', 'rpc_backend', 'neutron.openstack.common.rpc.impl_kombu')
  osicommon.set_config_ini(neutronConf, 'DEFAULT', 'rabbit_host', controlNodeIP)
  osicommon.set_config_ini(neutronConf, 'DEFAULT', 'rabbit_port', '5672')
  osicommon.set_config_ini(neutronConf, 'DEFAULT', 'allow_overlapping_ips', 'False')
  osicommon.set_config_ini(neutronConf, 'DEFAULT', 'root_helper', 'sudo neutron-rootwrap /etc/neutron/rootwrap.conf')
  osicommon.set_config_ini(neutronConf, 'DEFAULT', 'notify_nova_on_port_status_changes', 'True')
  osicommon.set_config_ini(neutronConf, 'DEFAULT', 'notify_nova_on_port_data_changes', 'True')
  osicommon.set_config_ini(neutronConf, 'DEFAULT', 'nova_url', "http://" + controlNodeIP + ":8774/v2")
  osicommon.set_config_ini(neutronConf, 'DEFAULT', 'nova_admin_username', 'nova')
  osicommon.set_config_ini(neutronConf, 'DEFAULT', 'nova_admin_password', 'nova')
  osicommon.set_config_ini(neutronConf, 'DEFAULT', 'nova_admin_tenant_id', service_tenant)
  osicommon.set_config_ini(neutronConf, 'DEFAULT', 'nova_admin_auth_url', "http://" + controlNodeIP + ":35357/v2.0/")
  osicommon.set_config_ini(neutronConf, 'database', 'connection', "mysql://neutron:%s@%s/neutron" %(databaseUserPassword,controlNodeIP))
  osicommon.set_config_ini(neutronConf, 'keystone_authtoken', 'auth_uri', "http://" + controlNodeIP + ":5000/v2.0")
  osicommon.set_config_ini(neutronConf, 'keystone_authtoken', 'identity_uri', "http://" + controlNodeIP + ":35357")
  osicommon.remove_config_ini(neutronConf, 'keystone_authtoken', 'auth_host')
  osicommon.remove_config_ini(neutronConf, 'keystone_authtoken', 'auth_protocol')
  osicommon.remove_config_ini(neutronConf, 'keystone_authtoken', 'auth_port')
  osicommon.set_config_ini(neutronConf, 'keystone_authtoken', 'admin_tenant_name', 'service')
  osicommon.set_config_ini(neutronConf, 'keystone_authtoken', 'admin_user', 'neutron')
  osicommon.set_config_ini(neutronConf, 'keystone_authtoken', 'admin_password', 'neutron')
  neutronPasteConf = '/etc/neutron/api-paste.ini'
  osicommon.set_config_ini(neutronPasteConf, 'filter:authtoken', 'auth_host', controlNodeIP)
  osicommon.set_config_ini(neutronPasteConf, 'filter:authtoken', 'auth_port', '35357')
  osicommon.set_config_ini(neutronPasteConf, 'filter:authtoken', 'auth_protocol', 'http')
  osicommon.set_config_ini(neutronPasteConf, 'filter:authtoken', 'admin_tenant_name', 'service')
  osicommon.set_config_ini(neutronPasteConf, 'filter:authtoken', 'admin_user', 'neutron')
  osicommon.set_config_ini(neutronPasteConf, 'filter:authtoken', 'admin_password', 'neutron')
  neutronPluginConf = '/etc/neutron/plugins/ml2/ml2_conf.ini'
  osicommon.set_config_ini(neutronPluginConf, 'ml2', 'type_drivers', 'gre')
  osicommon.set_config_ini(neutronPluginConf, 'ml2', 'tenant_network_types', 'gre')
  osicommon.set_config_ini(neutronPluginConf, 'ml2', 'mechanism_drivers', 'openvswitch')
  osicommon.set_config_ini(neutronPluginConf, 'ml2_type_gre', 'tunnel_id_ranges', '1:1000')
  osicommon.set_config_ini(neutronPluginConf, 'securitygroup', 'firewall_driver', 'neutron.agent.linux.iptables_firewall.OVSHybridIptablesFirewallDriver')
  osicommon.set_config_ini(neutronPluginConf, 'securitygroup', 'enable_security_group', 'True')
  osicommon.run_command("neutron-db-manage --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugins/ml2/ml2_conf.ini upgrade juno", True)
  osicommon.run_command("service neutron-server restart", True)
  osicommon.log('Completed Neutron')
#######################################################################


#######################################################################
def install_neutron_on_network_node(databaseUserPassword, controlNodeIP, networkNodeInstanceIP, networkNodeExternalNetworkInterface, internetNetworkInterface, providerExternalNetworkCIDR):
  if not databaseUserPassword or len(str(databaseUserPassword)) == 0:
    raise Exception("Unable to install/configure neutron, no database user password specified")
  if not controlNodeIP or len(str(controlNodeIP)) == 0:
    raise Exception("Unable to install/configure neutron, no control node IP specified")
  if not networkNodeInstanceIP or len(str(networkNodeInstanceIP)) == 0:
    raise Exception("Unable to install/configure neutron, no network node instance IP specified")
  if not networkNodeExternalNetworkInterface or len(str(networkNodeExternalNetworkInterface)) == 0:
    raise Exception("Unable to install/configure neutron, no network node external network interface specified")
  if not internetNetworkInterface or len(str(internetNetworkInterface)) == 0:
    raise Exception("Unable to install/configure neutron, no network node Internet network interface specified")
  if not providerExternalNetworkCIDR or len(str(providerExternalNetworkCIDR)) == 0:
    raise Exception("Unable to install/configure neutron, no Provider External Network CIDR specified")
  print ''
  osicommon.log('Installing Neutron')
  osicommon.run_command("apt-get install -y openvswitch-switch openvswitch-datapath-dkms" , True)
  osicommon.run_command("ovs-vsctl --may-exist add-br br-int" , True)
  #osicommon.run_command("ovs-vsctl --may-exist add-br br-eth2" , True)
  #osicommon.run_command("ovs-vsctl --may-exist add-port br-eth2 eth2" , True)
  osicommon.run_command("ovs-vsctl --may-exist add-br br-ex" , True)
  osicommon.run_command("ovs-vsctl --may-exist add-port br-ex " + networkNodeExternalNetworkInterface , True)
  osicommon.run_command("apt-get install -y neutron-plugin-openvswitch-agent neutron-dhcp-agent neutron-l3-agent neutron-metadata-agent neutron-lbaas-agent haproxy" , True)
  osicommon.log('Configuring Neutron')
  neutronConf = '/etc/neutron/neutron.conf'
  osicommon.set_config_ini(neutronConf, 'DEFAULT', 'core_plugin', 'ml2')
  osicommon.set_config_ini(neutronConf, 'DEFAULT', 'service_plugins', 'router,lbaas')
  osicommon.set_config_ini(neutronConf, 'DEFAULT', 'verbose', 'False')
  osicommon.set_config_ini(neutronConf, 'DEFAULT', 'debug', 'False')
  osicommon.set_config_ini(neutronConf, 'DEFAULT', 'auth_strategy', 'keystone')
  osicommon.set_config_ini(neutronConf, 'DEFAULT', 'rabbit_host', controlNodeIP)
  osicommon.set_config_ini(neutronConf, 'DEFAULT', 'rabbit_port', '5672')
  osicommon.set_config_ini(neutronConf, 'DEFAULT', 'allow_overlapping_ips', 'False')
  osicommon.set_config_ini(neutronConf, 'DEFAULT', 'root_helper', 'sudo neutron-rootwrap /etc/neutron/rootwrap.conf')
  osicommon.remove_config_ini(neutronConf, 'keystone_authtoken', 'auth_host')
  osicommon.remove_config_ini(neutronConf, 'keystone_authtoken', 'auth_port')
  osicommon.remove_config_ini(neutronConf, 'keystone_authtoken', 'auth_protocol')
  osicommon.set_config_ini(neutronConf, 'keystone_authtoken', 'admin_tenant_name', 'service')
  osicommon.set_config_ini(neutronConf, 'keystone_authtoken', 'admin_user', 'neutron')
  osicommon.set_config_ini(neutronConf, 'keystone_authtoken', 'admin_password', 'neutron')
  osicommon.set_config_ini(neutronConf, 'keystone_authtoken', 'auth_uri', "http://%s:5000/v2.0" %controlNodeIP)
  osicommon.set_config_ini(neutronConf, 'keystone_authtoken', 'identity_uri', "http://%s:35357" %controlNodeIP)
  osicommon.remove_config_ini(neutronConf, 'database', 'connection')
  neutronPasteConf = '/etc/neutron/api-paste.ini'
  osicommon.set_config_ini(neutronPasteConf, 'filter:authtoken', 'auth_host', controlNodeIP)
  osicommon.set_config_ini(neutronPasteConf, 'filter:authtoken', 'auth_port', '35357')
  osicommon.set_config_ini(neutronPasteConf, 'filter:authtoken', 'auth_protocol', 'http')
  osicommon.set_config_ini(neutronPasteConf, 'filter:authtoken', 'admin_tenant_name', 'service')
  osicommon.set_config_ini(neutronPasteConf, 'filter:authtoken', 'admin_user', 'neutron')
  osicommon.set_config_ini(neutronPasteConf, 'filter:authtoken', 'admin_password', 'neutron')
  neutronMetadataAgentConf = '/etc/neutron/metadata_agent.ini'
  osicommon.set_config_ini(neutronMetadataAgentConf, 'DEFAULT', 'auth_url', "http://%s:5000/v2.0" %controlNodeIP)
  osicommon.set_config_ini(neutronMetadataAgentConf, 'DEFAULT', 'auth_region', 'region')
  osicommon.set_config_ini(neutronMetadataAgentConf, 'DEFAULT', 'admin_tenant_name', 'service')
  osicommon.set_config_ini(neutronMetadataAgentConf, 'DEFAULT', 'admin_user', 'neutron')
  osicommon.set_config_ini(neutronMetadataAgentConf, 'DEFAULT', 'admin_password', 'neutron')
  osicommon.set_config_ini(neutronMetadataAgentConf, 'DEFAULT', 'nova_metadata_ip', controlNodeIP)
  osicommon.set_config_ini(neutronMetadataAgentConf, 'DEFAULT', 'nova_metadata_port', '8775')
  osicommon.set_config_ini(neutronMetadataAgentConf, 'DEFAULT', 'metadata_proxy_shared_secret', 'helloOpenStack')
  osicommon.set_config_ini(neutronMetadataAgentConf, 'DEFAULT', 'debug', 'True')
  neutronPluginConf = '/etc/neutron/plugins/ml2/ml2_conf.ini'
  osicommon.set_config_ini(neutronPluginConf, 'ml2', 'type_drivers', 'gre')
  osicommon.set_config_ini(neutronPluginConf, 'ml2', 'tenant_network_types', 'gre')
  osicommon.set_config_ini(neutronPluginConf, 'ml2', 'mechanism_drivers', 'openvswitch')
  osicommon.set_config_ini(neutronPluginConf, 'ml2_type_gre', 'tunnel_id_ranges', '1:1000')
  osicommon.set_config_ini(neutronPluginConf, 'database', 'sql_connection', "mysql://neutron:%s@%s/neutron" %(databaseUserPassword,controlNodeIP))
  osicommon.set_config_ini(neutronPluginConf, 'ovs', 'local_ip', networkNodeInstanceIP)
  osicommon.set_config_ini(neutronPluginConf, 'ovs', 'tunnel_type', 'gre')
  osicommon.set_config_ini(neutronPluginConf, 'ovs', 'enable_tunneling', 'True')
  #et_config_ini(neutronPluginConf, 'OVS', 'bridge_mappings', 'physnet1:br-eth2')
  #et_config_ini(neutronPluginConf, 'OVS', 'tenant_network_type', 'vlan')
  #et_config_ini(neutronPluginConf, 'OVS', 'network_vlan_ranges', 'physnet1:1000:2999')
  #et_config_ini(neutronPluginConf, 'OVS', 'integration_bridge', 'br-int')
  osicommon.set_config_ini(neutronPluginConf, 'securitygroup', 'firewall_driver', 'neutron.agent.linux.iptables_firewall.OVSHybridIptablesFirewallDriver')
  osicommon.set_config_ini(neutronPluginConf, 'securitygroup', 'enable_security_group', 'True')
  osicommon.run_command("echo 'dhcp-option-force=26,1454' > '/etc/neutron/dnsmasq-neutron.conf'")
  neutronDhcpAgentConf = '/etc/neutron/dhcp_agent.ini'
  osicommon.set_config_ini(neutronDhcpAgentConf, 'DEFAULT', 'interface_driver', 'neutron.agent.linux.interface.OVSInterfaceDriver')
  osicommon.set_config_ini(neutronDhcpAgentConf, 'DEFAULT', 'dhcp_driver', 'neutron.agent.linux.dhcp.Dnsmasq')
  osicommon.set_config_ini(neutronDhcpAgentConf, 'DEFAULT', 'use_namespaces', 'True')
  osicommon.set_config_ini(neutronDhcpAgentConf, 'DEFAULT', 'dnsmasq_config_file', '/etc/neutron/dnsmasq-neutron.conf')
  neutronL3AgentConf = '/etc/neutron/l3_agent.ini'
  osicommon.set_config_ini(neutronL3AgentConf, 'DEFAULT', 'interface_driver', 'neutron.agent.linux.interface.OVSInterfaceDriver')
  osicommon.set_config_ini(neutronL3AgentConf, 'DEFAULT', 'use_namespaces', 'True')
  neutronLbaasAgentConf = '/etc/neutron/lbaas_agent.ini'
  osicommon.set_config_ini(neutronLbaasAgentConf, 'DEFAULT', 'device_driver', 'neutron.services.loadbalancer.drivers.haproxy.namespace_driver.HaproxyNSDriver')
  osicommon.set_config_ini(neutronLbaasAgentConf, 'DEFAULT', 'interface_driver', 'neutron.agent.linux.interface.OVSInterfaceDriver')
  # iptables rule to get VM/Instance to Internet working
  # /etc/rc.local so rule is set on boot
  providerExternalNetworkCIDREscaped = str(providerExternalNetworkCIDR)
  providerExternalNetworkCIDREscaped = str(providerExternalNetworkCIDREscaped).replace('.', '\.').replace('/', '\/')
  iptablesRcLocalCommand = "grep -e '^iptables\s*\-t\s*nat\s*\-A\s*POSTROUTING\s\-s\s*" + providerExternalNetworkCIDREscaped + "\s*\-j\s*SNAT\s*\-\-to\-source' /etc/rc.local; if [ $? -eq 0 ] ; then sed -i 's/^iptables\s*\-t\s*nat\s*\-A\s*POSTROUTING\s\-s\s*" + providerExternalNetworkCIDREscaped + "\s*\-j\s*SNAT\s*\-\-to\-source.*/iptables \-t nat \-A POSTROUTING \-s " + providerExternalNetworkCIDREscaped + " \-j SNAT \-\-to\-source \`ip \-4 \-o addr show " + internetNetworkInterface + " \| sed " + '"' + "s\/\.*inet\\s*\/\/" + '"' + " \| cut \-f1 \-d\/\`/' /etc/rc.local; else awk '/^exit/{print " + '"' + "iptables -t nat -A POSTROUTING -s " + providerExternalNetworkCIDR + " -j SNAT --to-source `ip -4 -o addr show " + internetNetworkInterface + " | sed 's/.*inet\s*//' | cut -f1 -d/`" + '"' + "}1' /etc/rc.local >/etc/rc.local.new; mv /etc/rc.local.new /etc/rc.local; chmod 755 /etc/rc.local; fi;"
  osicommon.run_command(iptablesRcLocalCommand)
  # and run it now to get it active now
  iptablesCommand = "iptables -t nat -A POSTROUTING -s " + providerExternalNetworkCIDR + " -j SNAT --to-source `ip -4 -o addr show " + internetNetworkInterface + " | sed " + '"' + "s/.*inets*//" + '"' + " | cut -f1 -d/`"
  osicommon.run_command(iptablesCommand)
  osicommon.run_command("service neutron-plugin-openvswitch-agent restart", True)
  osicommon.run_command("service neutron-dhcp-agent restart", True)
  osicommon.run_command("service neutron-l3-agent restart", True)
  osicommon.run_command("service neutron-metadata-agent restart", True)
  osicommon.run_command("service neutron-lbaas-agent restart", True)
  osicommon.log('Completed Neutron')
#######################################################################


#######################################################################
def install_nova_on_compute_node(databaseUserPassword, controlNodeIP, computeNodeIP):
  if not databaseUserPassword or len(str(databaseUserPassword)) == 0:
    raise Exception("Unable to install/configure nova, no database user password specified")
  if not controlNodeIP or len(str(controlNodeIP)) == 0:
    raise Exception("Unable to install/configure nova, no control node IP specified")
  if not computeNodeIP or len(str(computeNodeIP)) == 0:
    raise Exception("Unable to install/configure nova, no compute node IP specified")
  print ''
  osicommon.log('Installing Nova')
  os.environ['DEBIAN_FRONTEND'] = 'noninteractive'
  osicommon.run_command("apt-get install -y qemu-kvm libvirt-bin python-libvirt" , True)
  osicommon.run_command("apt-get install -y nova-compute-kvm novnc python-guestfs" , True)
  # For Cinder
  osicommon.run_command("apt-get install -y sysfsutils tgt" , True)
  osicommon.log('Configuring Nova')
  osicommon.delete_file('/var/lib/nova/nova.sqlite')
  overRideExists = osicommon.run_command('dpkg-statoverride --list | egrep -c "/boot/vmlinuz-$(uname -r)"' + " | awk '{print $2}'")
  if str(overRideExists) == '0':
    osicommon.run_command("dpkg-statoverride --update --add root root 0644 /boot/vmlinuz-$(uname -r)")
  osicommon.run_command("echo '#!/bin/sh' > /etc/kernel/postinst.d/statoverride")
  osicommon.run_command("echo 'version=" + '"$1"' + "' >> /etc/kernel/postinst.d/statoverride")
  osicommon.run_command("echo '[ -z " + '"${version}" ] && exit 0' + "' >> /etc/kernel/postinst.d/statoverride")
  osicommon.run_command("echo 'dpkg-statoverride --update --add root root 0644 /boot/vmlinuz-${version}' >> /etc/kernel/postinst.d/statoverride")
  osicommon.run_command("chmod +x /etc/kernel/postinst.d/statoverride")
  novaConf = '/etc/nova/nova.conf'
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'logdir', '/var/log/nova')
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'lock_path', '/var/lib/nova')
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'root_helper', 'sudo nova-rootwrap /etc/nova/rootwrap.conf')
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'verbose', 'False')
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'debug', 'False')
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'rabbit_host', controlNodeIP)
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'rpc_backend', 'rabbit')
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'sql_connection', "mysql://nova:%s@%s/nova" %(databaseUserPassword,controlNodeIP))
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'glance_host', controlNodeIP)
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'glance_api_servers', "%s:9292" %controlNodeIP)
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'compute_driver', 'libvirt.LibvirtDriver')
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'dhcpbridge_flagfile', '/etc/nova/nova.conf')
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'firewall_driver', 'nova.virt.firewall.NoopFirewallDriver')
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'security_group_api', 'neutron')
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'libvirt_vif_driver', 'nova.virt.libvirt.vif.LibvirtGenericVIFDriver')
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'linuxnet_interface_driver', 'nova.network.linux_net.LinuxOVSInterfaceDriver')
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'auth_strategy', 'keystone')
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'novnc_enabled', 'true')
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'novncproxy_base_url', "http://%s:6080/vnc_auto.html" %controlNodeIP)
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'novncproxy_port', '6080')
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'vncserver_proxyclient_address', computeNodeIP)
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'my_ip', computeNodeIP)
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'vncserver_listen', '0.0.0.0')
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'network_api_class', 'nova.network.neutronv2.api.API')
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'neutron_admin_username', 'neutron')
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'neutron_admin_password', 'neutron')
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'neutron_admin_tenant_name', 'service')
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'neutron_admin_auth_url', "http://%s:35357/v2.0/" %controlNodeIP)
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'neutron_auth_strategy', 'keystone')
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'neutron_url', "http://%s:9696/" %controlNodeIP)
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'iscsi_helper', 'tgtadm')
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'volume_name_template', 'volume-%s')
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'volume_group', 'cinder-volumes')
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'iscsi_ip_address', controlNodeIP)
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'volume_api_class', 'nova.volume.cinder.API')
  osicommon.set_config_ini(novaConf, 'database', 'connection', "mysql://nova:%s@%s/nova" %(databaseUserPassword,controlNodeIP))
  osicommon.set_config_ini(novaConf, 'keystone_authtoken', 'auth_uri', "http://%s:5000/v2.0" %controlNodeIP)
  osicommon.set_config_ini(novaConf, 'keystone_authtoken', 'identity_uri', "http://%s:35357" %controlNodeIP)
  osicommon.remove_config_ini(novaConf, 'keystone_authtoken', 'auth_host')
  osicommon.remove_config_ini(novaConf, 'keystone_authtoken', 'auth_port')
  osicommon.remove_config_ini(novaConf, 'keystone_authtoken', 'auth_protocol')
  osicommon.set_config_ini(novaConf, 'keystone_authtoken', 'admin_tenant_name', 'service')
  osicommon.set_config_ini(novaConf, 'keystone_authtoken', 'admin_user', 'nova')
  osicommon.set_config_ini(novaConf, 'keystone_authtoken', 'admin_password', 'nova')
  osicommon.set_config_ini(novaConf, 'neutron', 'url', "http://%s:9696" %controlNodeIP)
  osicommon.set_config_ini(novaConf, 'neutron', 'auth_strategy', 'keystone')
  osicommon.set_config_ini(novaConf, 'neutron', 'admin_auth_url', "http://%s::35357/v2.0" %controlNodeIP)
  osicommon.set_config_ini(novaConf, 'neutron', 'admin_tenant_name', 'service')
  osicommon.set_config_ini(novaConf, 'neutron', 'admin_username', 'neutron')
  osicommon.set_config_ini(novaConf, 'neutron', 'admin_password', 'neutron')
  novaPasteApiConf = '/etc/nova/api-paste.ini'
  osicommon.set_config_ini(novaPasteApiConf, 'filter:authtoken', 'auth_host', controlNodeIP)
  osicommon.set_config_ini(novaPasteApiConf, 'filter:authtoken', 'auth_port', '35357')
  osicommon.set_config_ini(novaPasteApiConf, 'filter:authtoken', 'auth_protocol', 'http')
  osicommon.set_config_ini(novaPasteApiConf, 'filter:authtoken', 'admin_tenant_name', 'service')
  osicommon.set_config_ini(novaPasteApiConf, 'filter:authtoken', 'admin_user', 'nova')
  osicommon.set_config_ini(novaPasteApiConf, 'filter:authtoken', 'admin_password', 'nova')
  osicommon.set_config_ini(novaPasteApiConf, 'filter:authtoken', 'auth_version', 'v2.0')
  novaComputeConf = '/etc/nova/nova-compute.conf'
  osicommon.set_config_ini(novaComputeConf, 'DEFAULT', 'libvirt_type', 'qemu')
  osicommon.set_config_ini(novaComputeConf, 'DEFAULT', 'compute_driver', 'libvirt.LibvirtDriver')
  osicommon.set_config_ini(novaComputeConf, 'DEFAULT', 'libvirt_vif_type', 'ethernet')
  vxmOrSxm = osicommon.run_command("egrep -c '(vmx|svm)' /proc/cpuinfo | awk '{print $1}'")
  if str(vxmOrSxm) == '0':
    # no hardware acceleration, configure libvirt to use QEMU
    osicommon.set_config_ini(novaComputeConf, 'libvirt', 'virt_type', 'qemu')
    isIntel = osicommon.run_command("egrep -i -c 'intel' /proc/cpuinfo | awk '{print $1}'")
    if str(isIntel) == '0':
      # AMD
      osicommon.run_command("grep -e '^kvm_amd$' /etc/modules ; if [ ! $? -eq 0 ] ; then echo 'kvm_amd' >> /etc/modules; fi;")
    else:
      # Intel
      osicommon.run_command("grep -e '^kvm_intel$' /etc/modules ; if [ ! $? -eq 0 ] ; then echo 'kvm_intel' >> /etc/modules; fi;")
  osicommon.run_command("service libvirt-bin restart", True)
  osicommon.run_command("service nova-compute restart", True)
  osicommon.log('Completed Nova')
#######################################################################


#######################################################################
def install_nova_on_control_node(databaseUserPassword, controlNodeIP, mySQLPassword):
  if not databaseUserPassword or len(str(databaseUserPassword)) == 0:
    raise Exception("Unable to install/configure nova, no database user password specified")
  if not mySQLPassword or len(str(mySQLPassword)) == 0:
    raise Exception("Unable to install/configure nova, no MySQL Password specified")
  if not controlNodeIP or len(str(controlNodeIP)) == 0:
    raise Exception("Unable to install/configure nova, no control node IP specified")
  print ''
  osicommon.log('Installing Nova')
  osicommon.run_db_command(mySQLPassword, "CREATE DATABASE IF NOT EXISTS nova CHARACTER SET utf8 COLLATE utf8_general_ci;")
  osicommon.run_db_command(mySQLPassword, "GRANT ALL ON nova.* TO 'nova'@'%' IDENTIFIED BY '" + databaseUserPassword + "';")
  osicommon.run_command("apt-get install -y nova-api nova-cert nova-scheduler nova-conductor novnc nova-consoleauth nova-novncproxy python-novaclient" , True)
  osicommon.log('Configuring Nova')
  osicommon.delete_file('/var/lib/nova/nova.sqlite')
  novaConf = '/etc/nova/nova.conf'
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'logdir', '/var/log/nova')
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'lock_path', '/var/lib/nova')
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'root_helper', 'sudo nova-rootwrap /etc/nova/rootwrap.conf')
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'verbose', 'False')
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'debug', 'False')
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'rabbit_host', controlNodeIP)
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'rpc_backend', 'rabbit')
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'sql_connection', "mysql://nova:%s@%s/nova" %(databaseUserPassword,controlNodeIP))
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'glance_api_servers', "%s:9292" %controlNodeIP)
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'image_service', 'nova.image.glance.GlanceImageService')
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'dhcpbridge_flagfile', '/etc/nova/nova.conf')
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'auth_strategy', 'keystone')
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'novnc_enabled', 'true')
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'nova_url', "http://%s:8774/v2/" %controlNodeIP)
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'novncproxy_base_url', "http://%s:6080/vnc_auto.html" %controlNodeIP)
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'my_ip', controlNodeIP)
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'vncserver_proxyclient_address', controlNodeIP)
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'novncproxy_port', '6080')
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'vncserver_listen', controlNodeIP)
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'network_api_class', 'nova.network.neutronv2.api.API')
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'neutron_admin_username', 'neutron')
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'neutron_admin_password', 'neutron')
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'neutron_admin_tenant_name', 'service')
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'neutron_admin_auth_url', "http://%s:35357/v2.0/" %controlNodeIP)
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'neutron_auth_strategy', 'keystone')
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'neutron_url', "http://%s:9696/" %controlNodeIP)
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'firewall_driver', 'nova.virt.firewall.NoopFirewallDriver')
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'linuxnet_interface_driver', 'nova.network.linux_net.LinuxOVSInterfaceDriver')
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'security_group_api', 'neutron')
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'iscsi_helper', 'tgtadm')
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'volume_name_template', 'volume-%s')
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'volume_group', 'cinder-volumes')
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'iscsi_ip_address', controlNodeIP)
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'volume_api_class', 'nova.volume.cinder.API')
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'osapi_volume_listen_port', '5900')
  osicommon.set_config_ini(novaConf, 'DEFAULT', 'compute_driver', 'libvirt.LibvirtDriver')
  osicommon.set_config_ini(novaConf, 'database', 'connection', "mysql://nova:%s@%s/nova" %(databaseUserPassword,controlNodeIP))
  osicommon.set_config_ini(novaConf, 'keystone_authtoken', 'auth_uri', "http://%s:5000/v2.0" %controlNodeIP)
  osicommon.set_config_ini(novaConf, 'keystone_authtoken', 'identity_uri', "http://%s:35357" %controlNodeIP)
  osicommon.remove_config_ini(novaConf, 'keystone_authtoken', 'auth_host')
  osicommon.remove_config_ini(novaConf, 'keystone_authtoken', 'auth_port')
  osicommon.remove_config_ini(novaConf, 'keystone_authtoken', 'auth_protocol')
  osicommon.set_config_ini(novaConf, 'keystone_authtoken', 'admin_tenant_name', 'service')
  osicommon.set_config_ini(novaConf, 'keystone_authtoken', 'admin_user', 'nova')
  osicommon.set_config_ini(novaConf, 'keystone_authtoken', 'admin_password', 'nova')
  osicommon.set_config_ini(novaConf, 'neutron', 'service_metadata_proxy', 'True')
  osicommon.set_config_ini(novaConf, 'neutron', 'metadata_proxy_shared_secret', 'helloOpenStack')
  novaPasteApiConf = '/etc/nova/api-paste.ini'
  osicommon.set_config_ini(novaPasteApiConf, 'filter:authtoken', 'auth_host', controlNodeIP)
  osicommon.set_config_ini(novaPasteApiConf, 'filter:authtoken', 'auth_port', '35357')
  osicommon.set_config_ini(novaPasteApiConf, 'filter:authtoken', 'auth_protocol', 'http')
  osicommon.set_config_ini(novaPasteApiConf, 'filter:authtoken', 'admin_tenant_name', 'service')
  osicommon.set_config_ini(novaPasteApiConf, 'filter:authtoken', 'admin_user', 'nova')
  osicommon.set_config_ini(novaPasteApiConf, 'filter:authtoken', 'admin_password', 'nova')
  osicommon.set_config_ini(novaPasteApiConf, 'filter:authtoken', 'signing_dir', '/tmp/keystone-signing-nova')
  osicommon.set_config_ini(novaPasteApiConf, 'filter:authtoken', 'auth_version', 'v2.0')
  osicommon.run_command("nova-manage db sync")
  osicommon.run_command("service nova-api restart", True)
  osicommon.run_command("service nova-cert restart", True)
  osicommon.run_command("service nova-scheduler restart", True)
  osicommon.run_command("service nova-conductor restart", True)
  osicommon.run_command("service nova-consoleauth restart", True)
  osicommon.run_command("service nova-novncproxy restart", True)
  time.sleep(10)
  osicommon.run_command("nova-manage service list", True)
  osicommon.log('Completed Nova')
#######################################################################


#######################################################################
def install_ntp(ipControlNode):
  if not ipControlNode or len(str(ipControlNode)) == 0:
    raise Exception("Unable to install/configure NTP, no control node IP specified")
  print ''
  osicommon.log('Installing NTP')
  osicommon.run_command("apt-get install -y ntp" , True)
  osicommon.log('Configuring NTP')
  osicommon.run_command("sed -i 's/^server 0.ubuntu.pool.ntp.org/#server 0.ubuntu.pool.ntp.org/g' /etc/ntp.conf")
  osicommon.run_command("sed -i 's/^server 1.ubuntu.pool.ntp.org/#server 1.ubuntu.pool.ntp.org/g' /etc/ntp.conf")
  osicommon.run_command("sed -i 's/^server 2.ubuntu.pool.ntp.org/#server 2.ubuntu.pool.ntp.org/g' /etc/ntp.conf")
  osicommon.run_command("sed -i 's/^server 3.ubuntu.pool.ntp.org/#server 3.ubuntu.pool.ntp.org/g' /etc/ntp.conf")
  osicommon.run_command("sed -i 's/^server .*/server %s/g' /etc/ntp.conf" %ipControlNode)
  osicommon.run_command("service ntp restart", True)
  osicommon.log('Completed NTP')
#######################################################################


#######################################################################
def install_rabbitmq():
  print ''
  osicommon.log('Installing RabbitMQ')
  osicommon.run_command("apt-get install -y rabbitmq-server" , True)
  osicommon.run_command("service rabbitmq-server restart", True)
  time.sleep(10)
  osicommon.log('Completed RabbitMQ')
#######################################################################


#######################################################################
def install_vlan():
  print ''
  osicommon.log('Installing vlan')
  osicommon.run_command("apt-get install -y vlan" , True)
  osicommon.log('Completed vlan')
#######################################################################

