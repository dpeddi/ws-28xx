import logging
import CWeatherTraits

CWeatherTraits = CWeatherTraits.CWeatherTraits()

class USBHardware(object):
	def __init__(self):
		self.logger = logging.getLogger('ws28xx.USBHardware')

	def ToCurrentTempBytes(self,bufer,c, d):
		self.logger.debug("")

	def To2Pre(buffer,startOnLowNibble):
		self.logger.debug("")

	def ToPressureInhg(buffer, startOnLowNibble):
		self.logger.debug("")

	def ToRainAlarmBytes(buffer,alarm):
		self.logger.debug("")

	def ToDateTime(result, buffer, startOnLowNibble):
		self.logger.debug("")

	def ToTemperature(self,buffer, start, startOnLowNibble):
		self.logger.debug("")
		if True: #hack ident
		#if ( USBHardware::IsErr5(buffer, startOnLowNibble) ):
		#	v2 = CWeatherTraits::TemperatureNP();
		#else:
			if True: #hack ident
		#	if ( USBHardware::IsOFL5(buffer, startOnLowNibble) ):
		#		v2 = CWeatherTraits::TemperatureOFL();
		#	else:
				print buffer[0][start+0] & 0xf #0  0
				print buffer[0][start+0] >> 4  #0  0
				print buffer[0][start+1] & 0xf #4  0
				print buffer[0][start+1] >> 4  #9  3
				print buffer[0][start+2] & 0xf #5  5
				if startOnLowNibble:
					print "startOnLowNibble #1", startOnLowNibble
					rawtemp = (buffer[0][start+0] &0xf)*1000+(buffer[0][start+0] >>4 )*100+(buffer[0][start+1] &0xf)*0.1+(buffer[0][start+1] >> 4)+(buffer[0][start+2] &0x0f)*10
				else:
					print "startOnLowNibble #2", startOnLowNibble
					rawtemp = (buffer[0][start+0] &0xf)*100+(buffer[0][start+0] >>4 )*1000+(buffer[0][start+1] &0xf)+(buffer[0][start+1] >> 4)*10+(buffer[0][start+2] &0x0f)*0.1
				result = rawtemp - CWeatherTraits.TemperatureOffset()
		return result;

	def ReverseByteOrder(self,buf,start,Count):
		self.logger.debug("")
		nbuf=buf[0]
		#print nbuf
		for i in xrange(0, Count >> 1):
			tmp = nbuf[start + i]
			nbuf[start + i] = nbuf[start + Count - i - 1]
			nbuf[start + Count - i - 1 ] = tmp
		buf[0]=nbuf
