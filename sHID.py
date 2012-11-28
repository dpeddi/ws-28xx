## This driver is based is based on reverse engineering of HeavyWeather 2800 v 1.54
## All copyright goes to La Crosse Technology (c) 2008

## Python port by Eddi De Pieri <eddi@depieri.net>
## Use this software as your own risk.
## Me and La Crosse Technology is not responsable for any damage using this software

#
#ret = usb_interrupt_read(devh, 0x00000081, buf, 0x000000f, 1000);

#good tutorial code...
#http://moveonpc.googlecode.com/svn-history/r14/trunk/source/winhid.cpp

#import array
import platform
import sys
import logging
import time

usbWait =0.5

class sHID(object):
	'''
	Low level driver for ws-28xx
	'''
	logger = logging.getLogger('station.ws-2800.sHID')

	devh = None

	debug = 0

	def __init__(self):
		self.logger = logging.getLogger('ws28xx.sHID')

	def Find(self, vendorID, productID, versionNr):
		self.logger.debug("")
		try:
			import usb
		except Exception, e:
			self.logger.warning(e)
			return None
		busses = usb.busses()
		for bus in busses:
			for device in bus.devices:
				if device.idVendor == vendorID and device.idProduct == productID:
					self.usbDevice = device
					self.usbConfiguration = device.configurations[0]
					self.usbInterface = self.usbConfiguration.interfaces[0][0]
					self.usbEndpoint = self.usbInterface.endpoints[0]

					self.devh = device.open()
					self.logger.info("iManufacturer   %s" % self.devh.getString(device.iManufacturer,30))
					self.logger.info("iProduct        %s" % self.devh.getString(device.iProduct,30))
					self.logger.info("interfaceNumber %d" % self.usbInterface.interfaceNumber)

					try:
					  self.devh.detachKernelDriver(self.usbInterface.interfaceNumber)
					  self.logger.info("Unloaded other driver from interface %d" %
					      self.usbInterface.interfaceNumber)
					except usb.USBError, e:
					    pass

					self.devh.getDescriptor(0x1, 0, 0x12)
					time.sleep(usbWait)
					self.devh.getDescriptor(0x2, 0, 0x9)
					time.sleep(usbWait)
					self.devh.getDescriptor(0x2, 0, 0x22)
					time.sleep(usbWait)
					

					try:
						if platform.system() is 'Windows':
							#self.devh.setConfiguration(self.usbConfiguration)
							self.devh.setConfiguration(1)
						#self.devh.claimInterface(self.usbInterface)
						self.devh.claimInterface(0)
						#self.devh.setAltInterface(self.usbInterface)
						self.devh.setAltInterface(0)
						#self.devh.reset()
						#time.sleep(3.5)
						time.sleep(0.5)
						
						ret = self.devh.controlMsg(usb.TYPE_CLASS + usb.RECIP_INTERFACE,
									0x000000a, [], 0x0000000, 0x0000000, 1000);
						time.sleep(0.3)
								
						self.devh.getDescriptor(0x22, 0, 0x2a9)

						time.sleep(usbWait)

						return device

						#push wv5devices device

					except:
						#push wv5devices null 
						pass
					
					#the idea is to count wv5device to add data to config by allowing multiple instances of driver
					#new config struct: 
					#Transceiver_50
					#Transceiver_ad
					
					
					#while True:
					#	try:
					#		ret = self.devh.interruptRead(usb.ENDPOINT_IN + 1, 0xf, int(15 * 1000))
					#		#print ret
					#	except:
					#		break
					#	break

		return None

	def SetTX(self):
		import usb
		buffer = [0]*0x15
		buffer[0] = 0xd1;
		try:
			self.devh.controlMsg(usb.TYPE_CLASS + usb.RECIP_INTERFACE,       # requestType
		                                0x0000009,                                  # request
		                                buffer,                                     # buffer
		                                0x00003d1,                                  # value
		                                0x0000000,                                  # index
		                                1000)                                       # timeout
			result = 1
		except:
			result = 0

		i=0
		strbuf = ""
		for entry in buffer:
			strbuf += str("%.2x" % (buffer[i]))
			i+=1
		self.logger.debug(">%s" % strbuf)
		return result

	def SetRX(self):
		import usb
		buffer = [0]*0x15
		buffer[0] = 0xD0;
		try:
			self.devh.controlMsg(usb.TYPE_CLASS + usb.RECIP_INTERFACE,       # requestType
		                                0x0000009,                                  # request
		                                buffer,                                     # buffer
		                                0x00003d0,                                  # value
		                                0x0000000,                                  # index
		                                1000)                                       # timeout
			result = 1
		except:
			result = 0

		i=0
		strbuf = ""
		for entry in buffer:
			strbuf += str("%.2x" % (buffer[i]))
			i+=1
		self.logger.debug(">%s" % strbuf)
		return result

	def GetState(self,StateBuffer):
		import usb
		try:
			buffer = self.devh.controlMsg(requestType=usb.TYPE_CLASS | usb.RECIP_INTERFACE | usb.ENDPOINT_IN,
										  request=usb.REQ_CLEAR_FEATURE,
										  value=0x00003de,
										  index=0x0000000,
										  buffer=0x0a,
										  timeout=1000)
			StateBuffer[0]=[0]*0x2
			StateBuffer[0][0]=buffer[1]
			StateBuffer[0][1]=buffer[2]
			
			result = 1
		except:
			result = 0
			if self.debug == 1:
				buffer[1]=0x14
				StateBuffer[0]=[0]*0x2
				StateBuffer[0][0]=buffer[1]
				StateBuffer[0][1]=buffer[2]
				result =1

		i=0
		strbuf = ""
		for entry in buffer:
			strbuf += str("%.2x" % (buffer[i]))
			i+=1
		self.logger.debug("<%s" % strbuf)

		return result

	def ReadConfigFlash(self,addr,numBytes,data):
		self.logger.debug("")
		import usb
		if numBytes <= 512:
			while ( numBytes ):
				buffer=[0xcc]*0x0f #0x15
				buffer[0] = 0xdd
				buffer[1] = 0x0a
				buffer[2] = (addr >>8)  & 0xFF;
				buffer[3] = (addr >>0)  & 0xFF;

				try:
					ret = self.devh.controlMsg(usb.TYPE_CLASS + usb.RECIP_INTERFACE,       # requestType
					                                0x0000009,                                  # request
					                                buffer,                                     # buffer
					                                0x00003dd,                                  # value
					                                0x0000000,                                  # index
					                                1000)                                       # timeout
					result = 1
				except:
					result = 0

				i=0
				strbuf = ""
				for entry in buffer:
					strbuf += str("%.2x" % (buffer[i]))
					i+=1
				self.logger.debug(">%s" % strbuf)


				try:
					buffer = self.devh.controlMsg(requestType=usb.TYPE_CLASS | usb.RECIP_INTERFACE | usb.ENDPOINT_IN,
											   request=usb.REQ_CLEAR_FEATURE,
											   value=0x00003dc,
											   index=0x0000000,
											   buffer=0x15,
											   timeout=1000)
					result = 1
				except:
					result = 0
					if addr == 0x1F5 and self.debug == 1: #//fixme #debugging... without device
						print "sHID::ReadConfigFlash -emulated 0x1F5"
						buffer=[0xdc,0x0a,0x01,0xf5,0x00,0x01,0x78,0xa0,0x01,0x01,0x0c,0x0a,0x0a,0x00,0x41,0xff,0xff,0xff,0xff,0xff,0x00]

					if addr == 0x1F9 and self.debug == 1: #//fixme #debugging... without device
						print "sHID::ReadConfigFlash -emulated 0x1F9"
						buffer=[0xdc,0x0a,0x01,0xf9,0x01,0x01,0x0c,0x0a,0x0a,0x00,0x41,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0x00]
					if self.debug != 1:
						return 0;
						
				new_data=[0]*0x15
				if ( numBytes < 16 ):
					for i in xrange(0, numBytes):
						new_data[i] = buffer[i+4];
					numBytes = 0;
				else:
					for i in xrange(0, 16):
						new_data[i] = buffer[i+4];
					numBytes -= 16;
					addr += 16;

				i=0
				strbuf = ""
				for entry in buffer:
					strbuf += str("%.2x" % (buffer[i]))
					i+=1
				self.logger.debug("<%s" % strbuf)

			result = 1;
		else:
			result = 0;

		data[0] = new_data
		return result

	def SetState(self,state):
		import usb
		buffer = [0]*0x15
		buffer[0] = 0xd7;
		buffer[1] = state;
		try:
			self.devh.controlMsg(usb.TYPE_CLASS + usb.RECIP_INTERFACE,       # requestType
		                                0x0000009,                                  # request
		                                buffer,                                     # buffer
		                                0x00003d7,                                  # value
		                                0x0000000,                                  # index
		                                1000)                                       # timeout
			result = 1
		except:
			result = 0

		i=0
		strbuf = ""
		for entry in buffer:
			strbuf += str("%.2x" % (buffer[i]))
			i+=1
		self.logger.debug(">%s" % strbuf)
		return result


	def SetFrame(self,data,numBytes):
		import usb
#    00000000: d5 00 09 f0 f0 03 00 32 00 3f ff ff 00 00 00 00
#    00000000: d5 00 0c 00 32 c0 00 8f 45 25 15 91 31 20 01 00
#    00000000: d5 00 09 00 32 00 06 c1 00 3f ff ff 00 00 00 00
#    00000000: d5 00 09 00 32 01 06 c1 00 3f ff ff 00 00 00 00
#    00000000: d5 00 0c 00 32 c0 06 c1 47 25 15 91 31 20 01 00
#    00000000: d5 00 09 00 32 00 06 c1 00 30 01 a0 00 00 00 00
#    00000000: d5 00 09 00 32 02 06 c1 00 30 01 a0 00 00 00 00
#    00000000: d5 00 30 00 32 40 64 33 53 04 00 00 00 00 00 00
#    00000000: d5 00 09 00 32 00 06 ab 00 30 01 a0 00 00 00 00
#    00000000: d5 00 09 00 32 00 04 d0 00 30 01 a0 00 00 00 00
#    00000000: d5 00 09 00 32 02 04 d0 00 30 01 a0 00 00 00 00
#    00000000: d5 00 30 00 32 40 64 32 53 04 00 00 00 00 00 00
#    00000000: d5 00 09 00 32 00 04 cf 00 30 01 a0 00 00 00 00

		buffer = [0]*0x111
		buffer[0] = 0xd5;
		buffer[1] = numBytes >> 8;
		buffer[2] = numBytes;
		for i in xrange(0, numBytes):
			buffer[i+3] = data[i]

		try:
			self.devh.controlMsg(usb.TYPE_CLASS + usb.RECIP_INTERFACE,       # requestType
		                                0x0000009,                                  # request
		                                buffer,                                     # buffer
		                                0x00003d5,                                  # value
		                                0x0000000,                                  # index
		                                1000)                                       # timeout
			result = 1
		except:
			result = 0

		i=0
		strbuf = ""
		for entry in buffer:
			strbuf += str("%.2x" % (buffer[i]))
			i+=1
		self.logger.debug(">%s" % strbuf)
		return result

	def GetFrame(self,data,numBytes):
		import usb
		try:
			buffer = self.devh.controlMsg(requestType=usb.TYPE_CLASS | usb.RECIP_INTERFACE | usb.ENDPOINT_IN,
										  request=usb.REQ_CLEAR_FEATURE,
										  value=0x00003d6,
										  index=0x0000000,
										  buffer=0x111,
										  timeout=1000)
			result = 1
		except:
			result = 0

		new_data=[0]*0x131
		new_numBytes=(buffer[1] << 8 | buffer[2])& 0x1ff;
		for i in xrange(0, new_numBytes):
			new_data[i] = buffer[i+3];

		i=0
		strbuf = ""
		for entry in buffer:
			strbuf += str("%.2x" % (buffer[i]))
			i+=1
		self.logger.debug("<%s" % strbuf)

		data[0] = new_data
		numBytes[0] = new_numBytes
		return result


	def WriteReg(self,regAddr,data):
		import usb
		buffer = [0]*0x05
		buffer[0] = 0xf0;
		buffer[1] = regAddr & 0x7F;
		buffer[2] = 0x01;
		buffer[3] = data;
		buffer[4] = 0x00;
		try:
			self.devh.controlMsg(usb.TYPE_CLASS + usb.RECIP_INTERFACE,       # requestType
		                                0x0000009,                                  # request
		                                buffer,                                     # buffer
		                                0x00003f0,                                  # value
		                                0x0000000,                                  # index
		                                1000)                                       # timeout
			result = 1
		except:
			result = 0

		i=0
		strbuf = ""
		for entry in buffer:
			strbuf += str("%.2x" % (buffer[i]))
			i+=1
		self.logger.debug(">%s" % strbuf)
		return result

	def Execute(self,command):
		import usb
		buffer = [0]*0x0f #*0x15
		buffer[0] = 0xd9;
		buffer[1] = command;

		try:
			self.devh.controlMsg(usb.TYPE_CLASS + usb.RECIP_INTERFACE,       # requestType
		                                0x0000009,                                  # request
		                                buffer,                                     # buffer
		                                0x00003d9,                                  # value
		                                0x0000000,                                  # index
		                                1000)                                       # timeout
			result = 1
		except:
			result = 0

		i=0
		strbuf = ""
		for entry in buffer:
			strbuf += str("%.2x" % (buffer[i]))
			i+=1
		self.logger.debug(">%s" % strbuf)
		return result

	def SetPreamblePattern(self,pattern):
		import usb
		buffer = [0]*0x15
		buffer[0] = 0xd8;
		buffer[1] = pattern
		try:
			self.devh.controlMsg(usb.TYPE_CLASS + usb.RECIP_INTERFACE,       # requestType
		                                0x0000009,                                  # request
		                                buffer,                                     # buffer
		                                0x00003d8,                                  # value
		                                0x0000000,                                  # index
		                                1000)                                       # timeout
			result = 1

		except:
			result = 0

		i=0
		strbuf = ""
		for entry in buffer:
			strbuf += str("%.2x" % (buffer[i]))
			i+=1
		self.logger.debug(">%s" % strbuf)
		return result
