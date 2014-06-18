# OpenStack-Installation
Scripts to assist with getting up and running on OpenStack with a three node architecture: control, network, compute.

Based on the OpenStack [installation](http://docs.openstack.org/icehouse/install-guide/install/apt/content/) and [training](http://docs.openstack.org/training-guides/content/) guides as well as [work done previously](https://github.com/romilgupta/openstack-icehouse-scripts) by Romil Gupta.

Tested with [Ubuntu 12.04 LTS Server 64-bit](http://releases.ubuntu.com/precise/ubuntu-12.04.4-server-amd64.iso) running within [VirtualBox 4.3.10](https://www.virtualbox.org/wiki/Downloads).


## VirtualBox Host Networks
Within VirtualBox, go to File - Preferences to bring up Settings, then Network and select the Host-Only Networks tab to define three host-only networks for OpenStack.  Windows does not support naming the virtual network, so the default Windows host-only network names are included below for reference.

| Network   | Windows Network Name           | OpenStack Usage        | IPv4 Address  | IPv4 Mask      | DHCP |  
|:--------- |:------------------------------ |:---------------------- |:------------- |:-------------- |:---------|  
| vboxnet0  | Host-Only Ethernet Adapter #2  | Management             | 10.10.10.1    | 255.255.255.0  | Disabled |
| vboxnet1  | Host-Only Ethernet Adapter #3  | Instances/VMs          | 10.20.20.1    | 255.255.255.0  | Disabled |
| vboxnet2  | Host-Only Ethernet Adapter #4  | External/Floating IPs  | 192.168.100.1 | 255.255.255.0  | Disabled |


## Control Node
The OpenStack Control node will run NTP, RabbitMQ, MySQL, Keystone, Glance, Neutron, Nova, Cinder, Heat, and Horizon.

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
- You can assign any address appropriate for the network (.21s are shown, but you could just as easily use .11s).
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
- You can assign any address appropriate for the network (.22s are shown, but you could just as easily use .12s).
- As root, install ethtool (so gro can be managed within the network interface configuration): 

<pre>apt-get install -y ethtool</pre>

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
post-up ethtool -K $IFACE gro off

auto br-ex
iface br-ex inet static
address 192.168.100.2
netmask 255.255.255.0
post-up ethtool -K $IFACE gro off

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

- Edit icehouse-install.ini and ensure configuration looks good.  Within the control section, be sure the network_address_management matches the IP of your Control Node's manegement interface.  Pay close attention to the network section.  Make sure the instance, external (floating IPs), and internet interfaces match your host.  Also be sure the provider/external OpenStack network CIDR aligns with the host-only network you assigned in VirtualBox because a special iptables rule will be created on the network node (and added to /etc/rc.local) to source NAT all traffic coming from this network (ie, from your compute/instance VMs) to the IP Address on your host's Internet interface (ie, the one connected to the VirtualBox NAT network).  This is needed to get compute/instance VM connectivity out to the Internet.  Your compute/instance VMs are not accessible from the Internet because the external network floating IP range is on a VirtualBox host-only network.

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
- You can assign any address appropriate for the network (.23s are shown, but you could just as easily use .13s).
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

- Edit icehouse-install.ini and ensure configuration looks good.  Within the control section, be sure the network_address_management matches the IP of your Control Node's manegement interface.  Pay close attention to the compute section, ensuring the references to the network interfaces are correct.

<pre>vi icehouse-install.ini</pre>

- As root, run the installer:

<pre>python icehouse-setup-compute-node.py</pre>


# Using OpenStack
- For all of these command-line actions, you will either have to have environment variables configured in the shell for OpenStack clients to use (that you can set by sourcing a file), or use command-line arguments to specify them
- We will be showing the sourcing usage
- Source the admin credentials (created by the installation script on the Controller node)

<pre>source /root/openstack-admin.rc</pre>


## Adding Images to Glance
- Load the CirrOS image

<pre>glance image-create --name 'CirrOS 0.3.2 x86_64' --is-public=true --container-format=bare --disk-format=qcow2 --location http://download.cirros-cloud.net/0.3.2/cirros-0.3.2-x86_64-disk.img</pre>

- Load Ubuntu 12.04 Image

<pre>glance image-create --name 'Ubuntu 12.04 x86_64' --is-public=true --container-format=bare --disk-format=qcow2 --location http://uec-images.ubuntu.com/precise/current/precise-server-cloudimg-amd64-disk1.img</pre>

- Load the CentOS 6.5 Image

<pre>glance image-create --name 'CentOS 6.5 x86_64' --is-public=true --container-format=bare --disk-format=qcow2 --location http://repos.fedorapeople.org/repos/openstack/guest-images/centos-6.5-20140117.0.x86_64.qcow2</pre>

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
- We configured our VirtualBox host-only network to access the VMs as 192.168.100.0/24.  This is also what was within the icehouse-install.ini file as the OpenStack external/provider network that, during the installation of the Network Node, we configured iptables to SNAT traffic from in order to get VM/instance out to Internet traffic working.
- We will take this subnet, and use it as an allocation pool for floating IPs on the external subnet.  Note how the gateway is the IP Address assigned to the Network Node's interface on the external network.

<pre>neutron subnet-create ext-net --name ext-subnet --allocation-pool start=192.168.100.20,end=192.168.100.254 --disable-dhcp --gateway 192.168.100.2 192.168.100.0/24</pre>

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

- Create tenant subnet (this subnet is hidden behind the Network node, accessible only by the instance VMs).  Note we are reserving an early portion of the address space to be able to use for other things.

<pre>neutron subnet-create demo-net --name demo-subnet --dns-nameserver 8.8.8.8 --allocation-pool start=172.16.10.20,end=172.16.10.254 --gateway 172.16.10.1 172.16.10.0/24</pre>

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


## Updating Default Security Group
- Let's allow SSH (tcp 22) and PING (icmp) inbound from anywhere into our VM/compute instances

<pre>nova secgroup-add-rule default tcp 22 22 0.0.0.0/0</pre>

<pre>nova secgroup-add-rule default icmp -1 -1 0.0.0.0/0</pre>

- Confirm by listing the rules for the default security group

<pre>nova secgroup-list-rules default</pre>


## Launching Instances
- On a node with the OpenStack clients installed (the Controller node works), login to your user account (ie, brian is shown here)
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
| b657514b-1d0d-466b-97f8-19e35d4c7bfe | demo-net | 942213a1-1b4a-4de3-94d2-1dcead1052d0 172.16.10.0/24   |
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

<pre>nova list</pre>

- Get/Create a floating IP

<pre>nova floating-ip-create ext-net</pre>

- Confirm by listing the floating IPs

<pre>nova floating-ip-list</pre>

- Wait until the VM is running, and has networking running .... you can use the "nova list" command to see the Power State and Network (if you do not wait, the floating IP assignment may not take effect, in which case you can just disaassociate and then (re) associate the floating IP again)
- Associate a floating IP with the instance

<pre>nova floating-ip-associate ubuntu-demo-1 192.168.100.21</pre>

- Confirm by listing the nova instances

<pre>nova list</pre>

- Now, you should be able to SSH into the instance.  For Ubuntu, the ubuntu user has been configured with the SSH key pair you specified when launching the instance.
- From Linux, you can connect to the assigned floating IP using the SSH key identity file

<pre>ssh -i ~/.ssh/id_rsa ubuntu@192.168.100.21</pre>

- From Windows, you can use PuTTY's puttygen executable to convert the private key to a PuTTY private key (*.ppk) file and then within your PuTTY session, be sure to configure Connection - Data - Auto login username as well as Connection - SSH - Auth - Private key file for authentication and then you should be able to SSH to the floating IP.

- If testing the CirrOS image, the SSH key pair is setup for the cirros user
- If testing the CentOS image, the SSH key pair is setup for the cloud-user user

## Working With Block Storage (Cinder)
- Login to root on the Controller node and ensure the cinder-volumes volume group exists in LVM.  If it does not exist, configure the volume group within LVM (just the volume group, no need to setup any logical volumes because Cinder will manage them).
- On a node with the OpenStack clients installed (the Controller node works), login to your user account (ie, brian is shown here)
- Source the tenant .rc file

<pre>source openstack-brian.rc</pre>

- Create volume (size here is 1 GB, can be any number of GBs you have storage to support)

<pre>cinder create --display-name test-volume 1</pre>

- Confirm by listing the cinder volumes

<pre>cinder list</pre>

- IDs will vary, but here is some sample output

<pre>
+--------------------------------------+-----------+--------------+------+-------------+----------+-------------+
|                  ID                  |   Status  | Display Name | Size | Volume Type | Bootable | Attached to |
+--------------------------------------+-----------+--------------+------+-------------+----------+-------------+
| 65cf791a-8128-4335-9d53-a53bd51599db | available | test-volume  |  1   |     None    |  false   |             |
+--------------------------------------+-----------+--------------+------+-------------+----------+-------------+
</pre>

- List the VMs so we know the ID of the server we want to attach the volume to

<pre>nova list</pre>

- Again, IDs vary, but here we see

<pre>
+--------------------------------------+---------------+--------+------------+-------------+--------------------------------------+
| ID                                   | Name          | Status | Task State | Power State | Networks                             |
+--------------------------------------+---------------+--------+------------+-------------+--------------------------------------+
| 95ecf8f9-1955-45e7-b0c9-1d4eb4874d59 | cirros-demo-1 | ACTIVE | -          | Running     | demo-net=172.16.10.2, 192.168.100.21 |
| 7425c587-d404-4fa3-a096-3e84543abfa8 | ubuntu-demo-1 | BUILD  | spawning   | NOSTATE     |                                      |
+--------------------------------------+---------------+--------+------------+-------------+--------------------------------------+
</pre>

- Attach the volume (syntax: nova volume-attach server volume device).  Note, since we are using KVM, KVM only supports the device as being "auto".

<pre>nova volume-attach 95ecf8f9-1955-45e7-b0c9-1d4eb4874d59 65cf791a-8128-4335-9d53-a53bd51599db auto</pre>

- The output informs us as to what device was assigned on the VM

<pre>
+----------+--------------------------------------+
| Property | Value                                |
+----------+--------------------------------------+
| device   | /dev/vdb                             |
| id       | 65cf791a-8128-4335-9d53-a53bd51599db |
| serverId | 95ecf8f9-1955-45e7-b0c9-1d4eb4874d59 |
| volumeId | 65cf791a-8128-4335-9d53-a53bd51599db |
+----------+--------------------------------------+
</pre>

- Confirm by listing the cinder volumes

<pre>cinder list</pre>

- And, we can see it is attached

<pre>
+--------------------------------------+--------+--------------+------+-------------+----------+--------------------------------------+
|                  ID                  | Status | Display Name | Size | Volume Type | Bootable |             Attached to              |
+--------------------------------------+--------+--------------+------+-------------+----------+--------------------------------------+
| 65cf791a-8128-4335-9d53-a53bd51599db | in-use | test-volume  |  1   |     None    |  false   | 95ecf8f9-1955-45e7-b0c9-1d4eb4874d59 |
+--------------------------------------+--------+--------------+------+-------------+----------+--------------------------------------+
</pre>

- Now that it is attached, we can mount and use it on the VM
- Log into the VM and get to root
- Since this is the first we are using this volume, we need to format it

<pre>mkfs /dev/vdb</pre>

- Create a mount location

<pre>mkdir /cindervol</pre>

- Mount

<pre>mount /dev/vdb /cindervol</pre>

- Confirm by showing the disks on the VM

<pre>df -kh</pre>

- When done using the volume, unmount it

<pre>umount /cindervol</pre>

- The volume could now be presented again to this VM, or even to another VM

## Working With Orchestration (Heat)
- On a node with the OpenStack clients installed (the Controller node works), login to your user account (ie, brian is shown here)
- Source the tenant .rc file

<pre>source openstack-brian.rc</pre>

- Create a test Heat template file named heat-test.yaml (or whatever you want)

<pre>
heat_template_version: 2013-05-23

description: Simple template to deploy a single compute instance

parameters:
  keyName:
    type: string
    label: Key Name
    description: Name of key-pair to be used for compute instance
  image:
    type: string
    label: Image
    description: Image to be used for compute instance
  flavor:
    type: string
    label: Flavor
    description: Type of instance (flavor) to be used
  network:
    type: string
    label: Network
    description: Network to use for compute instance
  securityGroups:
    type: string
    label: Security Groups
    description: Security Groups to use for compute instance

resources:
  my_instance:
    type: OS::Nova::Server
    properties:
      key_name: { get_param: keyName }
      image: { get_param: image }
      flavor: { get_param: flavor }
      networks:
        - network: { get_param: network }
      security_groups: [ { get_param: securityGroups } ]
</pre>

- Within this simple Heat file, you can see we defined some input parameters (keyName, image, flavor, network, securityGroups) and then we are using them to boot a single compute instance.
- Create a Heat stack using this file (the last argument is the stack name ... you could use something else)

<pre>heat stack-create -f heat-test.yaml -P "image=CirrOS 0.3.2 x86_64;flavor=m1.tiny;keyName=brian-key;securityGroups=default;network=demo-net" brian2</pre>

- Confirm by listing your stacks

<pre>heat stack-list</pre>

- IDs will vary, but here is a sample:

<pre>
+--------------------------------------+------------+--------------------+----------------------+
| id                                   | stack_name | stack_status       | creation_time        |
+--------------------------------------+------------+--------------------+----------------------+
| f58a780e-b3e8-4840-bbe9-378e88829660 | brian2     | CREATE_IN_PROGRESS | 2014-06-14T20:34:49Z |
+--------------------------------------+------------+--------------------+----------------------+
</pre>

- We can continue to use the "heat stack-list" command to show the progress until it is complete.  Once Heat has finished, we will see our new instance running within Nova.

<pre>nova list</pre>

<pre>
+--------------------------------------+---------------------------------+--------+------------+-------------+--------------------------------------+
| ID                                   | Name                            | Status | Task State | Power State | Networks                             |
+--------------------------------------+---------------------------------+--------+------------+-------------+--------------------------------------+
| bee9e8ec-8843-4185-ab7d-c85da96fb8f0 | brian2-my_instance-fkfu3epgqhyo | ACTIVE | -          | Running     | demo-net=172.16.10.6                 |
+--------------------------------------+---------------------------------+--------+------------+-------------+--------------------------------------+
</pre>

- There is a lot more you can do with Heat, but this is just a simple example

## Load Balancer as a Service (LBaaS)
- The installation script configures Neutron to support LBaaS using haproxy and Open vSwitch
- On a node with the OpenStack clients installed (the Controller node works), login to your user account (ie, brian is shown here)
- Source the tenant .rc file

<pre>source openstack-brian.rc</pre>

- Lookup the ID of the subnet on the private demo-network (your IDs will differ)

<pre>neutron subnet-list</pre>

<pre>
+--------------------------------------+-------------+------------------+-------------------------------------------------------+
| id                                   | name        | cidr             | allocation_pools                                      |
+--------------------------------------+-------------+------------------+-------------------------------------------------------+
| 2150f65f-969a-4e46-87db-79895849fc88 | ext-subnet  | 192.168.100.0/24 | {"start": "192.168.100.20", "end": "192.168.100.254"} |
| d50c6d1f-7ab4-4582-82ca-738415ea1d44 | demo-subnet | 172.16.10.0/24   | {"start": "172.16.10.2", "end": "172.16.10.254"}      |
+--------------------------------------+-------------+------------------+-------------------------------------------------------+
</pre>

- Create an HTTP load balancer pool on that subnet

<pre>neutron lb-pool-create --lb-method ROUND_ROBIN --name my-pool --protocol HTTP --subnet-id d50c6d1f-7ab4-4582-82ca-738415ea1d44</pre>

- Confirm by listing the load balancer pools

<pre>neutron lb-pool-list</pre>

<pre>
+--------------------------------------+----------+----------+-------------+----------+----------------+--------+
| id                                   | name     | provider | lb_method   | protocol | admin_state_up | status |
+--------------------------------------+----------+----------+-------------+----------+----------------+--------+
| a4155a90-16a9-47b2-a9c3-fe754afe22a3 | my-pool  | haproxy  | ROUND_ROBIN | HTTP     | True           | ACTIVE |
+--------------------------------------+----------+----------+-------------+----------+----------------+--------+
</pre>

- Lookup the private network IP of the compute instance to make a member of this pool

<pre>nova list</pre>

<pre>
+--------------------------------------+---------------------------------+---------+------------+-------------+--------------------------------------+
| ID                                   | Name                            | Status  | Task State | Power State | Networks                             |
+--------------------------------------+---------------------------------+---------+------------+-------------+--------------------------------------+
| bee9e8ec-8843-4185-ab7d-c85da96fb8f0 | brian2-my_instance-fkfu3epgqhyo | SHUTOFF | -          | Shutdown    | demo-net=172.16.10.6                 |
| fe10a701-5bb3-441e-8e5a-b2fe8e743bc1 | cirros-demo-1                   | ACTIVE  | -          | Running     | demo-net=172.16.10.2, 192.168.100.21 |
| 1b9cdcdf-a167-4b1b-89f9-c32af2bfde1a | ubuntu-demo-1                   | ACTIVE  | -          | Running     | demo-net=172.16.10.7, 192.168.100.23 |
+--------------------------------------+---------------------------------+---------+------------+-------------+--------------------------------------+
</pre>

- Add the nova compute instance as a member of the load balancer pool

<pre>neutron lb-member-create --address 172.16.10.7 --protocol-port 80 my-pool</pre>

- Create a health monitor

<pre>neutron lb-healthmonitor-create --delay 3 --type HTTP --max-retries 3 --timeout 3</pre>

- Confirm by listing the health monitors

<pre>neutron lb-healthmonitor-list</pre>

<pre>
+--------------------------------------+------+----------------+
| id                                   | type | admin_state_up |
+--------------------------------------+------+----------------+
| 9f217c8d-5c7d-436f-a485-6ab5b07bfa00 | HTTP | True           |
+--------------------------------------+------+----------------+
</pre>

- Associate the health monitor with the pool

<pre>neutron lb-healthmonitor-associate 9f217c8d-5c7d-436f-a485-6ab5b07bfa00 my-pool</pre>

- Create a VIP for the pool (using the private subnet again)

<pre>neutron lb-vip-create --name myvip --protocol-port 80 --protocol HTTP --subnet-id d50c6d1f-7ab4-4582-82ca-738415ea1d44 my-pool</pre>

- Confirm by listing the VIPs

<pre>neutron lb-vip-list</pre>

<pre>
+--------------------------------------+---------+---------------+----------+----------------+--------+
| id                                   | name    | address       | protocol | admin_state_up | status |
+--------------------------------------+---------+---------------+----------+----------------+--------+
| 6b5ee27a-61b9-4a15-9b26-27620f9490bd | myvip   | 172.16.10.101 | HTTP     | True           | ACTIVE |
+--------------------------------------+---------+---------------+----------+----------------+--------+
</pre>

- Lookup an available floating IP within neutron (if need be, assign a new one using "nova floating-ip-create ext-net")

<pre>neutron floatingip-list</pre>

<pre>
+--------------------------------------+------------------+---------------------+--------------------------------------+
| id                                   | fixed_ip_address | floating_ip_address | port_id                              |
+--------------------------------------+------------------+---------------------+--------------------------------------+
| 12898832-b905-45fe-90ad-ec69f9266ba9 | 172.16.10.2      | 192.168.100.21      | e83a675f-0347-4d6e-b4e4-be1aa2f7ae41 |
| 5a5a1ea0-e43d-4b36-ae7c-87a99c9e5b1c | 172.16.10.100    | 192.168.100.22      | a04b43a5-ee57-4d63-b504-ff95bff97cd1 |
| 98b15f2f-3b6d-45f7-a7b1-27924f01a4d6 |                  | 192.168.100.24      |                                      |
| e38dd6bb-6d12-429e-80b9-a71bfda97b0e | 172.16.10.7      | 192.168.100.23      | 6327b2cb-63ee-4d1b-8261-d846c6008814 |
+--------------------------------------+------------------+---------------------+--------------------------------------+
</pre>

- Here, we can see 192.168.100.24 is available, and it's ID is 98b15f2f-3b6d-45f7-a7b1-27924f01a4d6
- Lookup the port corresponding to the VIP

<pre>neutron port-list</pre>

<pre>
+--------------------------------------+------------------------------------------+-------------------+--------------------------------------------------------------------------------------+
| id                                   | name                                     | mac_address       | fixed_ips                                                                            |
+--------------------------------------+------------------------------------------+-------------------+--------------------------------------------------------------------------------------+
| 2324db59-4a79-4cc1-b416-a281cab1d221 | vip-6b5ee27a-61b9-4a15-9b26-27620f9490bd | fa:16:3e:52:6a:9f | {"subnet_id": "d50c6d1f-7ab4-4582-82ca-738415ea1d44", "ip_address": "172.16.10.101"} |
| 6327b2cb-63ee-4d1b-8261-d846c6008814 |                                          | fa:16:3e:2c:0e:ca | {"subnet_id": "d50c6d1f-7ab4-4582-82ca-738415ea1d44", "ip_address": "172.16.10.7"}   |
| 78300abd-aa91-45d5-9d71-0b7dc9a5b027 |                                          | fa:16:3e:43:80:22 | {"subnet_id": "d50c6d1f-7ab4-4582-82ca-738415ea1d44", "ip_address": "172.16.10.6"}   |
| a04b43a5-ee57-4d63-b504-ff95bff97cd1 | vip-3e815344-73a4-45b9-a3bf-bc1924bf6157 | fa:16:3e:7b:f2:ea | {"subnet_id": "d50c6d1f-7ab4-4582-82ca-738415ea1d44", "ip_address": "172.16.10.100"} |
| a4d66f9d-b2e7-4e9f-bc19-8b2337982654 |                                          | fa:16:3e:1d:a4:ba | {"subnet_id": "d50c6d1f-7ab4-4582-82ca-738415ea1d44", "ip_address": "172.16.10.3"}   |
| d0bacc5b-3070-44dc-9480-a0509144be80 |                                          | fa:16:3e:4f:39:c0 | {"subnet_id": "d50c6d1f-7ab4-4582-82ca-738415ea1d44", "ip_address": "172.16.10.1"}   |
| e83a675f-0347-4d6e-b4e4-be1aa2f7ae41 |                                          | fa:16:3e:46:e6:40 | {"subnet_id": "d50c6d1f-7ab4-4582-82ca-738415ea1d44", "ip_address": "172.16.10.2"}   |
+--------------------------------------+------------------------------------------+-------------------+--------------------------------------------------------------------------------------+
</pre>

- The VIP is on port 2324db59-4a79-4cc1-b416-a281cab1d221
- With both the Floating IP ID and the VIP Port ID, assign the floating IP to the VIP within neutron (the syntax is "neutron floatingip-associate floatingIPID portID")

<pre>neutron floatingip-associate 98b15f2f-3b6d-45f7-a7b1-27924f01a4d6 2324db59-4a79-4cc1-b416-a281cab1d221</pre>

- If HTTP 80 is up on the Nova Compute instance and responding to the health monitor, you should now be able to access the HTTP instance using the floating IP (http://192.168.100.24)

## Heat Template For Two Web Servers and a Load Balancer
- First, we need to define a Heat template file (called something like heat-lbaas.yaml)

<pre>
heat_template_version: 2013-05-23

description: Template to deploy two compute instances as web servers and a load balancer

parameters:
  keyName:
    type: string
    label: Key Name
    description: Name of key-pair to be used for compute instance
  image:
    type: string
    label: Image
    description: Image to be used for compute instance
  flavor:
    type: string
    label: Flavor
    description: Type of instance (flavor) to be used
  floatingNetworkID:
    type: string
    label: Floating IP Network ID
    description: Network to use for floating IPs
  networkID:
    type: string
    label: Network
    description: Network to use for compute instance
  subnetID:
    type: string
    label: Subnet ID
    description: Subnet to use for load balancer

resources:
  web-server-security-group:
    type: OS::Neutron::SecurityGroup
    properties:
      name: web-server-security-group
      rules: [
        {remote_ip_prefix: 0.0.0.0/0,
        protocol: tcp,
        port_range_min: 22,
        port_range_max: 22},
        {remote_ip_prefix: 0.0.0.0/0,
        protocol: tcp,
        port_range_min: 80,
        port_range_max: 80},
        {remote_ip_prefix: 0.0.0.0/0,
        protocol: icmp}]
  web-server-1-port:
    type: OS::Neutron::Port
    properties:
      network_id: { get_param: networkID }
      security_groups: [{ get_resource: web-server-security-group }]
  web-server-2-port:
    type: OS::Neutron::Port
    properties:
      network_id: { get_param: networkID }
      security_groups: [{ get_resource: web-server-security-group }]
  web-server-1:
    type: OS::Nova::Server
    properties:
      key_name: { get_param: keyName }
      image: { get_param: image }
      flavor: { get_param: flavor }
      networks:
        - port: { get_resource: web-server-1-port }
      user_data: |
        #!/bin/bash -v
        sudo apt-get install -y apache2
  web-server-2:
    type: OS::Nova::Server
    properties:
      key_name: { get_param: keyName }
      image: { get_param: image }
      flavor: { get_param: flavor }
      networks:
        - port: { get_resource: web-server-2-port }
      user_data: |
        #!/bin/bash -v
        sudo apt-get install -y apache2
  http-health-monitor:
    type: OS::Neutron::HealthMonitor
    properties:
      type: HTTP
      delay: 3
      max_retries: 5
      timeout: 5
      http_method: GET
      url_path: /
  load-balancer-http-pool:
    type: OS::Neutron::Pool
    properties:
      protocol: HTTP
      monitors: [ { get_resource: http-health-monitor } ]
      subnet_id: { get_param: subnetID }
      lb_method: ROUND_ROBIN
      vip:
        protocol_port: 80
  load-balancer-http:
    type: OS::Neutron::LoadBalancer
    properties:
      members: [ { get_resource: web-server-1 }, { get_resource: web-server-2 } ]
      protocol_port: 80
      pool_id: { get_resource: load-balancer-http-pool }
  load-balancer-http-vip:
    type: OS::Neutron::FloatingIP
    properties:
      floating_network_id: { get_param: floatingNetworkID }
  load-balancer-http-vip-association:
    type: OS::Neutron::FloatingIPAssociation
    properties:
      floatingip_id: { get_resource: load-balancer-http-vip }
      port_id: { get_attr: [ load-balancer-http-pool, vip, port_id ] }

outputs:
  LoadBalancerVIP:
    description: Load Balancer VIP assigned
    value:
      str_replace:
        template: 'http://loadbalancer:80'
        params:
          loadbalancer: { get_attr: [load-balancer-http-vip, floating_ip_address] }
</pre>

- Then, we need to lookup some information (IDs of the networks and subnet on the internal network) to be able to pass into the template

<pre>neutron net-list</pre>

<pre>
+--------------------------------------+----------+-------------------------------------------------------+
| id                                   | name     | subnets                                               |
+--------------------------------------+----------+-------------------------------------------------------+
| 1c46bbdd-bb6b-4edb-8bf8-97e2c11f6c23 | demo-net | b95589c2-6ade-4e4f-89e4-1d130e15dbc2 172.16.10.0/24   |
| 3f64f785-619f-4fed-bad4-b81074782a0d | ext-net  | 2a8eb36b-793f-4633-a565-18528ca5d392 192.168.100.0/24 |
+--------------------------------------+----------+-------------------------------------------------------+
</pre>

<pre>neutron subnet-list</pre>

<pre>
+--------------------------------------+-------------+------------------+-------------------------------------------------------+
| id                                   | name        | cidr             | allocation_pools                                      |
+--------------------------------------+-------------+------------------+-------------------------------------------------------+
| 2a8eb36b-793f-4633-a565-18528ca5d392 | ext-subnet  | 192.168.100.0/24 | {"start": "192.168.100.20", "end": "192.168.100.254"} |
| b95589c2-6ade-4e4f-89e4-1d130e15dbc2 | demo-subnet | 172.16.10.0/24   | {"start": "172.16.10.20", "end": "172.16.10.254"}     |
+--------------------------------------+-------------+------------------+-------------------------------------------------------+
</pre>

- Now, we can launch the Heat stack.  Note, the stack will complete pretty quickly and Nova will report that the web servers are RUNNING, but this just means they are powered on.  It takes a little time for them to boot, complete cloud-init, and run the script to load Apache.  So, the load balancer will be created and monitoring ... and once Apache is loaded on the web servers, the load balancer will be online.

<pre>heat stack-create -f heat-ubuntu-lbaas.yaml -P "image=Ubuntu 12.04 x86_64;flavor=m1.small;keyName=brian-key;networkID=1c46bbdd-bb6b-4edb-8bf8-97e2c11f6c23;subnetID=b95589c2-6ade-4e4f-89e4-1d130e15dbc2;floatingNetworkID=3f64f785-619f-4fed-bad4-b81074782a0d" lbaas-ubuntu-stack</pre>

- When the stack completes, use the "heat stack-show" command to see the details, including within the "outputs" section the resulting floating IP that was assigned to the load balancer VIP.

<pre>heat stack-show lbaas-ubuntu-stack</pre>

<pre>
+----------------------+----------------------------------------------------------------------------------------------------------------------------+
| Property             | Value                                                                                                                      |
+----------------------+----------------------------------------------------------------------------------------------------------------------------+
| capabilities         | []                                                                                                                         |
| creation_time        | 2014-06-16T11:13:17Z                                                                                                       |
| description          | Template to deploy two compute instances as web servers                                                                    |
|                      | and a load balancer                                                                                                        |
| disable_rollback     | True                                                                                                                       |
| id                   | d86e23f6-cb9c-4471-85f1-cf0aea1319f6                                                                                       |
| links                | http://10.10.10.21:8004/v1/164f35d45e1946bb8c9cd06fa6ff0f07/stacks/lbaas-ubuntu-stack/d86e23f6-cb9c-4471-85f1-cf0aea1319f6 |
| notification_topics  | []                                                                                                                         |
| outputs              | [                                                                                                                          |
|                      |   {                                                                                                                        |
|                      |     "output_value": "http://192.168.100.22:80",                                                                            |
|                      |     "description": "Load Balancer VIP assigned",                                                                           |
|                      |     "output_key": "LoadBalancerVIP"                                                                                        |
|                      |   }                                                                                                                        |
|                      | ]                                                                                                                          |
| parameters           | {                                                                                                                          |
|                      |   "networkID": "1c46bbdd-bb6b-4edb-8bf8-97e2c11f6c23",                                                                     |
|                      |   "floatingNetworkID": "3f64f785-619f-4fed-bad4-b81074782a0d",                                                             |
|                      |   "OS::stack_id": "d86e23f6-cb9c-4471-85f1-cf0aea1319f6",                                                                  |
|                      |   "OS::stack_name": "lbaas-ubuntu-stack",                                                                                  |
|                      |   "image": "Ubuntu 12.04 x86_64",                                                                                          |
|                      |   "keyName": "brian-key",                                                                                                  |
|                      |   "subnetID": "b95589c2-6ade-4e4f-89e4-1d130e15dbc2",                                                                      |
|                      |   "flavor": "m1.small"                                                                                                     |
|                      | }                                                                                                                          |
| stack_name           | lbaas-ubuntu-stack                                                                                                         |
| stack_status         | CREATE_COMPLETE                                                                                                            |
| stack_status_reason  | Stack CREATE completed successfully                                                                                        |
| template_description | Template to deploy two compute instances as web servers                                                                    |
|                      | and a load balancer                                                                                                        |
| timeout_mins         | 60                                                                                                                         |
| updated_time         | None                                                                                                                       |
+----------------------+----------------------------------------------------------------------------------------------------------------------------+
</pre>

- Here, we see the resulting Load Balancer VIP URL is http://192.168.100.22:80
