#good tutorial code...
#http://moveonpc.googlecode.com/svn-history/r14/trunk/source/winhid.cpp

#import array
import logging

class sHID(object):
	'''
	Low level driver for ws-28xx
	'''
	logger = logging.getLogger('station.ws-2800.sHID')

	devh = None

	debug = 1

	def Find(self, vendorID, productID, versionNr):
		print "sHID::Find"
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
					self.devh = device.open()

					try:
						self.devh.detachKernelDriver(self.usbInterface.interfaceNumber)
						self.logger.info("Unloaded other driver from interface %d" %
							self.usbInterface.interfaceNumber)
						print "unloaded"
					except usb.USBError, e:
						print "Failed to detach KernelDriver"
						pass
					return device

	def SetTX(self):
		#print "sHID::SetTX"
		buffer = [0]*0x15
		buffer[0] = 0xD1;
		import usb
		try:
			self.devh.controlMsg(usb.TYPE_CLASS + usb.RECIP_INTERFACE,       # requestType
		                                0x0000000,                                  # request
		                                buffer,                                     # buffer
		                                0x0000000,                                  # value
		                                0x0000000,                                  # index
		                                1000)                                       # timeout
			result = 1
		except:
			i=0
			import sys
			sys.stdout.write("sHID::SetTX message: ")
			for entry in buffer:
				sys.stdout.write("%.2x" % (buffer[i]))
				i+=1
			sys.stdout.write(" fail\n")
			#pass
			result = 0
		return result
		#print "sHID::SetTX - end"

	def SetRX(self):
		#print "sHID::SetRX"
		buffer = [0]*0x15
		buffer[0] = 0xD0;
		import usb
		try:
			self.devh.controlMsg(usb.TYPE_CLASS + usb.RECIP_INTERFACE,       # requestType
		                                0x0000000,                                  # request
		                                buffer,                                     # buffer
		                                0x0000000,                                  # value
		                                0x0000000,                                  # index
		                                1000)                                       # timeout
			result = 1
		except:
			i=0
			import sys
			sys.stdout.write("sHID::SetRX message: ")
			for entry in buffer:
				sys.stdout.write("%.2x" % (buffer[i]))
				i+=1
			sys.stdout.write(" fail\n")
			#pass
			result = 0
		return result
		#print "sHID::SetRX - end"

	def GetState(self,StateBuffer):
		#print "sHID::GetState"
		buffer = [0]*0x5
		buffer[0] = 0xDE;

		import usb
		try:
			ret = self.devh.controlMsg(usb.USB_ENDPOINT_IN + usb.TYPE_CLASS + usb.RECIP_INTERFACE,  # requestType
		                                0x0000000,                                  # request
		                                buffer,                                     # buffer
		                                0x0000000,                                  # value
		                                0x0000000,                                  # index
		                                1000)                                       # timeout
			StateBuffer=[0]*0x2
			StateBuffer[0]=buffer[1]
			StateBuffer[1]=buffer[2]
			result = 1
		except:

			if self.debug == 1:
				buffer[1]=0x14
				StateBuffer=[0]*0x2
				StateBuffer[0]=buffer[1]
				StateBuffer[1]=buffer[2]

			i=0
			import sys
			sys.stdout.write("sHID::GetState message: ")
			for entry in buffer:
				sys.stdout.write("%.2x" % (buffer[i]))
				i+=1
			sys.stdout.write(" fail\n")
			result = 0
			#pass
			
			if self.debug == 1:
				return 1;
		
		return result

	def ReadConfigFlash(self,addr,numBytes,data):
		#print "sHID::ReadConfigFlash (partially implemented)"
		if numBytes <= 512:
			while ( numBytes ):
				buffer=[0xcc]*0x0f #0x15
				buffer[0] = 0xDD
				buffer[1] = 10;
				buffer[2] = (addr >>8)  & 0xFF;
				buffer[3] = (addr >>0)  & 0xFF;
				#//fixme
				#if ( !(unsigned __int8)HidD_SetFeature(*((_DWORD *)v5 + 20), &v6, 21) )
				#    return 0;
				try:
					import usb
					self.devh.controlMsg(usb.TYPE_CLASS + usb.RECIP_INTERFACE,       # requestType
					                                0x0000000,                                  # request
					                                buffer,                                     # buffer
					                                0x0000000,                                  # value
					                                0x0000000,                                  # index
					                                1000)                                       # timeout
				except:
					i=0
					import sys
					sys.stdout.write("sHID::ReadConfigFlash message: ")
					for entry in buffer:
						sys.stdout.write("%.2x" % (buffer[i]))
						i+=1
					sys.stdout.write(" fail\n")
					if self.debug != 1:
						return 0;

				buffer=[0]*0x15
				buffer[0] = 0xDC
				buffer[1] = 10;
				#//fixme
				#f ( !(unsigned __int8)HidD_GetFeature(*((_DWORD *)v5 + 20), &v6, 21) )
				# return 0;

				try:
					import usb
					self.devh.controlMsg(usb.USB_ENDPOINT_IN + usb.TYPE_CLASS + usb.RECIP_INTERFACE,  # requestType
					                                0x0000000,                                  # request
					                                buffer,                                     # buffer
					                                0x0000000,                                  # value
					                                0x0000000,                                  # index
					                                1000)                                       # timeout
				except:
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
					#for i, Register in enumerate(buffer)
					for i in xrange(0, numBytes):
						#print "eddi %d %x" %(i,buffer[i+4])
						new_data[i] = buffer[i+4];
					numBytes = 0;
				else:
					for i in xrange(0, 16):
						new_data[i] = buffer[i+4];
					numBytes -= 16;
					addr += 16;
			result = 1;
		else:
			result = 0;

		i=0
		import sys
		sys.stdout.write("sHID::ReadConfigFlash message: ")
		for entry in buffer:
			sys.stdout.write("%.2x" % (buffer[i]))
			i+=1
		sys.stdout.write(" fail\n")

		data[0] = new_data
		return result

	def SetState(self,a1):
		print "sHID::SetState (not implemented yet)"

	def SetFrame(self,a1,a2):
		print "sHID::SetFrame (not implemented yet)"

	def WriteReg(self,regAddr,data):
		#print "sHID::WriteReg"
		buffer = [0]*0x05
		buffer[0] = 0xF0;
		buffer[1] = regAddr & 0x7F;
		buffer[2] = 0x01;
		buffer[3] = data;
		buffer[4] = 0x00;
		try:
			self.devh.controlMsg(usb.TYPE_CLASS + usb.RECIP_INTERFACE,       # requestType
		                                0x0000000,                                  # request
		                                buffer,                                     # buffer
		                                0x0000000,                                  # value
		                                0x0000000,                                  # index
		                                1000)                                       # timeout
			result = 1
		except:
			i=0
			import sys
			sys.stdout.write("sHID::WriteReg message: ")
			for entry in buffer:
				sys.stdout.write("%.2x" % (buffer[i]))
				i+=1
			sys.stdout.write(" fail\n")
			result = 0
			#pass

		#print "sHID::WriteReg - end"
		return result

	def Execute(self,command):
		#print "sHID::Execute"
		buffer = [0]*0x0f #*0x15
		buffer[0] = 0xD9;
		buffer[1] = command;
		try:
			self.devh.controlMsg(usb.TYPE_CLASS + usb.RECIP_INTERFACE,       # requestType
		                                0x0000000,                                  # request
		                                buffer,                                     # buffer
		                                0x0000000,                                  # value
		                                0x0000000,                                  # index
		                                1000)                                       # timeout
			result = 1
		except:
			i=0
			import sys
			sys.stdout.write("sHID::Execute message: ")
			for entry in buffer:
				sys.stdout.write("%.2x" % (buffer[i]))
				i+=1
			sys.stdout.write(" fail\n")
			result = 0
			#pass

			if self.debug == 1:
				return 1;

		#print "sHID::Execute - end"
		return result

	def SetPreamblePattern(self,pattern):
		#print "sHID::Execute"
		buffer = [0]*0x0f #*0x15
		buffer[0] = 0xD8;
		buffer[1] = command;
		try:
			self.devh.controlMsg(usb.TYPE_CLASS + usb.RECIP_INTERFACE,       # requestType
		                                0x0000000,                                  # request
		                                buffer,                                     # buffer
		                                0x0000000,                                  # value
		                                0x0000000,                                  # index
		                                1000)                                       # timeout
			result = 1

		except:
			i=0
			import sys
			sys.stdout.write("sHID::SetPreamblePattern message: ")
			for entry in buffer:
				sys.stdout.write("%.2x" % (buffer[i]))
				i+=1
			sys.stdout.write(" fail\n")
			result = 0
			#pass

			if self.debug == 1:
				return 1;

		#print "sHID::SetPreamblePattern - end"
		return result
