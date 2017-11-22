import sys
import os

host_count = sys.argv[1]
node_count = sys.argv[2]
dir_name = sys.argv[3]

os.system("python gen-as-topo.py " + host_count + " " + node_count + " " + dir_name)

for i in range(int(host_count)):
	os.system("python gen-bgp.py " + dir_name + "/node-list-" + str(i + 1) + " " + dir_name + "/link-list-" + str(i + 1) \
		+ " " + dir_name + "/interlink-list-" + str(i + 1))

# give necessities to An Yuhao
an_dir = "/home/yupeng/quagga/new/BGP/peizhi/"

os.system("cut -d'#' -f3,6 host-node/interlink-list-*.bgp | tr '#' ' ' > " +dir_name + "/interlink-list-bgp.temp")

os.system("cat " + dir_name +  "/node-list-*.bgp > " + an_dir + "node.txt")
os.system("cat " + dir_name + "/link-list-*.bgp " + dir_name + "/interlink-list-bgp.temp > " + an_dir + "link.txt")

# combine all interlink.bgp together
os.system("cat " + dir_name + "/interlink-list-*.bgp > " + dir_name + "/interlink-list-all.bgp")

