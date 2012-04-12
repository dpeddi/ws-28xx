#!/usr/bin/python

## This driver is based is based on reverse engineering of HeavyWeather 2800 v 1.54
## All copyright goes to La Crosse Technology (c) 2008

## Python port by Eddi De Pieri <eddi@depieri.net>
## Use this software as your own risk.
## Me and La Crosse Technology is not responsable for any damage using this software

import logging
#from datetime import datetime
import USBHardware

USBHardware = USBHardware.USBHardware()

class CHistoryDataSet(object):

	def __init__(self):
		self.logger = logging.getLogger('ws28xx.CHistoryDataSet')

	def CHistoryDataSet_buf(self,buf,pos):
		self.logger.debug("")

		self.read(buf,pos)

	def read(self,buf,pos):
		self.logger.debug("")

		USBHardware.ReverseByteOrder(buf, pos + 0, 0x12);
		pBuffer = buf;
		#j__memcpy(buffer5, buf, 5u);
		#v3 = thisa;
		#LODWORD(thisa->m_Time.m_dt) = LODWORD(v2->m_dt);
		#HIDWORD(v3->m_Time.m_dt) = HIDWORD(v2->m_dt);
		#v3->m_Time.m_status = v2->m_status;
		self.m_Time = USBHardware.ToDateTime(buf, pos, 1);
		#j__memcpy(buffer2, pBuffer + 5, 2)
		#self.m_IndoorTemp = USBHardware.ToTemperatureRingBuffer(buffer2, 1);
		#j__memcpy(buffer2, pBuffer + 6, 2)
		#self.m_OutdoorTemp = USBHardware.ToTemperatureRingBuffer(buffer2, 0);
		self.m_PressureRelative = USBHardware.ToPressure(buf, pos + 8 , 1);
		#self.m_PressureAbsolute = CWeatherTraits.PressureNP(); #I think this should be sum to np..
		self.m_IndoorHumidity = USBHardware.ToHumidity(buf, pos + 10, 0);
		self.m_OutdoorHumidity = USBHardware.ToHumidity(buf, pos + 11, 0);
		self.m_RainCounterRaw = USBHardware.ByteToFloat(buf, pos + 12, 0, 16, 3);
		#j__memcpy(buffer2, pBuffer + 14, 2)
		#self.m_WindSpeed = USBHardware.ToWindspeedRingBuffer(buf, pos + 14);
		#j__memcpy((char *)&buffer1, pBuffer + 15, 1)
		#self.m_WindDirection = (buffer1 >> 4) & 0xF;
		#if ( self.m_WindSpeed == CWeatherTraits.WindNP() )
		#		self.m_WindDirection = 16;
		#if ( self.m_WindDirection < 0 && self.m_WindDirection > 16 )
		#		self.m_WindDirection = 16;
		#j__memcpy(buffer2, pBuffer + 16, 2)
		#self.m_Gust = USBHardware.ToWindspeedRingBuffer(buffer2);
		#if ( ATL::COleDateTime::GetYear(&self.m_Time) == 1999 )
		#{
		#		v12 = CTracer::Instance();
		#		CTracer::WriteTrace(
		#				v12,
		#				30,
		#				"Dataset has year 1999, will be removed as invalid, will not be included in rain calculation");
		#		ATL::COleDateTime::SetStatus(&self.m_Time, partial);
		#}
		#self._Dewpoint = CHistoryDataSet::CalculateDewpoint(thisa, self.m_OutdoorTemp, self.m_OutdoorHumidity);
		#self._Windchill = CHistoryDataSet::CalculateWindchill(thisa, self.m_OutdoorTemp, self.m_WindSpeed);

		self.logger.info("m_Time %s " % self.m_Time)
		print "m_Time %s " % self.m_Time
		print "m_PressureRelative", self.m_PressureRelative
		print "m_IndoorHumidity", self.m_IndoorHumidity
		print "m_OutdoorHumidity", self.m_OutdoorHumidity
		print "m_RainCounterRaw", self.m_RainCounterRaw
