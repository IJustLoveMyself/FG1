#!/usr/bin/env python
#coding:utf-8
import sys
import os
import select
import time
import platform
import logging
import socket
import subprocess
import multiprocessing
import RPi.GPIO as GPIO
import pywifi
from pywifi import const
from wifi import Cell, Scheme

def get_scan(iface):
	scan_error=0
	try:
		bsses = iface.scan_results()
		scan_error=0
		print "scan ok"
		return bsses
	except IndexError,NameError:
		scan_error=1
		print "scan error"
		return scan_error

##################扫描附近wifi，ssid和inform.txt中的ssid匹配，如果出现尝试连接，这里的扫描用的是pywifi自带的方法#########################################
def wifi_scan_pywifi(iface): 
#	try:
#		bsses = iface.scan_results()
#		scan_ok=1
#	except IndexError,NameError:
#		print "scan error"
#		scan_ok=0
#	if scan_error == 1:
	while True:
		bsses = iface.scan_results()
		if bsses !=1 :
			break
		time.sleep(3)		
	for bss in bsses:
		fd=open("inform.txt","r+")
		ssid=str(bss.ssid)
		while True:
				line=fd.readline()
				if len(line)==0:
					break
				line=line.splitlines()
				print line
				line=line[0].split(":")
				if (line[0].find(ssid)!=-1 and len(line[0])==len(ssid)):
						while True:
							if	wifi_connect(iface,line[0],line[1]) == 0:
								break
							time.sleep(3)					
		if iface.status()==const.IFACE_CONNECTED:
				break
	fd.close()
###############获取本机当前IP，在作为TCP服务器的时候需要使用##############################
def get_ipadress():
	fd=open("return.txt","w+")
	sub=subprocess.Popen("ifconfig wlan0",stdout=fd,shell=True)
	fd.close
	fd=open("return.txt","r+")
	while True:
		line=fd.readline()
		if  line.find("inet addr")!=-1:
	   		break
	print line
	ipadress=line.split(" ")
	ipadress=ipadress[11].split(":")	
	return ipadress[1]
############################开启本机的AP模式###############################################
def AP_mode():		
	sub=subprocess.Popen("sudo wpa_cli -i wlan0 disconnect",shell=True)
	time.sleep(1)
	fd=open("return.txt","w+")
	print "open return"
	sub=subprocess.Popen("sudo create_ap wlan0 eth0 xiaofeng",stdout=fd,shell=True)
	fd.close
	print "AP ok"
	fd=open("return.txt","r+")
	while True:
	  		line=fd.readline()
	  		if  line.find("PID")!=-1:
	     			break
	line=line.split(" ")
	return line[1]
###########与手机连接获取ssid和password#################################################
def get_inform(ipadress):
	s=socket.socket()
	port=12345
	s.bind((ipadress,port))
	s.listen(5)
	c,addr=s.accept()
	print "client",addr
	c.send("input wifi ssid:password")
	buf= c.recv(1024)
	s.close()
	print "client buf=",buf
	return buf
#######################一键配置wifi后对wifi信息保存####################################
def save_inform(buf):
	buf=buf+'\r\n'
	fd1=open("inform1.txt","w+")
	fd1.write(buf)
	buf=buf.split(":")
	buf=str(buf[0])
	fd2=open("inform.txt","r+")
	while True:
		line=fd2.readline()
		if len(line)==0:
			break
		m=line.split(":")
		m=str(m[0])
		if(len(buf)==len(m) and buf.find(m)!=-1):
			print line
		else:
			fd1.write(line)
	os.remove("inform.txt")
	os.rename("inform1.txt","inform.txt")

			
######################在本机AP模式下与手机进行连接通信，获取信息########################
def ap_trans_connect(iface):
	print "ap_trans_connect start"
	while True:
		pid=AP_mode()
		print "pid=",pid
		time.sleep(5)
		ipadress=get_ipadress()
		buf=get_inform(ipadress)
		if len(buf)==4 and buf.find("exit")!=-1:
			break
		sub=subprocess.Popen("sudo kill -9 "+pid,shell=True)
		inform=buf.split(":")
		while True:
			if wifi_connect(iface,inform[0],inform[1]) == 0:
				break
		print "wifi status is ",iface.status()
		if iface.status()==const.IFACE_CONNECTED:
			"wifi is connect"
			save_inform(buf)
			break
	print "break out ap_trans"

		

#########################wifi 连接#######################################       
def wifi_connect(iface,ssid,password):
	connect_error=0  #成功进行了一次连接，程序没有出现异常
	try:
		print "ssid=",ssid
		print "password=",password
		iface.disconnect()
		time.sleep(1)
		profile = pywifi.Profile()
		profile.ssid = ssid	
		profile.auth = const.AUTH_ALG_OPEN
		profile.akm.append(const.AKM_TYPE_WPA2PSK)
		profile.cipher = const.CIPHER_TYPE_CCMP
		profile.key = password

		iface.remove_all_network_profiles()
		tmp_profile = iface.add_network_profile(profile)
		iface.connect(tmp_profile)
		time.sleep(5)
		print "connect ok"
		connect_error=0
	except IndexError,NameError:
		print "connect error"
		connect_error=1
	return connect_error

		
