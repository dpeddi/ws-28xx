#!/usr/bin/python

## This driver is based is based on reverse engineering of HeavyWeather 2800 v 1.54
## All copyright goes to La Crosse Technology (c) 2008

## Python port by Eddi De Pieri <eddi@depieri.net>
## Use this software as your own risk.
## Me and La Crosse Technology is not responsable for any damage using this software

import logging
import datetime
import CWeatherTraits

CWeatherTraits = CWeatherTraits.CWeatherTraits()

class USBHardware(object):
	def __init__(self):
		self.logger = logging.getLogger('ws28xx.USBHardware')

	def IsOFL2(self, buffer, start, startOnLowNibble):
		if ( startOnLowNibble ):
			result =   (buffer[0][start+0] & 0xF) == 15 \
				or (buffer[0][start+0] >>  4) == 15
		else:
			result =   (buffer[0][start+0] >>  4) == 15 \
				or (buffer[0][start+1] & 0xF) == 15
		return result

	def IsOFL3(self, buffer, start, startOnLowNibble):
		if ( startOnLowNibble ):
			result =   (buffer[0][start+0] & 0xF) == 15 \
				or (buffer[0][start+0] >>  4) == 15 \
				or (buffer[0][start+1] & 0xF) == 15
		else:
			result =   (buffer[0][start+0] >>  4) == 15 \
				or (buffer[0][start+1] & 0xF) == 15 \
				or (buffer[0][start+1] >>  4) == 15
		return result;

	def IsOFL5(self, buffer, start, startOnLowNibble):
		if ( startOnLowNibble ):
			result =     (buffer[0][start+0] & 0xF) == 15 \
				  or (buffer[0][start+0] >>  4) == 15 \
				  or (buffer[0][start+1] & 0xF) == 15 \
				  or (buffer[0][start+1] >>  4) == 15 \
				  or (buffer[0][start+2] & 0xF) == 15
		else:
			result =     (buffer[0][start+0] >>  4) == 15 \
				  or (buffer[0][start+1] & 0xF) == 15 \
				  or (buffer[0][start+1] >>  4) == 15 \
				  or (buffer[0][start+2] & 0xF) == 15 \
				  or (buffer[0][start+2] >>  4) == 15
		return result

	def IsErr2(self,buffer,start,startOnLowNibble):
		if ( startOnLowNibble ):
			result =    (buffer[0][start+0] & 0xF) >= 10 \
				and (buffer[0][start+0] & 0xF) != 15 \
				 or (buffer[0][start+0] >>  4) >= 10 \
				and (buffer[0][start+0] >>  4) != 15
		else:
			result =    (buffer[0][start+0] >>  4) >= 10 \
				and (buffer[0][start+0] >>  4) != 15 \
				 or (buffer[0][start+1] & 0xF) >= 10 \
				and (buffer[0][start+1] & 0xF) != 15
		return result

	def IsErr3(self,buffer,start,startOnLowNibble):
		if ( startOnLowNibble ):
			result =     (buffer[0][start+0] & 0xF) >= 10 \
				 and (buffer[0][start+0] & 0xF) != 15 \
				 or  (buffer[0][start+0] >>  4) >= 10 \
				 and (buffer[0][start+0] >>  4) != 15 \
				 or  (buffer[0][start+1] & 0xF) >= 10 \
				 and (buffer[0][start+1] & 0xF) != 15
		else:
			result =     (buffer[0][start+0] >>  4) >= 10 \
				 and (buffer[0][start+0] >>  4) != 15 \
				 or  (buffer[0][start+1] & 0xF) >= 10 \
				 and (buffer[0][start+1] & 0xF) != 15 \
				 or  (buffer[0][start+1] >>  4) >= 10 \
				 and (buffer[0][start+1] >>  4) != 10
		return result

	def IsErr5(self,buffer,start,startOnLowNibble):
		if ( startOnLowNibble ):
			result =     (buffer[0][start+0] & 0xF) >= 10 \
				 and (buffer[0][start+0] & 0xF) != 15 \
				  or (buffer[0][start+0] >>  4) >= 10 \
				 and (buffer[0][start+0] >>  4) != 15 \
				  or (buffer[0][start+1] & 0xF) >= 10 \
				 and (buffer[0][start+1] & 0xF) != 15 \
				  or (buffer[0][start+1] >>  4) >= 10 \
				 and (buffer[0][start+1] >>  4) != 15 \
				  or (buffer[0][start+2] & 0xF) >= 10 \
				 and (buffer[0][start+2] & 0xF) != 15
		else:
			result =     (buffer[0][start+0] >>  4) >= 10 \
				 and (buffer[0][start+0] >>  4) != 15 \
				  or (buffer[0][start+1] & 0xF) >= 10 \
				 and (buffer[0][start+1] & 0xF) != 15 \
				  or (buffer[0][start+1] >>  4) >= 10 \
				 and (buffer[0][start+1] >>  4) != 15 \
				  or (buffer[0][start+2] & 0xF) >= 10 \
				 and (buffer[0][start+2] & 0xF) != 15 \
				  or (buffer[0][start+2] >>  4) >= 10 \
				 and (buffer[0][start+2] >>  4) != 15
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

	def ToRainAlarmBytes(buffer,alarm):
		self.logger.debug("")

	def ToDateTime(self, buffer, start, startOnLowNibble):
		self.logger.debug("")
		#print "buffer[0]", buffer[0]
		#ATL::COleDateTime::COleDateTime(&invalidDate);
		#ATL::COleDateTime::SetStatus(&invalidDate, partial);
		if ( self.IsErr2(buffer, start+0, startOnLowNibble)
		   or self.IsErr2(buffer, start+1, startOnLowNibble)
		   or self.IsErr2(buffer, start+2, startOnLowNibble)
		   or self.IsErr2(buffer, start+3, startOnLowNibble)
		   or self.IsErr2(buffer, start+4, startOnLowNibble)
		   or self.To2Pre(buffer, start+3, startOnLowNibble) > 12): #fix since I bugget my ws with corrupted date..
			#*(_QWORD *)&result->m_dt = (_QWORD)invalidDate.m_dt;
			#result->m_status = invalidDate.m_status;
			#return datetime.datetime.now()
			return datetime.datetime(1900, 01, 01, 00, 00) #fake too old date means invalid date
		else:
			minutes = self.To2Pre(buffer, start+0, startOnLowNibble)
			hours = self.To2Pre(buffer, start+1, startOnLowNibble)
			days = self.To2Pre(buffer, start+2, startOnLowNibble)
			month = self.To2Pre(buffer, start+3, startOnLowNibble)
			year = self.To2Pre(buffer, start+4, startOnLowNibble) + 2000;
			result = datetime.datetime(year, month, days, hours, minutes)
		#	*(_QWORD *)&result->m_dt = (_QWORD)dt.m_dt;
		#	result->m_status = dt.m_status;
		return result
		#return datetime.datetime.now()

	def ToHumidity(self,buffer,start,startOnLowNibble):
		self.logger.debug("")
		if ( self.IsErr2(buffer, start+0, startOnLowNibble) ):
			result = CWeatherTraits.HumidityNP();
		else:
			if ( self.IsOFL2(buffer, start+0, startOnLowNibble) ):
				result = CWeatherTraits.HumidityOFL()
			else:
				result = self.To2Pre(buffer, start, startOnLowNibble);
		return result;

	def ToTemperature(self,buffer, start, startOnLowNibble):
		self.logger.debug("")
		if ( self.IsErr5(buffer, start+0, startOnLowNibble) ):
			result = CWeatherTraits.TemperatureNP()
		else:
			if ( self.IsOFL5(buffer, start+0, startOnLowNibble) ):
				result = CWeatherTraits.TemperatureOFL()
			else:
				if startOnLowNibble:
					rawtemp = (buffer[0][start+0] & 0xf)*  0.001 \
						+ (buffer[0][start+0] >>  4)*  0.01  \
						+ (buffer[0][start+1] & 0xf)*  0.1   \
						+ (buffer[0][start+1] >>  4)*  1     \
						+ (buffer[0][start+2] & 0xf)* 10
				else:
					rawtemp = (buffer[0][start+0] >>  4)*  0.001 \
						+ (buffer[0][start+1] & 0xf)*  0.01  \
						+ (buffer[0][start+1] >>  4)*  0.1   \
						+ (buffer[0][start+2] & 0xf)*  1     \
						+ (buffer[0][start+2] >>  4)* 10
				result = rawtemp - CWeatherTraits.TemperatureOffset()
		return result;

	def To4Pre3Post(self,buffer,start):
		self.logger.debug("")
		if ( self.IsErr5(buffer, start+0, 1) or self.IsErr2(buffer, start+2, 0) ):
			result = CWeatherTraits.RainNP()
		else:
			if  ( self.IsOFL5(buffer, start+1, 1) or self.IsOFL2(buffer, start+2, 0) ):
				result = CWeatherTraits.RainOFL()
			else:
				result  = (buffer[0][start+0] & 0xf)*  0.001 \
					+ (buffer[0][start+0] >>  4)*  0.01  \
					+ (buffer[0][start+1] & 0xf)*  0.1   \
					+ (buffer[0][start+1] >>  4)*   1    \
					+ (buffer[0][start+2] & 0xf)*  10    \
					+ (buffer[0][start+2] >>  4)* 100    \
					+ (buffer[0][start+3] & 0xf)*1000
		return result

	def To4Pre2Post(self,buffer,start):
		self.logger.debug("")
		if ( self.IsErr2(buffer,start+0,1) or self.IsErr2(buffer,start+1, 1) or self.IsErr2(buffer, start+2, 1) ):
			result = CWeatherTraits.RainNP();
		else:
			if ( self.IsOFL2(buffer,start+0, 1) or self.IsOFL2(buffer, start+1, 1) or self.IsOFL2(buffer, start+2, 1) ):
				result = CWeatherTraits.RainOFL()
			else:
				result  = (buffer[0][start+0] & 0xf)*  0.01 \
					+ (buffer[0][start+0] >>  4)*  0.1  \
					+ (buffer[0][start+1] & 0xf)*   1   \
					+ (buffer[0][start+1] >>  4)*  10   \
					+ (buffer[0][start+2] & 0xf)* 100   \
					+ (buffer[0][start+2] >>  4)*1000
		return result

	def ToWindspeed(self,buffer,start): #m/s
		self.logger.debug("")
		val = self.ByteToFloat(buffer, start, 1, 16, 6);
		val = val / 256.0;
		val = val / 100.0;             #km/h
		val = val / 3.599999904632568; #m/s
		return val

	def ByteToFloat(self,buffer, start,startOnLowNibble, base, pre):
		self.logger.debug("")
		lowNibble = startOnLowNibble;
		val = 0;
		byteCounter = 0;
		i = 0;
		#for i in xrange(0,pre):
		while i < pre:
			if ( pre > 0 ):
				digit = 0;
				if ( lowNibble ):
					digit = buffer[0][start+byteCounter] & 0xF;
				else:
					digit = buffer[0][start+byteCounter] >> 4;
				if ( not lowNibble ):
					byteCounter += 1
				if lowNibble == 0:
					lowNibble=1
				else:
					lowNibble=0
				power = base**i
				val += digit * power
			i += 1
		return val

	def ReverseByteOrder(self,buf,start,Count):
		self.logger.debug("")
		nbuf=buf[0]
		#print nbuf
		for i in xrange(0, Count >> 1):
			tmp = nbuf[start + i]
			nbuf[start + i] = nbuf[start + Count - i - 1]
			nbuf[start + Count - i - 1 ] = tmp
		buf[0]=nbuf

	def ReadWindDirectionShared(self,buffer,start):
		self.logger.debug("")
		return (buffer[0][0+start] & 0xf, buffer[0][start] >> 4)

	def ReadPressureShared(self,buffer,start):
		self.logger.debug("")
		return ( self.ToPressure(buffer,start,1) , self.ToPressureInhg(buffer,start+2,0))

	def ToPressure(self,buffer,start,startOnLowNibble):
		if ( self.IsErr5(buffer, start+0, startOnLowNibble) ):
			result = CWeatherTraits.PressureNP();
		else:
			if ( self.IsOFL5(buffer, start+0, startOnLowNibble) ):
				result = CWeatherTraits.PressureOFL();
			else:
				if ( startOnLowNibble ):
					rawresult = (buffer[0][start+2] & 0xF)* 1000   \
						  + (buffer[0][start+1] >>  4)*  100   \
						  + (buffer[0][start+1] & 0xF)*   10   \
						  + (buffer[0][start+0] >>  4)*    1   \
						  + (buffer[0][start+0] & 0xF)*    0.1
				else:
					rawresult = (buffer[0][start+2] >>  4)* 1000   \
						  + (buffer[0][start+2] & 0xF)*  100   \
						  + (buffer[0][start+1] >>  4)*   10   \
						  + (buffer[0][start+1] & 0xF)*    1   \
						  + (buffer[0][start+0] >>  4)*    0.1
				result = rawresult
		return result

	def ToPressureInhg(self,buffer,start,startOnLowNibble):
		if ( self.IsErr5(buffer, start+0, startOnLowNibble) ):
			rawresult = CWeatherTraits.PressureNP();
		else:
			if ( self.IsOFL5(buffer, start+0, startOnLowNibble) ):
				rawresult = CWeatherTraits.PressureOFL()
			else:
				if ( startOnLowNibble ):
					rawresult = (buffer[0][start+2] & 0xF)* 100    \
						  + (buffer[0][start+1] >>  4)*  10    \
						  + (buffer[0][start+1] & 0xF)*   1    \
						  + (buffer[0][start+0] >>  4)*   0.1  \
						  + (buffer[0][start+0] & 0xF)*   0.01
				else:
					rawresult = (buffer[0][start+2] >>  4)* 100    \
						  + (buffer[0][start+2] & 0xF)*  10    \
						  + (buffer[0][start+1] >>  4)*   1    \
						  + (buffer[0][start+1] & 0xF)*   0.1  \
						  + (buffer[0][start+0] >>  4)*   0.01
				result = rawresult
		return result

	def ToTemperatureRingBuffer(self,buffer,start,startOnLowNibble):
		if ( self.IsErr3(buffer, start+0, startOnLowNibble) ):
			result = CWeatherTraits.TemperatureNP()
		else:
			if ( self.IsOFL3(buffer, start+0, startOnLowNibble) ):
				result = CWeatherTraits.TemperatureOFL()
			else:
				if ( startOnLowNibble ):
					#rawtemp   =  (buffer[0][start+0] & 0xF)* 10   \
					#	  +  (buffer[0][start+0] >>  4)*  1   \
					#	  +  (buffer[0][start+1] & 0xF)*  0.1
					rawtemp   =  (buffer[0][start+0] & 0xF)*  0.1 \
						  +  (buffer[0][start+0] >>  4)*  1   \
						  +  (buffer[0][start+1] & 0xF)* 10
				else:
					#rawtemp   =  (buffer[0][start+0] >>  4)* 10   \
					#	  +  (buffer[0][start+1] & 0xF)*  1   \
					#	  +  (buffer[0][start+1] >>  4)*  0.1
					rawtemp   =  (buffer[0][start+0] >>  4)*  0.1 \
						  +  (buffer[0][start+1] & 0xF)*  1   \
						  +  (buffer[0][start+1] >>  4)* 10  
				result = rawtemp - CWeatherTraits.TemperatureOffset()
		return result

	def ToWindspeedRingBuffer(self,buffer,start):
		if ( buffer[0][start+0] != 254 or (buffer[0][start+1] & 0xF) != 1 ):
			if ( buffer[0][start+0] != 255 or (buffer[0][start+1] & 0xF) != 1 ):
				val = self.ByteToFloat(buffer, start, 1, 16, 3);
				val = val / 10.0;
				result = val;
			else:
				result = CWeatherTraits.WindOFL();
		else:
				result = CWeatherTraits.WindNP();
		return result
