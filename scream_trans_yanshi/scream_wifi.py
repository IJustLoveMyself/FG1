#!/usr/bin/env python
#coding:utf-8
import pycurl
import select
import serial
import datetime
import multiprocessing
import RPi.GPIO as GPIO
import wifi_test
import pywifi
import subprocess
import os
import sys
import time 
import struct
import socket               # 导入 socket 模块

#######################################接收传感器数据，数据类型string########################################
def uart_rec_str(port):		
	rv_buf=""
	ch=''
	while True:
		ch=port.read()
		rv_buf+=ch
		if ch=='e':
			break
	return rv_buf	


###########################接收电机数据，数据类型hex#############################
def uart_rec_int(port):
	i=0
	ch=0
	res=0
	rtn_buf='' 
	rv_buf=[]
	r_flag=0
	while True:
		res=port.read()
#		print 'res: ',res,', type: ',type(res),', len: ',len(res)
		if res=='#':
			rv_buf.append(res)
#			print 'rv_buf: ',rv_buf
			if i==25:
				ch=(rv_buf[2]<<8)|rv_buf[1]
				rtn_buf+=str(ch)
				rtn_buf+=','
				ch=(rv_buf[6]<<24)|(rv_buf[5]<<16)|(rv_buf[4]<<8)|rv_buf[3]
				rtn_buf+=str(ch)
				rtn_buf+=','
				ch=(rv_buf[8]<<8)|rv_buf[7]
				rtn_buf+=str(ch)
				rtn_buf+=','
				ch=(rv_buf[12]<<24)|(rv_buf[11]<<16)|(rv_buf[10]<<8)|rv_buf[9]
				rtn_buf+=str(ch)
				rtn_buf+=','
				ch=(rv_buf[14]<<8)|rv_buf[13]
				rtn_buf+=str(ch)
				rtn_buf+=','
				ch=(rv_buf[18]<<24)|(rv_buf[17]<<16)|(rv_buf[16]<<8)|rv_buf[15]
				rtn_buf+=str(ch)
				rtn_buf+=','
				ch=(rv_buf[20]<<8)|rv_buf[19]
				rtn_buf+=str(ch)
				rtn_buf+=','
				ch=(rv_buf[24]<<24)|(rv_buf[23]<<16)|(rv_buf[22]<<8)|rv_buf[21]
				rtn_buf+=str(ch)
				return rtn_buf
			rv_buf=[]
			r_flag=0
			i=0			
		if r_flag==1:
			res = struct.unpack("b", res)   #将\xhh形式的字符串中的\x去掉
#			res=int(res,16)
			rv_buf.append(int(res[0]))   #以追加额方式存放在list中
			i=i+1
		if res=='$':
			r_flag=1
			rv_buf.append(res)
			i=i+1
#			rv_buf="$"

def data_write(buf):
	fds=open("/scream/upload/data.txt","a+")
	fds.write(buf)
	fds.close()
##############################多个串口数据接收处理############################			
def data_recev(port0,port1,port3,q_socket):       
	flag=0
	sendflag=0     
	send_buf0=""
	send_buf1=""
	send_buf3=""
	sock_buf=""
	data_buf=""
	data_buf_20_1=""
	data_buf_20_2=""
	data_buf_20_3=""
	data_buf_choose=0
	start_flag="start"
	stop_flag="stop"
	i=0  
	times=0
	fd3=open("/dev/myuart3","r+")
	fd1=open("/dev/myuart1","r+")
	fd0=open("/dev/myuart0","r+")
	port3.write(start_flag)
	port1.write(start_flag)
	port0.write(start_flag)
	while True:
		rlist,wlist,elist=select.select([fd0,fd1,fd3,],[],[],0)
		for fd in rlist:
			if(fd==fd3):
#				lock.acquire()
#				try:
				send_buf3=''
				send_buf3=uart_rec_int(port3)	
				flag=flag|0x0001			
#				finally:
#					lock.release() 
			if(fd==fd1):
				send_buf1=""
				send_buf1=uart_rec_str(port1)
				if send_buf1[0]=="s" :
					send_buf1=send_buf1[2:-1]
					flag=flag|0x0010
					sendflag=sendflag|0x01    
			if(fd==fd0):
				send_buf0=""
				send_buf0=uart_rec_str(port0)
				if send_buf0[0]=="s":
					send_buf0=send_buf0[2:-1]
					flag=flag|0x0100
					sendflag=sendflag|0x10  		
#		if(flag == 0x0111):
#					flag=0
#					time_0=str(datetime.datetime.now())
#					save_buf0=send_buf0.split("$")
#					save_buf1=send_buf1.split("$")
#					data_buf="S"+save_buf0[0]+save_buf1[0]+",P,"+save_buf0[1]+","+save_buf1[1]+",E,"+save_buf0[2]+save_buf1[2]
#					data_buf_20_1=data_buf_20_1+data_buf+send_buf3+"#"+time_0+"\r\n"
#					times+=1
#					#缓存20组去存储
#					if times==20:
#						if data_buf_choose==0:
#							data_buf_20_2=data_buf_20_1
#							data_buf_20_3=""
#							data_buf_20_1=""
#							data_buf_choose=1
#							p=multiprocessing.Process(target=data_write,args=(data_buf_20_2,))
#							p.start()
#						else:
#							data_buf_20_3=data_buf_20_1
#							data_buf_20_2=""
#							data_buf_20_1=""
#							data_buf_choose=0
#							p=multiprocessing.Process(target=data_write,args=(data_buf_20_3,))
#							p.start()
#						times=0		
#				
		if(sendflag==0x11):
			sendflag = 0
			save_buf0=send_buf0.split("$")
			save_buf1=send_buf1.split("$")
#			sock_buf="S"+save_buf0[0]+save_buf1[0]+",P,"+save_buf0[1]+","+save_buf1[1]+",E,"+save_buf0[2]+save_buf1[2]+'M'+send_buf3+',+'"e\r\n"
			sock_buf="S"+save_buf0[0]+save_buf1[0]+",e\r\n"
			if q_socket.empty() == True:
				q_socket.put(sock_buf)
		time.sleep(0.01)	
#		if(i==1):
#			port1.write(stop_flag)
#			port0.write(stop_flag)
#			fd0.close()
#			fd1.close()
#			fd3.close()
#			sock.close()
#			break
###################################数据上传###########################################			
#def upload():
#	c = pycurl.Curl()
##	c.setopt(c.URL,"http://192.168.2.114/upload/" )
#	c.setopt(c.URL,"http://192.168.2.213/http/upload/" )
#	c.setopt(c.HTTPPOST, [
#		('fileupload', (
#		# upload the contents of this file
#		c.FORM_FILE, "/scream/upload/data.txt",
#       		 # specify a different file name for the upload
#		c.FORM_FILENAME, "data.txt",
#		# specify a different content type
#		c.FORM_CONTENTTYPE, 'txt/plain',
#   		 )),
#		])	
#	c.perform()
#	c.close()
#	os.remove("/scream/upload/data.txt")
#	GPIO.output(22,1)
#	time.sleep(0.5)
#	GPIO.output(22,0)

#########################数据下载#####################################################	
#def download():
#	c = pycurl.Curl()
##	c.setopt(c.URL, "http://192.168.2.114/download/data.txt")
#	c.setopt(c.URL, "http://192.168.2.213/http/download/data.txt")
#	f=open("/scream/download/data.txt","wb")
#	c.setopt(c.WRITEDATA, f)
#	c.perform()	
#	f.close()
#	c.close()

##############获取文件名字，通过名字判断服务器端的数据是否更新########################
#def getname():
#	try:
#		c = pycurl.Curl()
##		c.setopt(c.URL, "http://192.168.2.114/download/name.txt")
#		c.setopt(c.URL, "http://192.168.2.213/http/download/name.txt")
#		f1=open("/scream/download/name1.txt","wb+")
#		c.setopt(c.WRITEDATA,f1)
#		c.perform()
#		c.close()
#		f1.close()
#	except (pycurl.error,IOError):
#		os.remove("/scream/download/name1.txt")
#		return 3
#	f1=open("/scream/download/name1.txt","r")                 
#	filename=f1.readline()
#	print(filename)         
#	f2=open("/scream/download/name.txt","r")
#	lastname=f2.readline()
#	print(lastname)
#	f2.close()
#	f1.close()
#	if filename.find(lastname)==-1:          #对比文件名字
#		f2=open("/scream/download/name.txt","wb+")
#		f2.write(filename)
#		f2.close()
#		os.remove("/scream/download/name1.txt")
#		return 1
#	else:
#		return 0

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
					data = 3	
				if data=='1' or times==0:
					break
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
	
	
i=0
ket_statue=True
key_flag=False	 
GPIO.setmode(GPIO.BCM)
GPIO.setup(22,GPIO.OUT) #喇叭
GPIO.setup(5,GPIO.OUT) #LED
GPIO.setup(17,GPIO.IN) #按键
port0=serial.Serial("/dev/myuart0",baudrate=115200,timeout=0)
port1=serial.Serial("/dev/myuart1",baudrate=115200,timeout=0)
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
q_socket = multiprocessing.Queue()
p_recv = multiprocessing.Process(target=data_recev,args=(port0,port1,port3,q_socket,))
p_sock = multiprocessing.Process(target=sock_server,args=(q_socket,))
p_recv.start()
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
		if (GPIO.input(17)==0 and key_statue==True):
			time.sleep(0.02)
			key_statue=False
			if (GPIO.input(17)==0):
					key_flag=True
					print 'key down'
		elif (GPIO.input(17)==1):
			key_statue=True
		time.sleep(0.1)			
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
#	port1.write("stop")
#	port0.write("stop")