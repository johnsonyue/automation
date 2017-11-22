#!/bin/bash

if [ $# -lt 5 ]; then
        echo "usage: $0 as_prefix local_interface_1 local_asn_1 remote_interface_1 remote_asn_1 ..."
        exit
fi

as_prefix=$1

temp=$(( ${#} - 1 ))
(( odd=${temp} % 4 ))
if [ ${odd} -ne 0 ]
then
	echo "Count of paramters must be times of 4"
	exit
fi

# get command line paramter
ipAddress=$2
ipAddress=${ipAddress%/*}
#asn=$3

localBgps=()
asn=$3
#localAsns=$3
remoteBgps=()
remoteAsns=()
for (( i=2; i<=$#; i=i+4 ))
do
	(( j=${i}+1 ))
	(( k=${i}+2 ))
	(( t=${i}+3 ))

	localBgps[${#localBgps[@]}]=${!i}
#	localAsns[${#localAsns[@]}]=${!j}
	
	remoteBgps[${#remoteBgps[@]}]=${!k}
	remoteAsns[${#remoteAsns[@]}]=${!t}

#	echo ${!j}
done

# for i in ${remoteAsns[@]}
# do
#	echo ${remoteAsns[0]}
# done

# exit

# neighborIpAddress=$4
# remote_asn=$5

interfaces=`ifconfig |awk -v RS=  '/'$ODMU_IP'/{print $1}' | grep -v lo`
OLD_IFS="$IFS"
IFS=" "
interfaces=($interfaces)
IFS="$OLD_IFS"


###prepare for bgpd.conf
neighbor_bgp=""
counter=0
for i in ${remoteBgps[@]}
do
	if [ $counter -eq 0 ]
	then
		neighbor_bgp="\n neighbor ${i%/*} remote-as ${remoteAsns[$counter]}"
	else
		neighbor_bgp=${neighbor_bgp}"\n neighbor ${i%/*} remote-as ${remoteAsns[$counter]}"
	fi
	let counter=$counter+1
done

ipList=()
netmaskList=()
otherIpList=()
otherNetmaskList=()
for i in ${interfaces[@]}
do
	ip link set mtu 1462 dev $i
#	echo "$i"
	temp=`/home/quagga/get_ip $i`
	ip=`echo $temp | awk -F ' ' '{print $1}'`
	netmask=`echo $temp | awk -F ' ' '{print $2}'`
	ipList[${#ipList[@]}]=${i}:${ip}
	netmaskList[${#netmaskList[@]}]=$netmask

	for j in ${localBgps[@]}
	do
		if [ "$ip"x = "${j}"x ]
		then
			continue 2
		fi
	done
	
	otherIpList[${#otherIpList[@]}]=$ip
	otherNetmaskList[${#otherNetmaskList[@]}]=$netmask
done

# for i in "${otherIpList[@]}"
# do 
# 	echo "$i"
# done

# echo $netmask

counter=0
network_bgp=""
network_ospf=""
for i in ${otherIpList[@]}
do
	prefix=`ipcalc -n ${i} ${otherNetmaskList[$counter]}`
	len=`ipcalc -p ${i} ${otherNetmaskList[$counter]}`
	temp_value=${prefix#*=}
	temp_value=${temp_value%.*}

	prefix=${prefix#*=}/${len#*=}
	if [ ${counter} -eq 0 ]
	then
#		network_bgp=" network "${prefix}
                network_ospf="\n network "${prefix}" area 0.0.0.0"
	else
#		network_bgp=${network_bgp}"\n network "${prefix}
		network_ospf=${network_ospf}"\n network "${prefix}" area 0.0.0.0"
	fi

	let counter=$counter+1
done

network_bgp=" network "${as_prefix}

###prepare ends


###prepare for zebra.conf
hostname=`hostname`

counter=0
interface_zebra=""
interface_ospf=""
for i in ${ipList[@]}
do
	veth_name=${i%:*}
	ipaddr=${i#*:}
	len=`ipcalc -p ${ipaddr} ${netmaskList[$counter]}`
	ipaddr=${ipaddr}/${len#*=}

	if [ $counter -eq 0 ]
	then
		interface_zebra="\ninterface  ${veth_name}\n ip address ${ipaddr}\n ipv6 nd suppress-ra"
		interface_ospf="\ninterface  ${veth_name}"
	else
		interface_zebra=${interface_zebra}"\ninterface  ${veth_name}\n ip address ${ipaddr}\n ipv6 nd suppress-ra"
		interface_ospf=${interface_ospf}"\ninterface ${veth_name}"
	fi

	let counter=$counter+1	
done

# echo ${ipList[0]}
# echo $ipaddr_1
###prepare ends


###prepare for ospfd.conf

###prepare ends


( cat <<EOF > /etc/quagga/bgpd.conf
!
hostname bgpd
password zebra
log file /var/log/quagga/quagga.log
log stdout
!
router bgp $asn
 bgp router-id $ipAddress
EOF
)
echo -e "$network_bgp" >> /etc/quagga/bgpd.conf
echo -e "\n timers bgp 1 3" >> /etc/quagga/bgpd.conf
echo -e "$neighbor_bgp" >> /etc/quagga/bgpd.conf
echo -e "!\nline vty\n!" >> /etc/quagga/bgpd.conf


( cat <<EOF > /etc/quagga/zebra.conf
!
hostname $hostname
log file /var/log/quagga/quagga.log
!
EOF
)
echo -e "$interface_zebra" >> /etc/quagga/zebra.conf
echo -e "\n" >> /etc/quagga/zebra.conf
( cat <<EOF >> /etc/quagga/zebra.conf
!
interface lo
!
ip forwarding
!
line vty
!
EOF
)


( cat <<EOF > /etc/quagga/ospfd.conf
!
hostname ospfd
password zebra
log file /var/log/quagga/quagga.log
log stdout
!
EOF
)
echo -e "$interface_ospf" >> /etc/quagga/ospfd.conf
echo -e "\n" >> /etc/quagga/ospfd.conf
( cat <<EOF >> /etc/quagga/ospfd.conf
!
interface lo
!
router ospf
 ospf router-id $ipAddress
 redistribute connected
 redistribute bgp
!
EOF
)
echo -e "$network_ospf" >> /etc/quagga/ospfd.conf
echo -e "\n" >> /etc/quagga/ospfd.conf
( cat <<EOF >> /etc/quagga/ospfd.conf
!
line vty
!
EOF
)

temp=${as_prefix%/*}
# echo ${as_prefix}

netmask=`ipcalc -m ${as_prefix}`
add_ip=${temp%.*}.2
ifconfig lo:0 $add_ip netmask ${netmask#*=} up
service zebra start
service bgpd start
# service ospfd start
