#!/usr/bin/python

import logging
import CWeatherTraits

CWeatherTraits = CWeatherTraits.CWeatherTraits()

class USBHardware(object):
	def __init__(self):
		self.logger = logging.getLogger('ws28xx.USBHardware')

	def IsOFL2(self, buffer, startOnLowNibble):
		if ( startOnLowNibble ):
			result = (buffer[0][0] & 0xF) == 15 or buffer[0][0] >> 4 == 15;
		else:
			result = buffer[0][0] >> 4 == 15 or (buffer[0][1] & 0xF) == 15;
		return result

	def IsOFL5(self, buffer, startOnLowNibble):
		if ( startOnLowNibble ):
			result =     (buffer[0][0] & 0xF) == 15 \
				  or (buffer[0][0] >>  4) == 15 \
				  or (buffer[0][1] & 0xF) == 15 \
				  or (buffer[0][1] >>  4) == 15 \
				  or (buffer[0][2] & 0xF) == 15
		else:
			result =     (buffer[0][0] >>  4) == 15 \
				  or (buffer[0][1] & 0xF) == 15 \
				  or (buffer[0][1] >>  4) == 15 \
				  or (buffer[0][2] & 0xF) == 15 \
				  or (buffer[0][2] >>  4) == 15
		return result

	def IsErr2(self,buffer,startOnLowNibble):
		if ( startOnLowNibble ):
			result = (buffer[0][0] & 0xF) >= 10 and (buffer[0][0] & 0xF) != 15 or (buffer[0][0] >> 4) >= 10 and buffer[0][0] >> 4 != 15;
		else:
			result = (buffer[0][0] >> 4) >= 10 and buffer[0][0] >> 4 != 15 or (buffer[0][1] & 0xF) >= 10 and (buffer[0][1] & 0xF) != 15;
		return result

	def IsErr5(self,buffer,startOnLowNibble):
		if ( startOnLowNibble ):
			result =     (buffer[0][0] & 0xF) >= 10 \
				 and (buffer[0][0] & 0xF) != 15 \
				  or (buffer[0][0] >>  4) >= 10 \
				 and (buffer[0][0] >>  4) != 15 \
				  or (buffer[0][1] & 0xF) >= 10 \
				 and (buffer[0][1] & 0xF) != 15 \
				  or (buffer[0][1] >>  4) >= 10 \
				 and (buffer[0][1] >>  4) != 15 \
				  or (buffer[0][2] & 0xF) >= 10 \
				 and (buffer[0][2] & 0xF) != 15
		else:
			result =     (buffer[0][0] >>  4) >= 10 \
				 and (buffer[0][0] >>  4) != 15 \
				  or (buffer[0][1] & 0xF) >= 10 \
				 and (buffer[0][1] & 0xF) != 15 \
				  or (buffer[0][1] >>  4) >= 10 \
				 and (buffer[0][1] >>  4) != 15 \
				  or (buffer[0][2] & 0xF) >= 10 \
				 and (buffer[0][2] & 0xF) != 15 \
				  or (buffer[0][2] >>  4) >= 10 \
				 and (buffer[0][2] >>  4) != 15
		return result

	def ToCurrentTempBytes(self,bufer,c, d):
		self.logger.debug("")

	def To2Pre(self,buffer, start, startOnLowNibble):
		self.logger.debug("")
		if startOnLowNibble:
			rawpre  = (buffer[0][start+0] & 0xf)*  1 \
				+ (buffer[0][start+0]  >> 4)* 10
		else:
			rawpre  = (buffer[0][start+0]  >> 4)*  1 \
				+ (buffer[0][start+1] & 0xf)* 10
		return rawpre

	def ToPressureInhg(buffer, startOnLowNibble):
		self.logger.debug("")

	def ToRainAlarmBytes(buffer,alarm):
		self.logger.debug("")

	def ToDateTime(result, buffer, startOnLowNibble):
		self.logger.debug("")

	def ToHumidity(self,buffer,start,startOnLowNibble):
		self.logger.debug("")
		if ( self.IsErr2(buffer, startOnLowNibble) ):
			result = CWeatherTraits.HumidityNP();
		else:
			if ( self.IsOFL2(buffer, startOnLowNibble) ):
				result = CWeatherTraits.HumidityOFL()
			else:
				result = self.To2Pre(buffer, start, startOnLowNibble);
		return result;

	def ToTemperature(self,buffer, start, startOnLowNibble):
		self.logger.debug("")
		if ( self.IsErr5(buffer, startOnLowNibble) ):
			result = CWeatherTraits.TemperatureNP()
		else:
			if ( self.IsOFL5(buffer, startOnLowNibble) ):
				result = CWeatherTraits.TemperatureOFL()
			else:
				if startOnLowNibble:
					rawtemp = (buffer[0][start+0] & 0xf)*  0.001 \
						+ (buffer[0][start+0] >> 4 )*  0.01  \
						+ (buffer[0][start+1] & 0xf)*  0.1   \
						+ (buffer[0][start+1] >>  4)*  1     \
						+ (buffer[0][start+2] & 0xf)* 10
					#0,50,96
				else:
					rawtemp = (buffer[0][start+0] >> 4 )*  0.001 \
						+ (buffer[0][start+1] & 0xf)*  0.01  \
						+ (buffer[0][start+1] >>  4)*  0.1   \
						+ (buffer[0][start+2] & 0xf)*  1     \
						+ (buffer[0][start+2] >>  4)* 10
				result = rawtemp - CWeatherTraits.TemperatureOffset()
		return result;

	def To4Pre2Post(self,buffer):
		pass

	def ToWindspeed(self,buffer):
		pass

	def ReverseByteOrder(self,buf,start,Count):
		self.logger.debug("")
		nbuf=buf[0]
		#print nbuf
		for i in xrange(0, Count >> 1):
			tmp = nbuf[start + i]
			nbuf[start + i] = nbuf[start + Count - i - 1]
			nbuf[start + Count - i - 1 ] = tmp
		buf[0]=nbuf
