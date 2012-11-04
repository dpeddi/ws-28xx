#!/usr/bin/python

## This driver is based is based on reverse engineering of HeavyWeather 2800 v 1.54
## All copyright goes to La Crosse Technology (c) 2008

## Python port by Eddi De Pieri <eddi@depieri.net>
## Use this software as your own risk.
## Me and La Crosse Technology is not responsable for any damage using this software

import time
import logging
import USBHardware
import CWeatherTraits
import CMinMaxMeasurement

CWeatherTraits = CWeatherTraits.CWeatherTraits()
USBHardware = USBHardware.USBHardware()

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
		self._GustMinMax = CMinMaxMeasurement.CMinMaxMeasurement()
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

		if 1 == 0:
		#if ( CMinMaxMeasurement::IsMinValueError(&thisa->_IndoorTempMinMax)
		#    || CMinMaxMeasurement::IsMinValueOverflow(&thisa->_IndoorTempMinMax) ):
		#    ATL::COleDateTime::SetStatus(&thisa->_IndoorTempMinMax._Min._Time, partial);
			pass
		else:
			self._IndoorTempMinMax._Min._Time = USBHardware.ToDateTime(newbuf, pos + 10, 0);
		if 1 == 0:
		#if ( CMinMaxMeasurement::IsMaxValueError(&thisa->_IndoorTempMinMax)
		#    || CMinMaxMeasurement::IsMaxValueOverflow(&thisa->_IndoorTempMinMax) ):
		#    ATL::COleDateTime::SetStatus(&thisa->_IndoorTempMinMax._Max._Time, partial);
			pass
		else:
			self._IndoorTempMinMax._Max._Time = USBHardware.ToDateTime(newbuf, pos + 15, 0);

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

		if 1 == 0:
		#  if ( CMinMaxMeasurement::IsMinValueError(&thisa->_OutdoorTempMinMax)
		#    || CMinMaxMeasurement::IsMinValueOverflow(&thisa->_OutdoorTempMinMax) ):
		#    ATL::COleDateTime::SetStatus(&thisa->_OutdoorTempMinMax._Min._Time, partial);
			pass
		else:
			self._OutdoorTempMinMax._Min._Time = USBHardware.ToDateTime(newbuf, pos + 28, 0)
		if 1 == 0:
		#  if ( CMinMaxMeasurement::IsMaxValueError(&thisa->_OutdoorTempMinMax)
		#    || CMinMaxMeasurement::IsMaxValueOverflow(&thisa->_OutdoorTempMinMax) ):
		#    ATL::COleDateTime::SetStatus(&thisa->_OutdoorTempMinMax._Max._Time, partial);
			pass
		else:
			self._OutdoorTempMinMax._Max._Time = USBHardware.ToDateTime(newbuf, pos + 33, 0)

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

		if 1 == 0:
		#  if ( CMinMaxMeasurement::IsMinValueError(&thisa->_WindchillMinMax)
		#    || CMinMaxMeasurement::IsMinValueOverflow(&thisa->_WindchillMinMax) )
		#    ATL::COleDateTime::SetStatus(&thisa->_WindchillMinMax._Min._Time, partial);
			pass
		else:
			self._WindchillMinMax._Min._Time = USBHardware.ToDateTime(newbuf, pos + 46, 0)

		if 1 == 0:
		#  if ( CMinMaxMeasurement::IsMaxValueError(&thisa->_WindchillMinMax)
		#    || CMinMaxMeasurement::IsMaxValueOverflow(&thisa->_WindchillMinMax) )
		#    ATL::COleDateTime::SetStatus(&thisa->_WindchillMinMax._Max._Time, partial);
			pass
		else:
			self._WindchillMinMax._Max._Time = USBHardware.ToDateTime(newbuf,pos + 51, 0)

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

		if 1 == 0:
		#  if ( CMinMaxMeasurement::IsMinValueError(&thisa->_DewpointMinMax)
		#    || CMinMaxMeasurement::IsMinValueOverflow(&thisa->_DewpointMinMax) )
		#    ATL::COleDateTime::SetStatus(&thisa->_DewpointMinMax._Min._Time, partial);
			pass
		else:
			self._DewpointMinMax._Min._Time = USBHardware.ToDateTime(newbuf, pos + 64, 0);

		if 1 == 0:
		#  if ( CMinMaxMeasurement::IsMaxValueError(&thisa->_DewpointMinMax)
		#    || CMinMaxMeasurement::IsMaxValueOverflow(&thisa->_DewpointMinMax) )
		#    ATL::COleDateTime::SetStatus(&thisa->_DewpointMinMax._Max._Time, partial);
			pass
		else:
			self._DewpointMinMax._Max._Time = USBHardware.ToDateTime(newbuf, pos + 69, 0)

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

		if 1 == 0:
		#  if ( CMinMaxMeasurement::IsMinValueError(&thisa->_IndoorHumidityMinMax)
		#    || CMinMaxMeasurement::IsMinValueOverflow(&thisa->_IndoorHumidityMinMax) )
		#    ATL::COleDateTime::SetStatus(&thisa->_IndoorHumidityMinMax._Min._Time, partial);
			pass
		else:
			self._IndoorHumidityMinMax._Min._Time = USBHardware.ToDateTime(newbuf, pos + 78, 1)

		if 1 == 0:
		#  if ( CMinMaxMeasurement::IsMaxValueError(&thisa->_IndoorHumidityMinMax)
		#    || CMinMaxMeasurement::IsMaxValueOverflow(&thisa->_IndoorHumidityMinMax) )
		#    ATL::COleDateTime::SetStatus(&thisa->_IndoorHumidityMinMax._Max._Time, partial);
			pass
		else:
			self._IndoorHumidityMinMax._Max._Time = USBHardware.ToDateTime(newbuf, pos + 83, 1)

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

		if 1 == 0:
		#  if ( CMinMaxMeasurement::IsMinValueError(&thisa->_OutdoorHumidityMinMax)
		#    || CMinMaxMeasurement::IsMinValueOverflow(&thisa->_OutdoorHumidityMinMax) )
		#    ATL::COleDateTime::SetStatus(&thisa->_OutdoorHumidityMinMax._Min._Time, partial);
			pass
		else:
			self._OutdoorHumidityMinMax._Min._Time = USBHardware.ToDateTime(newbuf, pos + 91, 1)

		if 1 == 0:
		#  if ( CMinMaxMeasurement::IsMaxValueError(&thisa->_OutdoorHumidityMinMax)
		#    || CMinMaxMeasurement::IsMaxValueOverflow(&thisa->_OutdoorHumidityMinMax) )
		#    ATL::COleDateTime::SetStatus(&thisa->_OutdoorHumidityMinMax._Max._Time, partial);
			pass
		else:
			self._OutdoorHumidityMinMax._Max._Time = USBHardware.ToDateTime(newbuf, pos + 96, 1)

		USBHardware.ReverseByteOrder(newbuf, pos + 101, 0xB);
		#thisa->_RainLastMonth = USBHardware::To4Pre2Post(buf + 101);
		#thisa->_RainLastMonthMax._Value = USBHardware::To4Pre2Post(buf + 104);
		#  thisa->_RainLastMonthMax._IsError = CWeatherTraits::RainNP();
		#  thisa->_RainLastMonthMax._IsOverflow = CWeatherTraits::RainOFL();
		#  if ( CMeasurement::IsError(&thisa->_RainLastMonthMax) || CMeasurement::IsOverflow(&thisa->_RainLastMonthMax) )
		#    ATL::COleDateTime::SetStatus(&thisa->_RainLastMonthMax._Time, partial);
		#  else
		#    v46 = USBHardware::ToDateTime((ATL::COleDateTime *)&v93, buf + 107, 1);
		#    v47 = (char *)&thisa->_RainLastMonthMax._Time;
		#    LODWORD(thisa->_RainLastMonthMax._Time.m_dt) = LODWORD(v46->m_dt);
		#    *((_DWORD *)v47 + 1) = HIDWORD(v46->m_dt);
		#    *((_DWORD *)v47 + 2) = v46->m_status;

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
		#    ATL::COleDateTime::SetStatus(&thisa->_RainLastWeekMax._Time, partial);
		#  else
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
		#    ATL::COleDateTime::SetStatus(&thisa->_Rain24HMax._Time, partial);
		#  else
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
		#    ATL::COleDateTime::SetStatus(&thisa->_Rain1HMax._Time, partial);
		#  else
		#    v58 = USBHardware::ToDateTime((ATL::COleDateTime *)&v96, buf + 140, 1);
		#    v59 = (char *)&thisa->_Rain1HMax._Time;
		#    LODWORD(thisa->_Rain1HMax._Time.m_dt) = LODWORD(v58->m_dt);
		#    *((_DWORD *)v59 + 1) = HIDWORD(v58->m_dt);
		#    *((_DWORD *)v59 + 2) = v58->m_status;

		USBHardware.ReverseByteOrder(newbuf, pos + 145, 9);
		self._RainTotal = USBHardware.To4Pre3Post(newbuf, pos + 145);
		#  v61 = USBHardware::ToDateTime((ATL::COleDateTime *)&v97, buf + 148, 0);
		#  v62 = (char *)&thisa->_LastRainReset;
		#  LODWORD(thisa->_LastRainReset.m_dt) = LODWORD(v61->m_dt);
		#  *((_DWORD *)v62 + 1) = HIDWORD(v61->m_dt);
		#  *((_DWORD *)v62 + 2) = v61->m_status;
		USBHardware.ReverseByteOrder(newbuf, pos + 154, 0xF);
		self._WindSpeed = USBHardware.ToWindspeed(newbuf,pos + 154);
		self._WindSpeedMinMax._Max._Value = USBHardware.ToWindspeed(newbuf, pos + 157);
		#  v80 = thisa->_WindSpeedMinMax._Min._Value == CWeatherTraits::WindNP();
		#  thisa->_WindSpeedMinMax._Max._IsError = v80;
		#  v80 = thisa->_WindSpeedMinMax._Min._Value == CWeatherTraits::WindOFL();
		#  thisa->_WindSpeedMinMax._Max._IsOverflow = v80;

		if 1 == 0:
		#  if ( CMinMaxMeasurement::IsMaxValueError(&thisa->_WindSpeedMinMax)
		#    || CMinMaxMeasurement::IsMaxValueOverflow(&thisa->_WindSpeedMinMax) )
		#    ATL::COleDateTime::SetStatus(&thisa->_WindSpeedMinMax._Max._Time, partial);
			pass
		else:
			self._WindSpeedMinMax._Max._Time = USBHardware.ToDateTime(newbuf, pos + 160, 1)
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
		USBHardware.ReverseByteOrder(newbuf, pos + 169, 0xF)
		self._Gust = USBHardware.ToWindspeed(newbuf, pos + 169)
		self._GustMinMax._Max._Value = USBHardware.ToWindspeed(newbuf, pos + 172)
		#  v80 = thisa->_GustMinMax._Min._Value == CWeatherTraits::WindNP();
		#  thisa->_GustMinMax._Max._IsError = v80;
		#  v80 = thisa->_GustMinMax._Min._Value == CWeatherTraits::WindOFL();
		#  thisa->_GustMinMax._Max._IsOverflow = v80;
		if 1 == 0:
		#  if ( CMinMaxMeasurement::IsMaxValueError(&thisa->_GustMinMax)
		#    || CMinMaxMeasurement::IsMaxValueOverflow(&thisa->_GustMinMax) )
		#    ATL::COleDateTime::SetStatus(&thisa->_GustMinMax._Max._Time, partial);
			pass
		else:
			self._GustMinMax._Max._Time = USBHardware.ToDateTime(newbuf, pos + 175, 1)

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
		#    ATL::COleDateTime::SetStatus(&thisa->_PressureRelative_hPaMinMax._Min._Time, partial);
		#    ATL::COleDateTime::SetStatus(&thisa->_PressureRelative_inHgMinMax._Min._Time, partial);
		#  else
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

		#  if ( CMinMaxMeasurement::IsMaxValueError(&thisa->_PressureRelative_hPaMinMax)
		#    || CMinMaxMeasurement::IsMaxValueOverflow(&thisa->_PressureRelative_hPaMinMax) )
		#    ATL::COleDateTime::SetStatus(&thisa->_PressureRelative_hPaMinMax._Max._Time, partial);
		#    ATL::COleDateTime::SetStatus(&thisa->_PressureRelative_inHgMinMax._Max._Time, partial);
		#  else
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

		#  thisa->_PressureRelative_inHgMinMax._Min._Value = CWeatherTraits::PressureOFL();
		#  thisa->_PressureRelative_inHgMinMax._Min._IsError = 1;
		#  thisa->_PressureRelative_inHgMinMax._Min._IsOverflow = 1;
		#  thisa->_PressureRelative_inHgMinMax._Max._Value = CWeatherTraits::PressureOFL();
		#  thisa->_PressureRelative_inHgMinMax._Max._IsError = 1;
		#  thisa->_PressureRelative_inHgMinMax._Max._IsOverflow = 1;
		#  std::bitset<29>::bitset<29>((std::bitset<29> *)&v102, 0);
		#  thisa->_AlarmMarkedFlags._Array[0] = v102;

		self.logger.info("_WeatherState=%s _WeatherTendency=%s" % ( CWeatherTraits.forecastMap[self._WeatherState], CWeatherTraits.trends[self._WeatherTendency]))
		self.logger.info("_IndoorTemp=     %7.2f _Min=%7.2f(%s) _Max=%7.2f(%s)" % (self._IndoorTemp, self._IndoorTempMinMax._Min._Value, self._IndoorTempMinMax._Min._Time, self._IndoorTempMinMax._Max._Value, self._IndoorTempMinMax._Max._Time))
		self.logger.info("_IndoorHumidity= %7.2f _Min=%7.2f(%s) _Max=%7.2f(%s)" % (self._IndoorHumidity, self._IndoorHumidityMinMax._Min._Value, self._IndoorHumidityMinMax._Min._Time, self._IndoorHumidityMinMax._Max._Value, self._IndoorHumidityMinMax._Max._Time))
		self.logger.info("_OutdoorTemp=    %7.2f _Min=%7.2f(%s) _Max=%7.2f(%s)" % (self._OutdoorTemp, self._OutdoorTempMinMax._Min._Value, self._OutdoorTempMinMax._Min._Time, self._OutdoorTempMinMax._Max._Value, self._OutdoorTempMinMax._Max._Time))
		self.logger.info("_OutdoorHumidity=%7.2f _Min=%7.2f(%s) _Max=%7.2f(%s)" % (self._OutdoorHumidity, self._OutdoorHumidityMinMax._Min._Value, self._OutdoorHumidityMinMax._Min._Time, self._OutdoorHumidityMinMax._Max._Value, self._OutdoorHumidityMinMax._Max._Time))
		self.logger.info("_Windchill=      %7.2f _Min=%7.2f(%s) _Max=%7.2f(%s)" % (self._Windchill, self._WindchillMinMax._Min._Value, self._WindchillMinMax._Min._Time, self._WindchillMinMax._Max._Value, self._WindchillMinMax._Max._Time))
		self.logger.info("_Dewpoint=       %7.2f _Min=%7.2f(%s) _Max=%7.2f(%s)" % (self._Dewpoint, self._DewpointMinMax._Min._Value, self._DewpointMinMax._Min._Time, self._DewpointMinMax._Max._Value, self._DewpointMinMax._Max._Time))
		self.logger.info("_WindSpeed=      %7.2f                                   _Max=%7.2f(%s)" % (self._WindSpeed * 3.6, self._WindSpeedMinMax._Max._Value * 3.6, self._WindSpeedMinMax._Max._Time))
		self.logger.info("_Gust=           %7.2f                                   _Max=%7.2f(%s)" % (self._Gust * 3.6,      self._GustMinMax._Max._Value * 3.6, self._GustMinMax._Max._Time))
		self.logger.info("_PressureRelative_hPa=%8.2f" % self._PressureRelative_hPa)
		self.logger.info("_PressureRelative_inHg=%7.2f" % self._PressureRelative_inHg)
		self.logger.info("_Rain1H=%8.2f" % self._Rain1H)
		self.logger.info("_Rain1HMax._Value=%8.2f" % self._Rain1HMax._Value)
