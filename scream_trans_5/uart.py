#!/usr/bin/env python
#coding:utf-8
import pycurl
import select
import serial
import datetime
import multiprocessing
import RPi.GPIO as GPIO
import os
import sys
import time 
import struct
import socket  


class Uart_data:
	def uart_sensor_data(self,port):
		rv_buf=""
		ch=''
		flag=0
		i=0
		while True:
			ch=port.read()
			if flag==2:
				rv_buf+=ch
				i=i+1			
			if flag==1 and ch == chr(0x53):
				flag=2
				rv_buf+=ch
				i=i+1
			if flag ==1 and ch!=chr(0x53):
				rv_buf=''
				i=0
				flag=0		
			if flag==0 and ch == chr(0x55):
				rv_buf+=ch
				flag=1
				i=i+1	
			if i==11:
				return rv_buf				
	def uart_rec_str(self,port):		
		rv_buf=""
		ch=''
		while True:
			ch=port.read()
			rv_buf+=ch
			if ch=='e':
				break
		return rv_buf	
###########################接收电机数据，数据类型hex#############################
	def uart_rec_int(self,port):
		i=0
		ch=0
		res=0
		rtn_buf='' 
		rv_buf=[]
		r_flag=0
		while True:
			res=port.read()
#			print 'res: ',res,', type: ',type(res),', len: ',len(res)
			if res=='#':
				rv_buf.append(res)
#				print 'rv_buf: ',rv_buf
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
#				res=int(res,16)
				rv_buf.append(int(res[0]))   #以追加额方式存放在list中
				i=i+1
			if res=='$':
				r_flag=1
				rv_buf.append(res)
				i=i+1
#				rv_buf="$"
###############################################
	def data_write(self,buf):
		fds=open("/scream/upload/data.txt","a+")
		fds.write(buf)
		fds.close()
##############################多个串口数据接收处理############################			
	def data_recev(self,port0,port1,port3,q_socket,q_sensor):       
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
		port1.write(start_flag)
		port0.write(start_flag)
		while True:
			rlist,wlist,elist=select.select([fd0,fd1,fd3,],[],[],)
			for fd in rlist:
				if(fd==fd3):
					send_buf3=''
					send_buf3=self.uart_rec_int(port3)	
					flag=flag|0x0001			
				if(fd==fd1):
					send_buf1=""
					send_buf1=self.uart_rec_str(port1)
					if send_buf1[0]=="s" :
						send_buf1=send_buf1[2:-1]
						flag=flag|0x0010
						sendflag=sendflag|0x01    
				if(fd==fd0):
					send_buf0=""
					send_buf0=self.uart_rec_str(port0)
					if send_buf0[0]=="s":
						send_buf0=send_buf0[2:-1]
						flag=flag|0x0100
						sendflag=sendflag|0x10  		
#			if(flag == 0x0111):
#						flag=0
#						time_0=str(datetime.datetime.now())
#						save_buf0=send_buf0.split("$")
#						save_buf1=send_buf1.split("$")
#						data_buf="S"+save_buf0[0]+save_buf1[0]+",P,"+save_buf0[1]+","+save_buf1[1]+",E,"+save_buf0[2]+save_buf1[2]
#						data_buf_20_1=data_buf_20_1+data_buf+send_buf3+"#"+time_0+"\r\n"
#						times+=1
#						#缓存20组去存储
#						if times==20:
#							if data_buf_choose==0:
#								data_buf_20_2=data_buf_20_1
#								data_buf_20_3=""
#								data_buf_20_1=""
#								data_buf_choose=1
#								p=multiprocessing.Process(target=self.data_write,args=(data_buf_20_2,))
#								p.start()
#							else:
#								data_buf_20_3=data_buf_20_1
#								data_buf_20_2=""
#								data_buf_20_1=""
#								data_buf_choose=0
#								p=multiprocessing.Process(target=self.data_write,args=(data_buf_20_3,))
#								p.start()
#							times=0		
#			
			print 'sendflag',sendflag		
			if(sendflag==0x11):
				sendflag = 0
				save_buf0=send_buf0.split("$")
				save_buf1=send_buf1.split("$")
				sock_buf="S"+save_buf0[0]+save_buf1[0]+",P,"+save_buf0[1]+","+save_buf1[1]+",E,"+save_buf0[2]+save_buf1[2]+"e\r\n"
	#			sock_buf="S"+save_buf0[0]+save_buf1[0]+',M,'+send_buf3+','+"e\r\n"
				if q_socket.empty() == True:
					q_socket.put(sock_buf)
				if not q_sensor.empty():
					back_sensor = q_sensor.get()
					back_H = (back_sensor&0xff00)>>8
					back_L = (back_sensor&0xff)
					lis0 = save_buf0[0].split(',')
					lis1 = save_buf1[0].split(',')
					left_leg_H = (int(lis0[1])&0xff00)>>8
					left_leg_L = (int(lis0[1])&0xff)
					left_thigh_H = (int(lis0[3])&0xff00)>>8
					left_thigh_L = (int(lis0[3])&0xff)
					right_leg_H = (int(lis1[1])&0xff00)>>8
					right_leg_L = (int(lis1[1])&0xff)
					right_thigh_H = (int(lis1[3])&0xff00)>>8
					right_thigh_L = (int(lis1[3])&0xff)
					sensor_list = ['start',chr(left_leg_H),chr(left_leg_L),chr(left_thigh_H),chr(left_thigh_L),
												chr(right_leg_H),chr(right_leg_L),chr(right_thigh_H),chr(right_thigh_L),
												chr(back_H),chr(back_L),'#']
					print sensor_list
					sensor_buf = ''.join(sensor_list)
					port3.write(sensor_buf)
	#				sensor_buf = start_flag+chr(left_leg_H)+chr(left_leg_L)+chr(left_thigh_H)+chr(left_thigh_L)+\
	#										 chr(right_leg_H)+chr(right_leg_L)+chr(right_thigh_H)+chr(right_thigh_L)+\
	#										 chr(back_H)+chr(back_L)+'#'				
			time.sleep(0.01)	
	#		if(i==1):
	#			port1.write(stop_flag)
	#			port0.write(stop_flag)
	#			fd0.close()
	#			fd1.close()
	#			fd3.close()
	#			sock.close()
	#			break
	###############获取背部传感器数据的值#################################
	def get_sensor(self,port):
		error = 0
		try:
			time.sleep(1)
			data_sum = 0
			port.flushInput()
			send_buf=''
			send_buf=self.uart_sensor_data(port)
			for i in range(10):
				data_sum = data_sum+ord(send_buf[i])
			if data_sum&0xff == ord(send_buf[10]):
				sensor = int((ord(send_buf[3])<<8|ord(send_buf[2]))/32768.0*180)
				port.close()
				return sensor
		except IndexError, error:		
			print error
			return 0
	##########################获得正确的值后将值放入队列中################
	def sensor(self,port,q_sensor):
		sensor_data = 0
		while(sensor_data == 0):
			sensor_data = self.get_sensor(port)
		if q_sensor.empty() ==True:			
			q_sensor.put(sensor_data)
			print 'ok'
			time.sleep(5)
