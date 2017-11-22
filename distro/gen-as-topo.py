import sys
import os

host_count = int(sys.argv[1])
node_count = int(sys.argv[2])

dir_name = sys.argv[3]

link_dict = {}



for h in range(host_count):
	f = open(dir_name + "/node-list-" + str(h + 1), 'w')

	for n in range(node_count):
	
		asn = (h + 1) * 1000 + n + 1
		prefix = str(h + 1) + "." + str(n + 1) + ".0.0/16"
		f.writelines(str( asn ) + "#" + "ASN-" + str(asn) + "#" + prefix + "\n"  )
	
	
	f.close()

# create asrela.txt

for h in range(host_count):
        f = open(dir_name + "/link-list-" + str(h + 1), 'w')
	used = 1
        for n in range(node_count):
                asn_a = (h + 1) * 1000 + n + 1
                if (used + 1 > node_count):
			break
		asn_b = (h + 1) * 1000 + used + 1
		f.writelines( str( asn_a ) + "#" + str( asn_b )  + "#50M#P2C\n" )
                if (used + 2 > node_count):
			break
		asn_c = (h + 1) * 1000 + used + 2
                used += 2
		f.writelines( str( asn_a ) + "#" + str( asn_c )  + "#50M#P2C\n" )
		
		
        f.close()
		
for h in range(host_count):
	asn_a = (h + 1) * 1000  + 1
	f = open(dir_name + "/interlink-list-" + str(h + 1), 'w')
	for k in range(host_count):
		if h != k:
			asn_b = (k + 1) * 1000 + 1
			f.writelines( str( asn_a ) + "#" + str( asn_b )  + "#50M#P2P#" + str(h + 1) + "#" + str(k + 1) + "\n" )
			
	f.close()


