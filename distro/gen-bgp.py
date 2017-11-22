import sys


f1 = open(sys.argv[1], 'r')
f1_lines = f1.readlines()

f2 = open(sys.argv[2], 'r')
f2_lines = f2.readlines()

f3 = open(sys.argv[3], 'r')
f3_lines = f3.readlines()

fwNode = open(sys.argv[1] + ".bgp", 'w')
fwLink = open(sys.argv[2] + ".bgp", 'w')
fwInter = open(sys.argv[3] + ".bgp", 'w')

as_list = []
as_dict = {}
for i in range(len(f1_lines)):
	f1_lines[i] = f1_lines[i].strip()
	temp = f1_lines[i].split("#")

	as_list.append(temp[0])
	as_dict[temp[0]] = temp[-1]


network_dict = {}
for i in as_list:
	temp_list = ["130", "146", "162", "178", "194", "210", "226"]
	network_dict[i] = temp_list

prefix_dict = {}	
for i in as_list:
	network = as_dict[i].split("/")[0]
	netLen = as_dict[i].split("/")[1]
	if int(netLen) > 24:
		print "netLen > 24"
		exit()

	temp_list = network.split(".")
	

	prefix_dict[i]  = temp_list[0] + "." + temp_list[1] + "." +  temp_list[2] + "."
	

node_dict = {}

for asn in as_list:

	node_dict[asn] = "BGP#"


for asn in as_list:
	i = 0
	while i < len(f2_lines):
		f2_lines[i] = f2_lines[i].strip()
		temp = f2_lines[i].split("#")

		as_1 = temp[0]
		as_2 = temp[1]

		if as_1 == asn:
			gen_network = prefix_dict[asn] + (network_dict[asn])[0] + "/28"
			gen_network_2 = prefix_dict[asn] + str( int( (network_dict[asn])[0] ) + 1 ) + "/28"
			fwLink.writelines(gen_network + " " + gen_network_2 + "\n")
			(network_dict[asn]).remove((network_dict[asn])[0])

			f2_lines.remove(f2_lines[i])

			if as_1 not in as_list or as_2 not in as_list:
				print "error"
				exit()
	
			node_dict[as_1] += (gen_network + "|")
			node_dict[as_2] += (gen_network_2 + "|")
			
			continue		

		i += 1

for i in node_dict:
	#node_dict[i] += "#" + i
	node_dict[i] = node_dict[i][:-1] +  "#" + i
	fwNode.writelines(node_dict[i] + "\n")

for i in range(len(f3_lines)):
	f3_lines[i] = f3_lines[i].strip()
	split = f3_lines[i].split("#")

	asn_1 = split[0]
	asn_2 = split[1]
        if (int(asn_1) > int(asn_2)):
		break  
	
	fasn2 = open("host-node/node-list-" + split[-1], 'r')
	asn2NodeLines = fasn2.readlines()

	for i in range(len(asn2NodeLines)):
		asn2NodeLines[i] = asn2NodeLines[i].strip()
		temp_list = asn2NodeLines[i].split("#")
		as_dict[temp_list[0]] = temp_list[-1]
	fasn2.close()	

	ip_from_asprefix = as_dict[str(asn_1)].split("/")[0]
	ip_split = ip_from_asprefix.split(".")
	new_ip1 = ip_split[0] + "." + ip_split[1] + "." + ip_split[2] + ".2"

	ip_from_asprefix = as_dict[str(asn_2)].split("/")[0]
	ip_split = ip_from_asprefix.split(".")
	new_ip2 = ip_split[0] + "." + ip_split[1] + "." + ip_split[2] + ".2"

	gen_network = prefix_dict[asn_1] + (network_dict[asn_1])[0] + "/28"
	gen_network_2 = prefix_dict[asn_1] + str( int( (network_dict[asn_1])[0] ) + 1 ) + "/28"


	fwInter.writelines(split[-2] + "#" + asn_1 + "#" + new_ip1 + "#" + gen_network + "#" + split[-1] + "#" + asn_2 + "#"  + new_ip2 + "#" + gen_network_2 + "\n")

f1.close()
f2.close()
f3.close()
fwNode.close()
fwLink.close()
fwInter.close()

