
import array
import logging

class sHID(object):
	'''
	Low level driver for ws-28xx
	'''
	logger = logging.getLogger('station.ws-2800.sHID')

	devh = None

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

	def SetRX(self):
		print "sHID::SetRX"
		buffer = array.array("h",range(0x15))
		buffer[0] = 0xD0;
		for i in range(1,0x15):
			buffer[i] = 0;
		import usb
		try:
		    self.devh.controlMsg(usb.TYPE_CLASS + usb.RECIP_INTERFACE,       # requestType
		                                0x0000000,                                  # request
		                                buffer,                                     # buffer
		                                0x0000000,                                  # value
		                                0x0000000,                                  # index
		                                1000)                                       # timeout
		except:
		    i=0
		    import sys
		    sys.stdout.write("sHID::SetRX message:")
		    for entry in buffer:
			sys.stdout.write("%x" % (buffer[i]))
			i+=1
		    sys.stdout.write(" fail\n")
		    pass
		print "sHID::SetRX end"

	def GetState(self,StateBuffer):
		print "sHID::GetState (not implemented yet)"

