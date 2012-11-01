#!/usr/bin/python

## This driver is based is based on reverse engineering of HeavyWeather 2800 v 1.54
## All copyright goes to La Crosse Technology (c) 2008

## Python port by Eddi De Pieri <eddi@depieri.net>
## Use this software as your own risk.
## Me and La Crosse Technology is not responsable for any damage using this software

from configobj import ConfigObj
import logging
import USBHardware

USBHardware = USBHardware.USBHardware()

class CWeatherStationConfig(object):
	def __init__(self):
		self.logger = logging.getLogger('ws28xx.CWeatherStationConfig')

		filename= "/etc/WV5Datastore.cfg"
		config = ConfigObj(filename)
		config.filename = filename
		try:
			self._CheckSumm = int(config['ws28xx']['CheckSumm'])
		except:
			self._CheckSumm = 0

		self._ClockMode = 0
		self._TemperatureFormat = 0
		self._PressureFormat = 0
		self._RainFormat = 0
		self._WindspeedFormat = 0
		self._WeatherThreshold = 0
		self._StormThreshold = 0
		self._LCDContrast = 0
		self._LowBatFlags = 0
		self._ResetMinMaxFlags = 0
		self._HistoryInterval = 0

	def readAlertFlags(self,buf):
		print "CWeatherStationConfig::readAlertFlags"

	def GetResetMinMaxFlags(self):
		print "CWeatherStationConfig::GetResetMinMaxFlags"

	def CWeatherStationConfig_buf(self,buf,start):
		newbuf=[0]
		newbuf[0] = buf[0]
		#CWeatherStationHighLowAlarm::CWeatherStationHighLowAlarm(&this->_AlarmTempIndoor);
		#v4 = 0;
		#CWeatherStationHighLowAlarm::CWeatherStationHighLowAlarm(&thisa->_AlarmTempOutdoor);
		#LOBYTE(v4) = 1;
		#CWeatherStationHighLowAlarm::CWeatherStationHighLowAlarm(&thisa->_AlarmHumidityOutdoor);
		#LOBYTE(v4) = 2;
		#CWeatherStationHighLowAlarm::CWeatherStationHighLowAlarm(&thisa->_AlarmHumidityIndoor);
		#LOBYTE(v4) = 3;
		#CWeatherStationWindAlarm::CWeatherStationWindAlarm(&thisa->_AlarmGust);
		#LOBYTE(v4) = 4;
		#CWeatherStationHighLowAlarm::CWeatherStationHighLowAlarm(&thisa->_AlarmPressure);
		#LOBYTE(v4) = 5;
		#CWeatherStationHighAlarm::CWeatherStationHighAlarm(&thisa->_AlarmRain24H);
		#LOBYTE(v4) = 6;
		#CWeatherStationWindDirectionAlarm::CWeatherStationWindDirectionAlarm(&thisa->_AlarmWindDirection);
		#LOBYTE(v4) = 7;
		#std::bitset<23>::bitset<23>(&thisa->_ResetMinMaxFlags);
		self.read(newbuf,start);

	def GetCheckSum(self):
		self.logger.debug("")
		self.CalcCheckSumm()
		return self._CheckSumm

	def CalcCheckSumm(self):
		self.logger.debug("")
		t = [0]
		t[0] = [0]*1024
		#self._ = self.write(t);
		#print "CWeatherStationConfig._CheckSumm (should be retrieved) --> 0x%x" % self._CheckSumm

	def read(self,buf,start):
		self.logger.debug("wsconfig")
		nbuf=[0]
		nbuf[0]=buf[0]
		#print "read",nbuf[0]
		CheckSumm = nbuf[0][43+start] | (nbuf[0][42+start] << 8);
		self._CheckSumm = CheckSumm;
		CheckSumm -= 7;
		self._ClockMode = nbuf[0][0+start] & 1;
		self._TemperatureFormat = (nbuf[0][0+start] >> 1) & 1;
		self._PressureFormat = (nbuf[0][0+start] >> 2) & 1;
		self._RainFormat = (nbuf[0][0+start] >> 3) & 1;
		self._WindspeedFormat = (nbuf[0][0+start] >> 4) & 0xF;
		self._WeatherThreshold = nbuf[0][1+start] & 0xF;
		self._StormThreshold = (nbuf[0][1+start] >> 4) & 0xF;
		self._LCDContrast = nbuf[0][2+start] & 0xF;
		self._LowBatFlags = (nbuf[0][2+start] >> 4) & 0xF;


		USBHardware.ReverseByteOrder(nbuf,3+start, 4)
		#buf=nbuf[0]
		#CWeatherStationConfig::readAlertFlags(thisa, buf + 3+start);
		USBHardware.ReverseByteOrder(nbuf, 7+start, 5);
		#v2 = USBHardware.ToTemperature(nbuf, 7+start, 1);
		#CWeatherStationHighLowAlarm::SetLowAlarm(&self._AlarmTempIndoor, v2);
		#v3 = USBHardware.ToTemperature(nbuf + 9+start, 0);
		#self._AlarmTempIndoor.baseclass_0.baseclass_0.vfptr[2].__vecDelDtor(
		#  (CWeatherStationAlarm *)&self._AlarmTempIndoor,
		#  LODWORD(v3));
		#j___RTC_CheckEsp(v4);
		USBHardware.ReverseByteOrder(nbuf, 12+start, 5);
		#v5 = USBHardware.ToTemperature(nbuf, 12+start, 1);
		#CWeatherStationHighLowAlarm::SetLowAlarm(&self._AlarmTempOutdoor, v5);
		#v6 = USBHardware.ToTemperature(nbuf, 14+start, 0);
		#self._AlarmTempOutdoor.baseclass_0.baseclass_0.vfptr[2].__vecDelDtor(
		#  (CWeatherStationAlarm *)&self._AlarmTempOutdoor,
		#  LODWORD(v6));
		USBHardware.ReverseByteOrder(nbuf, 17+start, 2);
		#v8 = USBHardware.ToHumidity(nbuf, 17+start, 1);
		#CWeatherStationHighLowAlarm::SetLowAlarm(&self._AlarmHumidityIndoor, v8);
		#v9 = USBHardware.ToHumidity(nbuf, 18+start, 1);
		#self._AlarmHumidityIndoor.baseclass_0.baseclass_0.vfptr[2].__vecDelDtor(
		#  (CWeatherStationAlarm *)&self._AlarmHumidityIndoor,
		#  LODWORD(v9));
		USBHardware.ReverseByteOrder(nbuf, 19+start, 2);
		#v11 = USBHardware.ToHumidity(nbuf, 19+start, 1);
		#CWeatherStationHighLowAlarm::SetLowAlarm(&self._AlarmHumidityOutdoor, v11);
		#v12 = USBHardware.ToHumidity(nbuf, 20+start, 1);
		#self._AlarmHumidityOutdoor.baseclass_0.baseclass_0.vfptr[2].__vecDelDtor(
		#  (CWeatherStationAlarm *)&self._AlarmHumidityOutdoor,
		#  LODWORD(v12));
		USBHardware.ReverseByteOrder(nbuf, 21+start, 4);
		#v14 = USBHardware.To4Pre3Post(nbuf, 21+start);
		#self._AlarmRain24H.baseclass_0.vfptr[2].__vecDelDtor((CWeatherStationAlarm *)&self._AlarmRain24H, LODWORD(v14));
		self._HistoryInterval = nbuf[0][25+start] & 0xF;
		#USBHardware.ReverseByteOrder(nbuf, 26+start, 3u);
		##v16 = USBHardware._ToWindspeed(nbuf, 26+start);
		#CWeatherStationWindAlarm::SetHighAlarmRaw(&self._AlarmGust, v16);
		#USBHardware.ReverseByteOrder(nbuf, 29+start, 5u);
		#USBHardware.ReadPressureShared(nbuf, 29+start, &a, &b);
		#v17 = Conversions::ToInhg(a);
		#v25 = b - v17;
		#if ( fabs(v25) > 1.0 )
		#{
		#  Conversions::ToInhg(a);
		#  v18 = CTracer::Instance();
		#  CTracer::WriteTrace(v18, 30, "low pressure alarm difference: %f");
		#}
		#CWeatherStationHighLowAlarm::SetLowAlarm(&self._AlarmPressure, a);
		USBHardware.ReverseByteOrder(nbuf, 34+start, 5);
		#USBHardware.ReadPressureShared(nbuf, 34+start, &a, &b);
		#v19 = Conversions::ToInhg(a);
		#v25 = b - v19;
		#if ( fabs(v25) > 1.0 )
		#{
		#  Conversions::ToInhg(a);
		#  v20 = CTracer::Instance();
		#  CTracer::WriteTrace(v20, 30, "high pressure alarm difference: %f");
		#}
		#self._AlarmPressure.baseclass_0.baseclass_0.vfptr[2].__vecDelDtor(
		#  (CWeatherStationAlarm *)&self._AlarmPressure,
		#  LODWORD(a));
		t = nbuf[0][39+start];
		t <<= 8;
		t |= nbuf[0][40+start];
		t <<= 8;
		t |= nbuf[0][41+start];
		#std::bitset<23>::bitset<23>((std::bitset<23> *)&v26, t);
		#self._ResetMinMaxFlags._Array[0] = v22;
		#for ( i = 0; i < 0x27; ++i )
		for i in xrange(0, 38):
			CheckSumm -= nbuf[0][i+start];
		#if ( CheckSumm ): for now is better to comment it
			#self._CheckSumm = -1;

		filename= "/etc/WV5Datastore.cfg"
		config = ConfigObj(filename)
		config.filename = filename
		config['ws28xx'] = {}
		config['ws28xx']['CheckSumm'] = str(self._CheckSumm)
		config['ws28xx']['ClockMode'] = str(self._ClockMode)

		config['ws28xx']['TemperatureFormat'] = str(self._TemperatureFormat)
		config['ws28xx']['PressureFormat'] = str(self._PressureFormat)
		config['ws28xx']['RainFormat'] = str(self._RainFormat)
		config['ws28xx']['WindspeedFormat'] = str(self._WindspeedFormat)
		config['ws28xx']['WeatherThreshold'] = str(self._WeatherThreshold)
		config['ws28xx']['StormThreshold'] = str(self._StormThreshold)
		config['ws28xx']['LCDContrast'] = str(self._LCDContrast)
		config['ws28xx']['LowBatFlags'] = str(self._LowBatFlags)
		config['ws28xx']['HistoryInterval'] = str(self._HistoryInterval)
		config.write()

		return 1;

	def write(self,buf):
		self.logger.debug("")
		new_buf = [0]
		new_buf[0]=buf[0]
		CheckSumm = 7;
		new_buf[0][0] = 16 * (self._WindspeedFormat & 0xF) + 8 * (self._RainFormat & 1) + 4 * (self._PressureFormat & 1) + 2 * (self._TemperatureFormat & 1) + self._ClockMode & 1;
		new_buf[0][1] = self._WeatherThreshold & 0xF | 16 * self._StormThreshold & 0xF0;
		new_buf[0][2] = self._LCDContrast & 0xF | 16 * self._LowBatFlags & 0xF0;
		#CWeatherStationConfig::writeAlertFlags(nbuf, 3);
		#((void (__thiscall *)(CWeatherStationHighLowAlarm *))thisa->_AlarmTempIndoor.baseclass_0.baseclass_0.vfptr[1].__vecDelDtor)(&thisa->_AlarmTempIndoor);
		#v25 = v2;
		#v24 = CWeatherTraits.TemperatureOffset() + v2;
		#v21 = v24;
		#v22 = CWeatherTraits.TemperatureOffset() + CWeatherStationHighLowAlarm::GetLowAlarm(&thisa->_AlarmTempIndoor);
		#v4 = v22;
		#USBHardware::ToTempAlarmBytes(nbuf, 7, v22, v21);
		#((void (__thiscall *)(CWeatherStationHighLowAlarm *))thisa->_AlarmTempOutdoor.baseclass_0.baseclass_0.vfptr[1].__vecDelDtor)(&thisa->_AlarmTempOutdoor);
		#v25 = v4;
		#v24 = CWeatherTraits.TemperatureOffset() + v4;
		#v21 = v24;
		#v22 = CWeatherTraits.TemperatureOffset() + CWeatherStationHighLowAlarm::GetLowAlarm(&thisa->_AlarmTempOutdoor);
		#v6 = v22;
		#USBHardware::ToTempAlarmBytes(nbuf, 12, v22, v21);
		#((void (__thiscall *)(CWeatherStationHighLowAlarm *))thisa->_AlarmHumidityIndoor.baseclass_0.baseclass_0.vfptr[1].__vecDelDtor)(&thisa->_AlarmHumidityIndoor);
		#v21 = v6;
		#v8 = CWeatherStationHighLowAlarm::GetLowAlarm(&thisa->_AlarmHumidityIndoor);
		#v9 = v8;
		#USBHardware::ToHumidityAlarmBytes(nbuf, 17, v9, v21);
		#((void (__thiscall *)(CWeatherStationHighLowAlarm *))thisa->_AlarmHumidityOutdoor.baseclass_0.baseclass_0.vfptr[1].__vecDelDtor)(&thisa->_AlarmHumidityOutdoor);
		#v21 = v8;
		#v11 = CWeatherStationHighLowAlarm::GetLowAlarm(&thisa->_AlarmHumidityOutdoor);
		#v12 = v11;
		#USBHardware::ToHumidityAlarmBytes(nbuf, 19, v12, v21);
		#((void (__thiscall *)(CWeatherStationHighAlarm *))thisa->_AlarmRain24H.baseclass_0.vfptr[1].__vecDelDtor)(&thisa->_AlarmRain24H);
		#v21 = v11;
		#USBHardware::ToRainAlarmBytes(nbuf, 21, v21);
		new_buf[0][25] = self._HistoryInterval & 0xF;
		#v21 = CWeatherStationWindAlarm::GetHighAlarmRaw(&thisa->_AlarmGust);
		#USBHardware::_ToWindspeedAlarmBytes(nbuf, 26, v21);
		#v21 = CWeatherStationHighLowAlarm::GetLowAlarm(&thisa->_AlarmPressure);
		#v21 = Conversions::ToInhg(v21);
		#v14 = CWeatherStationHighLowAlarm::GetLowAlarm(&thisa->_AlarmPressure);
		#v15 = CWeatherStationHighLowAlarm::GetLowAlarm(&thisa->_AlarmPressure);
		#USBHardware::ToPressureBytesShared(nbuf, 29, v15, v21);
		#((void (__thiscall *)(CWeatherStationHighLowAlarm *))thisa->_AlarmPressure.baseclass_0.baseclass_0.vfptr[1].__vecDelDtor)(&thisa->_AlarmPressure);
		#((void (__thiscall *)(CWeatherStationHighLowAlarm *))thisa->_AlarmPressure.baseclass_0.baseclass_0.vfptr[1].__vecDelDtor)(&thisa->_AlarmPressure);
		#USBHardware::ToPressureBytesShared(nbuf, 34, Conversions::ToInhg(CWeatherStationHighLowAlarm::GetLowAlarm(&thisa->_AlarmPressure)), Conversions::ToInhg(CWeatherStationHighLowAlarm::GetLowAlarm(&thisa->_AlarmPressure)))

		#print "debugxxx ", type(self._ResetMinMaxFlags)
		new_buf[0][39] = (self._ResetMinMaxFlags >>  0) & 0xFF;
		new_buf[0][40] = (self._ResetMinMaxFlags >>  8) & 0xFF; #BYTE1(self._ResetMinMaxFlags);
		new_buf[0][41] = (self._ResetMinMaxFlags >> 16) & 0xFF;

		#for ( i = 0; i < 39; ++i )
		for i in xrange(0, 38):
		    CheckSumm += new_buf[0][i];
		new_buf[0][42] = (CheckSumm >> 8) & 0xFF #BYTE1(CheckSumm);
		new_buf[0][43] = (CheckSumm >> 0) & 0xFF #CheckSumm;
		buf[0] = new_buf[0]
		return CheckSumm

