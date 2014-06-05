# OpenStack-Installation
Scripts to assist with getting up and running on OpenStack with a three node architecture: control, network, compute.

Based on the OpenStack [installation](http://docs.openstack.org/icehouse/install-guide/install/apt/content/) and [training](http://docs.openstack.org/training-guides/content/) guides as well as [work done previously](https://github.com/romilgupta/openstack-icehouse-scripts) by Romil Gupta.

Tested with [Ubuntu 12.04 LTS Server 64-bit](http://releases.ubuntu.com/precise/ubuntu-12.04.4-server-amd64.iso) running within [VirtualBox 4.3.10](https://www.virtualbox.org/wiki/Downloads).


## VirtualBox Host Networks
Within VirtualBox, go to File - Preferences to bring up Settings, then Network and select the Host-Only Networks tab to define three host-only networks for OpenStack.  Windows does not support naming the virtual network, so the default Windows host-only network names are included below for reference.

| Network        | Windows Network Name           | OpenStack Usage | IPv4 Address           | IPv4 Mask      | DHCP |  
|:-------------- |:------------------------------ |:--------------- |:---------------------- |:-------------- |:---------|  
| vboxnet0       | Host-Only Ethernet Adapter #2  | Management      | 10.10.10.1             | 255.255.255.0  | Disabled |
| vboxnet1       | Host-Only Ethernet Adapter #3  | Instances/VMs   | 10.20.20.1             | 255.255.255.0  | Disabled |
| vboxnet2       | Host-Only Ethernet Adapter #4  | External        | 192.168.100.1          | 255.255.255.0  | Disabled |


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
- Network Adapter 2: NAT (type = Intel PRO/1000 with promiscuous mode deny).


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

# The primary network interface
auto eth1
iface eth1 inet dhcp
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

# OpenStack Instance interface
auto eth1
iface eth1 inet static
address 10.20.20.22
netmask 255.255.255.0

# OpenStack External interface
auto eth2
iface eth2 inet manual
up ifconfig $IFACE 0.0.0.0 up
up ip link set $IFACE promisc on
down ip link set $IFACE promisc off
down ifconfig $IFACE down

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

# OpenStack Instance interface
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


# Using OpenStack
- For all of these command-line actions, you will either have to have environment variables configured in the shell for OpenStack clients to use (that you can set by sourcing a file), or use command-line arguments to specify them
- We will be showing the sourcing usage
- Source the admin credentials (created by the installation script)

<pre>source /root/openstack-admin.rc</pre>


## Adding CirrOS Image to Glance
- Load the CirrOS image

<pre>glance image-create --name 'CirrOS 0.3.2 x86_64' --is-public=true --container-format=bare --disk-format=qcow2 --location http://download.cirros-cloud.net/0.3.2/cirros-0.3.2-x86_64-disk.img</pre>

- Load Ubuntu 12.04 Image

<pre>glance image-create --name 'Ubuntu 12.04 x86_64' --is-public=true --container-format=bare --disk-format=qcow2 --location http://uec-images.ubuntu.com/precise/current/precise-server-cloudimg-amd64-disk1.img</pre>

- Confirm by listing Glance images

<pre>glance image-list</pre>


## Adding Tenants/Projects
- Create the tenant/project

<pre>keystone tenant-create --name=demo --enabled true</pre>

- Confirm by listing tenants

<pre>keystone tenant-list</pre>


## Editing Quotas For Tenants/Projects
- Determine the tenant ID of the tenant to view/edit using tenant-list

<pre>keystone tenant-list</pre>

- This yields output like

<pre>
+----------------------------------+---------+---------+
|                id                |   name  | enabled |
+----------------------------------+---------+---------+
| ec2404d2031a4242b4cbdf854f3dfe53 |  admin  |   True  |
| 2c708f8442ed437d8b8cb5a9c1bfb51c |   demo  |   True  |
| 53c5939d64fc42359a1d5776dc8822cf | service |   True  |
+----------------------------------+---------+---------+
</pre>

- So, we will be working with the demo tenant, whose tenant ID is 2c708f8442ed437d8b8cb5a9c1bfb51c

- Viewing current quota

<pre>nova quota-show --tenant 2c708f8442ed437d8b8cb5a9c1bfb51c</pre>

- This shows us something like

<pre>
+-----------------------------+-------+
| Quota                       | Limit |
+-----------------------------+-------+
| instances                   | 10    |
| cores                       | 20    |
| ram                         | 51200 |
| floating_ips                | 10    |
| fixed_ips                   | -1    |
| metadata_items              | 128   |
| injected_files              | 5     |
| injected_file_content_bytes | 10240 |
| injected_file_path_bytes    | 255   |
| key_pairs                   | 100   |
| security_groups             | 10    |
| security_group_rules        | 20    |
+-----------------------------+-------+
</pre>

- Let's adjust the number of key pairs to 200

<pre>nova quota-update --key-pairs 200 2c708f8442ed437d8b8cb5a9c1bfb51c</pre>


## Adding Users
- Create the user

<pre>keystone user-create --name brian --pass password --enabled true --tenant 2c708f8442ed437d8b8cb5a9c1bfb51c</pre>

- Confirm by listing users

<pre>keystone user-list</pre>


## Creating External Network
- Create a network with an external router

<pre>neutron net-create ext-net --shared --router:external=True</pre>

- Confirm by listing the networks

<pre>neutron net-list</pre>

## Creating Subnet on External Network
- We configured our VirtualBox host-only network to access the VMs as 192.168.100.0/24
- We will take this subnet, and use it as an allocation pool for floating IPs on the external subnet

<pre>neutron subnet-create ext-net --name ext-subnet --allocation-pool start=192.168.100.2,end=192.168.100.254 --disable-dhcp --gateway 192.168.100.1 192.168.100.0/24</pre>

- Confirm by listing subnets

<pre>neutron subnet-list</pre>


## Creating Tenant Network
- Setup a tenant .rc file ... based on the tenant you configured

<pre>
export OS_USERNAME=brian
export OS_PASSWORD=password
export OS_TENANT_NAME=demo
export OS_AUTH_URL=http://10.10.10.21:5000/v2.0
</pre>

- Source the tenant .rc file

<pre>source openstack-brian.rc</pre>

- Create tenant network

<pre>neutron net-create demo-net</pre>

- Confirm by listing networks

<pre>neutron net-list</pre>

- Create tenant subnet (this subnet is hidden behind the Network node, accessible only by the instance VMs)

<pre>neutron subnet-create demo-net --name demo-subnet --gateway 192.168.150.1 192.168.150.0/24</pre>

- Confirm by listing tenant subnets

<pre>neutron subnet-list</pre>

- Create tenant network router

<pre>neutron router-create demo-router</pre>

- Confirm by listing routers

<pre>neutron router-list</pre>

- Add the subnet to the router

<pre>neutron router-interface-add demo-router demo-subnet</pre>

- Set gateway on router for external network

<pre>neutron router-gateway-set demo-router ext-net</pre>

- If you login to the Horizon Dashboard as the tenant user, you will be able to see a visual representation under Networks, Network Topology


## Launching Instances
- On a node with the OpenStack clients installed, login to your user account (ie, brian is shown here)
- Source the tenant .rc file

<pre>source openstack-brian.rc</pre>

- Generate an SSH key pair

<pre>ssh-keygen</pre>

- Add the key pair to Nova

<pre>nova keypair-add --pub-key ~/.ssh/id_rsa.pub brian-key</pre>

- Confirm by listing the key pairs

<pre>nova keypair-list</pre>

- List the images

<pre>nova image-list</pre>

- Your IDs will differ, but here is an example

<pre>
+--------------------------------------+---------------------+--------+--------+
| ID                                   | Name                | Status | Server |
+--------------------------------------+---------------------+--------+--------+
| 8347b57f-4080-4eb7-8133-46b7e34ff9ea | CirrOS 0.3.2 x86_64 | ACTIVE |        |
| fa428499-b375-4f42-bdf2-6754c0e9440b | Ubuntu 12.04 x86_64 | ACTIVE |        |
+--------------------------------------+---------------------+--------+--------+
</pre>

- List the networks

<pre>neutron net-list</pre>

- Again, IDs will vary, but in our environment we have

<pre>
+--------------------------------------+----------+-------------------------------------------------------+
| id                                   | name     | subnets                                               |
+--------------------------------------+----------+-------------------------------------------------------+
| 851b9707-1dbd-43c3-bae2-f10773cce808 | ext-net  | d66bab2c-8b05-4eb9-924a-41653c458018 192.168.100.0/24 |
| b657514b-1d0d-466b-97f8-19e35d4c7bfe | demo-net | 942213a1-1b4a-4de3-94d2-1dcead1052d0 192.168.150.0/24 |
+--------------------------------------+----------+-------------------------------------------------------+
</pre>

- List the security groups

<pre>nova secgroup-list</pre>

- IDs will be different in your environment, but here we see

<pre>
+--------------------------------------+---------+-------------+
| Id                                   | Name    | Description |
+--------------------------------------+---------+-------------+
| 7ee7fd2a-6b59-48b5-b730-c3fced70c473 | default | default     |
| 37bbd3cd-1612-4929-a211-bfd81e84fed4 | demo    | Ping, SSH   |
+--------------------------------------+---------+-------------+
</pre>

- Now that we have the required info, we can launch an instance (NIC Net ID is the ID of our demo-net network, and note that for Ubuntu we need at least a m1.small flavor)

<pre>nova boot --flavor m1.small --image 'Ubuntu 12.04 x86_64' --nic net-id=b657514b-1d0d-466b-97f8-19e35d4c7bfe --security-group default --key-name brian-key ubuntu-demo-1</pre>

- Confirm by listing the nova instances

<pre>nova list<pre>

