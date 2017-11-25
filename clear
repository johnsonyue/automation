#!/bin/bash
ifconfig br0 down && brctl delbr br0;
ifconfig br1 down && brctl delbr br1;
ovs-vsctl del-br ovs0;
docker ps -a | grep centos-quagga-bgp | awk '{print $NF}' | xargs -I {} bash -c "docker stop {} && docker rm {}"
docker network ls | grep -E "net_[0-9]+" | awk '{print $1}' | xargs -I {} bash -c "docker network rm {}"
