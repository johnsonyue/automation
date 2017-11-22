# generate topology

# no ibgp supported



import os
import sys
import re
from IPy import IP

# set ping source and destination 
# ***source_ip and dest_ip must be a host and***
# ***source_ip and dest_ip can not be zombies and ***
# ***source_ip can not be control***
source_ip = "200.0.2.4"
dest_ip = "10.0.14.2"
if source_ip == "" or dest_ip == "":
	print "Please specify the ping test source and destination"
	exit()
# set ends

config_file_path = "/home/yupeng/"
#fnode = open(config_file_path + "node.txt", 'r')
#flink = open(config_file_path + "link.txt", 'r')
#fNewNode = open(config_file_path + "new-node.txt", 'w')
fnode = open(sys.argv[1], 'r')
flink = open(sys.argv[2], 'r')
fNewNode = open(sys.argv[4], 'w')
linkLines = flink.readlines()
nodeLines = fnode.readlines()

# write to new-node.txt
newNodeLines = nodeLines
for i in range(len(newNodeLines)):
	newNodeLines[i] = newNodeLines[i].strip()
#end

print "Checking topology files ..."
ipList = []
for nodeLine in nodeLines:
	nodeLine = nodeLine.strip()
	res = nodeLine.split("#")
	ipAddresses = res[1].split("|")
	for i in ipAddresses:
		ipList.append(i)

for ipaddr in ipList:
#	print ipaddr
	resFile = os.popen("ipcalc " + ipaddr + " | grep 'Network:'")
	res = resFile.readlines()[0][:-1]
#	print res
	network = re.split(" +", res)[1]

	ipInNetwork = IP(network)
	firstIp = ipInNetwork[1]
	lastIp = ipInNetwork[-1]

#	print ipaddr.split("/")[0], firstIp, lastIp
#	print type(ipaddr.split("/")[0]), type(firstIp), type(lastIp)	

	if ipaddr.split("/")[0] == str(firstIp):
		print ipaddr + ": can not be the first ip address in this network segmentation."
		exit()
	if ipaddr.split("/")[0] == str(lastIp):
                print ipaddr + ": can not be the last ip address in this network segmentation."
                exit()

print "Creating required networks ..."
counter = 1
network_dict = {}
for linkLine in linkLines:
#	print linkLine,
	linkLine = linkLine.strip()
	interfaces = linkLine.split(" ")
	
	# get network number
	interface = interfaces[0]
	resFile = os.popen("ipcalc " + interface + " | grep 'Network:'")
	res = resFile.readlines()[0][:-1]
	network = re.split(" +", res)[1]
	
	print network

	os.system("docker network create net_" + str(counter) + " --subnet " + network)
	network_dict[network] = "net_" + str(counter)
	counter += 1
for i in network_dict:
	print "Created Network: " + i + ", Name: " + network_dict[i]


print "Created required networks successfully."

container_list = []

# times = 0

f_asinfo = open(sys.argv[3], 'r')
asInfoLines = f_asinfo.readlines()
asPrefixDict = {}
for i in range(len(asInfoLines)):
	asInfoLines[i] = asInfoLines[i].strip()
	temp_list = asInfoLines[i].split("#")

	asPrefixDict[temp_list[0]] = temp_list[-1]



for nodeLine in nodeLines:
# 	times += 1
	
	nodeLine = nodeLine.strip()	

#	print nodeLine
	
	res = nodeLine.split("#")
	deviceType = res[0]
	ipList = res[1].split("|")
	asn = res[2]

	# print asn

#	print ipList[0]

	network = (os.popen("ipcalc " + ipList[0] + " | grep 'Network:'")).readlines()[0][:-1]
	network = re.split(" +", network)[1]
#	print "#" + network
	

#########################
	asn_1 = asn
	ip_from_asprefix = asPrefixDict[str(asn_1)].split("/")[0]
	ip_split = ip_from_asprefix.split(".")

	new_ip_for_name = ip_split[0] + "." + ip_split[1] + "." + ip_split[2] + ".2"
	new_ip = ip_split[0] + "." + ip_split[1] + "." + ip_split[2] + ".2/" + asPrefixDict[str(asn_1)].split("/")[1]

	for index in range(len(newNodeLines)):
		temp = newNodeLines[index].split("#")
		if temp[2] == str(asn_1) and temp[0] == "BGP":
			newNodeLines[index] = temp[0] + "#" + new_ip + "|" + temp[1] + "#" + temp[2]	
#########################

	if deviceType == "BGP":
		containerIdFile = os.popen("docker run -dit --privileged --net=" + network_dict[network] + " --name=" + new_ip_for_name + " --ip=" + ipList[0].split("/")[0]  + " -v /home/quagga:/home/quagga centos-quagga-bgp /bin/bash")
	else:
		containerIdFile = os.popen("docker run -dit --privileged --net=" + network_dict[network] + " --name=" + ipList[0].split("/")[0] + " --ip=" + ipList[0].split("/")[0]  + " -v /home/quagga:/home/quagga centos-quagga-bgp /bin/bash")

	containerId = containerIdFile.readlines()[0][:-1]
	container_list.append(containerId)

	min_host = os.popen("ipcalc " + ipList[0] + " | grep 'HostMin:'").readlines()[0][:-1]
	min_host = re.split(" +", min_host)[1]	

	os.system("docker exec " + containerId + " route del default gw " + min_host)

	containerInterface = (os.popen("docker inspect -f '{{.NetworkSettings.Networks." + network_dict[network] + ".IPAddress}}' " + containerId)).readlines()[0][:-1]
	if deviceType == "BGP":
		containerInterface = new_ip_for_name
	print "Created container: " + containerId + ", IP: " + containerInterface

	os.system("docker exec " + containerId + " python /home/quagga/bot_sub.py &")

	if deviceType != "HOST":
		i = 1
		while i < len(ipList):
			network = (os.popen("ipcalc " + ipList[i] + " | grep 'Network:'")).readlines()[0][:-1]
        		network = re.split(" +", network)[1]
#			print "docker network connect --ip " + ipList[i].split("/")[0] + " " + network_dict[network] + " " + containerId
			os.system("docker network connect --ip " + ipList[i].split("/")[0] + " " + network_dict[network] + " " + containerId)
			#print "HERE"
			i += 1	
	
#	if times == 3:
#		exit()

	
	if deviceType == "HOST":
		gateway = ipList[-1].split("/")[0]
#		print "docker exec " + containerId + " /home/zombie-config.sh " + gateway
	
		# write file /home/yupeng/quagga/new/BGP/host-ip-id.txt
		hostIp = ipList[0].split("/")[0]
		# write ends

		os.system("docker exec " + containerId + " /home/quagga/zombie-config.sh " + gateway)
#		if (source_ip != hostIp):
#			os.system("docker exec " + containerId + " python /home/quagga/bot_sub.py &")
		
		# process ping test
		if (source_ip == hostIp and source_ip != "" and dest_ip != ""):
			print "Please ping test manually, Destination:  " + dest_ip
			print "*** Example: ping " + dest_ip + " | tee /home/quagga/new/BGP/ping.txt ***"
			print "and then press CTRL + P + Q to continue running the topo_gen.py script."
			os.system("docker attach " + containerId)
		# ends
			

	elif deviceType == "OSPF":
		os.system("docker exec " + containerId + " /home/quagga/ospf-router.sh")
	elif deviceType == "BGP":
		asn_1 = asn
		# find which ip address(es) is used on BGP communications
		
		local_remote = []
		
		my_ip_list = []
		for ipAddress in ipList:
			my_ip_list.append(ipAddress)

		for ip_index in my_ip_list:
			for linkLine in linkLines:
                                linkLine = linkLine.strip()
                                link = linkLine.split(" ")
				if ip_index in link:
					nodeInLink = link
                                        break
			if nodeInLink == "":
                                print "ip address " + ip_index +  " does not appears in link.txt"
                                continue

			if len(nodeInLink) > 2:
				print "assert: neighbor of one interface more than 1, not bgp interface"
				continue

			neighbor = ""
                        for node in nodeInLink:
                                if node == ip_index:
                                        continue
                                neighbor = node
                                break
			
			tempNodeLines = nodeLines
			for tempNodeLine in tempNodeLines:
                                tempNodeLine = tempNodeLine.strip()
                                res = tempNodeLine.split("#")
                                ipListSplit = res[1].split("|")

				#print tempNodeLine			
	
				if (neighbor in ipListSplit) and res[0] == "BGP" and str(res[2]) != str(asn_1):
					#print ip_index
                                        #print asn_1
                                        #print neighbor
                                        #print str(res[2])
					local_remote.append(ip_index.split("/")[0] + " " + str(asn_1) + " " + neighbor.split("/")[0] + " " + str(res[2]))

		para_str = ""
		for i in local_remote:
			para_str += i + " "
		
		#print para_str
		#exit()
		
#		print "docker exec " + containerId + " /home/quagga/bgp-router.sh " + asPrefixDict[str(asn_1)] + " " + para_str + " > /home/log"			
		os.system("docker exec " + containerId + " /home/quagga/bgp-router.sh " + asPrefixDict[str(asn_1)] + " " + para_str)
		
	else:
		print "Unknown device type."
		exit()

for i in newNodeLines:
	fNewNode.writelines(i + "\n")

fnode.close()
flink.close()
fNewNode.close()

