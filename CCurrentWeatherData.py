#!/usr/bin/python

import time
import logging
import USBHardware
import CWeatherTraits
import CMinMaxMeasurement

CWeatherTraits = CWeatherTraits.CWeatherTraits()
USBHardware = USBHardware.USBHardware()

windDirMap = { 0:"N", 1:"NNE", 2:"NE", 3:"ENE", 4:"E", 5:"ESE", 6:"SE", 7:"SSE",
              8:"S", 9:"SSW", 10:"SW", 11:"WSW", 12:"W", 13:"WNW", 14:"NW", 15:"NWN", 16:"err", 17:"inv" }

class CCurrentWeatherData(object):

	def __init__(self):
		self.logger = logging.getLogger('ws28xx.CCurrentWeatherData')

		self._PressureRelative_hPa = CWeatherTraits.PressureNP()
		self._PressureRelative_hPaMinMax = CMinMaxMeasurement.CMinMaxMeasurement()
		self._PressureRelative_inHg = CWeatherTraits.PressureNP()
		self._PressureRelative_inHgMinMax = CMinMaxMeasurement.CMinMaxMeasurement()
		self._WindSpeed = CWeatherTraits.WindNP()
		self._WindSpeedMinMax = CMinMaxMeasurement.CMinMaxMeasurement()
		self._WindDirection = 16
		self._WindDirection1 = 16
		self._WindDirection2 = 16
		self._WindDirection3 = 16
		self._WindDirection4 = 16
		self._WindDirection5 = 16
		self._Gust = CWeatherTraits.WindNP()
		self._GustDirection = 16
		self._GustDirection1 = 16
		self._GustDirection2 = 16
		self._GustDirection3 = 16
		self._GustDirection4 = 16
		self._GustDirection5 = 16
		self._Rain1H = CWeatherTraits.RainNP()
		self._Rain1HMax = CMinMaxMeasurement.CMinMaxMeasurement()
		self._Rain24H = CWeatherTraits.RainNP()
		self._Rain24HMax = CMinMaxMeasurement.CMinMaxMeasurement()
		self._RainLastWeek = CWeatherTraits.RainNP()
		self._RainLastWeekMax = CMinMaxMeasurement.CMinMaxMeasurement()
		self._RainLastMonth = CWeatherTraits.RainNP()
		self._RainLastMonthMax = CMinMaxMeasurement.CMinMaxMeasurement()
		self._RainTotal = CWeatherTraits.RainNP()
		self._LastRainReset = time.time()
		self._IndoorTemp = CWeatherTraits.TemperatureNP()
		self._IndoorTempMinMax = CMinMaxMeasurement.CMinMaxMeasurement()
		self._OutdoorTemp = CWeatherTraits.TemperatureNP()
		self._OutdoorTempMinMax = CMinMaxMeasurement.CMinMaxMeasurement()
		self._IndoorHumidity = CWeatherTraits.HumidityNP()
		self._IndoorHumidityMinMax = CMinMaxMeasurement.CMinMaxMeasurement()
		self._OutdoorHumidity = CWeatherTraits.HumidityNP()
		self._OutdoorHumidityMinMax = CMinMaxMeasurement.CMinMaxMeasurement()
		self._Dewpoint = CWeatherTraits.TemperatureNP()
		self._DewpointMinMax = CMinMaxMeasurement.CMinMaxMeasurement()
		self._Windchill = CWeatherTraits.TemperatureNP()
		self._WindchillMinMax = CMinMaxMeasurement.CMinMaxMeasurement()
		self._WeatherState = 3
		self._WeatherTendency = 3
		self._AlarmRingingFlags = 0
		self._AlarmMarkedFlags = 0

	def CCurrentWeatherData_buf(self,buf,pos):
		self.logger.debug("")
		#CMinMaxMeasurement::CMinMaxMeasurement(&this->_PressureRelative_hPaMinMax);
		#CMinMaxMeasurement::CMinMaxMeasurement(&thisa->_PressureRelative_inHgMinMax);
		#CMinMaxMeasurement::CMinMaxMeasurement(&thisa->_WindSpeedMinMax);
		#CMinMaxMeasurement::CMinMaxMeasurement(&thisa->_GustMinMax);
		#CMeasurement::CMeasurement(&thisa->_Rain1HMax);
		#CMeasurement::CMeasurement(&thisa->_Rain24HMax);
		#CMeasurement::CMeasurement(&thisa->_RainLastWeekMax);
		#CMeasurement::CMeasurement(&thisa->_RainLastMonthMax);
		self._LastRainReset = time.time()
		#CMinMaxMeasurement::CMinMaxMeasurement(&thisa->_IndoorTempMinMax);
		#CMinMaxMeasurement::CMinMaxMeasurement(&thisa->_OutdoorTempMinMax);
		#CMinMaxMeasurement::CMinMaxMeasurement(&thisa->_IndoorHumidityMinMax);
		#CMinMaxMeasurement::CMinMaxMeasurement(&thisa->_OutdoorHumidityMinMax);
		#CMinMaxMeasurement::CMinMaxMeasurement(&thisa->_DewpointMinMax);
		#CMinMaxMeasurement::CMinMaxMeasurement(&thisa->_WindchillMinMax);
		#std::bitset<29>::bitset<29>(&thisa->_AlarmRingingFlags);
		#std::bitset<29>::bitset<29>(&thisa->_AlarmMarkedFlags);
		self.read(buf,pos);

	def read(self,buf,pos):
		self.logger.debug("")
		newbuf = [0]
		newbuf[0] = buf[0]
		USBHardware.ReverseByteOrder(newbuf, pos + 0, 2);
		#CCurrentWeatherData::readAlarmFlags(thisa, buf, &thisa->_AlarmRingingFlags);
		self._WeatherState = newbuf[0][pos + 2] & 0xF;

		self._WeatherTendency = (newbuf[0][pos + 2] >> 4) & 0xF;

		USBHardware.ReverseByteOrder(newbuf, pos + 3, 0x12);
		self._IndoorTemp = USBHardware.ToTemperature(newbuf, pos + 3, 1)

		self._IndoorTempMinMax._Min._Value = USBHardware.ToTemperature(newbuf, pos + 5, 0);
		if self._IndoorTempMinMax._Min._Value == CWeatherTraits.TemperatureNP():
			self._IndoorTempMinMax._Min._IsError = 1
		else:
			self._IndoorTempMinMax._Min._IsError = 1
		if self._IndoorTempMinMax._Min._Value == CWeatherTraits.TemperatureOFL():
			self._IndoorTempMinMax._Min._IsOverflow = 1
		else:
			self._IndoorTempMinMax._Min._IsOverflow = 0

		self._IndoorTempMinMax._Max._Value = USBHardware.ToTemperature(newbuf, pos + 8, 1)
		if self._IndoorTempMinMax._Max._Value == CWeatherTraits.TemperatureNP():
			self._IndoorTempMinMax._Max._IsError = 1
		else:
			self._IndoorTempMinMax._Max._IsError = 0
		if self._IndoorTempMinMax._Max._Value == CWeatherTraits.TemperatureOFL():
			self._IndoorTempMinMax._Max._IsOverflow = 1
		else:
			self._IndoorTempMinMax._Max._IsOverflow = 0

		#if ( CMinMaxMeasurement::IsMinValueError(&thisa->_IndoorTempMinMax)
		#    || CMinMaxMeasurement::IsMinValueOverflow(&thisa->_IndoorTempMinMax) ):
		#    ATL::COleDateTime::SetStatus(&thisa->_IndoorTempMinMax._Min._Time, partial);
		#else:
		#    v5 = USBHardware::ToDateTime(&result, buf + 10, 0);
		#    v6 = (char *)&thisa->_IndoorTempMinMax._Min._Time;
		#    LODWORD(thisa->_IndoorTempMinMax._Min._Time.m_dt) = LODWORD(v5->m_dt);
		#    *((_DWORD *)v6 + 1) = HIDWORD(v5->m_dt);
		#    *((_DWORD *)v6 + 2) = v5->m_status;
		#if ( CMinMaxMeasurement::IsMaxValueError(&thisa->_IndoorTempMinMax)
		#    || CMinMaxMeasurement::IsMaxValueOverflow(&thisa->_IndoorTempMinMax) ):
		#    ATL::COleDateTime::SetStatus(&thisa->_IndoorTempMinMax._Max._Time, partial);
		#else:
		#    v7 = USBHardware::ToDateTime((ATL::COleDateTime *)&v82, buf + 15, 0);
		#    v8 = (char *)&thisa->_IndoorTempMinMax._Max._Time;
		#    LODWORD(thisa->_IndoorTempMinMax._Max._Time.m_dt) = LODWORD(v7->m_dt);
		#    *((_DWORD *)v8 + 1) = HIDWORD(v7->m_dt);
		#    *((_DWORD *)v8 + 2) = v7->m_status;

		USBHardware.ReverseByteOrder(newbuf, pos + 21, 0x12);
		self._OutdoorTemp = USBHardware.ToTemperature(newbuf, pos + 21, 1)

		self._OutdoorTempMinMax._Min._Value = USBHardware.ToTemperature(newbuf, pos + 23, 0);
		if self._OutdoorTempMinMax._Min._Value == CWeatherTraits.TemperatureNP():
			self._OutdoorTempMinMax._Min._IsError = 1
		else:
			self._OutdoorTempMinMax._Min._IsError = 0
		if self._OutdoorTempMinMax._Min._Value == CWeatherTraits.TemperatureOFL():
			self._OutdoorTempMinMax._Min._IsOverflow = 1
		else:
			self._OutdoorTempMinMax._Min._IsOverflow = 0

		self._OutdoorTempMinMax._Max._Value = USBHardware.ToTemperature(newbuf, pos + 26, 1)
		if self._OutdoorTempMinMax._Max._Value == CWeatherTraits.TemperatureNP():
			self._OutdoorTempMinMax._Max._IsError = 1
		else:
			self._OutdoorTempMinMax._Max._IsError = 0
		if self._OutdoorTempMinMax._Max._Value == CWeatherTraits.TemperatureOFL():
			self._OutdoorTempMinMax._Max._IsOverflow = 1
		else:
			self._OutdoorTempMinMax._Max._IsOverflow = 0

		#  if ( CMinMaxMeasurement::IsMinValueError(&thisa->_OutdoorTempMinMax)
		#    || CMinMaxMeasurement::IsMinValueOverflow(&thisa->_OutdoorTempMinMax) ):
		#    ATL::COleDateTime::SetStatus(&thisa->_OutdoorTempMinMax._Min._Time, partial);
		#  else:
		#    v12 = USBHardware::ToDateTime((ATL::COleDateTime *)&v83, buf + 28, 0);
		#    v13 = (char *)&thisa->_OutdoorTempMinMax._Min._Time;
		#    LODWORD(thisa->_OutdoorTempMinMax._Min._Time.m_dt) = LODWORD(v12->m_dt);
		#    *((_DWORD *)v13 + 1) = HIDWORD(v12->m_dt);
		#    *((_DWORD *)v13 + 2) = v12->m_status;
		#  if ( CMinMaxMeasurement::IsMaxValueError(&thisa->_OutdoorTempMinMax)
		#    || CMinMaxMeasurement::IsMaxValueOverflow(&thisa->_OutdoorTempMinMax) ):
		#    ATL::COleDateTime::SetStatus(&thisa->_OutdoorTempMinMax._Max._Time, partial);
		#  else:
		#    v14 = USBHardware::ToDateTime((ATL::COleDateTime *)&v84, buf + 33, 0);
		#    v15 = (char *)&thisa->_OutdoorTempMinMax._Max._Time;
		#    LODWORD(thisa->_OutdoorTempMinMax._Max._Time.m_dt) = LODWORD(v14->m_dt);
		#    *((_DWORD *)v15 + 1) = HIDWORD(v14->m_dt);
		#    *((_DWORD *)v15 + 2) = v14->m_status;
		USBHardware.ReverseByteOrder(newbuf, pos + 39, 0x12);
		self._Windchill = USBHardware.ToTemperature(newbuf, pos + 39, 1);
		self._WindchillMinMax._Min._Value = USBHardware.ToTemperature(newbuf, pos + 41, 0);
		if self._WindchillMinMax._Min._Value == CWeatherTraits.TemperatureNP():
			self._WindchillMinMax._Min._IsError = 1
		else:
			self._WindchillMinMax._Min._IsError = 0
		if self._WindchillMinMax._Min._Value == CWeatherTraits.TemperatureOFL():
			self._WindchillMinMax._Min._IsOverflow = 1
		else:
			self._WindchillMinMax._Min._IsOverflow = 0
		self._WindchillMinMax._Max._Value = USBHardware.ToTemperature(newbuf, pos + 44, 1);
		if self._WindchillMinMax._Max._Value == CWeatherTraits.TemperatureNP():
			self._WindchillMinMax._Max._IsError = 1
		else:
			self._WindchillMinMax._Max._IsError = 0
		if self._WindchillMinMax._Max._Value == CWeatherTraits.TemperatureOFL():
			self._WindchillMinMax._Max._IsOverflow = 1
		else:
			self._WindchillMinMax._Max._IsOverflow = 0

		#  if ( CMinMaxMeasurement::IsMinValueError(&thisa->_WindchillMinMax)
		#    || CMinMaxMeasurement::IsMinValueOverflow(&thisa->_WindchillMinMax) )
		#  {
		#    ATL::COleDateTime::SetStatus(&thisa->_WindchillMinMax._Min._Time, partial);
		#  }
		#  else
		#  {
		#    v19 = USBHardware::ToDateTime((ATL::COleDateTime *)&v85, buf + 46, 0);
		#    v20 = (char *)&thisa->_WindchillMinMax._Min._Time;
		#    LODWORD(thisa->_WindchillMinMax._Min._Time.m_dt) = LODWORD(v19->m_dt);
		#    *((_DWORD *)v20 + 1) = HIDWORD(v19->m_dt);
		#    *((_DWORD *)v20 + 2) = v19->m_status;
		#  }
		#  if ( CMinMaxMeasurement::IsMaxValueError(&thisa->_WindchillMinMax)
		#    || CMinMaxMeasurement::IsMaxValueOverflow(&thisa->_WindchillMinMax) )
		#  {
		#    ATL::COleDateTime::SetStatus(&thisa->_WindchillMinMax._Max._Time, partial);
		#  }
		#  else
		#  {
		#    v21 = USBHardware::ToDateTime((ATL::COleDateTime *)&v86, buf + 51, 0);
		#    v22 = (char *)&thisa->_WindchillMinMax._Max._Time;
		#    LODWORD(thisa->_WindchillMinMax._Max._Time.m_dt) = LODWORD(v21->m_dt);
		#    *((_DWORD *)v22 + 1) = HIDWORD(v21->m_dt);
		#    *((_DWORD *)v22 + 2) = v21->m_status;
		#  }
		USBHardware.ReverseByteOrder(newbuf, pos + 57, 0x12);
		self._Dewpoint = USBHardware.ToTemperature(newbuf, pos + 57, 1);
		self._DewpointMinMax._Min._Value = USBHardware.ToTemperature(newbuf, pos + 59, 0);
		if self._DewpointMinMax._Min._Value == CWeatherTraits.TemperatureNP():
			self._DewpointMinMax._Min._IsError = 1
		else:
			self._DewpointMinMax._Min._IsError = 0
		if self._DewpointMinMax._Min._Value == CWeatherTraits.TemperatureOFL():
			self._DewpointMinMax._Min._IsOverflow = 1
		else:
			self._DewpointMinMax._Min._IsOverflow = 0
		self._DewpointMinMax._Max._Value = USBHardware.ToTemperature(newbuf, pos + 62, 1);
		if self._DewpointMinMax._Max._Value == CWeatherTraits.TemperatureNP():
			self._DewpointMinMax._Max._IsError = 1
		else:
			self._DewpointMinMax._Max._IsError = 0
		if self._DewpointMinMax._Max._Value == CWeatherTraits.TemperatureOFL():
			self._DewpointMinMax._Max._IsOverflow = 1
		else:
			self._DewpointMinMax._Max._IsOverflow = 0

		#  if ( CMinMaxMeasurement::IsMinValueError(&thisa->_DewpointMinMax)
		#    || CMinMaxMeasurement::IsMinValueOverflow(&thisa->_DewpointMinMax) )
		#  {
		#    ATL::COleDateTime::SetStatus(&thisa->_DewpointMinMax._Min._Time, partial);
		#  }
		#  else
		#  {
		#    v26 = USBHardware::ToDateTime((ATL::COleDateTime *)&v87, buf + 64, 0);
		#    v27 = (char *)&thisa->_DewpointMinMax._Min._Time;
		#    LODWORD(thisa->_DewpointMinMax._Min._Time.m_dt) = LODWORD(v26->m_dt);
		#    *((_DWORD *)v27 + 1) = HIDWORD(v26->m_dt);
		#    *((_DWORD *)v27 + 2) = v26->m_status;
		#  }
		#  if ( CMinMaxMeasurement::IsMaxValueError(&thisa->_DewpointMinMax)
		#    || CMinMaxMeasurement::IsMaxValueOverflow(&thisa->_DewpointMinMax) )
		#  {
		#    ATL::COleDateTime::SetStatus(&thisa->_DewpointMinMax._Max._Time, partial);
		#  }
		#  else
		#  {
		#    v28 = USBHardware::ToDateTime((ATL::COleDateTime *)&v88, buf + 69, 0);
		#    v29 = (char *)&thisa->_DewpointMinMax._Max._Time;
		#    LODWORD(thisa->_DewpointMinMax._Max._Time.m_dt) = LODWORD(v28->m_dt);
		#    *((_DWORD *)v29 + 1) = HIDWORD(v28->m_dt);
		#    *((_DWORD *)v29 + 2) = v28->m_status;
		#  }

		USBHardware.ReverseByteOrder(newbuf, pos + 75, 0xD);
		self._IndoorHumidity = USBHardware.ToHumidity(buf, pos + 75, 1)

		self._IndoorHumidityMinMax._Min._Value = USBHardware.ToHumidity(newbuf, pos + 76, 1)
		if self._IndoorHumidityMinMax._Min._Value == CWeatherTraits.HumidityNP():
			self._IndoorHumidityMinMax._Min._IsError = 1
		else:
			self._IndoorHumidityMinMax._Min._IsError = 0
		if self._IndoorHumidityMinMax._Min._Value == CWeatherTraits.HumidityOFL():
			self._IndoorHumidityMinMax._Min._IsOverflow = 1
		else:
			self._IndoorHumidityMinMax._Min._IsOverflow = 0
		self._IndoorHumidityMinMax._Max._Value = USBHardware.ToHumidity(newbuf, pos + 77, 1)
		if self._IndoorHumidityMinMax._Max._Value == CWeatherTraits.HumidityNP():
			self._IndoorHumidityMinMax._Max._IsError = 1
		else:
			self._IndoorHumidityMinMax._Max._IsError = 0
		if self._IndoorHumidityMinMax._Max._Value == CWeatherTraits.HumidityOFL():
			self._IndoorHumidityMinMax._Max._IsOverflow = 1
		else:
			self._IndoorHumidityMinMax._Max._IsOverflow = 0
		#  if ( CMinMaxMeasurement::IsMinValueError(&thisa->_IndoorHumidityMinMax)
		#    || CMinMaxMeasurement::IsMinValueOverflow(&thisa->_IndoorHumidityMinMax) )
		#  {
		#    ATL::COleDateTime::SetStatus(&thisa->_IndoorHumidityMinMax._Min._Time, partial);
		#  }
		#  else
		#  {
		#    v33 = USBHardware::ToDateTime((ATL::COleDateTime *)&v89, buf + 78, 1);
		#    v34 = (char *)&thisa->_IndoorHumidityMinMax._Min._Time;
		#    LODWORD(thisa->_IndoorHumidityMinMax._Min._Time.m_dt) = LODWORD(v33->m_dt);
		#    *((_DWORD *)v34 + 1) = HIDWORD(v33->m_dt);
		#    *((_DWORD *)v34 + 2) = v33->m_status;
		#  }
		#  if ( CMinMaxMeasurement::IsMaxValueError(&thisa->_IndoorHumidityMinMax)
		#    || CMinMaxMeasurement::IsMaxValueOverflow(&thisa->_IndoorHumidityMinMax) )
		#  {
		#    ATL::COleDateTime::SetStatus(&thisa->_IndoorHumidityMinMax._Max._Time, partial);
		#  }
		#  else
		#  {
		#    v35 = USBHardware::ToDateTime((ATL::COleDateTime *)&v90, buf + 83, 1);
		#    v36 = (char *)&thisa->_IndoorHumidityMinMax._Max._Time;
		#    LODWORD(thisa->_IndoorHumidityMinMax._Max._Time.m_dt) = LODWORD(v35->m_dt);
		#    *((_DWORD *)v36 + 1) = HIDWORD(v35->m_dt);
		#    *((_DWORD *)v36 + 2) = v35->m_status;
		#  }

		USBHardware.ReverseByteOrder(newbuf, pos + 88, 0xD);
		self._OutdoorHumidity = USBHardware.ToHumidity(newbuf,pos + 88, 1)

		self._OutdoorHumidityMinMax._Min._Value = USBHardware.ToHumidity(newbuf, pos + 89, 1);
		if self._OutdoorHumidityMinMax._Min._Value == CWeatherTraits.HumidityNP():
			self._OutdoorHumidityMinMax._Min._IsError = 1
		else:
			self._OutdoorHumidityMinMax._Min._IsError = 0
		if self._OutdoorHumidityMinMax._Min._Value == CWeatherTraits.HumidityOFL():
			self._OutdoorHumidityMinMax._Min._IsOverflow = 1
		else:
			self._OutdoorHumidityMinMax._Min._IsOverflow = 0

		self._OutdoorHumidityMinMax._Max._Value = USBHardware.ToHumidity(newbuf, pos + 90, 1);
		if self._OutdoorHumidityMinMax._Max._Value == CWeatherTraits.HumidityNP():
			self._OutdoorHumidityMinMax._Max._IsError = 1
		else:
			self._OutdoorHumidityMinMax._Max._IsError = 0
		if self._OutdoorHumidityMinMax._Max._Value == CWeatherTraits.HumidityOFL():
			self._OutdoorHumidityMinMax._Max._IsOverflow = 1
		else:
			self._OutdoorHumidityMinMax._Max._IsOverflow = 0

		#  if ( CMinMaxMeasurement::IsMinValueError(&thisa->_OutdoorHumidityMinMax)
		#    || CMinMaxMeasurement::IsMinValueOverflow(&thisa->_OutdoorHumidityMinMax) )
		#  {
		#    ATL::COleDateTime::SetStatus(&thisa->_OutdoorHumidityMinMax._Min._Time, partial);
		#  }
		#  else
		#  {
		#    v40 = USBHardware::ToDateTime((ATL::COleDateTime *)&v91, buf + 91, 1);
		#    v41 = (char *)&thisa->_OutdoorHumidityMinMax._Min._Time;
		#    LODWORD(thisa->_OutdoorHumidityMinMax._Min._Time.m_dt) = LODWORD(v40->m_dt);
		#    *((_DWORD *)v41 + 1) = HIDWORD(v40->m_dt);
		#    *((_DWORD *)v41 + 2) = v40->m_status;
		#  }
		#  if ( CMinMaxMeasurement::IsMaxValueError(&thisa->_OutdoorHumidityMinMax)
		#    || CMinMaxMeasurement::IsMaxValueOverflow(&thisa->_OutdoorHumidityMinMax) )
		#  {
		#    ATL::COleDateTime::SetStatus(&thisa->_OutdoorHumidityMinMax._Max._Time, partial);
		#  }
		#  else
		#  {
		#    v42 = USBHardware::ToDateTime((ATL::COleDateTime *)&v92, buf + 96, 1);
		#    v43 = (char *)&thisa->_OutdoorHumidityMinMax._Max._Time;
		#    LODWORD(thisa->_OutdoorHumidityMinMax._Max._Time.m_dt) = LODWORD(v42->m_dt);
		#    *((_DWORD *)v43 + 1) = HIDWORD(v42->m_dt);
		#    *((_DWORD *)v43 + 2) = v42->m_status;
		#  }
		USBHardware.ReverseByteOrder(newbuf, pos + 101, 0xB);
		#thisa->_RainLastMonth = USBHardware::To4Pre2Post(buf + 101);
		#thisa->_RainLastMonthMax._Value = USBHardware::To4Pre2Post(buf + 104);
		#  thisa->_RainLastMonthMax._IsError = CWeatherTraits::RainNP();
		#  thisa->_RainLastMonthMax._IsOverflow = CWeatherTraits::RainOFL();
		#  if ( CMeasurement::IsError(&thisa->_RainLastMonthMax) || CMeasurement::IsOverflow(&thisa->_RainLastMonthMax) )
		#  {
		#    ATL::COleDateTime::SetStatus(&thisa->_RainLastMonthMax._Time, partial);
		#  }
		#  else
		#  {
		#    v46 = USBHardware::ToDateTime((ATL::COleDateTime *)&v93, buf + 107, 1);
		#    v47 = (char *)&thisa->_RainLastMonthMax._Time;
		#    LODWORD(thisa->_RainLastMonthMax._Time.m_dt) = LODWORD(v46->m_dt);
		#    *((_DWORD *)v47 + 1) = HIDWORD(v46->m_dt);
		#    *((_DWORD *)v47 + 2) = v46->m_status;
		#  }
		USBHardware.ReverseByteOrder(newbuf, pos + 112, 0xB);
		#  v48 = USBHardware::To4Pre2Post(buf + 112);
		#  thisa->_RainLastWeek = v48;
		#  v49 = USBHardware::To4Pre2Post(buf + 115);
		#  thisa->_RainLastWeekMax._Value = v49;
		#  v80 = thisa->_RainLastWeekMax._Value == CWeatherTraits::RainNP();
		#  thisa->_RainLastWeekMax._IsError = v80;
		#  v80 = thisa->_RainLastWeekMax._Value == CWeatherTraits::RainOFL();
		#  thisa->_RainLastWeekMax._IsOverflow = v80;
		#  if ( CMeasurement::IsError(&thisa->_RainLastWeekMax) || CMeasurement::IsOverflow(&thisa->_RainLastWeekMax) )
		#  {
		#    ATL::COleDateTime::SetStatus(&thisa->_RainLastWeekMax._Time, partial);
		#  }
		#  else
		#  {
		#    v50 = USBHardware::ToDateTime((ATL::COleDateTime *)&v94, buf + 118, 1);
		#    v51 = (char *)&thisa->_RainLastWeekMax._Time;
		#    LODWORD(thisa->_RainLastWeekMax._Time.m_dt) = LODWORD(v50->m_dt);
		#    *((_DWORD *)v51 + 1) = HIDWORD(v50->m_dt);
		#    *((_DWORD *)v51 + 2) = v50->m_status;
		#  }
		USBHardware.ReverseByteOrder(newbuf, pos + 123, 0xB)
		#  thisa->_Rain24H = USBHardware::To4Pre2Post(buf + 123);
		#  v53 = USBHardware::To4Pre2Post(buf + 126);
		#  thisa->_Rain24HMax._Value = v53;
		#  v80 = thisa->_Rain24HMax._Value == CWeatherTraits::RainNP();
		#  thisa->_Rain24HMax._IsError = v80;
		#  v80 = thisa->_Rain24HMax._Value == CWeatherTraits::RainOFL();
		#  thisa->_Rain24HMax._IsOverflow = v80;
		#  if ( CMeasurement::IsError(&thisa->_Rain24HMax) || CMeasurement::IsOverflow(&thisa->_Rain24HMax) )
		#  {
		#    ATL::COleDateTime::SetStatus(&thisa->_Rain24HMax._Time, partial);
		#  }
		#  else
		#  {
		#    v54 = USBHardware::ToDateTime((ATL::COleDateTime *)&v95, buf + 129, 1);
		#    v55 = (char *)&thisa->_Rain24HMax._Time;
		#    LODWORD(thisa->_Rain24HMax._Time.m_dt) = LODWORD(v54->m_dt);
		#    *((_DWORD *)v55 + 1) = HIDWORD(v54->m_dt);
		#    *((_DWORD *)v55 + 2) = v54->m_status;
		#  }
		USBHardware.ReverseByteOrder(newbuf, pos + 134, 0xB);
		self._Rain1H = USBHardware.To4Pre2Post(newbuf,pos + 134);
		self._Rain1HMax._Value = USBHardware.To4Pre2Post(newbuf,pos + 137);
		#  v80 = thisa->_Rain1HMax._Value == CWeatherTraits::RainNP();
		#  thisa->_Rain1HMax._IsError = v80;
		#  v80 = thisa->_Rain1HMax._Value == CWeatherTraits::RainOFL();
		#  thisa->_Rain1HMax._IsOverflow = v80;
		#  if ( CMeasurement::IsError(&thisa->_Rain1HMax) || CMeasurement::IsOverflow(&thisa->_Rain1HMax) )
		#  {
		#    ATL::COleDateTime::SetStatus(&thisa->_Rain1HMax._Time, partial);
		#  }
		#  else
		#  {
		#    v58 = USBHardware::ToDateTime((ATL::COleDateTime *)&v96, buf + 140, 1);
		#    v59 = (char *)&thisa->_Rain1HMax._Time;
		#    LODWORD(thisa->_Rain1HMax._Time.m_dt) = LODWORD(v58->m_dt);
		#    *((_DWORD *)v59 + 1) = HIDWORD(v58->m_dt);
		#    *((_DWORD *)v59 + 2) = v58->m_status;
		#  }
		USBHardware.ReverseByteOrder(newbuf, pos + 145, 9);
		self._RainTotal = USBHardware.To4Pre3Post(newbuf, pos + 145);
		#  v61 = USBHardware::ToDateTime((ATL::COleDateTime *)&v97, buf + 148, 0);
		#  v62 = (char *)&thisa->_LastRainReset;
		#  LODWORD(thisa->_LastRainReset.m_dt) = LODWORD(v61->m_dt);
		#  *((_DWORD *)v62 + 1) = HIDWORD(v61->m_dt);
		#  *((_DWORD *)v62 + 2) = v61->m_status;
		USBHardware.ReverseByteOrder(newbuf, pos + 154, 0xF);
		self._WindSpeed = USBHardware.ToWindspeed(newbuf,pos + 154);
		#  v64 = USBHardware::ToWindspeed(buf + 157);
		#  thisa->_WindSpeedMinMax._Max._Value = v64;
		#  v80 = thisa->_WindSpeedMinMax._Min._Value == CWeatherTraits::WindNP();
		#  thisa->_WindSpeedMinMax._Max._IsError = v80;
		#  v80 = thisa->_WindSpeedMinMax._Min._Value == CWeatherTraits::WindOFL();
		#  thisa->_WindSpeedMinMax._Max._IsOverflow = v80;
		#  if ( CMinMaxMeasurement::IsMaxValueError(&thisa->_WindSpeedMinMax)
		#    || CMinMaxMeasurement::IsMaxValueOverflow(&thisa->_WindSpeedMinMax) )
		#  {
		#    ATL::COleDateTime::SetStatus(&thisa->_WindSpeedMinMax._Max._Time, partial);
		#  }
		#  else
		#  {
		#    v65 = USBHardware::ToDateTime((ATL::COleDateTime *)&v98, buf + 160, 1);
		#    v66 = (char *)&thisa->_WindSpeedMinMax._Max._Time;
		#    LODWORD(thisa->_WindSpeedMinMax._Max._Time.m_dt) = LODWORD(v65->m_dt);
		#    *((_DWORD *)v66 + 1) = HIDWORD(v65->m_dt);
		#    *((_DWORD *)v66 + 2) = v65->m_status;
		#  }
		#  WindErrFlags = buf[165];
		(w ,w1) = USBHardware.ReadWindDirectionShared(newbuf, pos + 166)
		(w2,w3) = USBHardware.ReadWindDirectionShared(newbuf, pos + 167)
		(w4,w5) = USBHardware.ReadWindDirectionShared(newbuf, pos + 168)
		self._WindDirection = w;
		self._WindDirection1 = w1;
		self._WindDirection2 = w2;
		self._WindDirection3 = w3;
		self._WindDirection4 = w4;
		self._WindDirection5 = w5;
		#  CCurrentWeatherData::CheckWindErrFlags(
		#    thisa,
		#    WindErrFlags,
		#    &thisa->_WindSpeed,
		#    &thisa->_WindSpeedMinMax,
		#    &thisa->_WindDirection,
		#    &thisa->_WindDirection1,
		#    &thisa->_WindDirection2,
		#    &thisa->_WindDirection3,
		#    &thisa->_WindDirection4,
		#    &thisa->_WindDirection5);
		USBHardware.ReverseByteOrder(newbuf, pos + 169, 0xF);
		self._Gust = USBHardware.ToWindspeed(newbuf, pos + 169);
		#  thisa->_GustMinMax._Max._Value = USBHardware::ToWindspeed(buf + 172);
		#  v80 = thisa->_GustMinMax._Min._Value == CWeatherTraits::WindNP();
		#  thisa->_GustMinMax._Max._IsError = v80;
		#  v80 = thisa->_GustMinMax._Min._Value == CWeatherTraits::WindOFL();
		#  thisa->_GustMinMax._Max._IsOverflow = v80;
		#  if ( CMinMaxMeasurement::IsMaxValueError(&thisa->_GustMinMax)
		#    || CMinMaxMeasurement::IsMaxValueOverflow(&thisa->_GustMinMax) )
		#  {
		#    ATL::COleDateTime::SetStatus(&thisa->_GustMinMax._Max._Time, partial);
		#  }
		#  else
		#  {
		#    v69 = USBHardware::ToDateTime((ATL::COleDateTime *)&v99, buf + 175, 1);
		#    v70 = (char *)&thisa->_GustMinMax._Max._Time;
		#    LODWORD(thisa->_GustMinMax._Max._Time.m_dt) = LODWORD(v69->m_dt);
		#    *((_DWORD *)v70 + 1) = HIDWORD(v69->m_dt);
		#    *((_DWORD *)v70 + 2) = v69->m_status;
		#  }
		GustErrFlags = newbuf[0][180];
		(g ,g1) = USBHardware.ReadWindDirectionShared(newbuf, pos + 181)
		(g2,g3) = USBHardware.ReadWindDirectionShared(newbuf, pos + 182)
		(g4,g5) = USBHardware.ReadWindDirectionShared(newbuf, pos + 183)
		self._GustDirection = g;
		self._GustDirection1 = g1;
		self._GustDirection2 = g2;
		self._GustDirection3 = g3;
		self._GustDirection4 = g4;
		self._GustDirection5 = g5;
		#  CCurrentWeatherData::CheckWindErrFlags(
		#    thisa,
		#    GustErrFlags,
		#    &thisa->_Gust,
		#    &thisa->_GustMinMax,
		#    &thisa->_GustDirection,
		#    &thisa->_GustDirection1,
		#    &thisa->_GustDirection2,
		#    &thisa->_GustDirection3,
		#    &thisa->_GustDirection4,
		#    &thisa->_GustDirection5);
		USBHardware.ReverseByteOrder(newbuf, pos + 184, 0x19)
		(self._PressureRelative_hPa, self._PressureRelative_inHg) = USBHardware.ReadPressureShared(newbuf, pos + 184)
		(self._PressureRelative_hPaMinMax._Min._Value,self._PressureRelative_inHgMinMax._Min._Value) = USBHardware.ReadPressureShared(newbuf, pos + 189)
		(self._PressureRelative_hPaMinMax._Max._Value,self._PressureRelative_inHgMinMax._Max._Value) = USBHardware.ReadPressureShared(newbuf, pos + 194)
		#  thisa->_PressureRelative_hPaMinMax._Min._Value = CWeatherTraits::PressureOFL();
		#  thisa->_PressureRelative_hPaMinMax._Min._IsError = 1;
		#  thisa->_PressureRelative_hPaMinMax._Min._IsOverflow = 1;
		#  thisa->_PressureRelative_hPaMinMax._Max._Value = CWeatherTraits::PressureOFL();
		#  thisa->_PressureRelative_hPaMinMax._Max._IsError = 1;
		#  thisa->_PressureRelative_hPaMinMax._Max._IsOverflow = 1;
		#  if ( CMinMaxMeasurement::IsMinValueError(&thisa->_PressureRelative_hPaMinMax)
		#    || CMinMaxMeasurement::IsMinValueOverflow(&thisa->_PressureRelative_hPaMinMax) )
		#  {
		#    ATL::COleDateTime::SetStatus(&thisa->_PressureRelative_hPaMinMax._Min._Time, partial);
		#    ATL::COleDateTime::SetStatus(&thisa->_PressureRelative_inHgMinMax._Min._Time, partial);
		#  }
		#  else
		#  {
		#    v71 = USBHardware::ToDateTime((ATL::COleDateTime *)&v100, buf + 199, 1);
		#    v72 = (char *)&thisa->_PressureRelative_hPaMinMax._Min._Time;
		#    LODWORD(thisa->_PressureRelative_hPaMinMax._Min._Time.m_dt) = LODWORD(v71->m_dt);
		#    *((_DWORD *)v72 + 1) = HIDWORD(v71->m_dt);
		#    *((_DWORD *)v72 + 2) = v71->m_status;
		#    v73 = (char *)&thisa->_PressureRelative_hPaMinMax._Min._Time;
		#    v74 = (char *)&thisa->_PressureRelative_inHgMinMax._Min._Time;
		#    LODWORD(thisa->_PressureRelative_inHgMinMax._Min._Time.m_dt) = LODWORD(thisa->_PressureRelative_hPaMinMax._Min._Time.m_dt);
		#    *((_DWORD *)v74 + 1) = *((_DWORD *)v73 + 1);
		#    *((_DWORD *)v74 + 2) = *((_DWORD *)v73 + 2);
		#  }
		#  if ( CMinMaxMeasurement::IsMaxValueError(&thisa->_PressureRelative_hPaMinMax)
		#    || CMinMaxMeasurement::IsMaxValueOverflow(&thisa->_PressureRelative_hPaMinMax) )
		#  {
		#    ATL::COleDateTime::SetStatus(&thisa->_PressureRelative_hPaMinMax._Max._Time, partial);
		#    ATL::COleDateTime::SetStatus(&thisa->_PressureRelative_inHgMinMax._Max._Time, partial);
		#  }
		#  else
		#  {
		#    v75 = USBHardware::ToDateTime((ATL::COleDateTime *)&v101, buf + 204, 1);
		#    v76 = (char *)&thisa->_PressureRelative_hPaMinMax._Max._Time;
		#    LODWORD(thisa->_PressureRelative_hPaMinMax._Max._Time.m_dt) = LODWORD(v75->m_dt);
		#    *((_DWORD *)v76 + 1) = HIDWORD(v75->m_dt);
		#    *((_DWORD *)v76 + 2) = v75->m_status;
		#    v77 = (char *)&thisa->_PressureRelative_hPaMinMax._Max._Time;
		#    v78 = (char *)&thisa->_PressureRelative_inHgMinMax._Max._Time;
		#    LODWORD(thisa->_PressureRelative_inHgMinMax._Max._Time.m_dt) = LODWORD(thisa->_PressureRelative_hPaMinMax._Max._Time.m_dt);
		#    *((_DWORD *)v78 + 1) = *((_DWORD *)v77 + 1);
		#    *((_DWORD *)v78 + 2) = *((_DWORD *)v77 + 2);
		#  }
		#  thisa->_PressureRelative_inHgMinMax._Min._Value = CWeatherTraits::PressureOFL();
		#  thisa->_PressureRelative_inHgMinMax._Min._IsError = 1;
		#  thisa->_PressureRelative_inHgMinMax._Min._IsOverflow = 1;
		#  thisa->_PressureRelative_inHgMinMax._Max._Value = CWeatherTraits::PressureOFL();
		#  thisa->_PressureRelative_inHgMinMax._Max._IsError = 1;
		#  thisa->_PressureRelative_inHgMinMax._Max._IsOverflow = 1;
		#  std::bitset<29>::bitset<29>((std::bitset<29> *)&v102, 0);
		#  thisa->_AlarmMarkedFlags._Array[0] = v102;

		self.logger.debug("self._IndoorTemp=%d" % self._IndoorTemp)
		self.logger.debug("self._IndoorTempMinMax._Min._Value=%d" % self._IndoorTempMinMax._Min._Value)
		self.logger.debug("self._IndoorTempMinMax._Max._Value=%d" % self._IndoorTempMinMax._Max._Value)
		self.logger.debug("self._OutdoorTemp=%d" % self._OutdoorTemp)
		self.logger.debug("self._OutdoorTempMinMax._Min._Value=%d" % self._OutdoorTempMinMax._Min._Value)
		self.logger.debug("self._OutdoorTempMinMax._Max._Value=%d" % self._OutdoorTempMinMax._Max._Value)
		self.logger.debug("self._Windchill=%d" % self._Windchill)
		self.logger.debug("self._WindchillMinMax._Min._Value=%d" % self._WindchillMinMax._Min._Value)
		self.logger.debug("self._WindchillMinMax._Max._Value=%d" % self._WindchillMinMax._Max._Value)
		self.logger.debug("self._Dewpoint=%d" % self._Dewpoint)
		self.logger.debug("self._DewpointMinMax._Min._Value=%d" % self._DewpointMinMax._Min._Value)
		self.logger.debug("self._DewpointMinMax._Max._Value=%d" % self._DewpointMinMax._Max._Value)
		self.logger.debug("self._IndoorHumidity=%d" % self._IndoorHumidity)
		self.logger.debug("self._IndoorHumidityMinMax._Min._Value=%d" % self._IndoorHumidityMinMax._Min._Value)
		self.logger.debug("self._IndoorHumidityMinMax._Max._Value=%d" % self._IndoorHumidityMinMax._Max._Value)
		self.logger.debug("self._OutdoorHumidity=%d" % self._OutdoorHumidity)
		self.logger.debug("self._OutdoorHumidityMinMax._Min._Value=%d" % self._OutdoorHumidityMinMax._Min._Value)
		self.logger.debug("self._OutdoorHumidityMinMax._Max._Value=%d" % self._OutdoorHumidityMinMax._Max._Value)
		self.logger.debug("self._WindSpeed=%d" % self._WindSpeed)
		self.logger.debug("self._Gust=%d" % self._Gust)
		self.logger.debug("self._PressureRelative_hPa=%d" % self._PressureRelative_hPa)
		self.logger.debug("self._PressureRelative_inHg=%d" % self._PressureRelative_inHg)
		self.logger.debug("self._Rain1H=%d" % self._Rain1H)
		self.logger.debug("self._Rain1HMax._Value=%d" % self._Rain1HMax._Value)
		print "_WeatherState=%d _WeatherTendency=%d" % (self._WeatherState, self._WeatherTendency)
		print "_IndoorTemp=     %7.2f _Min=%7.2f _Max=%7.2f" % (self._IndoorTemp, self._IndoorTempMinMax._Min._Value, self._IndoorTempMinMax._Max._Value)
		print "_IndoorHumidity= %7.2f _Min=%7.2f _Max=%7.2f" % (self._IndoorHumidity, self._IndoorHumidityMinMax._Min._Value,self._IndoorHumidityMinMax._Max._Value)
		print "_OutdoorTemp=    %7.2f _Min=%7.2f _Max=%7.2f" % (self._OutdoorTemp, self._OutdoorTempMinMax._Min._Value, self._OutdoorTempMinMax._Max._Value)
		print "_OutdoorHumidity=%7.2f _Min=%7.2f _Max=%7.2f" % (self._OutdoorHumidity, self._OutdoorHumidityMinMax._Min._Value,self._OutdoorHumidityMinMax._Max._Value)
		print "_Windchill=      %7.2f _Min=%7.2f _Max=%7.2f" % (self._Windchill, self._WindchillMinMax._Min._Value, self._WindchillMinMax._Max._Value)
		print "_Dewpoint=       %7.2f _Min=%7.2f _Max=%7.2f" % (self._Dewpoint, self._DewpointMinMax._Min._Value, self._DewpointMinMax._Max._Value)
		print "_WindSpeed=%7.2f _Gust=%7.2f" % (self._WindSpeed * 3.6,self._Gust * 3.6)
		print "_Rain1H=%7.2f" % self._Rain1H
		print "_Rain1HMax._Value=%7.2f" % self._Rain1HMax._Value
		print "_RainTotal=%7.2f" % self._RainTotal
		print "w=%d , w1=%d, w2=%d, w3=%d, w4=%d, w5=%d" % (w, w1, w2, w3, w4, w5)
		print "w=%s , w1=%s, w2=%s, w3=%s, w4=%s, w5=%s" % (windDirMap[w], windDirMap[w1], windDirMap[w2], windDirMap[w3], windDirMap[w4], windDirMap[w5])
		print "g=%d , g1=%d, g2=%d, g3=%d, g4=%d, g5=%d" % (g, g1, g2, g3, g4, g5)
		print "g=%s , g1=%s, g2=%s, g3=%s, g4=%s, g5=%s" % (windDirMap[g], windDirMap[g1], windDirMap[g2], windDirMap[g3], windDirMap[g4], windDirMap[g5])
		print "_PressureRelative_hPa= %7.2f" % self._PressureRelative_hPa
		print "_PressureRelative_inHg=%7.2f" % self._PressureRelative_inHg
