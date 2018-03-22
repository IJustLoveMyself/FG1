#!/usr/bin/env python
#***********coding:utf-8********
from bluepy import btle
import subprocess
import time
class Ble_test:
	def __init__(self):
		self.conn = btle.Peripheral()
		self.scanner = btle.Scanner()
	def ble_search(self):
		lis = []
		devices = []
		try:
			devices = self.scanner.scan(2)
		except btle.BTLEException,error:
			print error
			sub=subprocess.Popen("sudo hciconfig hci0 down",shell=True)
			time.sleep(2)
			sub=subprocess.Popen("sudo hciconfig hci0 up",shell=True)
		if len(devices)!=0:
			for dev in devices:
				try:
					value = dev.getScanData()
					if len(value)!=0 :
						print value
						if len(value[0]) == 3 and str(value[0][2]) == "SCREAM" :
							print 1
							if len(lis) == 0:
								lis.append(str(value[0][2]))
								lis.append(str(dev.addr))
								lis.append(dev.rssi)
							else :
								if dev.rssi > lis[2]:
									lis[1] = str(dev.addr)
				except:
					print "error at ble_search"
		if len(lis)	== 3:
			return lis
		else:
			 return None
	def ble_connect(self,addr):
			try:
				self.conn.connect(addr,"random")
			except btle.BTLEException,error:
				print "error at ble_connect"
				self.conn.disconnect()
				print error
				return 0
			else:
				self.conn.writeCharacteristic(0x000f,str(bytearray([1, 0])),withResponse=True)
				return 1
	def ble_rec(self,addrbuf):
		sum_data = 0
		re = self.conn.waitForNotifications(10)
		if re == True:
			data = self.conn.readCharacteristic(0x000e)
			print addrbuf
			self.conn.writeCharacteristic(0x0011,addrbuf,withResponse=True)
			if len(data) == 12:
				if ord(data[0]) == 0x9A and ord(data[1]) == 0x9B:
					for i in range(0,11):
						sum_data = sum_data + ord(data[i])
					sum_data = sum_data&0xff
					if sum_data == ord(data[11]):
						print 'data=',ord(data[10])	
						return data[10]								
		return None
	def addr_to_chr(self,buf):
		addr = ''
		lis = buf.split(":")
		addr = lis[5]+lis[4]+lis[3]+lis[2]+lis[1]+lis[0]
		print addr
#		for data in lis:
#			addr = addr+chr(int(data,16))
		return addr
	def ble_main(self,q_ble):
		lis = ['key',0]
		while True:
			res = self.ble_search()
			if res != None:
				print "search ok"
				break
			else:
				print "search ble ing"
		while True:
			try:
				conn_ok = self.ble_connect(res[1])
				if conn_ok == 1:
					print "connect ok"
					addr = self.addr_to_chr(res[1])
					while True:
						ctr_data = self.ble_rec(addr)
						if ctr_data != None:
							lis[1] = ctr_data
							if q_ble.empty() == True:
								q_ble.put(lis)
								print lis
			except (btle.BTLEException,IOError),error:
				print error
if __name__ == '__main__':
	tests = Ble_test()
	res = tests.ble_search()
	if res != None:
		while True:
			try:
				conn_ok = tests.ble_connect(res[1])
				if conn_ok == 1:
					print "connect ok"
					print res[1]
					addr = tests.addr_to_chr(res[1])
					while True:
						data = tests.ble_rec(addr)
						print data
			except (btle.BTLEException,IOError),error:
				print error
				conn_ok=0
