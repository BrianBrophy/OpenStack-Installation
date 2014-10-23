import fcntl
import os
import socket
import struct
import subprocess
import sys
import time

from datetime import datetime


# This will be lazy-loaded once python dependencies are on the system
iniparse = None


#######################################################################
def delete_file(filePath):
  if os.path.exists(filePath) and os.path.isfile(filePath):
    os.remove(filePath)
#######################################################################


#######################################################################
def get_config_ini(filePath, section, key):
  if not os.path.exists(filePath):
    raise Exception("Unable to get config value from INI, file " + str(filePath) + " does not exist")
  if not os.path.isfile(filePath):
    raise Exception("Unable to get config value from INI, path " + str(filePath) + " is not a file")
  global iniparse
  if iniparse is None:
    iniparse = __import__('iniparse')
  config = iniparse.ConfigParser()
  config.readfp(open(filePath))
  return config.get(section, key)
#######################################################################


#######################################################################
def get_network_address(interfaceName):
  if not interfaceName or len(str(interfaceName)) == 0:
    raise Exception("Unable to get network address, no interface name specified")
  try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', interfaceName[:15]))[20:24])
  except:
    raise Exception("Unable to get network address for interface " + str(interfaceName))
#######################################################################


#######################################################################
def log(message):
  if message and len(str(message)) > 0:
    print datetime.now().strftime('%m/%d/%Y %H:%M:%S,%f') + " " + str(message)
#######################################################################


#######################################################################
def remove_config_ini(filePath, section, key):
  if not os.path.exists(filePath):
    raise Exception("Unable to remove config key in INI, file " + str(filePath) + " does not exist")
  if not os.path.isfile(filePath):
    raise Exception("Unable to remove config key in INI, path " + str(filePath) + " is not a file")
  global iniparse
  if iniparse is None:
    iniparse = __import__('iniparse')
  config = iniparse.ConfigParser()
  config.readfp(open(filePath))
  if config.has_section(section):
    if config.has_option(section, key):
      config.remove_option(section, key)
  with open(filePath, 'w') as f:
    config.write(f)
#######################################################################


#######################################################################
def run_command(command, display=False):
  if not command or command is None:
    raise Exception("Unable to run command, no command specified")
  #log("Running: " + str(command))
  process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  if display:
    while True:
      nextline = process.stdout.readline()
      if nextline == '' and process.poll() != None:
        break
      sys.stdout.write(nextline)
      sys.stdout.flush()

  output, stderr = process.communicate()
  exitCode = process.returncode

  if (exitCode == 0):
    return output.strip()
  else:
    log("Failed to run: " + str(command))
    raise Exception(str(output) + ', return code: ' + str(exitCode))
#######################################################################


#######################################################################
def run_db_command(rootPassword, command):
  if not rootPassword or len(str(rootPassword)) == 0:
    raise Exception("Unable to run database command, no root password specified")
  if not command or len(str(command)) == 0:
    raise Exception("Unable to run database command, no command specified")
  cmd = """mysql -uroot -p%s -e "%s" """ % (rootPassword, command)
  output = run_command(cmd)
  return output
#######################################################################


#######################################################################
def set_config_ini(filePath, section, key, value):
  if not os.path.exists(filePath):
    raise Exception("Unable to set config value in INI, file " + str(filePath) + " does not exist")
  if not os.path.isfile(filePath):
    raise Exception("Unable to set config value in INI, path " + str(filePath) + " is not a file")
  global iniparse
  if iniparse is None:
    iniparse = __import__('iniparse')
  config = iniparse.ConfigParser()
  config.readfp(open(filePath))
  if not config.has_section(section):
    config.add_section(section)
    value += '\n'
  config.set(section, key, value)
  with open(filePath, 'w') as f:
    config.write(f)
#######################################################################


#######################################################################
def set_sysctl(key, value):
  if not key or len(str(key)) == 0:
    raise Exception("Unable to set sysctl configuration, no key specified")
  if not value or len(str(value)) == 0:
    raise Exception("Unable to set sysctl configuration, no value specified")
  cmd = """grep -i '^%s\s*=' /etc/sysctl.conf; if [ $? -eq 0 ] ; then sed -i 's/^%s\s*=.*/%s=%s/' /etc/sysctl.conf; else echo '%s=%s' >>/etc/sysctl.conf; fi; sysctl -p;""" % (key,key,key,value,key,value)
  output = run_command(cmd)
  return output
#######################################################################

