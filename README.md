# OpenStack-Installation
Scripts to assist with getting up and running on OpenStack with a three node architecture: control, network, compute.

Based on the OpenStack [installation](http://docs.openstack.org/icehouse/install-guide/install/apt/content/) and [training](http://docs.openstack.org/training-guides/content/) guides as well as [work done previously](https://github.com/romilgupta/openstack-icehouse-scripts) by Romil Gupta.

Tested with [Ubuntu 12.04 LTS Server 64-bit](http://releases.ubuntu.com/precise/ubuntu-12.04.4-server-amd64.iso) running within [VirtualBox 4.3.10](https://www.virtualbox.org/wiki/Downloads).


## VirtualBox Host Networks
Within VirtualBox, go to File - Preferences to bring up Settings, then Network and select the Host-Only Networks tab to define three host-only networks for OpenStack.  Windows does not support naming the virtual network, so the default Windows host-only network names are included below for reference.

| Network        | Windows Network Name           | IPv4 Address           | IPv4 Mask      | DHCP |  
|:-------------- |:------------------------------ |:---------------------- |:-------------- |:---------|  
| vboxnet0       | Host-Only Ethernet Adapter #2  | 10.10.10.1             | 255.255.255.0  | Disabled |
| vboxnet1       | Host-Only Ethernet Adapter #3  | 10.20.20.1             | 255.255.255.0  | Disabled |
| vboxnet2       | Host-Only Ethernet Adapter #4  | 192.168.100.1          | 255.255.255.0  | Disabled |


## Control Node
The OpenStack Control node will run NTP, RabbitMQ, MySQL, Keystone, Glance, Neutron, Nova, Cinder, and Horizon.

### VM Configuration
- Type: Linux
- Version: Ubuntu (64-bit)
- Memory: 2048 MB
- Processors: 1
- Video Memory: 16 MB
- Monitor Count: 1
- Storage: CD/DVD drive on the IDE Controller and a 16 GB disk on the SATA Controller
- Audio: Can be disabled
- Network Adapter 1: vboxnet0: VirtualBox Host-Only Ethernet Adapter #2 (type = Paravirtualized Network with promiscuous mode all)
- Network Adapter 2: vboxnet2: VirtualBox Host-Only Ethernet Adapter #4 (type = Paravirtualized Network with promiscuous mode all)
- Network Adapter 3: NAT (type = Intel PRO/1000 with promiscuous mode deny).


### OS Installation
- Boot off the Ubuntu 12.04 Server ISO to begin installation:
- Select the language and the default menu option of Install Ubuntu Server
- Configure the keyboard layout
- For the primary network interface, select the adapter assigned to the Intel chipset
- Hostname: openstackcontrol
- User: Configure a non-root user (suggestion: control)
- Configure Time Zone
- Disk Partitioning:
 * 512 MB Primary (mounted as /boot, flagged bootable)
 * 1024 MB Logical (swap)
 * 8.0 GB Logical (used for LVM) and in LVM create a volume group vgroot and volume volroot, assigned to mount as / and formatted for ext4
 * 4 GB Logical (used for LVM) and in LVM create a volume group named cinder-volumes (not formatted nor mounted as it will be managed by OpenStack)
 * (Remainder) Logical (for XFS) but no mounting at this time (we will setup later for object storage)
- Continue with the installation (base install will proceed)
- Configure automatic updates (suggest disabling so as not to impact OpenStack)
- When selecting additional packages, be sure you add OpenSSH server (nothing else needed)
- Install GRUB boot loader on install disk
- Reboot


### Network Configuration
- You can assign any address appropriate for the network (.21s are shown, but you could just as easily use .11s).  It is recomended you choose some number low in the network range in case you want to use the other half of the range for compute instances.
- As root, edit /etc/network/interfaces to configure networking (be sure to check the MAC addresses as reported in the VM network configuration in VirtualBox with the OS representation as reported by ifconfig to ensure correct assignments)

<pre>
# The loopback network interface
auto lo
iface lo inet loopback

# OpenStack Management interface
auto eth0
iface eth0 inet static
address 10.10.10.21
netmask 255.255.255.0

# OpenStack API interface
auto eth1
iface eth1 inet static
address 192.168.100.21
netmask 255.255.255.0

# The primary network interface
auto eth2
iface eth2 inet dhcp
</pre>

- As root, restart networking: 

<pre>service networking restart</pre>

- You should now be able to SSH into the VM on the 10.10.10.x address you assigned


### OpenStack Installation
- Install git (as root): 

<pre>apt-get install -y git</pre>

- Download the git contents to the VM

<pre>git clone https://github.com/BrianBrophy/OpenStack-Installation.git</pre>

- Edit icehouse-install.ini and ensure configuration looks good

<pre>vi icehouse-install.ini</pre>

- As root, run the installer:

<pre>python icehouse-setup-control-node.py</pre>


## Network Node
The OpenStack Network node will run NTP and Neutron.

### VM Configuration
- Type: Linux
- Version: Ubuntu (64-bit)
- Memory: 2048 MB
- Processors: 1
- Video Memory: 16 MB
- Monitor Count: 1
- Storage: CD/DVD drive on the IDE Controller and a 8 GB disk on the SATA Controller
- Audio: Can be disabled
- Network Adapter 1: vboxnet0: VirtualBox Host-Only Ethernet Adapter #2 (type = Paravirtualized Network with promiscuous mode all)
- Network Adapter 2: vboxnet1: VirtualBox Host-Only Ethernet Adapter #3 (type = Paravirtualized Network with promiscuous mode all)
- Network Adapter 3: vboxnet2: VirtualBox Host-Only Ethernet Adapter #4 (type = Paravirtualized Network with promiscuous mode all)
- Network Adapter 4: NAT (type = Intel PRO/1000 with promiscuous mode deny).


### OS Installation
- Boot off the Ubuntu 12.04 Server ISO to begin installation:
- Select the language and the default menu option of Install Ubuntu Server
- Configure the keyboard layout
- For the primary network interface, select the adapter assigned to the Intel chipset
- Hostname: openstacknetwork
- User: Configure a non-root user (suggestion: network)
- Configure Time Zone
- Disk Partitioning:
 * 512 MB Primary (mounted as /boot, flagged bootable)
 * 1024 MB Logical (swap)
 * (Remainder) Logical (used for LVM) and in LVM create a volume group vgroot and volume volroot, assigned to mount as / and formatted for ext4
- Continue with the installation (base install will proceed)
- Configure automatic updates (suggest disabling so as not to impact OpenStack)
- When selecting additional packages, be sure you add OpenSSH server (nothing else needed)
- Install GRUB boot loader on install disk
- Reboot


### Network Configuration
- You can assign any address appropriate for the network (.22s are shown, but you could just as easily use .12s).  It is recomended you choose some number low in the network range in case you want to use the other half of the range for compute instances.
- As root, edit /etc/network/interfaces to configure networking (be sure to check the MAC addresses as reported in the VM network configuration in VirtualBox with the OS representation as reported by ifconfig to ensure correct assignments)

<pre>
# The loopback network interface
auto lo
iface lo inet loopback

# OpenStack Management interface
auto eth0
iface eth0 inet static
address 10.10.10.22
netmask 255.255.255.0

# OpenStack Data interface
auto eth1
iface eth1 inet static
address 10.20.20.22
netmask 255.255.255.0

# OpenStack API interface
auto eth2
iface eth2 inet manual
up ifconfig $IFACE 0.0.0.0 up
up ip link set $IFACE promisc on
down ip link set $IFACE promisc off
down ifconfig $IFACE down

auto br-ex
iface br-ex inet static
address 192.168.100.22
netmask 255.255.255.0
dns-nameservers 8.8.8.8

# The primary network interface
auto eth3
iface eth3 inet dhcp
</pre>

- As root, restart networking: 

<pre>service networking restart</pre>

- You should now be able to SSH into the VM on the 10.10.10.x address you assigned


### OpenStack Installation
- Install git (as root): 

<pre>apt-get install -y git</pre>

- Download the git contents to the VM

<pre>git clone https://github.com/BrianBrophy/OpenStack-Installation.git</pre>

- Edit icehouse-install.ini and ensure configuration looks good.  Pay close attention to the network section, ensuring the references to the control node addresses are correct.

<pre>vi icehouse-install.ini</pre>

- As root, run the installer:

<pre>python icehouse-setup-network-node.py</pre>


## Compute Node
The OpenStack Compute node will run NTP, Nova, and Neutron.


### VM Configuration
- Type: Linux
- Version: Ubuntu (64-bit)
- Memory: 4096 MB (allocating more will yield more resources for OpenStack Compute instances)
- Processors: 1 (allocating more will yield more resources for OpenStack Compute instances)
- Video Memory: 16 MB
- Monitor Count: 1
- Storage: CD/DVD drive on the IDE Controller and a 16 GB disk on the SATA Controller
- Audio: Can be disabled
- Network Adapter 1: vboxnet0: VirtualBox Host-Only Ethernet Adapter #2 (type = Paravirtualized Network with promiscuous mode all)
- Network Adapter 2: vboxnet1: VirtualBox Host-Only Ethernet Adapter #3 (type = Paravirtualized Network with promiscuous mode all)
- Network Adapter 3: NAT (type = Intel PRO/1000 with promiscuous mode deny).


### OS Installation
- Boot off the Ubuntu 12.04 Server ISO to begin installation:
- Select the language and the default menu option of Install Ubuntu Server
- Configure the keyboard layout
- For the primary network interface, select the adapter assigned to the Intel chipset
- Hostname: openstackcompute
- User: Configure a non-root user (suggestion: compute)
- Configure Time Zone
- Disk Partitioning:
 * 512 MB Primary (mounted as /boot, flagged bootable)
 * 1024 MB Logical (swap)
 * (Remainder) Logical (used for LVM) and in LVM create a volume group vgroot and volume volroot, assigned to mount as / and formatted for ext4
- Continue with the installation (base install will proceed)
- Configure automatic updates (suggest disabling so as not to impact OpenStack)
- When selecting additional packages, be sure you add OpenSSH server (nothing else needed)
- Install GRUB boot loader on install disk
- Reboot


### Network Configuration
- You can assign any address appropriate for the network (.23s are shown, but you could just as easily use .13s).  It is recomended you choose some number low in the network range in case you want to use the other half of the range for compute instances.
- As root, edit /etc/network/interfaces to configure networking (be sure to check the MAC addresses as reported in the VM network configuration in VirtualBox with the OS representation as reported by ifconfig to ensure correct assignments)

<pre>
# The loopback network interface
auto lo
iface lo inet loopback

# OpenStack Management interface
auto eth0
iface eth0 inet static
address 10.10.10.23
netmask 255.255.255.0

# OpenStack Data interface
auto eth1
iface eth1 inet static
address 10.20.20.23
netmask 255.255.255.0

# The primary network interface
auto eth2
iface eth2 inet dhcp
</pre>

- As root, restart networking: 

<pre>service networking restart</pre>

- You should now be able to SSH into the VM on the 10.10.10.x address you assigned


### OpenStack Installation
- Install git (as root): 

<pre>apt-get install -y git</pre>

- Download the git contents to the VM

<pre>git clone https://github.com/BrianBrophy/OpenStack-Installation.git</pre>

- Edit icehouse-install.ini and ensure configuration looks good.  Pay close attention to the compute section, ensuring the references to the control node addresses are correct.

<pre>vi icehouse-install.ini</pre>

- As root, run the installer:

<pre>python icehouse-setup-compute-node.py</pre>
