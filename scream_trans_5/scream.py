#!/usr/bin/env python
#coding:utf-8
import select
import serial
import datetime
import multiprocessing
import RPi.GPIO as GPIO
#import wifi_test
#import pywifi
import subprocess
import os
import sys
import time 
import uart
import data
import server
    
i=0
key_statue = True
key_flag = False 
GPIO.setmode(GPIO.BCM)
GPIO.setup(22,GPIO.OUT) #喇叭
GPIO.setup(5,GPIO.OUT) #LED
GPIO.setup(17,GPIO.IN) #按键
port0=serial.Serial("/dev/myuart0",baudrate=115200,timeout=0)
port1=serial.Serial("/dev/myuart1",baudrate=115200,timeout=0)
port2=serial.Serial("/dev/myuart2",baudrate=115200,timeout=0)
port3=serial.Serial("/dev/myuart3",baudrate=115200,timeout=0)
#fd1=open("/scream/upload/data.txt","a+")
#fd1.close()
#fd2=open("/scream/download/name1.txt","a+")
#fd2.close()
#fd3=open("/scream/download/name.txt","a+")
#fd3.close()
#while True:
#	filename=getname()
#	print(filename)
#	if filename!=3:
#		break
#if(filename==1):  #初始化比较文件名字，不同就下载
#	download()
#GPIO.output(5,1)
uartdata = uart.Uart_data()
q_socket = multiprocessing.Queue()
q_sensor = multiprocessing.Queue()
p_recv = multiprocessing.Process(target=uartdata.data_recev,args=(port0,port1,port3,q_socket,q_sensor,))
p_sock = multiprocessing.Process(target=server.sock_server,args=(q_socket,))
p_sensor = multiprocessing.Process(target=uartdata.sensor,args=(port2,q_sensor,))
p_recv.start()
p_sensor.start()
p_sock.start()
#wifi = pywifi.PyWiFi()
#iface = wifi.interfaces()[0]
#pid = wifi_test.AP_mode()
##蜂鸣器#########
GPIO.output(22,1)
time.sleep(0.5)
GPIO.output(22,0)
######################
try:
	while True:
		time.sleep(1)
		if (GPIO.input(17)==0 and key_statue==True):
			time.sleep(0.02)
			key_statue=False
			if (GPIO.input(17)==0):
					key_flag=True
					print 'key down'
		elif (GPIO.input(17)==1):
			key_statue=True			
#		if key_flag == True:
#			key_flag = False
#			sub=subprocess.Popen("sudo kill -9 "+pid,shell=True)
#			time.sleep(2)
#			while True:
#				if wifi_test.wifi_connect(iface,ssid,password) == 0:
#					GPIO.output(22,1)
#					time.sleep(0.5)
#					GPIO.output(22,0)
#					break
except (KeyboardInterrupt,AssertionError):
	GPIO.cleanup(17)
	GPIO.cleanup(22)
	GPIO.cleanup(5)
	port1.write("stop")
	port0.write("stop")