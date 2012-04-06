#!/usr/bin/python

## This driver is based is based on reverse engineering of HeavyWeather 2800 v 1.54
## All copyright goes to La Crosse Technology (c) 2008

## Python port by Eddi De Pieri <eddi@depieri.net>
## Use this software as your own risk.
## Me and La Crosse Technology is not responsable for any damage using this software

class CHistoryDataSet(object):

	def __init__(self):
		pass

	def CHistoryDataSet_buf(self):
		self.read(buf)

	def read(self,buf):
		USBHardware.ReverseByteOrder(buf, 0x12u);
		pBuffer = buf;
		j__memcpy(buffer5, buf, 5u);
		v2 = USBHardware.ToDateTime(&result, buffer5, 1);
		v3 = thisa;
		LODWORD(thisa->m_Time.m_dt) = LODWORD(v2->m_dt);
		HIDWORD(v3->m_Time.m_dt) = HIDWORD(v2->m_dt);
		v3->m_Time.m_status = v2->m_status;
		j__memcpy(buffer2, pBuffer + 5, 2u);
		self.m_IndoorTemp = USBHardware.ToTemperatureRingBuffer(buffer2, 1);
		j__memcpy(buffer2, pBuffer + 6, 2u);
		self.m_OutdoorTemp = USBHardware.ToTemperatureRingBuffer(buffer2, 0);
		j__memcpy(buffer3, pBuffer + 8, 3u);
		self.m_PressureRelative = USBHardware.ToPressure(buffer3, 1);
		self.m_PressureAbsolute = CWeatherTraits.PressureNP();
		j__memcpy(buffer2, pBuffer + 10, 2u);
		self.m_IndoorHumidity = USBHardware.ToHumidity(buffer2, 0);
		j__memcpy(buffer2, pBuffer + 11, 2u);
		self.m_OutdoorHumidity = USBHardware.ToHumidity(buffer2, 0);
		j__memcpy(buffer2, pBuffer + 12, 2u);
		self.m_RainCounterRaw = USBHardware.ByteToFloat(buffer2, 0, 16, 3);
		j__memcpy(buffer2, pBuffer + 14, 2u);
		self.m_WindSpeed = USBHardware.ToWindspeedRingBuffer(buffer2);
		j__memcpy((char *)&buffer1, pBuffer + 15, 1u);
		self.m_WindDirection = (buffer1 >> 4) & 0xF;
		if ( self.m_WindSpeed == CWeatherTraits.WindNP() )
				self.m_WindDirection = 16;
		if ( self.m_WindDirection < 0 && self.m_WindDirection > 16 )
				self.m_WindDirection = 16;
		j__memcpy(buffer2, pBuffer + 16, 2u);
		self.m_Gust = USBHardware.ToWindspeedRingBuffer(buffer2);
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
