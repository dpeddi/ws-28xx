#!/usr/bin/python
#1011602060032L
#01 01 22 02 06 00 50

import logging
import threading
#import shelve #http://docs.python.org/library/pickle.html
import sHID
import time
from datetime import datetime
from datetime import timedelta


usbWait = 0.5

sHID = sHID.sHID()

# testBit() returns a nonzero result, 2**offset, if the bit at 'offset' is one.
def testBit(int_type, offset):
    mask = 1 << offset
    return(int_type & mask)

# setBit() returns an integer with the bit at 'offset' set to 1.
def setBit(int_type, offset):
    mask = 1 << offset
    return(int_type | mask)

# setBitVal() returns an integer with the bit at 'offset' set to 1.
def setBitVal(int_type, offset, val):
    mask = val << offset
    return(int_type | mask)

# clearBit() returns an integer with the bit at 'offset' cleared.
def clearBit(int_type, offset):
    mask = ~(1 << offset)
    return(int_type & mask)

# toggleBit() returns an integer with the bit at 'offset' inverted, 0 -> 1 and 1 -> 0.
def toggleBit(int_type, offset):
    mask = 1 << offset
    return(int_type ^ mask)

# Abstract struct class       
class Struct:
    def __init__ (self, *argv, **argd):
        if len(argd):
            # Update by dictionary
            self.__dict__.update (argd)
        else:
            # Update by position
            attrs = filter (lambda x: x[0:2] != "__", dir(self))
            for n in range(len(argv)):
                setattr(self, attrs[n], argv[n])

class ws28xxError(IOError):
	"Used to signal an error condition"

#FFFFFFFF ; enum EHistoryInterval (standard)
#FFFFFFFF hi01Min          = 0
#FFFFFFFF hi05Min          = 1
#FFFFFFFF hi10Min          = 2
#FFFFFFFF hi15Min          = 3
#FFFFFFFF hi20Min          = 4
#FFFFFFFF hi30Min          = 5
#FFFFFFFF hi60Min          = 6
#FFFFFFFF hi02Std          = 7
#FFFFFFFF hi04Std          = 8
#FFFFFFFF hi06Std          = 9
#FFFFFFFF hi08Std          = 0Ah
#FFFFFFFF hi12Std          = 0Bh
#FFFFFFFF hi24Std          = 0Ch


#FFFFFFFF ; ---------------------------------------------------------------------------
#FFFFFFFF
#FFFFFFFF ; enum EWindspeedFormat (standard)
#FFFFFFFF wfMs             = 0
#FFFFFFFF wfKnots          = 1
#FFFFFFFF wfBFT            = 2
#FFFFFFFF wfKmh            = 3
#FFFFFFFF wfMph            = 4
#FFFFFFFF
#FFFFFFFF ; ---------------------------------------------------------------------------
#FFFFFFFF
#FFFFFFFF ; enum ERainFormat (standard)
#FFFFFFFF rfMm             = 0
#FFFFFFFF rfInch           = 1
#FFFFFFFF
#FFFFFFFF ; ---------------------------------------------------------------------------
#FFFFFFFF
#FFFFFFFF ; enum EPressureFormat (standard)
#FFFFFFFF pfinHg           = 0
#FFFFFFFF pfHPa            = 1
#FFFFFFFF
#FFFFFFFF ; ---------------------------------------------------------------------------
#FFFFFFFF
#FFFFFFFF ; enum ETemperatureFormat (standard)
#FFFFFFFF tfFahrenheit     = 0
#FFFFFFFF tfCelsius        = 1
#FFFFFFFF
#FFFFFFFF ; ---------------------------------------------------------------------------
#FFFFFFFF
#FFFFFFFF ; enum EClockMode (standard)
#FFFFFFFF ct24H            = 0
#FFFFFFFF ctAmPm           = 1
#FFFFFFFF
#FFFFFFFF ; enum EWeatherTendency (standard)
#FFFFFFFF TREND_NEUTRAL    = 0
#FFFFFFFF TREND_UP         = 1
#FFFFFFFF TREND_DOWN       = 2
#FFFFFFFF TREND_ERR        = 3
#FFFFFFFF
#FFFFFFFF ; ---------------------------------------------------------------------------
#FFFFFFFF
#FFFFFFFF ; enum EWeatherState (standard)
#FFFFFFFF WEATHER_BAD      = 0
#FFFFFFFF WEATHER_NEUTRAL  = 1
#FFFFFFFF WEATHER_GOOD     = 2
#FFFFFFFF WEATHER_ERR      = 3
#FFFFFFFF
#FFFFFFFF ; ---------------------------------------------------------------------------
#FFFFFFFF

class EWindDirection:
	 wdN              = 0
	 wdNNE            = 1
	 wdNE             = 2
	 wdENE            = 3
	 wdE              = 4
	 wdESE            = 5
	 wdSE             = 6
	 wdSSE            = 7
	 wdS              = 8
	 wdSSW            = 9
	 wdSW             = 0x0A
	 wdWSW            = 0x0B
	 wdW              = 0x0C
	 wdWNW            = 0x0D
	 wdNW             = 0x0E
	 wdNNW            = 0x0F
	 wdERR            = 0x10
	 wdInvalid        = 0x11

class EResetMinMaxFlags:
	 rmTempIndoorHi   = 0
	 rmTempIndoorLo   = 1
	 rmTempOutdoorHi  = 2
	 rmTempOutdoorLo  = 3
	 rmWindchillHi    = 4
	 rmWindchillLo    = 5
	 rmDewpointHi     = 6
	 rmDewpointLo     = 7
	 rmHumidityIndoorLo  = 8
	 rmHumidityIndoorHi  = 9
	 rmHumidityOutdoorLo  = 0x0A
	 rmHumidityOutdoorHi  = 0x0B
	 rmWindspeedHi    = 0x0C
	 rmWindspeedLo    = 0x0D
	 rmGustHi         = 0x0E
	 rmGustLo         = 0x0F
	 rmPressureLo     = 0x10
	 rmPressureHi     = 0x11
	 rmRain1hHi       = 0x12
	 rmRain24hHi      = 0x13
	 rmRainLastWeekHi  = 0x14
	 rmRainLastMonthHi  = 0x15
	 rmRainTotal      = 0x16
	 rmInvalid        = 0x17

class ERequestType:
	rtGetCurrent     = 0
	rtGetHistory     = 1
	rtGetConfig      = 2
	rtSetConfig      = 3
	rtSetTime        = 4
	rtFirstConfig    = 5
	rtINVALID        = 6

#ERequestType.rtGetCurrent

class ERequestState:
	rsQueued         = 0
	rsRunning        = 1
	rsFinished       = 2
	rsPreamble       = 3
	rsWaitDevice     = 4
	rsWaitConfig     = 5
	rsError          = 6
	rsChanged        = 7
	rsINVALID        = 8

class CDataStore(object):

	class TTransceiverSettings:
		VendorId	= 0x6666
		ProductId	= 0x5555
		VersionNo	= 1
		Frequency	= 905000000
		manufacturer	= "LA CROSSE TECHNOLOGY"
		product		= "Weather Direct Light Wireless Device"

	class TRequest:
		Type = 6
		State = 6
		TTL = 90000
		Lock = 0
		CondFinish = 0

	class TLastStat:
		LastBatteryStatus = None
		LastHistoryIndex = 0
		LastLinkQuality = 0
		OutstandingHistorySets = 0
		WeatherClubTransmissionErrors = 0
		LastCurrentWeatherTime = None
		LastHistoryDataTime = None
		LastConfigTime = None
		LastWeatherClubTransmission = None

	class TSettings:
		CommModeInterval = 4
		DeviceId = None
		DeviceRegistered = False
		PreambleDuration = 5000
		RegisterWaitTime = 20000
		TransceiverIdChanged = None
		TransceiverID = None

	TransceiverSerNo = None
	TransceiveID = None

	isService = 0
	Guards = 0;
	HistoryData = 0;
	Flags = 0;
	Settings = 0;
	TransceiverSettings = 0;
	WeatherClubSettings = 0;
	LastSeen = 0;
	CurrentWeather = 0;
	DeviceConfig = 0;
	FrontEndConfig = 0;
	LastStat = 0;
	Request = 0;

	LastHistTimeStamp = 0;
	BufferCheck = 0;

	def __init__(self,_isService):
		self.logger = logging.getLogger('ws28xx.CDataStore')
		self.logger.debug("isservice x",_isService)
		self.Request = CDataStore.TRequest()
		self.LastStat = CDataStore.TLastStat()

		self.Settings = CDataStore.TSettings()
		self.TransceiverSettings = CDataStore.TTransceiverSettings()

		#ShelveDataStore=shelve.open("WV5DataStore",writeback=True)

		#if ShelveDataStore.has_key("Settings"):
		#	self.DataStore.Settings = ShelveDataStore["Settings"]
		#else:
		#	print ShelveDataStore.keys()
		if self.Request:
		    print "CDataStore::__init__ ok"

	#def CDataStore::getFlag<FLAG_TRANSCEIVER_SETTING_CHANGE> <4>

	def getFlag_FLAG_FAST_CURRENT_WEATHER(self):		# <2>
		return self.Flags_FLAG_SERVICE_RUNNING

	def getFlag_FLAG_TRANSCEIVER_PRESENT(self):		# <0>
		return self.Flags_FLAG_TRANSCEIVER_PRESENT

	#def CDataStore::getFlag<FLAG_SERVICE_RUNNING>		# <3>

	#def setFlag<FLAG_TRANSCEIVER_SETTING_CHANGE>:		# <4>
		#std::bitset<5>::set(thisa->Flags, 4u, val);

	#def CDataStore::setFlag<FLAG_FAST_CURRENT_WEATHER>#	 <2>
		#std::bitset<5>::set(thisa->Flags, 2u, val);

	def setFlag_FLAG_TRANSCEIVER_PRESENT(self,val):		# <0>
		#std::bitset<5>::set(thisa->Flags, 0, val);
		self.Flags_FLAG_TRANSCEIVER_PRESENT = val
		self.Flags = setBitVal(self.Flags,0,val)

	def setFlag_FLAG_SERVICE_RUNNING(self,val):		# <3>
		#std::bitset<5>::set(thisa->Flags, 3u, val);
		self.Flags_FLAG_SERVICE_RUNNING = val
		self.Flags = setBitVal(self.Flags,3,val)

	def RequestNotify(self):
		self.logger.debug("RequestNotify - implement me")
		self.Request.CondFinish = 1

	def operator(self):
		return (self.Guards
		   and self.HistoryData
		   and self.Flags
		   and self.Settings
		   and self.TransceiverSettings
		   and self.WeatherClubSettings
		   and self.LastSeen
		   and self.CurrentWeather
		   and self.DeviceConfig
		   and self.FrontEndConfig
		   and self.LastStat
		   and self.Request
		   and self.LastHistTimeStamp
		   and self.BufferCheck);

	def getDeviceRegistered(self):
		#print "getDeviceRegistered",self.Settings.DeviceRegistered
		return self.Settings.DeviceRegistered

	def setDeviceRegistered(self,registered):
		print "setDeviceRegistered",registered
		self.Settings.DeviceRegistered = registered;

	def setDeviceId(self,val):
		print "setDeviceId",val
		self.Settings.DeviceRegistered = val

	def getRequestType(self):
		#print "getRequestType():",self.Request.Type
		return self.Request.Type

	def getRequestState(self):
		#print "getRequestState():",self.Request.State
		return self.Request.State

	def getPreambleDuration(self):
		return self.Settings.PreambleDuration

	def getRegisterWaitTime(self):
		return self.Settings.RegisterWaitTime

	def setRequestState(self,state):
		#print "setRequestState():"
		self.Request.State = state;
		#print "DEBUG: setRequestState",self.Request.State

	def addHistoryData(self,Data):
		print "CDataStore::addHistoryData"

	def setTransceiverID(self,tid):
		print "CDataStore::setTransceiverID"
		if tid != None:
			if self.Settings.TransceiverID != None and self.Settings.TransceiverID != tid:
				self.Settings.TransceiverIdChanged = 1
				self.Settings.TransceiverID = tid
		print "CDataStore::setTransceiverID:",self.Settings.TransceiverID

	def setTransceiverSerNo(self,inp):
		print "CDataStore::setTransceiverSerNo", inp
		self.TransceiverSerNo = inp

	def setLastHistoryIndex(self,val):
		print "CDataStore::setLastHistoryIndex"
		self.LastStat.LastHistoryIndex = val
		print "DEBUG: setLastHistoryIndex",self.LastStat.LastHistoryIndex

	def getLastHistoryIndex(self):
		print "CDataStore::getLastHistoryIndex"
		#ATL::CStringT<char_ATL::StrTraitATL<char_ATL::ChTraitsCRT<char>>>::CStringT<char_ATL::StrTraitATL<char_ATL::ChTraitsCRT<char>>>(
		#    &FuncName,
		#    "unsigned int __thiscall CDataStore::getLastHistoryIndex(void) const");
		#v9 = 0;
		#  ATL::CStringT<char_ATL::StrTraitATL<char_ATL::ChTraitsCRT<char>>>::CStringT<char_ATL::StrTraitATL<char_ATL::ChTraitsCRT<char>>>(
		#    &Name,
		#    "Guards->Status");
		#  LOBYTE(v9) = 1;
		#  CScopedLock::CScopedLock(&lock, &thisa->Guards->Status, &Name, &FuncName);
		#  LOBYTE(v9) = 0;
		#  ATL::CStringT<char_ATL::StrTraitATL<char_ATL::ChTraitsCRT<char>>>::_CStringT<char_ATL::StrTraitATL<char_ATL::ChTraitsCRT<char>>>(&Name);
		#  v9 = -1;
		#  ATL::CStringT<char_ATL::StrTraitATL<char_ATL::ChTraitsCRT<char>>>::_CStringT<char_ATL::StrTraitATL<char_ATL::ChTraitsCRT<char>>>(&FuncName);
		#  v6 = thisa->LastStat->LastHistoryIndex;
		#  CScopedLock::_CScopedLock(&lock);
		print "DEBUG: getLastHistoryIndex", self.LastStat.LastHistoryIndex
		return self.LastStat.LastHistoryIndex


	def GetCurrentWeather(self):
		print "CDataStore::GetCurrentWeather"
		if 1 == 1:  #if ( CSingleInstance::IsRunning(this) && CDataStore::getFlag<0>(thisa) && CDataStore::getDeviceRegistered(thisa) )
			self.Request.Type = ERequestType.rtGetCurrent;
			self.Request.State = 0;
			self.Request.TTL = 90000;

	def GetHistory(self):
		print "CDataStore::GetHistory"
		if 1 == 1:  #if ( CSingleInstance::IsRunning(this) && CDataStore::getFlag<0>(thisa) && CDataStore::getDeviceRegistered(thisa) )
			self.Request.Type = ERequestType.rtGetHistory;
			self.Request.State = 0;
			self.Request.TTL = 90000;

	def GetConfig(self):
		print "CDataStore::GetConfig"
		if 1 == 1:  #if ( CSingleInstance::IsRunning(this) && CDataStore::getFlag<0>(thisa) && CDataStore::getDeviceRegistered(thisa) )
			self.Request.Type = ERequestType.rtGetConfig;
			self.Request.State = 0;
			self.Request.TTL = 90000;

	def SetConfig(self):
		print "CDataStore::SetConfig"
		if 1 == 1:  #if ( CSingleInstance::IsRunning(this) && CDataStore::getFlag<0>(thisa) && CDataStore::getDeviceRegistered(thisa) )
			self.Request.Type = ERequestType.rtSetConfig;
			self.Request.State = 0;
			self.Request.TTL = 90000;

	def SetTime(self):
		print "CDataStore::SetTime"
		if 1 == 1:  #if ( CSingleInstance::IsRunning(this) && CDataStore::getFlag<0>(thisa) && CDataStore::getDeviceRegistered(thisa) )
			self.Request.Type = ERequestType.rtSetTime;
			self.Request.State = 0;
			self.Request.TTL = 90000;

#CDataStore::EErrorType __thiscall CDataStore::FirstTimeConfig(CDataStore *this, unsigned int *ID, const unsigned int *TimeOut);
	def FirstTimeConfig(self): #getRegisteredWaitTime (timeout= GetRegisterWaitTime GetPreambleDuration)
		print "CDataStore::FirstTimeConfig"
		#if ( CSingleInstance::IsRunning(this) && CDataStore::getFlag<0>(thisa))
		if self.getFlag_FLAG_TRANSCEIVER_PRESENT():
			self.Settings.DeviceRegistered = 0;
			self.Settings.DeviceId = None;
			self.LastStat.LastHistoryIndex = None;
			self.LastStat.OutstandingHistorySets = None;

			self.Request.Type = ERequestType.rtFirstConfig;
			self.Request.State = 0;
			self.Request.TTL = 90000;

			self.BufferCheck = 0

			#pratiamente occupa condfinisch per il tempo del timeout intanto che il thread gira...
			#quando passa il timeout reimposta in uno stato farlocco il device
			#if 1==1:
			#if not self.Request.CondFinish: #//fixme

			#	if self.Request.State == 2:
			#		ID = CDataStore.getDeviceId(self.DataStore);
			#		self.Request.Type = 6;
			#		self.Request.State = 8;
			#		v23 = 0;
			#		v30 = -1;
			#		print "ID %x" % ID #e allora?
			#	else:
			#		self.Request.Type = 6;
			#		self.Request.State = 8;
			#		v24 = 1;
			#		v30 = -1;
			#else:
			#	self.Request.Type = 6;
			#	self.Request.State = 8;
			#	v25 = 1;
			#	v30 = -1;

	def GetDeviceConfigCS(self):
		print "CDataStore::GetDeviceConfigCS"
		#CWeatherStationConfig::CWeatherStationConfig((CWeatherStationConfig *)&v8, &result);
		#v4 = v1;
		#v3 = v1;
		#LOBYTE(v12) = 6;
		#v7 = CWeatherStationConfig::GetCheckSum((CWeatherStationConfig *)v1);
		#LOBYTE(v12) = 5;
		#CWeatherStationConfig::_CWeatherStationConfig((CWeatherStationConfig *)&v8);
		#LOBYTE(v12) = 4;
		#CWeatherStationConfig::_CWeatherStationConfig(&result);
		#v12 = -1;
		return CWeatherStationConfig.GetCheckSum()

	def RequestTick(self):
		if self.Request.Type != 6:
			self.Request.TTL -= 1
			if not self.Request.TTL:
				self.Request.Type = 6
				self.Request.State = 8
				print "internal timeout, request aborted"



class CWeatherStationConfig(object):
	_CheckSumm = 0
	_ClockMode = 0
	_TemperatureFormat = 0
	_PressureFormat = 0
	_RainFormat = 0
	_WindspeedFormat = 0
	_WeatherThreshold = 0
	_StormThreshold = 0
	_LCDContrast = 0
	_LowBatFlags = 0

	def GetCheckSum(self):
		print "CWeatherStationConfig::GetCheckSum"
		CWeatherStationConfig.CalcCheckSumm()
		#self._CheckSumm

	def CalcCheckSumm(self):
		print "CWeatherStationConfig::CalcCheckSumm"
		t = [0]*1024
		self._CheckSumm = CWeatherStationConfig.write(t);
		print "CWeatherStationConfig._CheckSumm (should be retrieved) --> ",self._CheckSumm

	def read(self,buf):
		print "CWeatherStationConfig::read"

	def readAlertFlags(self,buf):
		print "CWeatherStationConfig::readAlertFlags"

	def GetResetMinMaxFlags(self):
		print "CWeatherStationConfig::GetResetMinMaxFlags"

	def write(self,buf):
		print "CWeatherStationConfig::write (ot implemented yet)"

		#CheckSumm = 7;
		#new_buf[0] = 16 * (self._WindspeedFormat & 0xF) + 8 * (self._RainFormat & 1) + 4 * (self._PressureFormat & 1) + 2 * (self._TemperatureFormat & 1) + self._ClockMode & 1;
		#new_buf[1] = self._WeatherThreshold & 0xF | 16 * self._StormThreshold & 0xF0;
		#new_buf[2] = self._LCDContrast & 0xF | 16 * self._LowBatFlags & 0xF0;
		#CWeatherStationConfig::writeAlertFlags(buf + 3);
		#((void (__thiscall *)(CWeatherStationHighLowAlarm *))thisa->_AlarmTempIndoor.baseclass_0.baseclass_0.vfptr[1].__vecDelDtor)(&thisa->_AlarmTempIndoor);
		#v25 = v2;
		#v24 = CWeatherTraits::TemperatureOffset() + v2;
		#v21 = v24;
		#v22 = CWeatherTraits::TemperatureOffset() + CWeatherStationHighLowAlarm::GetLowAlarm(&thisa->_AlarmTempIndoor);
		#v4 = v22;
		#USBHardware::ToTempAlarmBytes(buf + 7, v22, v21);
		#((void (__thiscall *)(CWeatherStationHighLowAlarm *))thisa->_AlarmTempOutdoor.baseclass_0.baseclass_0.vfptr[1].__vecDelDtor)(&thisa->_AlarmTempOutdoor);
		#v25 = v4;
		#v24 = CWeatherTraits::TemperatureOffset() + v4;
		#v21 = v24;
		#v22 = CWeatherTraits::TemperatureOffset() + CWeatherStationHighLowAlarm::GetLowAlarm(&thisa->_AlarmTempOutdoor);
		#v6 = v22;
		#USBHardware::ToTempAlarmBytes(buf + 12, v22, v21);
		#((void (__thiscall *)(CWeatherStationHighLowAlarm *))thisa->_AlarmHumidityIndoor.baseclass_0.baseclass_0.vfptr[1].__vecDelDtor)(&thisa->_AlarmHumidityIndoor);
		#v21 = v6;
		#v8 = CWeatherStationHighLowAlarm::GetLowAlarm(&thisa->_AlarmHumidityIndoor);
		#v9 = v8;
		#USBHardware::ToHumidityAlarmBytes(buf + 17, v9, v21);
		#((void (__thiscall *)(CWeatherStationHighLowAlarm *))thisa->_AlarmHumidityOutdoor.baseclass_0.baseclass_0.vfptr[1].__vecDelDtor)(&thisa->_AlarmHumidityOutdoor);
		#v21 = v8;
		#v11 = CWeatherStationHighLowAlarm::GetLowAlarm(&thisa->_AlarmHumidityOutdoor);
		#v12 = v11;
		#USBHardware::ToHumidityAlarmBytes(buf + 19, v12, v21);
		#((void (__thiscall *)(CWeatherStationHighAlarm *))thisa->_AlarmRain24H.baseclass_0.vfptr[1].__vecDelDtor)(&thisa->_AlarmRain24H);
		#v21 = v11;
		#USBHardware::ToRainAlarmBytes(buf + 21, v21);
		#		buf[25] = thisa->_HistoryInterval & 0xF;
		#v21 = CWeatherStationWindAlarm::GetHighAlarmRaw(&thisa->_AlarmGust);
		#USBHardware::_ToWindspeedAlarmBytes(buf + 26, v21);
		#v21 = CWeatherStationHighLowAlarm::GetLowAlarm(&thisa->_AlarmPressure);
		#v21 = Conversions::ToInhg(v21);
		#v14 = CWeatherStationHighLowAlarm::GetLowAlarm(&thisa->_AlarmPressure);
		#v15 = CWeatherStationHighLowAlarm::GetLowAlarm(&thisa->_AlarmPressure);
		#USBHardware::ToPressureBytesShared(buf + 29, v15, v21);
		#((void (__thiscall *)(CWeatherStationHighLowAlarm *))thisa->_AlarmPressure.baseclass_0.baseclass_0.vfptr[1].__vecDelDtor)(&thisa->_AlarmPressure);
		#((void (__thiscall *)(CWeatherStationHighLowAlarm *))thisa->_AlarmPressure.baseclass_0.baseclass_0.vfptr[1].__vecDelDtor)(&thisa->_AlarmPressure);
		#USBHardware::ToPressureBytesShared(buf + 34, Conversions::ToInhg(CWeatherStationHighLowAlarm::GetLowAlarm(&thisa->_AlarmPressure)), Conversions::ToInhg(CWeatherStationHighLowAlarm::GetLowAlarm(&thisa->_AlarmPressure)))

		#new_buf[39] = self._ResetMinMaxFlags;
		#new_buf[40] = BYTE1(self._ResetMinMaxFlags);
		#new_buf[41] = self._ResetMinMaxFlags >> 16;

		#for ( i = 0; i < 39; ++i )
		#    CheckSumm += new_buf[i];
		#new_buf[42] = (CheckSumm >>8)  & 0xFF #BYTE1(CheckSumm);
		#new_buf[43] = (CheckSumm >>0)  & 0xFF #CheckSumm;
		buf[0] = new_buf
		return CheckSumm

class CCommunicationService(object):

	RepeatCount = True
	RepeatSize = None
	RepeatInterval = None
	RepeatTime = None #ptime

	Regenerate = 0
	GetConfig = 0

	TimeSent = 0
	TimeUpdate = 0
	TimeUpdateComplete = 0

	DataStore = None

	AX5051RegisterNames_map = dict()


	class AX5051RegisterNames:
		REVISION         = 0x0
		SCRATCH          = 0x1
		POWERMODE        = 0x2
		XTALOSC          = 0x3
		FIFOCTRL         = 0x4
		FIFODATA         = 0x5
		IRQMASK          = 0x6
		IFMODE           = 0x8
		PINCFG1          = 0x0C
		PINCFG2          = 0x0D
		MODULATION       = 0x10
		ENCODING         = 0x11
		FRAMING          = 0x12
		CRCINIT3         = 0x14
		CRCINIT2         = 0x15
		CRCINIT1         = 0x16
		CRCINIT0         = 0x17
		FREQ3            = 0x20
		FREQ2            = 0x21
		FREQ1            = 0x22
		FREQ0            = 0x23
		FSKDEV2          = 0x25
		FSKDEV1          = 0x26
		FSKDEV0          = 0x27
		IFFREQHI         = 0x28
		IFFREQLO         = 0x29
		PLLLOOP          = 0x2C
		PLLRANGING       = 0x2D
		PLLRNGCLK        = 0x2E
		TXPWR            = 0x30
		TXRATEHI         = 0x31
		TXRATEMID        = 0x32
		TXRATELO         = 0x33
		MODMISC          = 0x34
		FIFOCONTROL2     = 0x37
		ADCMISC          = 0x38
		AGCTARGET        = 0x39
		AGCATTACK        = 0x3A
		AGCDECAY         = 0x3B
		AGCCOUNTER       = 0x3C
		CICDEC           = 0x3F
		DATARATEHI       = 0x40
		DATARATELO       = 0x41
		TMGGAINHI        = 0x42
		TMGGAINLO        = 0x43
		PHASEGAIN        = 0x44
		FREQGAIN         = 0x45
		FREQGAIN2        = 0x46
		AMPLGAIN         = 0x47
		TRKFREQHI        = 0x4C
		TRKFREQLO        = 0x4D
		XTALCAP          = 0x4F
		SPAREOUT         = 0x60
		TESTOBS          = 0x68
		APEOVER          = 0x70
		TMMUX            = 0x71
		PLLVCOI          = 0x72
		PLLCPEN          = 0x73
		PLLRNGMISC       = 0x74
		AGCMANUAL        = 0x78
		ADCDCLEVEL       = 0x79
		RFMISC           = 0x7A
		TXDRIVER         = 0x7B
		REF              = 0x7C
		RXMISC           = 0x7D

	def __init__(self):
		self.logger = logging.getLogger('ws28xx.CCommunicationService')
		self.logger.debug("__init__")
		self.DataStore = CDataStore(1)
		self.Instance = self.CCommunicationService()

	def operator(self):
		self.logger.debug("operator")

	def getInstance(self):
		self.logger.debug("getInstance (partially implemented)")
		self.CCommunicationService();

	def buildTimeFrame(self,Buffer,checkMinuteOverflow):
		self.logger.debug("buildTimeFrame (not yet implemented)")

		#00000000: d5 00 0c 00 32 c0 00 8f 45 25 15 91 31 20 01 00
		#00000000: d5 00 0c 00 32 c0 06 c1 47 25 15 91 31 20 01 00
		#                             3  4  5  6  7  8  9 10 11
		#DeviceCheckSum = CDataStore::GetDeviceConfigCS
		DeviceCheckSum = 0x27f5
		now = time.time()
		tm = time.localtime(now)
		tu = time.gmtime(now)

		Second = tm[5]
		if ( checkMinuteOverflow and (Second <= 5 or Second >= 55) ):
			if ( Second < 55 ):
				Second = 6 - Second
			else:
				Second = 60 - Second + 6;
			#v11 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
			#HistoryIndex = CDataStore::getLastHistoryIndex(v11);
			#CCommunicationService::buildACKFrame(thisa, Buffer, 0, &DeviceCheckSum, &HistoryIndex, Second);
			print "buildTimeFrame #1 to be implemented"
		else:
			new_Buffer[2] = 0xc0
			new_Buffer[3] = (DeviceCheckSum >>8)  & 0xFF #BYTE1(DeviceCheckSum);
			new_Buffer[4] = (DeviceCheckSum >>0)  & 0xFF #DeviceCheckSum;
			new_Buffer[5] = (tm[5] % 10) + (0x10 * tm[5] // 10); #sec
			new_Buffer[6] = (tm[4] % 10) + (0x10 * tm[4] // 10); #min
			new_Buffer[7] = (tm[3] % 10) + (0x10 * tm[3] // 10); #hour
			DayOfWeek = tm[7] - 1;
			if ( DayOfWeek == 1 ):
				DayOfWeek = 7;
			new_Buffer[8] = DayOfWeek % 10 + (0x10 *  tm[2] % 10) #DoW + Day
			new_Buffer[9] =  (tm[2] // 10) + (0x10 *  tm[1] % 10) #day + month
			new_Buffer[10] = (tm[1] // 10) + (0x10 * (tm[0] - 2000) % 10); #month + year
			new_Buffer[11] = (tm[0] - 2000) // 10; year
			self.Regenerate = 1
			self.TimeSent = 1

	def buildConfigFrame(self,Buffer,Data):
		print "buildConfigFrame (not yet implemented)"
		Buffer[2] = 0x40;
		Buffer[3] = 0x64;
		#CWeatherStationConfig::write(Data, &(*Buffer)[4]);
		raise "buildConfigFrame: error... unimplemented"
		self.Regenerate = 0;
		self.TimeSent = 0;

	def buildACKFrame(self,Buffer, Action, CheckSum, HistoryIndex, ComInt):
		print "buildACKFrame (not yet implemented)"
#			if ( !Action && ComInt == -1 ):
#				v28 = 0;
#				if ( !Stat.LastCurrentWeatherTime.m_status ):
#				ATL::COleDateTime::operator_(&now, &ts, &Stat.LastCurrentWeatherTime);
#				if ( ATL::COleDateTimeSpan::GetTotalSeconds(&ts) >= 8.0 )
#					Action = 5;
#				v28 = -1;
#			Buffer[2] = Action & 0xF;
#			v7 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
#			v21 = CDataStore::GetDeviceConfigCS(v7);
#			if ( HistoryIndex >= 0x705 ):
#				HistoryAddress = -1;
#			else:
#			{
#				v8 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
#				if ( !CDataStore::getBufferCheck(v8) )
#				{
#				if ( !ATL::COleDateTime::GetStatus(&Stat.LastHistoryDataTime) )
#				{
#					v9 = ATL::COleDateTime::operator_(&now, &result, &Stat.LastHistoryDataTime);
#					if ( ATL::COleDateTimeSpan::operator>(v9, &BUFFER_OVERFLOW_SPAN) )
#					{
#					val = 1;
#					v10 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
#					CDataStore::setBufferCheck(v10, &val);
#					}
#				}
#				}
#				v11 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
#				if ( CDataStore::getBufferCheck(v11) != 1
#				&& (v12 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore), CDataStore::getBufferCheck(v12) != 2) )
#				{
#				HistoryAddress = 18 * *HistoryIndex + 0x1a0;
#				}
#				else
#				{
#				if ( *HistoryIndex )
#					HistoryAddress = 18 * (*HistoryIndex - 1) + 0x1a0;
#				else
#					HistoryAddress = 0x7fe8;
#				v20 = 2;
#				v13 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
#				CDataStore::setBufferCheck(v13, (CDataStore::TBufferCheck *)&v20);
#				}
#			}
#			(*Buffer)[3] = *(_WORD *)CheckSum >> 8;
#			(*Buffer)[4] = *(_BYTE *)CheckSum;
#			if ( ComInt == -1 )
#			{
#				v14 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
#				ComInt = CDataStore::getCommModeInterval(v14);
#			}
#			(Buffer)[5] = ComInt >> 4;
#			(Buffer)[6] = (HistoryAddress >> 16) & 0xF | 16 * (ComInt & 0xF);
#			(Buffer)[7] = BYTE1(HistoryAddress);
#			(Buffer)[8] = HistoryAddress;
#			thisa->Regenerate = 0;
#		thisa->TimeSent = 0;
	

	def handleWsAck():
		print "handleWsAck (not yet implemented)"

	def handleConfig(self,Buffer,Length):
		print "handleConfig (not yet implemented)"
		diff = 0;
		#j__memcpy(t, (char *)Buffer, *Length);
		#CWeatherStationConfig::CWeatherStationConfig(&c, &t[4]);
		#v73 = 0;
		#j__memset(t, -52, *Length);
		#CWeatherStationConfig::write(&c, &t[4]);
		#USBHardware::ReverseByteOrder(&t[7], 4u);
		#USBHardware::ReverseByteOrder(&t[11], 5u);
		#USBHardware::ReverseByteOrder(&t[16], 5u);
		#USBHardware::ReverseByteOrder(&t[21], 2u);
		#USBHardware::ReverseByteOrder(&t[23], 2u);
		#USBHardware::ReverseByteOrder(&t[25], 4u);
		#USBHardware::ReverseByteOrder(&t[30], 3u);
		#USBHardware::ReverseByteOrder(&t[33], 5u);
		#USBHardware::ReverseByteOrder(&t[38], 5u);
		#for ( i = 4; i < 0x30; ++i )
		#{
		#	if ( t[i] != (*Buffer)[i] )
		#	{
		#		c1 = (char *)(unsigned __int8)t[i];
		#		c2 = (*Buffer)[i];
		#		v43 = c2;
		#		v42 = c1;
		#		v41.baseclass_0.m_pszData = (char *)i;
		#		v3 = CTracer::Instance();
		#		CTracer::WriteTrace(
		#				#v3,
		#				#30,
		#				#"Generated config differs from received in byte#: %02i generated = %04x		#rececived = %04x");
		#		diff = 1;
		#	}
		#}
		#if ( diff )
		#{
		#		#v43 = *Length;
		#		#v42 = t;
		#		#v41.baseclass_0.m_pszData = (char *)v43;
		#		#v47 = &v41;
		#		#ATL::CStringT<char_ATL::StrTraitATL<char_ATL::ChTraitsCRT<char>>>::CStringT<char_ATL::StrTraitATL<char_ATL::ChTraitsCRT<char>>>(
		#		#		#&v41,
		#		#		#"Config_Gen");
		#		#v46 = v4;
		#		#rhs = v4;
		#		#LOBYTE(v73) = 1;
		#		#v5 = CTracer::Instance();
		#		#LOBYTE(v73) = 0;
		#		#CTracer::WriteDump(v5, 30, v41, v42, v43);
		#		#v43 = *Length;
		#		#v42 = (char *)Buffer;
		#		#v41.baseclass_0.m_pszData = (char *)v43;
		#		#v48 = &v41;
		#		#ATL::CStringT<char_ATL::StrTraitATL<char_ATL::ChTraitsCRT<char>>>::CStringT<char_ATL::StrTraitATL<char_ATL::ChTraitsCRT<char>>>(
		#		#		#&v41,
		#		#		#"Config_Rec");
		#		#v46 = v6;
		#		#rhs = v6;
		#		#LOBYTE(v73) = 2;
		#		#v7 = CTracer::Instance();
		#		#LOBYTE(v73) = 0;
		#		#CTracer::WriteDump(v7, 30, v41, v42, v43);
		#}
		#v73 = -1;
		#CWeatherStationConfig::_CWeatherStationConfig(&c);
		#CWeatherStationConfig::CWeatherStationConfig(&RecConfig, &(*Buffer)[4]);
		#v73 = 3;
		if 1==1: #hack ident
		#if ( CWeatherStationConfig::operator bool(&RecConfig) )
		#{
			rt = CDataStore.getRequestType(self.DataStore);
		#	#ATL::COleDateTime::GetTickCount(&now);
		#	#v43 = (CDataStore::ERequestState)&now;
		#	#v9 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
		#	#CDataStore::setLastSeen(self.DataStore, (ATL::COleDateTime *)v43);
		#	#v43 = (*Buffer)[2] & 0xF;
		#	std::bitset<4>::bitset<4>(&BatteryStat, v43);
		#	#v43 = (CDataStore::ERequestState)&BatteryStat;
		#	#CDataStore::setLastBatteryStatus(self.DataStore, (std::bitset<4> *)v43);
		#	#Quality = (*Buffer)[3] & 0x7F;
		#	#v43 = (CDataStore::ERequestState)&Quality;
		#	#CDataStore::setLastLinkQuality(v11, (const unsigned int *)v43);
		#	#FrontCS = CDataStore::GetFrontEndConfigCS(self.DataStore);
		#	HistoryIndex = CDataStore.getLastHistoryIndex(self.DataStore);
		#	#v46 = (CWeatherStationConfig *)rt;
		#		#switch ( rt )
		#		#{
			if 1==1: #hack ident
				if   rt == 3:
					print "handleConfig rt==3"
		#		#			#v43 = (CDataStore::ERequestState)&result;
		#		#			#v14 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
		#		#			#v46 = CDataStore::getFrontEndConfig(v14, (CWeatherStationConfig *)v43);
		#		#			#rhs = v46;
		#		#			#LOBYTE(v73) = 4;
		#		#			#v51 = CWeatherStationConfig::operator__(&RecConfig, v46);
		#		#			#LOBYTE(v73) = 3;
		#		#			#CWeatherStationConfig::_CWeatherStationConfig(&result);
		#		#			#if ( v51 )
		#		#			#{
		#		#			#		#*Length = CCommunicationService::buildACKFrame(thisa, Buffer, 0, &FrontCS, &HistoryIndex, 0xFFFFFFFFu);
		#		#			#		#v43 = (CDataStore::ERequestState)&now;
		#		#			#		#v15 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
		#		#			#		#CDataStore::setLastConfigTime(v15, (ATL::COleDateTime *)v43);
		#		#			#		#v43 = (CDataStore::ERequestState)&RecConfig;
		#		#			#		#v16 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
		#		#			#		#CDataStore::setDeviceConfig(v16, (CWeatherStationConfig *)v43);
		#		#			#		#v43 = 2;
		#		#			#		#v17 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
		#		#			#		#CDataStore::setRequestState(v17, v43);
		#		#			#		#v18 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
		#		#			#		#CDataStore::RequestNotify(v18);
		#		#			#}
		#		#			#else
		#		#			#{
		#		#			#		#CheckSum = CWeatherStationConfig::GetCheckSum(&RecConfig);
		#		#			#		#*Length = CCommunicationService::buildACKFrame(thisa, Buffer, 2, &CheckSum, &HistoryIndex, 0xFFFFFFFFu);
		#		#			#		#v43 = 1;
		#		#			#		#v19 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
		#		#			#		#CDataStore::setRequestState(v19, v43);
		#		#			#}
		#		#			#break;
				#elif rt == 2:
		#		#		#		#v43 = (CDataStore::ERequestState)&now;
		#		#		#		#v20 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
		#		#		#		#CDataStore::setLastConfigTime(v20, (ATL::COleDateTime *)v43);
		#		#		#		#v43 = (CDataStore::ERequestState)&RecConfig;
		#		#		#		#v21 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
		#		#		#		#CDataStore::setDeviceConfig(v21, (CWeatherStationConfig *)v43);
		#		#		#		#v54 = CWeatherStationConfig::GetCheckSum(&RecConfig);
		#		#		#		#*Length = CCommunicationService::buildACKFrame(thisa, Buffer, 0, &v54, &HistoryIndex, 0xFFFFFFFFu);
		#		#		#		#v43 = 2;
		#		#		#		#v22 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
		#		#		#		#CDataStore::setRequestState(v22, v43);
		#		#		#		#v23 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
		#		#		#		#CDataStore::RequestNotify(v23);
		#		#		#		#break;
				#elif rt == 0:
		#		#		#		#v43 = (CDataStore::ERequestState)&now;
		#		#		#		#v24 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
		#		#		#		#CDataStore::setLastConfigTime(v24, (ATL::COleDateTime *)v43);
		#		#		#		#v43 = (CDataStore::ERequestState)&RecConfig;
		#		#		#		#v25 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
		#		#		#		#CDataStore::setDeviceConfig(v25, (CWeatherStationConfig *)v43);
		#		#		#		#v55 = CWeatherStationConfig::GetCheckSum(&RecConfig);
		#		#		#		#*Length = CCommunicationService::buildACKFrame(thisa, Buffer, 5, &v55, &HistoryIndex, 0xFFFFFFFFu);
		#		#		#		#v43 = 1;
		#		#		#		#v26 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
		#		#		#		#CDataStore::setRequestState(v26, v43);
		#		#		#		#break;
				#elif rt == 1:
		#		#		#		#v43 = (CDataStore::ERequestState)&now;
		#		#		#		#v27 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
		#		#		#		#CDataStore::setLastConfigTime(v27, (ATL::COleDateTime *)v43);
		#		#		#		#v43 = (CDataStore::ERequestState)&RecConfig;
		#		#		#		#v28 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
		#		#		#		#CDataStore::setDeviceConfig(v28, (CWeatherStationConfig *)v43);
		#		#		#		#v56 = CWeatherStationConfig::GetCheckSum(&RecConfig);
		#		#		#		#*Length = CCommunicationService::buildACKFrame(thisa, Buffer, 4, &v56, &HistoryIndex, 0xFFFFFFFFu);
		#		#		#		#v43 = 1;
		#		#		#		#v29 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
		#		#		#		#CDataStore::setRequestState(v29, v43);
		#		#		#		#break;
				#elif rt == 4:
		#		#		#		#v43 = (CDataStore::ERequestState)&now;
		#		#		#		#v30 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
		#		#		#		#CDataStore::setLastConfigTime(v30, (ATL::COleDateTime *)v43);
		#		#		#		#v43 = (CDataStore::ERequestState)&RecConfig;
		#		#		#		#v31 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
		#		#		#		#CDataStore::setDeviceConfig(v31, (CWeatherStationConfig *)v43);
		#		#		#		#v57 = CWeatherStationConfig::GetCheckSum(&RecConfig);
		#		#		#		#*Length = CCommunicationService::buildACKFrame(thisa, Buffer, 1, &v57, &HistoryIndex, 0xFFFFFFFFu);
		#		#		#		#v43 = 1;
		#		#		#		#v32 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
		#		#		#		#CDataStore::setRequestState(v32, v43);
		#		#		#		#break;
				elif rt == 5:
					print "handleConfig rt==5"
		#		#	#v43 = (CDataStore::ERequestState)&now;
		#		#	#CDataStore::setLastConfigTime(self.DataStore, (ATL::COleDateTime *)v43);
		#		#	#v43 = (CDataStore::ERequestState)&RecConfig;
		#		#	#CDataStore::setDeviceConfig(self.DataStore, (CWeatherStationConfig *)v43);
		#		#	#v58 = CWeatherStationConfig::GetCheckSum(&RecConfig);
		#		#	#*Length = CCommunicationService::buildACKFrame(thisa, Buffer, 0, &v58, &HistoryIndex, 0xFFFFFFFFu);
		#		#	#CDataStore::setRequestState(self.DataStore, 2);
		#		#	#CDataStore::RequestNotify(self.DataStore);
				#elif rt == 6:
		#		#	#v43 = (CDataStore::ERequestState)&now;
		#		#	#CDataStore::setLastConfigTime(self.DataStore, (ATL::COleDateTime *)v43);
		#		#	#v43 = (CDataStore::ERequestState)&RecConfig;
		#		#	#CDataStore::setDeviceConfig(self.DataStore, (CWeatherStationConfig *)v43);
		#		#	#v59 = CWeatherStationConfig::GetCheckSum(&RecConfig);
		#		#	#*Length = CCommunicationService::buildACKFrame(thisa, Buffer, 0, &v59, &HistoryIndex, 0xFFFFFFFFu);
		#		#	break;
				#else:
		#		#	break;
		#}
		#else
		#{
		#		#*Length = 0;
		#}
		#v73 = -1;
		#CWeatherStationConfig::_CWeatherStationConfig(&RecConfig);


	def handleCurrentData():
		print "handleCurrentData (not yet implemented)"
#			rtGetCurrent     = 0
#			rtGetHistory     = 1
#			rtGetConfig      = 2
#			rtSetConfig      = 3
#			rtSetTime        = 4
#			rtFirstConfig    = 5
#			rtINVALID        = 6
		if   rt == 0: #rtGetCurrent
			print "0"
			#self.buildACKFrame(Buffer, 0, &DeviceCS, &HistoryIndex, 0xFFFFFFFFu);
		elif rt == 1:
			print "1"
		elif rt == 2:
			print "2"
		elif rt == 3:
			print "3"
		elif rt == 4:
			print "4"
		elif rt == 5:
			print "5"
		elif rt == 6:
			print "6"

	def handleHistoryData():
		print "handleHistoryData (not yet implemented)"

	def handleNextAction(self,Buffer,Length):
		print "handleNextAction (not yet implemented)"

		print "handleNextAction:: Buffer[0] %x" % Buffer[0]
		print "handleNextAction:: Buffer[1] %x" % Buffer[1]
		print "handleNextAction:: Buffer[2] %x (CWeatherStationConfig *)" % (Buffer[2] & 0xF)
		#ATL::COleDateTime::GetTickCount(&now);
		#v3 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
		#rt = CDataStore::getRequestType(v3);
		rt = CDataStore.getRequestType(self.DataStore)
		#v4 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
		#HistoryIndex = CDataStore::getLastHistoryIndex(v4);
		#v5 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
		#DeviceCS = CDataStore::GetDeviceConfigCS(v5);
		#v6 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
		#CDataStore::setLastSeen(v6, &now);
		Quality = Buffer[3] & 0x7F;
		print "Quality %d" % Quality
		#v7 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
		#CDataStore::setLastLinkQuality(v7, &Quality);
		if (Buffer[2] & 0xF) == 2: #(CWeatherStationConfig *)
			print "handleNextAction Buffer[2] == 2"
		#	v8 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
		#	v16 = CDataStore::getFrontEndConfig(v8, &result);
		#	Data = v16;
		#	v24 = 0;
			Length = self.buildConfigFrame(Buffer, v16);
		#	v24 = -1;
		#	CWeatherStationConfig::_CWeatherStationConfig(&result);
		else:
			print "handleNextAction Buffer[2] == 3"
			if (Buffer[2] & 0xF) == 3: #(CWeatherStationConfig *)
				Length = self.buildTimeFrame(Buffer, 1);
			else:
				DeviceCS = [None]
				HistoryIndex = [None]
				if rt == 2:
					Length = self.buildACKFrame(Buffer, 3, DeviceCS, HistoryIndex, 0xFFFFFFFF);
					#v9 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
					CDataStore.setRequestState(self.DataStore, ERequestState.rsRunning);
				elif rt == 0:
					Length = self.buildACKFrame(Buffer, 5, DeviceCS, HistoryIndex, 0xFFFFFFFF);
					#v10 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
					CDataStore.setRequestState(self.DataStore, ERequestState.rsRunning);
				elif rt == 1:
					Length = self.buildACKFrame(Buffer, 4, DeviceCS, HistoryIndex, 0xFFFFFFFF);
					#v11 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
					CDataStore.setRequestState(self.DataStore, ERequestState.rsRunning);
				elif rt == 3:
					Length = self.buildACKFrame(Buffer, 2, DeviceCS, HistoryIndex, 0xFFFFFFFF);
					#v12 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
					CDataStore.setRequestState(self.DataStore, ERequestState.rsRunning);
				elif rt == 4:
					Length = self.buildACKFrame(Buffer, 1, DeviceCS, HistoryIndex, 0xFFFFFFFF);
					#v13 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
					CDataStore.setRequestState(self.DataStore, ERequestState.rsRunning);
				else:
					#v14 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
					if ( CDataStore.getFlag<2>(self.DataStore) ):
						Length = self.buildACKFrame(Buffer, 5, DeviceCS, HistoryIndex, 0xFFFFFFFF);
					else:
						Length = self.buildACKFrame(Buffer, 0, DeviceCS, HistoryIndex, 0xFFFFFFFF);
		raise "xxx"

	def CCommunicationService(self):
		print "CDataStore.operator: CDataStore.operator(self.DataStore)"
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.IFMODE]     = 0x00;
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.MODULATION] = 0x41;
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.ENCODING]   = 0x07;
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.FRAMING]    = 0x84;
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.CRCINIT3]   = 0xff;
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.CRCINIT2]   = 0xff;
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.CRCINIT1]   = 0xff;
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.CRCINIT0]   = 0xff;
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.FREQ3]      = 0x38;
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.FREQ2]      = 0x90;
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.FREQ1]      = 0x00;
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.FREQ0]      = 0x01;
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.PLLLOOP]    = 0x1d;
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.PLLRANGING] = 0x08;
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.PLLRNGCLK]  = 0x03;
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.MODMISC]    = 0x03;
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.SPAREOUT]   = 0x00;
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.TESTOBS]    = 0x00;
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.APEOVER]    = 0x00;
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.TMMUX]      = 0x00;
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.PLLVCOI]    = 0x01;
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.PLLCPEN]    = 0x01;
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.RFMISC]     = 0xb0;
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.REF]        = 0x23;
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.IFFREQHI]   = 0x20;
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.IFFREQLO]   = 0x00;
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.ADCMISC]    = 0x01;
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.AGCTARGET]  = 0x0e;
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.AGCATTACK]  = 0x11;
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.AGCDECAY]   = 0x0e;
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.CICDEC]     = 0x3f;
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.DATARATEHI] = 0x19;
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.DATARATELO] = 0x66;
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.TMGGAINHI]  = 0x01;
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.TMGGAINLO]  = 0x96;
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.PHASEGAIN]  = 0x03;
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.FREQGAIN]   = 0x04;
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.FREQGAIN2]  = 0x0a;
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.AMPLGAIN]   = 0x06;
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.AGCMANUAL]  = 0x00;

		self.AX5051RegisterNames_map[self.AX5051RegisterNames.ADCDCLEVEL] = 0x10;
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.RXMISC]     = 0x35;
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.FSKDEV2]    = 0x00;
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.FSKDEV1]    = 0x31;
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.FSKDEV0]    = 0x27;
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.TXPWR]      = 0x03;
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.TXRATEHI]   = 0x00;
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.TXRATEMID]  = 0x51;
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.TXRATELO]   = 0xec;
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.TXDRIVER]   = 0x88;
		print "Here I should start the rf thread"
		child = threading.Thread(target=self.doRFCommunication)
		child.start()

	def caluculateFrequency(self,Frequency):
		#print "CCommunicationService::caluculateFrequency"
		FreqVal =  long(Frequency / 16000000.0 * 16777216.0);
		FreqCorrection = [None]
		if sHID.ReadConfigFlash(0x1F5, 4, FreqCorrection):
			CorVal = FreqCorrection[0][0] << 8;
			CorVal |= FreqCorrection[0][1];
			CorVal <<= 8;
			CorVal |= FreqCorrection[0][2];
			CorVal <<= 8;
			CorVal |= FreqCorrection[0][3];
			FreqVal += CorVal;
		if ( not (FreqVal % 2) ):
			FreqVal+=1;
			self.AX5051RegisterNames_map[self.AX5051RegisterNames.FREQ3] = (FreqVal >>24) & 0xFF;
			#print "dd %x" % (self.AX5051RegisterNames_map[self.AX5051RegisterNames.FREQ3])
			self.AX5051RegisterNames_map[self.AX5051RegisterNames.FREQ2] = (FreqVal >>16) & 0xFF;
			#print "dd %x" % (self.AX5051RegisterNames_map[self.AX5051RegisterNames.FREQ2])
			self.AX5051RegisterNames_map[self.AX5051RegisterNames.FREQ1] = (FreqVal >>8)  & 0xFF;
			#print "dd %x" % (self.AX5051RegisterNames_map[self.AX5051RegisterNames.FREQ1])
			self.AX5051RegisterNames_map[self.AX5051RegisterNames.FREQ0] = (FreqVal >>0)  & 0xFF;
			#print "dd %x" % (self.AX5051RegisterNames_map[self.AX5051RegisterNames.FREQ0])
		#print "CCommunicationService::caluculateFrequency - end"

	def GenerateResponse(self,Buffer,Length):
		self.logger.debug("GenerateResponse (not fully implemented yet)")
		#if Length[0] == 0:
		#    print "CCommunicationService->Buffer=[None]"
		#else:
		#    print "CCommunicationService->Buffer=",Buffer
		
		newBuffer = Buffer[0]
		if Length[0] != 0:
			RequestType = CDataStore.getRequestType(self.DataStore)
			print "CCommunicationService::RequestType",RequestType
			if CDataStore.getDeviceRegistered(self.DataStore):

				RegisterdID = CDataStore.getDeviceId(self.DataStore)
				ID = (Buffer[0][0] <<8)| Buffer[0][1]
				print "RegisteredID: %x ID:%x" % (RegisterdID,ID)

				if ID == RegisterdID:
					print ((Buffer[0][2] & 0xE0) - 0x20)
					responseType = (Buffer[0][2] & 0xE0) - 0x20
					print "Length %x RegisteredID x%x responseType: x%x" % (Length[0], RegisteredID, responseType)
					if responseType == 0x00:
						#    00000000: 00 00 06 00 32 20
						if Length[0] == 0x06:
							self.handleWsAck(newBuffer, Length[0]);
						else:
							newLength = 0
					elif responseType == 0x20:
						#    00000000: 00 00 30 00 32 40
						if Length[0] == 0x30:
							self.handleConfig(newBuffer, Length[0]);
						else:
							newLength = 0
					elif responseType == 0x40:
						#    00000000: 00 00 d7 00 32 60
						if Length[0] == 0xd7:
							self.handleCurrentData(newBuffer, Length[0]);
						else:
							newLength = 0
					elif responseType == 0x60:
						#    00000000: 00 00 1e 00 32 80
						if Length[0] == 0x1e:
							self.handleHistoryData(newBuffer, Length[0]);
						else:
							newLength = 0
					elif responseType == 0x80:
						#    00000000: 00 00 06 f0 f0 a1
						#    00000000: 00 00 06 00 32 a3
						#    00000000: 00 00 06 00 32 a2
						if Length[0] == 0x06:
							self.handleNextAction(newBuffer, Length[0]);
						else:
							newLength = 0
					else:
						newLength = 0

			
				else:
					newLength = 0
			else:
				if RequestType == 5:
					buffer = [None]
					sHID.ReadConfigFlash(0x1fe, 2, buffer);
					#    00000000: dd 0a 01 fe 18 f6 aa 01 2a a2 4d 00 00 87 16 
					TransceiverID = buffer[0][0] << 8;
					TransceiverID += buffer[0][1];
					print "GenerateResponse: TransceiverID", TransceiverID
					print "GenerateResponse: Length[0]",Length[0]
					print "Buffer[0]", Buffer[0]
					if (    Length[0]            !=    6
					    or  Buffer[0][0]         != 0xf0
					    or  Buffer[0][1]         != 0xf0
					    or (Buffer[0][2] & 0xe0) != 0xa0
					    or (Buffer[0][2] & 0x0f) != 1 ):
						ReceivedId  = Buffer[0][0] <<8;
						ReceivedId += Buffer[0][1];
						print "GenerateResponse: ReceivedId",ReceivedId
						if ( Length[0] != 6 or ReceivedId != TransceiverID or (Buffer[0][2] & 0xE0) != 0xa0 or (Buffer[0][2] & 0xF) != 3 ):
							if ( Length[0] != 48
							 or ReceivedId != TransceiverID
							 or (Buffer[0][2] & 0xE0) != 0x40
							 or CDataStore.getRequestState(self.DataStore) != 5):
								newLength = 0;
							else:
								if Length[0] == 9:
									CDataStore.setDeviceId(self.DataStore,TransceiverID);
									CDataStore.setDeviceRegistered(self.DataStore, True);
						else:
							newLength = self.buildTimeFrame(Buffer,1);

						newLength = 0
					else:
						print "run handleConfig..."
						newLength = Length[0]
						newBuffer = Buffer[0]
						self.handleConfig(newBuffer, newLength);
				else:
					newLength = 0
		else:
			self.logger.debug("GetRequestState try to repeat (implement me)")
			#print "repeatCount",self.RepeatCount
			if self.RepeatCount:
				#print "RS:RepeatCount = ",self.RepeatCount
				if 2 == 1:
				#if self.RepeatTime > microsec_clock::universal_time:
					if self.Regenerate:
						newLength = self.buildTimeFrame(Buffer,1);
					else:
						print "implementami - copia data su buffer"
						#Buffer = self.RepeatData, self.RepeatSize
			#else:
			#	print "RS:RepeatCount = ",self.RepeatCount
			time.sleep(0.2)
			newLength = 0

		Buffer[0] = newBuffer
		Length[0] = newLength
		if newLength == 0:
			return 0
		return 1

			
#CDataStore.setRequestState(self.DataStore, ERequestState.

		#_RTC_CheckStackVars();
		#return j___RTC_CheckEsp();

	def TransceiverInit(self):
		#print "CCommunicationService::TransceiverInit"
		print "CCommunicationService::TransceiverInit (partially implemented)"

		t=CDataStore.TTransceiverSettings
		self.caluculateFrequency(t.Frequency);

		buffer = [None]
		if ( sHID.ReadConfigFlash(0x1F9, 7, buffer) ):
			ID  = buffer[0][5] << 8;
			ID += buffer[0][6];
			print "CCommunicationService::TransceiverInit TransceiverID 0x%x" % ID

			SN  = buffer[0][0] << 48
			SN += buffer[0][1] << 40
			SN += buffer[0][2] << 32
			SN += buffer[0][3] << 24
			SN += buffer[0][4] << 16
			SN += buffer[0][5] << 8
			SN += buffer[0][6] << 0
			#print "CCommunicationService::TransceiverInit setTransceiverSerNo %s - ????" % SN
			CDataStore.setTransceiverSerNo(self.DataStore,hex(SN))

			for i, Register in enumerate(self.AX5051RegisterNames_map):
				sHID.WriteReg(Register,self.AX5051RegisterNames_map[Register])

			if sHID.Execute(5):
				sHID.SetPreamblePattern(0xaa)
				if sHID.SetState(0):
					#print "fixme: subsecond duration" //fixme
					if sHID.SetRX():
						v67 = 1  #//fixme:and so?
						v78 = -1 #//fixme:and so?

		#raise NotImplementedError()
		#raise ws28xxError("not implemented yet")

		#security_check_cookie

	def doRFCommunication(self):
		import usb
		print "CCommunicationService::doRFCommunication"

		TransceiverSettings=CDataStore.TTransceiverSettings
		device = sHID.Find(TransceiverSettings.VendorId,TransceiverSettings.ProductId,TransceiverSettings.VersionNo)
		if device:
			self.TransceiverInit()
			CDataStore.setFlag_FLAG_TRANSCEIVER_PRESENT(self.DataStore, 1);
			sHID.SetRX()
		else:
			raise "no ws"
		ReceiverState = 0 #cancellami
		while True:
			RequestType = CDataStore.getRequestType(self.DataStore)
			self.logger.debug("RequestType = %d" % RequestType)
			if RequestType == ERequestType.rtFirstConfig: # ==5
				RequestState = CDataStore.getRequestState(self.DataStore)
				self.logger.debug("RequestState #1 = %d" % RequestState)
				if RequestState == ERequestState.rsWaitDevice: # == 4
					self.logger.debug("self.getRequestState == 4")
					if DeviceWaitEndTime <= datetime.now():
						CDataStore.setRequestState(self.DataStore,ERequestState.rsError);
						CDataStore.RequestNotify(self.DataStore);
				else:
					sHID.SetPreamblePattern(0xaa)
					sHID.SetState(0x1e)
					self.logger.debug("sHID.SetState(0x1e)")
					CDataStore.setRequestState(self.DataStore,ERequestState.rsPreamble)
					PreambleDuration = CDataStore.getPreambleDuration(self.DataStore);
					PreambleEndTime = datetime.now() + timedelta(microseconds=PreambleDuration)
					while True:
						if not ( PreambleEndTime >= datetime.now() ):
							break
						if RequestType != CDataStore.getRequestType(self.DataStore):
							break
						CDataStore.RequestTick(self.DataStore);
						time.sleep(0.0001) #(thread
						CDataStore.setFlag_FLAG_SERVICE_RUNNING(self.DataStore, True);

					if RequestType == CDataStore.getRequestType(self.DataStore):
						CDataStore.setRequestState(self.DataStore,ERequestState.rsWaitDevice)
						RegisterWaitTime = CDataStore.getRegisterWaitTime(self.DataStore)
						DeviceWaitEndTime = datetime.now() + timedelta(microseconds=RegisterWaitTime)
					ret = sHID.SetRX(); #make state from 14 to 15

			DataLength = [0]
			DataLength[0] = 0
			StateBuffer = [None]
			ret = sHID.GetState(StateBuffer);
			if ret == 1:
				FrameBuffer=[0]
				FrameBuffer[0]=[0]*0x03
				ReceiverState = StateBuffer[0][0];
				if ReceiverState == 0x16:
					ret = sHID.GetFrame(FrameBuffer, DataLength);
					if ret == None:
						raise ws28xxError("USBDevice->GetFrame returned false")
					if DataLength[0]:
						print "Receiverstate = 22 - I don't understand what do do..."
						v24 = DataLength;
						v23 = FrameBuffer;
						#v22.baseclass_0.m_pszData = FrameBuffer;
						#v43 = &v22;
						#CTracer::WriteDump((CTracer *)td, 50, v22, v23, v24);
				rel_time = self.GenerateResponse(FrameBuffer, DataLength); #// return 0 no error, return 1 runtime error
										# this one prepare the ackframe  
				if rel_time == 1:
					if DataLength[0] != 0:
						v24 = DataLength;
						v23 = FrameBuffer;
						#v22.baseclass_0.m_pszData = FrameBuffer;
						#v44 = &v22;
						#ATL::CStringT<char_ATL::StrTraitATL<char_ATL::ChTraitsCRT<char>>>::CStringT<char_ATL::StrTraitATL<char_ATL::ChTraitsCRT<char>>>(
						#  &v22,
						#  "Tra");
						#rel_time = v14;
						#v29 = v14;
						#LOBYTE(v67) = 4;
						#td = (boost::posix_time::time_duration *)CTracer::Instance();
						#LOBYTE(v67) = 0;
						#CTracer::WriteDump((CTracer *)td, 50, v22, v23, v24);
					sHID.SetState(0);
					ret = sHID.SetFrame(FrameBuffer[0], DataLength[0]); # send the ackframe prepared by GenerateResponse
					if ret == None:
						print "USBDevice->SetFrame returned false"  #it shouldn't be blocking
						#goto LABEL_49
					ret = sHID.SetTX();
					if ret == None:
						print ws28xxError("USBDevice->SetTX returned false")  #it shouldn't be blocking
						#goto LABEL_49
					ReceiverState = 0xc8;
					timeout = 1000;
					while True:
						print "sono sull'while stronzo"
						ret = sHID.GetState(StateBuffer);
						if ret == None:
							raise "USBDevice->GetState returned false" #it shouldn't be blocking
						ReceiverState = StateBuffer[0];
						if ( not StateBuffer[0]) or (ReceiverState == 0x15 ):
#LABEL_42	
							if (timeout >= 0) and self.RepeatCount:
								self.RepeatCount = False;
								#*(_QWORD *)&v23 = self.RepeatInterval;
								#a delay until I get 0x15
								time.sleep(0.0001)
							break;
	
						timeout -= 1;
						#if ( !timeout )
							#goto label_42
#LABEL_49
				if ReceiverState != 0x15:
					ret = sHID.SetRX(); #make state from 14 to 15
					time.sleep(0.5)
				
				#if ReceiverState == 0x15:
				#	if CDataStore.getRequestType(self.DataStore) == 6:
				#		#CDataStore.GetCurrentWeather(self.DataStore)
				#		CDataStore.FirstTimeConfig(self.DataStore)

			if not ret:
				CDataStore.setFlag_FLAG_TRANSCEIVER_PRESENT(self.DataStore, 0);


#filehandler = open("WV5DataStore", 'w')
#pickle.dump(CDataStore.TransceiverSettings, filehandler)

#myCCommunicationService.getInstance()
#myCCommunicationService.doRFCommunication()

#t = ThreadClass()
#t.start()
#
#
#time.sleep(5)
#while 1:
#   pass

if __name__ == "__main__":
	import logging
#CRITICAL 50 
#ERROR 40 
#WARNING 30 
#INFO 20 
#DEBUG 10 
#NOTSET 0 
#	logging.basicConfig(format='%(asctime)s %(name)s %(message)s',filename="HeavyWeatherService.log",level=logging.DEBUG)
	logging.basicConfig(format='%(asctime)s %(name)s %(message)s',filename="HeavyWeatherService.log",level=logging.DEBUG)
	logging.debug('This message should go to the log file')

	myCCommunicationService = CCommunicationService()
	time.sleep(10)
	CDataStore.FirstTimeConfig(myCCommunicationService.DataStore)
	#CDataStore.GetCurrentWeather(myCCommunicationService.DataStore)
	while 1:
		pass

	#myCCommunicationService.logger.debug("Started main()")
	#rim
	#myCCommunicationService.logger.debug("Finished main()")
