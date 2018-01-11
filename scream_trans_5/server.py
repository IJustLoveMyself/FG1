#!/usr/bin/env python
#coding:utf-8
import pycurl
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
import struct
import socket   

##############socket通信，server端 UDP####################################################
##############data = '0' 开始发送 data = '1' 断开连接 data = '2' 心跳包，每个15s一个，50ms*350>15s
def sock_server(q_socket):	
	while True:
		buf = ''
		address = ('', 7321)
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
		s.bind(address)
		print 'wait'
		data, addr = s.recvfrom(1024)
		print data	
		if data == '0':
			times=350
			while True:	
				if not q_socket.empty():
					buf = q_socket.get()
					s.sendto(buf,addr)
					times=times-1
			#轮询检测接收，当有接受的时候i=1 退出循环，连接后UDP的发送不会超时，
			#需要通过这种方法来检测客户端关闭，当客户端关闭，退出发送循环，重新等待客户端连接
				rlist,wlist,elist=select.select([s],[],[],0)
				for fd in rlist:
					if fd == s:
						data, addr = s.recvfrom(1024)
				if data== '2':
					print "connecting"
					times=350
					data = '3'	
				if data=='1' or times==0:
					break
				time.sleep(0.01)
		s.close()
	
##############socket通信，server端 TCP####################################################

#def sock_server(q_socket):
#	while True:
#		buf = ''
#		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         # 创建 socket 对象
##		host = socket.gethostname() # 获取本地主机名
#		
#		port = 7321                # 设置端口
##设置允许重复连接
#		s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
##设置设置无等待延时发送，提高小包数据发送性能
#		s.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1)
#		s.bind(("", port))        # 绑定端口
#		s.listen(5)                 # 等待客户端连接
#		print 'wait client'
#		c, addr = s.accept()     # 建立客户端连接。
#		while True:
#			try:
#				if not q_socket.empty():
#					buf = q_socket.get()
#					buf = buf + str(datetime.datetime.now())+'\n'
#					i=c.send(buf)
##					print 'send time=',str(datetime.datetime.now())
##					data = c.recv(1024)					
##					print 'recv time=',str(datetime.datetime.now())
#					
#			except:
#				c.close() 	# 关闭连接
#				break          