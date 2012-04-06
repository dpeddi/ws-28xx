#!/usr/bin/python

## This driver is based is based on reverse engineering of HeavyWeather 2800 v 1.54
## All copyright goes to La Crosse Technology (c) 2008

## Python port by Eddi De Pieri <eddi@depieri.net>
## Use this software as your own risk.
## Me and La Crosse Technology is not responsable for any damage using this software

import logging
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
			result = (buffer[0][start+0] >> 4) >= 10 and buffer[0][start+0] >> 4 != 15 or (buffer[0][start+1] & 0xF) >= 10 and (buffer[0][start+1] & 0xF) != 15;
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

	def ToDateTime(result, buffer, startOnLowNibble):
		self.logger.debug("")

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

	def ToDateTime(self,buffer,startOnLowNibble):
		pass
#  ATL::COleDateTime::COleDateTime(&invalidDate);
#  ATL::COleDateTime::SetStatus(&invalidDate, partial);
#  if ( USBHardware::IsErr2(buffer, startOnLowNibble)
#    || USBHardware::IsErr2(buffer + 1, startOnLowNibble)
#    || USBHardware::IsErr2(buffer + 2, startOnLowNibble)
#    || USBHardware::IsErr2(buffer + 3, startOnLowNibble)
#    || USBHardware::IsErr2(buffer + 4, startOnLowNibble) )
#  {
#    *(_QWORD *)&result->m_dt = (_QWORD)invalidDate.m_dt;
#    result->m_status = invalidDate.m_status;
#  }
#  else
#  {
#    v3 = USBHardware::To2Pre(buffer, startOnLowNibble);
#    minutes = j___ftol2_sse(v3);
#    v4 = USBHardware::To2Pre(buffer + 1, startOnLowNibble);
#    hours = j___ftol2_sse(v4);
#    v5 = USBHardware::To2Pre(buffer + 2, startOnLowNibble);
#    days = j___ftol2_sse(v5);
#    v6 = USBHardware::To2Pre(buffer + 3, startOnLowNibble);
#    month = j___ftol2_sse(v6);
#    v7 = USBHardware::To2Pre(buffer + 4, startOnLowNibble);
#    year = j___ftol2_sse(v7) + 2000;
#    ATL::COleDateTime::COleDateTime(&dt, year, month, days, hours, minutes, 0);
#    *(_QWORD *)&result->m_dt = (_QWORD)dt.m_dt;
#    result->m_status = dt.m_status;
#  }
#  _RTC_CheckStackVars(&v18, &stru_55ADA8);
#  j___RTC_CheckEsp(v8);
#  return v9;

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
						  + (buffer[0][start+0] & 0xF)*   0.1  \
						  + (buffer[0][start+0] >>  4)*   0.01
				result = rawresult
		return result
