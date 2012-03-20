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
					self.usbEndpoint = self.usbInterface.endpoints[0]

					self.devh = device.open()
					print "iManufacturer   %s" % self.devh.getString(device.iManufacturer,30)
					print "iProduct        %s" % self.devh.getString(device.iProduct,30)
					print "interfaceNumber %d" % self.usbInterface.interfaceNumber

					try:
					  #self.devh.detachKernelDriver(self.usbInterface.interfaceNumber)
					  self.logger.info("Unloaded other driver from interface %d" %
					      self.usbInterface.interfaceNumber)
					except usb.USBError, e:
					  pass

					#self.devh.setAltInterface(0)
					
					self.devh.getDescriptor(0x1, 0, 0x12)
					time.sleep(usbWait)
					self.devh.getDescriptor(0x2, 0, 0x9)
					time.sleep(usbWait)
					self.devh.getDescriptor(0x2, 0, 0x22)
					time.sleep(usbWait)
					if platform.system() is 'Windows':
						#self.devh.setConfiguration(self.usbConfiguration)
						self.devh.setConfiguration(1)
					#self.devh.claimInterface(self.usbInterface)
					self.devh.claimInterface(0)
					#self.devh.setAltInterface(self.usbInterface)
					self.devh.setAltInterface(0)
					#self.devh.reset()
					time.sleep(3.5)
					
					ret = self.devh.controlMsg(usb.TYPE_CLASS + usb.RECIP_INTERFACE,
								0x000000a, [], 0x0000000, 0x0000000, 1000);
					time.sleep(0.3)
								
					self.devh.getDescriptor(0x22, 0, 0x2a9)
					
					while True:
						try:
							ret = self.devh.interruptRead(usb.ENDPOINT_IN + 1, 0xf,
                                           int(15 * 1000))
							print ret
						except:
							break
						break

					time.sleep(usbWait)

					#try:
					#	self.devh.claimInterface(0)
					#	print "claimed"
					#except:
					#	if not hasattr(self.devh, 'detachKernelDriver'):
					#		raise RuntimeError(
					#			"Please upgrade pyusb (or python-usb) to 0.4 or higher")
					#try:
					#<-----					self.devh.setAltInterface(0)
					#except usb.USBError:
					#<-----					raise "failed setAlt"
					#try:
					#	self.devh.detachKernelDriver(self.usbInterface.interfaceNumber)
					#<-----					self.logger.info("Unloaded other driver from interface %d" %
					#<-----										self.usbInterface.interfaceNumber)
					#	print "unloaded"
					#except usb.USBError, e:
					#					raise "Failed to detach KernelDriver"
					#					pass
					time.sleep(usbWait)

					return device
		return None

	def SetTX(self):
    		print "sHID::SetTX"
		buffer = [0]*0x15
		buffer[0] = 0xd1;
		import usb
		try:
			#int usb_control_msg(usb_dev_handle *dev, int requesttype, int request, int value, int index, char *bytes, int size, int timeout);
			#ret = usb_control_msg(devh, USB_TYPE_CLASS + USB_RECIP_INTERFACE, 0x0000009, 0x00003d1, 0x0000000, buf, 0x0000015, 1000);
			self.devh.controlMsg(usb.TYPE_CLASS + usb.RECIP_INTERFACE,       # requestType
		                                0x0000009,                                  # request
		                                buffer,                                     # buffer
		                                0x00003d1,                                  # value
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
			if result == 1:
				sys.stdout.write(" ok\n")
			else:
				sys.stdout.write(" fail\n")
			#pass
			result = 0
		return result
		#print "sHID::SetTX - end"

	def SetRX(self):
		print "sHID::SetRX"
		buffer = [0]*0x15
		buffer[0] = 0xD0;
		import usb
		try:
			#int usb_control_msg(usb_dev_handle *dev, int requesttype, int request, int value, int index, char *bytes, int size, int timeout);
			#ret = usb_control_msg(USB_TYPE_CLASS + USB_RECIP_INTERFACE, 0x0000009, 0x00003d0, 0x0000000, buf, 0x0000015, 1000)
			self.devh.controlMsg(usb.TYPE_CLASS + usb.RECIP_INTERFACE,       # requestType
		                                0x0000009,                                  # request
		                                buffer,                                     # buffer
		                                0x00003d0,                                  # value
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
			if result == 1:
				sys.stdout.write(" ok\n")
			else:
				sys.stdout.write(" fail\n")
			#pass
			result = 0
		return result
		#print "sHID::SetRX - end"

	def GetState(self,StateBuffer):
		print "sHID::GetState"
		#buffer = [0]*0x0a
		#buffer[0] = 0xde;

		import usb
		try:
			#int usb_control_msg(usb_dev_handle *dev, int requesttype, int request, int value, int index, char *bytes, int size, int timeout);
			#ret = usb_control_msg(devh, USB_TYPE_CLASS + USB_RECIP_INTERFACE + USB_ENDPOINT_IN, 0x0000001, 0x00003de, 0x0000000, buf, 0x000000a, 1000);
			#ret = self.devh.controlMsg(usb.TYPE_CLASS + usb.RECIP_INTERFACE + usb.ENDPOINT_IN,  # requestType
		    #                            0x0000001,                                  # request
		    #                            buffer,                                     # buffer
		    #                            0x00003de,                                  # value
		    #                            0x0000000,                                  # index
		    #                            1000)                                       # timeout
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
			if self.debug == 1:
				buffer[1]=0x14
				StateBuffer[0]=[0]*0x2
				StateBuffer[0][0]=buffer[1]
				StateBuffer[0][1]=buffer[2]

			i=0
			import sys
			sys.stdout.write("sHID::GetState message: ")
			for entry in buffer:
				sys.stdout.write("%.2x" % (buffer[i]))
				i+=1
			if result == 1:
				sys.stdout.write(" ok\n")
			else:
				sys.stdout.write(" fail\n")
			result = 0
			#pass
			
			if self.debug == 1:
				return 1;
		
		return result

	def ReadConfigFlash(self,addr,numBytes,data):
		print "sHID::ReadConfigFlash"
		import usb
		if numBytes <= 512:
			while ( numBytes ):
				buffer=[0xcc]*0x0f #0x15
				buffer[0] = 0xdd
				buffer[1] = 0x0a
				buffer[2] = (addr >>8)  & 0xFF;
				buffer[3] = (addr >>0)  & 0xFF;

				i=0
				import sys
				sys.stdout.write("sHID::ReadConfigFlash message: ")
				for entry in buffer:
					sys.stdout.write("%.2x" % (buffer[i]))
					i+=1
				print

				#//fixme
				#if ( !(unsigned __int8)HidD_SetFeature(*((_DWORD *)v5 + 20), &v6, 21) )
				#    return 0;
				try:
						#int usb_control_msg(usb_dev_handle *dev, int requesttype, int request, int value, int index, char *bytes, int size, int timeout);
					#ret = usb_control_msg(devh, USB_TYPE_CLASS + USB_RECIP_INTERFACE, 0x0000009, 0x00003dd, 0x0000000, buf, 0x000000f, 1000);
					ret = self.devh.controlMsg(usb.TYPE_CLASS + usb.RECIP_INTERFACE,       # requestType
					                                0x0000009,                                  # request
					                                buffer,                                     # buffer
					                                0x00003dd,                                  # value
					                                0x0000000,                                  # index
					                                1000)                                       # timeout
					print "retdd:",ret 
					result = 1
				except:
					i=0
					import sys
					sys.stdout.write("sHID::ReadConfigFlash message1: ")
					for entry in buffer:
						sys.stdout.write("%.2x" % (buffer[i]))
						i+=1
					sys.stdout.write(" fail\n")
					#if self.debug != 1:
					#	return 0;

				#buffer=[0]*0x15
				#buffer[0] = 0xdc
				#buffer[1] = 0x0a;
				#//fixme
				#f ( !(unsigned __int8)HidD_GetFeature(*((_DWORD *)v5 + 20), &v6, 21) )
				# return 0;

				time.sleep(0.5)

				try:
					#int usb_control_msg(usb_dev_handle *dev, int requesttype, int request, int value, int index, char *bytes, int size, int timeout);
					#ret = usb_control_msg(devh, USB_TYPE_CLASS + USB_RECIP_INTERFACE + USB_ENDPOINT_IN, 0x0000001, 0x00003dc, 0x0000000, buf, 0x0000015, 1000);
					buffer = self.devh.controlMsg(requestType=usb.TYPE_CLASS | usb.RECIP_INTERFACE | usb.ENDPOINT_IN,
											   request=usb.REQ_CLEAR_FEATURE,
											   value=0x00003dc,
											   index=0x0000000,
											   buffer=0x15,
											   timeout=1000)

					print "retdc:",buffer 
					result = 1
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
		sys.stdout.write("sHID::ReadConfigFlash message2: ")
		for entry in new_data:
			sys.stdout.write("%.2x" % (new_data[i]))
			i+=1
		if result == 1:
			sys.stdout.write(" ok\n")
		else:
			sys.stdout.write(" fail\n")

		data[0] = new_data
		return result

	def SetState(self,a1):
		print "sHID::SetState"
		buffer = [0]*0x15
		buffer[0] = 0xd7;
		try:
			import usb
			#int usb_control_msg(usb_dev_handle *dev, int requesttype, int request, int value, int index, char *bytes, int size, int timeout);
			#ret = usb_control_msg(devh, USB_TYPE_CLASS + USB_RECIP_INTERFACE, 0x0000009, 0x00003d7, 0x0000000, buf, 0x0000015, 1000);
			self.devh.controlMsg(usb.TYPE_CLASS + usb.RECIP_INTERFACE,       # requestType
		                                0x0000009,                                  # request
		                                buffer,                                     # buffer
		                                0x00003d7,                                  # value
		                                0x0000000,                                  # index
		                                1000)                                       # timeout
			result = 1
		except:
			i=0
			import sys
			sys.stdout.write("sHID::SetState message: ")
			for entry in buffer:
				sys.stdout.write("%.2x" % (buffer[i]))
				i+=1
			sys.stdout.write(" fail\n")
			result = 0
			#pass
			if self.debug == 1:
				return 1;

		#print "sHID::SetState - end"
		return result


	def SetFrame(self,data,numBytes):
		print "sHID::SetFrame (not fully implemented yet)"
		v4 = 0xd5;
		#  v5 = (unsigned __int8)a3 >> 8;
		# v6 = a3;
		#  for ( i = 0; i < a3; ++i )
		#    v7[i] = *(_BYTE *)a2++;

		#  for ( i = a3 + 3; i < 0x131; ++i )
		#    *(&v4 + i) = 0;
		#  if ( (unsigned __int8)HidD_SetFeature(*(_DWORD *)(this + 80), &v4, 273) )

		buffer = [0]*0x111
		buffer[0] = 0xd5;
		buffer[1] = numBytes >> 8;
		buffer[2] = numBytes;

		try:
			#ret = usb_control_msg(devh, USB_TYPE_CLASS + USB_RECIP_INTERFACE, 0x0000009, 0x00003d5, 0x0000000, buf, 0x0000111, 1000);
			self.devh.controlMsg(usb.TYPE_CLASS + usb.RECIP_INTERFACE,       # requestType
		                                0x0000009,                                  # request
		                                buffer,                                     # buffer
		                                0x00003d5,                                  # value
		                                0x0000000,                                  # index
		                                1000)                                       # timeout
			result = 1
		except:
			i=0
			import sys
			sys.stdout.write("sHID::SetFrame message: ")
			for entry in buffer:
				sys.stdout.write("%.2x" % (buffer[i]))
				i+=1
			sys.stdout.write(" fail\n")
			result = 0
			#pass
			if self.debug == 1:
				return 1;

		#print "sHID::SetFrame - end"
		return result

	def GetFrame(self,data,numBytes):
		print "sHID::GetFrame (not fully implemented yet)"

		buffer = [0]*0x111
		buffer[0] = 0xd6;

		try:
			#ret = usb_control_msg(devh, USB_TYPE_CLASS + USB_RECIP_INTERFACE + USB_ENDPOINT_IN, 0x0000001, 0x00003d6, 0x0000000, buf, 0x0000111, 1000);r
			self.devh.controlMsg(usb.TYPE_CLASS + usb.RECIP_INTERFACE + usb.ENDPOINT_IN,       # requestType
		                                0x0000001,                                  # request
		                                buffer,                                     # buffer
		                                0x00003d6,                                  # value
		                                0x0000000,                                  # index
		                                1000)                                       # timeout
			result = 1
		except:
			i=0
			import sys
			sys.stdout.write("sHID::GetFrame message: ")
			for entry in buffer:
				sys.stdout.write("%.2x" % (buffer[i]))
				i+=1
			sys.stdout.write(" fail\n")
			result = 0
			#pass

			#*(_DWORD *)a3 = (v6 | (unsigned __int16)(v5 << 8)) & 0x1FF;
			#    for ( i = 0; i < *(_DWORD *)a3; ++i )
			#      *(_BYTE *)a2++ = v7[i];
		new_data=[0]*0x15
		for i in xrange(0, ((buffer[1] << 8 | buffer[2])& 0x1ff) ):
			new_data[i] = buffer[i+1];

		#print "sHID::GetFrame - end"
		return result


	def WriteReg(self,regAddr,data):
		print "sHID::WriteReg"
		buffer = [0]*0x05
		buffer[0] = 0xf0;
		buffer[1] = regAddr & 0x7F;
		buffer[2] = 0x01;
		buffer[3] = data;
		buffer[4] = 0x00;
		try:
			import usb
			#int usb_control_msg(usb_dev_handle *dev, int requesttype, int request, int value, int index, char *bytes, int size, int timeout);
			#ret = usb_control_msg(devh, USB_TYPE_CLASS + USB_RECIP_INTERFACE, 0x0000009, 0x00003f0, 0x0000000, buf, 0x0000005, 1000);
			self.devh.controlMsg(usb.TYPE_CLASS + usb.RECIP_INTERFACE,       # requestType
		                                0x0000009,                                  # request
		                                buffer,                                     # buffer
		                                0x00003f0,                                  # value
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
			if self.debug == 1:
				return 1;
		#print "sHID::WriteReg - end"
		return result

	def Execute(self,command):
		print "sHID::Execute"
		buffer = [0]*0x0f #*0x15
		buffer[0] = 0xd9;
		buffer[1] = command;

		try:
			import usb
			#int usb_control_msg(usb_dev_handle *dev, int requesttype, int request, int value, int index, char *bytes, int size, int timeout);
			#ret = usb_control_msg(devh, USB_TYPE_CLASS + USB_RECIP_INTERFACE, 0x0000009, 0x00003d9, 0x0000000, buf, 0x000000f, 1000);
			self.devh.controlMsg(usb.TYPE_CLASS + usb.RECIP_INTERFACE,       # requestType
		                                0x0000009,                                  # request
		                                buffer,                                     # buffer
		                                0x00003d9,                                  # value
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
		print "sHID::SetPreamblePattern"
		buffer = [0]*0x15
		buffer[0] = 0xd8;
		buffer[1] = pattern
		try:
			import usb
			#int usb_control_msg(usb_dev_handle *dev, int requesttype, int request, int value, int index, char *bytes, int size, int timeout);
			#ret = usb_control_msg(devh, USB_TYPE_CLASS + USB_RECIP_INTERFACE, 0x0000009, 0x00003d8, 0x0000000, buf, 0x0000015, 1000);
			self.devh.controlMsg(usb.TYPE_CLASS + usb.RECIP_INTERFACE,       # requestType
		                                0x0000009,                                  # request
		                                buffer,                                     # buffer
		                                0x00003d8,                                  # value
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
