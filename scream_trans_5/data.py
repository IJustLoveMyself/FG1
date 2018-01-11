#!/usr/env/bin python
#coding:utf-8
import pycurl
import datetime
import RPi.GPIO as GPIO
import os
import sys
import time   

##################################数据上传###########################################	
class DataLoad:
	def upload(self):
		c = pycurl.Curl()
	#	c.setopt(c.URL,"http://192.168.2.114/upload/" )
		c.setopt(c.URL,"http://192.168.2.213/http/upload/" )
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
		GPIO.output(22,1)
		time.sleep(0.5)
		GPIO.output(22,0)

	########################数据下载#####################################################	
	def download(self):
		c = pycurl.Curl()
	#	c.setopt(c.URL, "http://192.168.2.114/download/data.txt")
		c.setopt(c.URL, "http://192.168.2.213/http/download/data.txt")
		f=open("/scream/download/data.txt","wb")
		c.setopt(c.WRITEDATA, f)
		c.perform()	
		f.close()
		c.close()

	#############获取文件名字，通过名字判断服务器端的数据是否更新########################
	def getname(self):
		try:
			c = pycurl.Curl()
	#		c.setopt(c.URL, "http://192.168.2.114/download/name.txt")
			c.setopt(c.URL, "http://192.168.2.213/http/download/name.txt")
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
		
