#!/usr/bin/env python
#coding:utf-8
import pycurl
import select
import serial
import bluetooth
import datetime
import multiprocessing
import RPi.GPIO as GPIO
import os
import sys
import time 
import struct


#################蓝牙连接##########################
def blurtooth():
	service_matches = bluetooth.find_service( address = "00:1B:10:F1:FB:D4" )
	while len(service_matches) == 0:
		print "wait connect"
		service_matches = bluetooth.find_service( address = "00:1B:10:F1:FB:D4" )
		time.sleep(1)
	first_match = service_matches[0]
	port = first_match["port"]
	name = first_match["name"]
	host = first_match["host"]
	print "connecting to \"%s\" on %s port:%s" % (name, host, port)
	return port
#########################	
def ble_find(pipe0,pipe1):
	i=0
	while True:
		if i==0:
			service_matches = bluetooth.find_service( address = "00:1B:10:F1:FB:D4" )
			while len(service_matches) == 0:
				service_matches = bluetooth.find_service( address = "00:1B:10:F1:FB:D4" )
				time.sleep(0.5)
			print "find ok"
			i=1
			pipe0.send(1)#扫描到会向数据处理程序发送信号，提示可以进行蓝牙连接
		if i==1:
			#在没有收到信号时
			rlist,wlist,elist=select.select([pipe0,pipe1,],[],[],)
			for fd in rlist:
				if fd==pipe0:
					i=pipe0.recv()
					print "A"
				if fd==pipe1:
					i=pipe1.recv()
					print "B"
#######################################接收传感器数据，数据类型string########################################
def uart_rec_str(port):
	ch=''
	rv_buf="S"
	r_flag=0
	while True:
		ch=port.read()		
		if ch=='#':
			r_flag=0
			return rv_buf			
		if r_flag==1:
			rv_buf+=ch
		if ch=='$':
			r_flag=1
#			rv_buf="$"

###########################接收电机数据，数据类型hex#############################
def uart_rec_int(port):
	i=0
	ch=0
	res=0 
	rv_buf=[]
	rtn_buf="M,"
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

########################通过socket发送蓝牙数据##########################
def bt_send(buf,btfd):
	try:	
		btfd.send(buf)
	except bluetooth.BluetoothError:
		port=blurtooth()
		btfd.connect(("00:1B:10:F1:FB:D4", port))
		

def data_write(buf):
	fds=open("/scream/upload/data.txt","a+")
	fds.write(buf)
	fds.close()
##############################多个串口数据接收处理############################			
def data_recev(port0,port1,lock,pipe0,ble_pipe):       
	flag=0
	ble_connflag=0  
	ble_sendflag=0     
	send_buf0=""
	send_buf1=""
	ble_buf=""
	data_buf=""
	data_buf_20_1=""
	data_buf_20_2=""
	data_buf_20_3=""
	data_buf_choose=0
	start_flag="start"
	stop_flag="stop"
	i=0  
	times=0
	fd0=open("/dev/myuart0","r+")
	fd1=open("/dev/myuart1","r+")
	port1.write(start_flag)
	port0.write(start_flag)
	while True:
		rlist,wlist,elist=select.select([fd0,fd1,pipe0,ble_pipe,],[],[],)
		for fd in rlist:
			if(fd==fd0):
				lock.acquire()
				try:
					send_buf0=uart_rec_int(port0)	
					flag=flag|0x01			
				finally:
					lock.release() 
			if(fd==fd1):
					send_buf1=uart_rec_str(port1)
					if(len(send_buf1.split(','))==10):
						ble_sendflag=1
						flag=flag|0x10
			if(fd==pipe0):
					i=pipe0.recv()
					print i
			if(fd==ble_pipe):
					ble_connflag=ble_pipe.recv()	#接收蓝牙扫描进程的信号，标志位=1
					print "recv ok"				
		if(flag == 0x10):
					flag=0
					time_0=str(datetime.datetime.now())
					data_buf=send_buf0+','+send_buf1+","+time_0+"\r\n"
					data_buf_20_1+=data_buf
					times+=1
					#缓存20组去存储
					if times==20:
						if data_buf_choose==0:
							data_buf_20_2=data_buf_20_1
							data_buf_20_3=""
							data_buf_20_1=""
							data_buf_choose=1
							p=multiprocessing.Process(target=data_write,args=(data_buf_20_2,))
							p.start()
						else:
							data_buf_20_3=data_buf_20_1
							data_buf_20_2=""
							data_buf_20_1=""
							data_buf_choose=0
							p=multiprocessing.Process(target=data_write,args=(data_buf_20_3,))
							p.start()
						times=0					
#					fds.write(data_buf)
		if ble_connflag==1:   #如果标志位=1，建立蓝牙连接
			port=blurtooth()
			sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
			sock.connect(("00:1B:10:F1:FB:D4", port))
			ble_connflag=2
			print "connect ok"
		if(ble_sendflag==1 and ble_connflag==2): #标志位=2，蓝牙连接已建立，可以进行数据收发
			ble_sendflag=0
			ble_buf=send_buf1
			x=ble_buf.split(',')
			ble_data=","+x[1]+","+x[3]+","+x[5]+","+x[7]+","
			ble_buf="start"+ble_data+"e\r\n"
			try:
				sock.send(ble_buf)
			except bluetooth.BluetoothError:
				ble_connflag=0
				print "start find"
				ble_pipe.send(0)
			ble_buf=""
		if(i==1):
			port1.write(stop_flag)
			port0.write(stop_flag)
			fd0.close()
			fd1.close()
			sock.close()
			break
###################################数据上传###################################################				
def upload():
	c = pycurl.Curl()
	c.setopt(c.URL,"http://192.168.2.114/upload/" )
#	c.setopt(c.URL,"http://192.168.2.213/http/upload/" )
	c.setopt(c.HTTPPOST, [
		('fileupload', (
		# upload the contents of this file
		c.FORM_FILE, "/scream/upload/data.txt",
       		 # specify a different file name for the upload
		c.FORM_FILENAME, "data.txt",
		# specify a different content type
		c.FORM_CONTENTTYPE, 'txt/plain',
   		 )),
		])	
	c.perform()
	c.close()
	os.remove("/scream/upload/data.txt")
	GPIO.output(13,1)
	time.sleep(0.5)
	GPIO.output(13,0)

#########################数据下载#####################################################	
def download():
	c = pycurl.Curl()
	c.setopt(c.URL, "http://192.168.2.114/download/data.txt")
#	c.setopt(c.URL, "http://192.168.2.213/http/download/data.txt")
	f=open("/scream/download/data.txt","wb")
	c.setopt(c.WRITEDATA, f)
	c.perform()	
	f.close()
	c.close()

##############获取文件名字，通过名字判断服务器端的数据是否更新#############################
def getname():
	try:
		c = pycurl.Curl()
		c.setopt(c.URL, "http://192.168.2.114/download/name.txt")
#		c.setopt(c.URL, "http://192.168.2.213/http/download/name.txt")
		f1=open("/scream/download/name1.txt","wb+")
		c.setopt(c.WRITEDATA,f1)
		c.perform()
		c.close()
		f1.close()
	except (pycurl.error,IOError):
		os.remove("/scream/download/name1.txt")
		return 3
	f1=open("/scream/download/name1.txt","r")                 
	filename=f1.readline()
	print(filename)         
	f2=open("/scream/download/name.txt","r")
	lastname=f2.readline()
	print(lastname)
	f2.close()
	f1.close()
	if filename.find(lastname)==-1:          #对比文件名字
		f2=open("/scream/download/name.txt","wb+")
		f2.write(filename)
		f2.close()
		os.remove("/scream/download/name1.txt")
		return 1
	else:
		return 0
	
	
#def data_send(port,lock):
#	while True:
#		lock.acquire()
#			try:
##				time_1=str(datetime.datetime.now())
##				send_buf1+=time_1
##				fdm.write(send_buf1)
#				port.write(send_buf)	
#			finally:
#				lock.release()2017/6/16 星期五 上午 11:24:512017/6/16 星期五 上午 11:24:51
#		sleep(0.05)
########################################################################################	
i=0
key_flag=False
start_flag=False
ble_findflag=0
first_times=True			 
GPIO.setmode(GPIO.BOARD)
GPIO.setup(13,GPIO.OUT) #喇叭
GPIO.setup(11,GPIO.OUT) #LED
GPIO.setup(7,GPIO.IN) #按键
port0=serial.Serial("/dev/myuart0",baudrate=115200,timeout=0)
port1=serial.Serial("/dev/myuart1",baudrate=115200,timeout=0)
fd1=open("/scream/upload/data.txt","a+")
fd1.close()
fd2=open("/scream/download/name1.txt","a+")
fd2.close()
fd3=open("/scream/download/name.txt","a+")
fd3.close()
while True:
	filename=getname()
	print(filename)
	if filename!=3:
		break
if(filename==1):  #初始化比较文件名字，不同就下载
	download()
GPIO.output(13,1)
time.sleep(0.5)
GPIO.output(13,0)
lock = multiprocessing.Lock()	#创建锁
uart_pipe=multiprocessing.Pipe()
ble_pipe0=multiprocessing.Pipe()
ble_pipe1=multiprocessing.Pipe()
GPIO.output(11,1)
p4=multiprocessing.Process(target=ble_find,args=(ble_pipe0[0],ble_pipe1[0],))
p4.start()
try:
	while True:
		if (GPIO.input(7)==0):
			time.sleep(0.2)
			if (GPIO.input(7)==0):
				if (key_flag==True):
					key_flag=False
				else:
					key_flag=True
					i=i+1
		if (key_flag==True and start_flag==False):
			p1=multiprocessing.Process(target=data_recev,args=(port0,port1,lock,uart_pipe[0],ble_pipe0[1],))
			GPIO.output(11,0)
			start_flag=True
			p1.start()
			if first_times==False:
				#不是初次启动接收进程，向蓝牙扫描进程发送开始扫描信号
				ble_pipe1[1].send(0)		
		if(key_flag==False and start_flag==True ):
			p3=multiprocessing.Process(target=upload,args=())
			start_flag=False
			first_times=False
			GPIO.output(11,1)
			#发送信号，结束串口接收程序
			uart_pipe[1].send(1)
			p3.start()
except (KeyboardInterrupt,AssertionError):
	GPIO.cleanup(13)
	GPIO.cleanup(11)
	GPIO.cleanup(7)