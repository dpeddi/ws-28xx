#!/usr/bin/python

## This driver is based is based on reverse engineering of HeavyWeather 2800 v 1.54
## All copyright goes to La Crosse Technology (c) 2008

## Python port by Eddi De Pieri <eddi@depieri.net>
## Use this software as your own risk.
## Me and La Crosse Technology is not responsable for any damage using this software

import logging
import traceback

import time
import threading
#import shelve 
#import mmap #http://docs.python.org/library/mmap.html
import USBHardware
import sHID
import CCurrentWeatherData
from CWeatherStationConfig import CWeatherStationConfig
import CWeatherTraits
from datetime import datetime
from datetime import timedelta

def handleError(self, record):
	traceback.print_stack()
logging.Handler.handleError = handleError

sHID = sHID.sHID()
USBHardware = USBHardware.USBHardware()
#CCurrentWeatherData = CCurrentWeatherData.CCurrentWeatherData()
#CWeatherStationConfig = CWeatherStationConfig.CWeatherStationConfig()
CWeatherTraits = CWeatherTraits.CWeatherTraits()

#def equal(a, b):
    #return abs(a - b) < 1e-6
#
#if equal(f1, f2):

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

class ws28xxError(IOError):
	"Used to signal an error condition"

class EHistoryInterval:
	hi01Min          = 0
	hi05Min          = 1
	hi10Min          = 2
	hi15Min          = 3
	hi20Min          = 4
	hi30Min          = 5
	hi60Min          = 6
	hi02Std          = 7
	hi04Std          = 8
	hi06Std          = 9
	hi08Std          = 0xA
	hi12Std          = 0xB
	hi24Std          = 0xC

class EWindspeedFormat:
	wfMs             = 0
	wfKnots          = 1
	wfBFT            = 2
	wfKmh            = 3
	wfMph            = 4

class ERainFormat:
	rfMm             = 0
	rfInch           = 1

class EPressureFormat:
	pfinHg           = 0
	pfHPa            = 1

class ETemperatureFormat:
	tfFahrenheit     = 0
	tfCelsius        = 1

class EClockMode:
	ct24H            = 0
	ctAmPm           = 1

class  EWeatherTendency:
	TREND_NEUTRAL    = 0
	TREND_UP         = 1
	TREND_DOWN       = 2
	TREND_ERR        = 3

class EWeatherState:
	WEATHER_BAD      = 0
	WEATHER_NEUTRAL  = 1
	WEATHER_GOOD     = 2
	WEATHER_ERR      = 3

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

windDirMap = { 0:"N", 1:"NNE", 2:"NE", 3:"ENE", 4:"E", 5:"ESE", 6:"SE", 7:"SSE",
              8:"S", 9:"SSW", 10:"SW", 11:"WSW", 12:"W", 13:"WNW", 14:"NW", 15:"NWN", 16:"err", 17:"inv" }


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

	class TTransceiverSettings(object): 
		# void __thiscall CDataStore::TTransceiverSettings::TTransceiverSettings(CDataStore::TTransceiverSettings *this);
		def __init__(self):
			self.VendorId	= 0x6666
			self.ProductId	= 0x5555
			self.VersionNo	= 1
			self.Frequency	= 905000000
			self.manufacturer	= "LA CROSSE TECHNOLOGY"
			self.product		= "Weather Direct Light Wireless Device"

	class TRequest(object):
		# void __thiscall CDataStore::TRequest::TRequest(CDataStore::TRequest *this);
		def __init__(self):
			self.Type = 6
			self.State = 6
			self.TTL = 90000
			self.Lock = 0
			self.CondFinish = threading.Condition()

	class TLastStat(object):
		# void __thiscall CDataStore::TLastStat::TLastStat(CDataStore::TLastStat *this);
		def __init__(self):
			self.LastBatteryStatus = [0]
			self.LastHistoryIndex = 0
			self.LastLinkQuality = 0
			self.OutstandingHistorySets = -1
			self.WeatherClubTransmissionErrors = 0
			self.LastCurrentWeatherTime = None
			self.LastHistoryDataTime = None
			self.LastConfigTime = None
			self.LastWeatherClubTransmission = None

	class TSettings(object):
		#void __thiscall CDataStore::TSettings::TSettings(CDataStore::TSettings *this);
		def __init__(self):
			self.CommModeInterval = 4
			self.DeviceId = -1
			self.DeviceRegistered = False
			self.PreambleDuration = 5000
			self.RegisterWaitTime = 20000
			self.TransceiverIdChanged = None
			self.TransceiverID = -1

	# void __thiscall CDataStore::CDataStore(CDataStore *this, bool _isService);
	def __init__(self,_isService):
		self.logger = logging.getLogger('ws28xx.CDataStore')
		self.logger.debug("isservice=%x" %_isService)
		self.isService = _isService
		#self.MemSegment = shelve???? o mmap??
		#self.DataStoreAllocator = shelve???? mmap???
		self.Guards = 0;
		self.HistoryData = 0;
		self.Flags = 0;
		self.Settings = 0;
		self.TransceiverSettings = 0;
		self.WeatherClubSettings = 0;
		self.LastSeen = 0;
		self.CurrentWeather = CCurrentWeatherData.CCurrentWeatherData();
		self.DeviceConfig = 0;
		self.FrontEndConfig = 0;
		self.LastStat = 0;
		self.Request = 0;
		self.LastHistTimeStamp = 0;
		self.BufferCheck = 0;

		self.Request = CDataStore.TRequest()

		self.Request.CondFinish = threading.Condition()

		self.LastStat = CDataStore.TLastStat()

		self.Settings = CDataStore.TSettings()
		self.TransceiverSettings = CDataStore.TTransceiverSettings()

		self.DeviceConfig = CWeatherStationConfig()

		self.TransceiverSerNo = None
		self.TransceiveID = None

		#ShelveDataStore=shelve.open("WV5DataStore",writeback=True)

		#if ShelveDataStore.has_key("Settings"):
		#	self.DataStore.Settings = ShelveDataStore["Settings"]
		#else:
		#	print ShelveDataStore.keys()
		if self.Request:
		    self.logger.debug("ok")

	def getDeviceConfig(self,result):
		self.logger.debug("")

	def getDeviceId(self):
		self.logger.debug("Settings.DeviceId=%x" % self.Settings.DeviceId)
		return self.Settings.DeviceId

	def setDeviceId(self,val):
		self.logger.debug("val=%x" % val)
		self.Settings.DeviceId = val

	def getFlag_FLAG_TRANSCEIVER_SETTING_CHANGE(self):	# <4>
		self.logger.debug("")
		#return self.Flags_FLAG_TRANSCEIVER_SETTING_CHANGE
		#std::bitset<5>::at(thisa->Flags, &result, 4u);
		return testBit(self.Flags, 4)

	def getFlag_FLAG_FAST_CURRENT_WEATHER(self):		# <2>
		self.logger.debug("")
		#return self.Flags_FLAG_SERVICE_RUNNING
		#std::bitset<5>::at(thisa->Flags, &result, 2u);
		return testBit(self.Flags, 2)

	def getFlag_FLAG_TRANSCEIVER_PRESENT(self):		# <0>
		self.logger.debug("")
		#return self.Flags_FLAG_TRANSCEIVER_PRESENT
		return testBit(self.Flags, 0)

	def getFlag_FLAG_SERVICE_RUNNING(self):			# <3>
		self.logger.debug("")
		#return self.Flags_FLAG_SERVICE_RUNNING
		return testBit(self.Flags, 3)

	def setFlag_FLAG_TRANSCEIVER_SETTING_CHANGE(self,val):	# <4>
		self.logger.debug("")
		#std::bitset<5>::set(thisa->Flags, 4u, val);
		self.Flags = setBitVal(self.Flags,4,val)

	def setFlag_FLAG_FAST_CURRENT_WEATHER(self,val):	# <2>
		self.logger.debug("")
		#std::bitset<5>::set(thisa->Flags, 2u, val);
		self.Flags = setBitVal(self.Flags,2,val)

	def setFlag_FLAG_TRANSCEIVER_PRESENT(self,val):		# <0>
		self.logger.debug("")
		#std::bitset<5>::set(thisa->Flags, 0, val);
		self.Flags_FLAG_TRANSCEIVER_PRESENT = val
		self.Flags = setBitVal(self.Flags,0,val)

	def setFlag_FLAG_SERVICE_RUNNING(self,val):		# <3>
		self.logger.debug("")
		#std::bitset<5>::set(thisa->Flags, 3u, val);
		self.Flags_FLAG_SERVICE_RUNNING = val
		self.Flags = setBitVal(self.Flags,3,val)

	def setLastLinkQuality(self,Quality):
		self.logger.debug("Quality=%d",Quality)
		self.LastStat.LastLinkQuality = Quality

	def setLastSeen(self,time):
		self.logger.debug("time=%d",time)
		self.LastSeen = time

	def getLastSeen(self):
		self.logger.debug("LastSeen=%d",self.LastSeen)
		return self.LastSeen

	def setLastBatteryStatus(self, BatteryStat):
		self.logger.debug("")
		print "Battery 3=%d 0=%d 1=%d 2=%d" % (testBit(BatteryStat,3),testBit(BatteryStat,0),testBit(BatteryStat,1),testBit(BatteryStat,2))
		self.LastStat.LastBatteryStatus = BatteryStat

	def setCurrentWeather(self,Data):
		self.logger.debug("")
		self.CurrentWeather = Data

	def RequestNotify(self):
		self.logger.debug("implement me")
		#ATL::CStringT<char_ATL::StrTraitATL<char_ATL::ChTraitsCRT<char>>>::CStringT<char_ATL::StrTraitATL<char_ATL::ChTraitsCRT<char>>>(
		#    &FuncName,
		#    "void __thiscall CDataStore::RequestNotify(void) const");
		#v6 = 0;
		#ATL::CStringT<char_ATL::StrTraitATL<char_ATL::ChTraitsCRT<char>>>::CStringT<char_ATL::StrTraitATL<char_ATL::ChTraitsCRT<char>>>(
		#    &Name,
		#    "Request->Lock");
		#LOBYTE(v6) = 1;
		#CScopedLock::CScopedLock(&lock, &thisa->Request->Lock, &Name, &FuncName);
		#LOBYTE(v6) = 3;
		#ATL::CStringT<char_ATL::StrTraitATL<char_ATL::ChTraitsCRT<char>>>::_CStringT<char_ATL::StrTraitATL<char_ATL::ChTraitsCRT<char>>>(&Name);
		#LOBYTE(v6) = 4;
		#ATL::CStringT<char_ATL::StrTraitATL<char_ATL::ChTraitsCRT<char>>>::_CStringT<char_ATL::StrTraitATL<char_ATL::ChTraitsCRT<char>>>(&FuncName);
		#boost::interprocess::interprocess_condition::notify_all(&thisa->Request->CondFinish);
		#v6 = -1;
		#self.Request.CondFinish.notifyAll()
		#CScopedLock::_CScopedLock(&lock);

	def setLastCurrentWeatherTime(self,time):
		self.logger.debug("time=%d" % time)
		self.LastStat.LastCurrentWeatherTime = time

	def getBufferCheck(self):
		self.logger.debug("self.BufferCheck=%x" % self.BufferCheck)
		return self.BufferCheck

	def setBufferCheck(self,val):
		self.logger.debug("self.BufferCheck=%x" % val)
		self.BufferCheck = val

	def operator(self):
		self.logger.debug("")
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
		self.logger.debug("self.Settings.DeviceRegistered=%x" % self.Settings.DeviceRegistered)
		return self.Settings.DeviceRegistered

	def setDeviceRegistered(self,registered):
		self.logger.debug("Registered=%i" % registered)
		self.Settings.DeviceRegistered = registered;

	def getRequestType(self):
		self.logger.debug("Request.Type=%d" % self.Request.Type)
		return self.Request.Type

	def getRequestState(self):
		self.logger.debug("Request.State=%d" % self.Request.State)
		return self.Request.State

	def getPreambleDuration(self):
		self.logger.debug("Settings.PreambleDuration=%d" % self.Settings.PreambleDuration)
		return self.Settings.PreambleDuration

	def getRegisterWaitTime(self):
		self.logger.debug("Settings.RegisterWaitTime=%d" % self.Settings.RegisterWaitTime)
		return self.Settings.RegisterWaitTime

	def setRequestState(self,state):
		self.logger.debug("state=%x",state)
		self.Request.State = state;

	def getCommModeInterval(self):
		self.logger.debug("getCommModeInterval=%x" % self.Settings.CommModeInterval)
		return self.Settings.CommModeInterval

	def setCommModeInterval(self,val):
		self.logger.debug("val=%x" % val)
		self.Settings.CommModeInterval = val

	def addHistoryData(self,Data):
		self.logger.debug("")

	def setTransceiverID(self,tid):
		if tid != None:
			if self.Settings.TransceiverID != None and self.Settings.TransceiverID != tid:
				self.Settings.TransceiverIdChanged = 1
				self.Settings.TransceiverID = tid
		self.logger.debug("self.Settings.TransceiverID=%x" % self.Settings.TransceiverID)

	def setOutsatndingHistorySets(self,val):
		self.logger.debug("val=%d" % val)
		self.LastStat.OutstandingHistorySets = val
		pass

	def setTransceiverSerNo(self,inp):
		self.logger.debug("inp=%s" % inp)
		self.TransceiverSerNo = inp

	def setLastHistoryIndex(self,val):
		self.LastStat.LastHistoryIndex = val
		self.logger.debug("self.LastStat.LastHistoryIndex=%x" % self.LastStat.LastHistoryIndex)

	def getLastHistoryIndex(self):
		self.logger.debug("")
		print "CDataStore::getLastHistoryIndex %x" % self.LastStat.LastHistoryIndex
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
		return self.LastStat.LastHistoryIndex

	def FirstTimeConfig(self,ID,TimeOut):
		print "CDataStore::FirstTimeConfig"
		#if ( CSingleInstance::IsRunning(this) && CDataStore::getFlag<0>(thisa))
		if self.getFlag_FLAG_TRANSCEIVER_PRESENT():
			self.Settings.DeviceRegistered = False;
			self.Settings.DeviceId = -1;
			self.LastStat.LastHistoryIndex = 0xffff;
			self.LastStat.OutstandingHistorySets = -1;

			self.Request.Type = ERequestType.rtFirstConfig;
			self.Request.State = 0;
			self.Request.TTL = 90000;

			self.BufferCheck = 0

			try:
				self.Request.CondFinish.acquire()
			except:
				pass
			if self.Request.CondFinish.wait(timedelta(milliseconds=TimeOut).seconds):
				print "e' passato il timeout lo state e':",self.Request.State
				print "e' passato il timeout lo state e':",ERequestState.rsFinished
				if self.Request.State == ERequestState.rsFinished: #2
					ID[0] = self.getDeviceId();
					self.Request.Type = ERequestType.rtINVALID #6;
					self.Request.State = ERequestState.rsINVALID #8;
					print "FirstTimeConfig found an ID"
				else:
					self.Request.Type = ERequestType.rtINVALID #6;
					self.Request.State = ERequestState.rsINVALID #8;
					print "FirstTimeConfig failed"
			#else:
			#	self.Request.Type = 6;
			#	self.Request.State = 8;
			#	v25 = 1;
			#	v30 = -1;
			self.Request.CondFinish.release()


	def GetCurrentWeather(self,Weather,TimeOut):
		self.logger.debug("timeout=%d" % TimeOut)
		#if ( CSingleInstance::IsRunning(this) && CDataStore::getFlag<0>(thisa) && CDataStore::getDeviceRegistered(thisa) )
		if self.getFlag_FLAG_TRANSCEIVER_PRESENT() and self.getDeviceRegistered():
			self.Request.Type = ERequestType.rtGetCurrent;
			self.Request.State = 0;
			self.Request.TTL = 90000;

			try:
			    self.Request.CondFinish.acquire()
			except:
			    pass
			if self.Request.CondFinish.wait(timedelta(milliseconds=TimeOut).seconds):
				self.Request.Type = ERequestType.rtINVALID #6;
				self.Request.State = ERequestState.rsINVALID #8;
				#CDataStore::getCurrentWeather(thisa, Weather);
		#		v23 = 0;
		#		v30 = -1;
			else:
				self.Request.Type = ERequestType.rtINVALID #6;
				self.Request.State = ERequestState.rsINVALID #8;
		#		v24 = 1;
		#		v30 = -1;
			self.Request.CondFinish.release()

	def GetHistory(self,TimeOut):
		print "CDataStore::GetHistory"
		#if ( CSingleInstance::IsRunning(this) && CDataStore::getFlag<0>(thisa) && CDataStore::getDeviceRegistered(thisa) )
		if self.getFlag_FLAG_TRANSCEIVER_PRESENT() and self.getDeviceRegistered():
			self.Request.Type = ERequestType.rtGetHistory;
			self.Request.State = 0;
			self.Request.TTL = 90000;

			try:
			    self.Request.CondFinish.acquire()
			except:
			    pass
			if self.Request.CondFinish.wait(timedelta(milliseconds=TimeOut).seconds):
				self.Request.Type = ERequestType.rtINVALID #6;
				self.Request.State = ERequestState.rsINVALID #8;
				#CDataStore::getHistoryData(thisa, History, 1);
		#		v23 = 0;
		#		v30 = -1;
			else:
				self.Request.Type = ERequestType.rtINVALID #6;
				self.Request.State = ERequestState.rsINVALID #8;
		#		v24 = 1;
		#		v30 = -1;
			self.Request.CondFinish.release()

	def GetConfig(self):
		print "CDataStore::GetConfig"
		#if ( CSingleInstance::IsRunning(this) && CDataStore::getFlag<0>(thisa) && CDataStore::getDeviceRegistered(thisa) )
		if self.getFlag_FLAG_TRANSCEIVER_PRESENT() and self.getDeviceRegistered():
			self.Request.Type = ERequestType.rtGetConfig;
			self.Request.State = 0;
			self.Request.TTL = 90000;
		else:
			print "GetConfig - warning: flag False or getDeviceRegistered false"

	def SetConfig(self):
		print "CDataStore::SetConfig"
		#if ( CSingleInstance::IsRunning(this) && CDataStore::getFlag<0>(thisa) && CDataStore::getDeviceRegistered(thisa) )
		if self.getFlag_FLAG_TRANSCEIVER_PRESENT() and self.getDeviceRegistered():
			self.Request.Type = ERequestType.rtSetConfig;
			self.Request.State = 0;
			self.Request.TTL = 90000;
		else:
			print "SetConfig - warning: flag False or getDeviceRegistered false"

	def SetTime(self):
		print "CDataStore::SetTime"
		#if ( CSingleInstance::IsRunning(this) && CDataStore::getFlag<0>(thisa) && CDataStore::getDeviceRegistered(thisa) )
		if self.getFlag_FLAG_TRANSCEIVER_PRESENT() and self.getDeviceRegistered():
			self.Request.Type = ERequestType.rtSetTime;
			self.Request.State = 0;
			self.Request.TTL = 90000;
		else:
			print "SetTime - warning: flag False or getDeviceRegistered false"

	def GetDeviceConfigCS(self):
		self.logger.debug("")
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
		return CWeatherStationConfig.GetCheckSum(self.DeviceConfig)

	def RequestTick(self):
		self.logger.debug("")
		if self.Request.Type != 6:
			self.Request.TTL -= 1
			if not self.Request.TTL:
				self.Request.Type = 6
				self.Request.State = 8
				print "internal timeout, request aborted"

class CCommunicationService(object):

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
		self.logger.debug("")

		self.RepeatCount = 0
		self.RepeatSize = 0
		self.RepeatInterval = None
		self.RepeatTime = datetime.now() #ptime
	
		self.Regenerate = 0
		self.GetConfig = 0

		self.TimeSent = 0
		self.TimeUpdate = 0
		self.TimeUpdateComplete = 0

		self.DataStore = None

		self.DataStore = CDataStore(1)
		self.Instance = self.CCommunicationService()

	def operator(self):
		self.logger.debug("")

	def getInstance(self):
		self.logger.debug("partially implemented")
		self.CCommunicationService();

	def buildTimeFrame(self,Buffer,checkMinuteOverflow):
		self.logger.debug("checkMinuteOverflow=%x" % checkMinuteOverflow)

		DeviceCheckSum = CDataStore.GetDeviceConfigCS(self.DataStore)
		now = time.time()
		tm = time.localtime(now)
		tu = time.gmtime(now)

		new_Buffer=[0]
		new_Buffer[0]=Buffer[0]
		Second = tm[5]
		if Second > 59:
			Second = 0 # I don't know if La Crosse support leap seconds...
		if ( checkMinuteOverflow and (Second <= 5 or Second >= 55) ):
			if ( Second < 55 ):
				Second = 6 - Second
			else:
				Second = 60 - Second + 6;
			HistoryIndex = CDataStore.getLastHistoryIndex(self.DataStore);
			Length = self.buildACKFrame(new_Buffer, 0, DeviceCheckSum, HistoryIndex, Second);
			Buffer[0]=new_Buffer[0]
		else:
		#00000000: d5 00 0c 00 32 c0 00 8f 45 25 15 91 31 20 01 00
		#00000000: d5 00 0c 00 32 c0 06 c1 47 25 15 91 31 20 01 00
		#                             3  4  5  6  7  8  9 10 11
			new_Buffer[0][2] = 0xc0
			new_Buffer[0][3] = (DeviceCheckSum >>8)  & 0xFF #BYTE1(DeviceCheckSum);
			new_Buffer[0][4] = (DeviceCheckSum >>0)  & 0xFF #DeviceCheckSum;
			new_Buffer[0][5] = (tm[5] % 10) + 0x10 * (tm[5] // 10); #sec
			new_Buffer[0][6] = (tm[4] % 10) + 0x10 * (tm[4] // 10); #min
			new_Buffer[0][7] = (tm[3] % 10) + 0x10 * (tm[3] // 10); #hour
			#DayOfWeek = tm[6] - 1; #ole from 1 - 7 - 1=Sun... 0-6 0=Sun
			DayOfWeek = tm[6];      #py  prom 0 - 6 - 0=Mon
			#if ( DayOfWeek == 1 ): # this was for OLE::Time
			#	DayOfWeek = 7;  # this was for OLE::Time
			new_Buffer[0][8] = DayOfWeek % 10 + 0x10 *  (tm[2] % 10)          #DoW + Day
			new_Buffer[0][9] =  (tm[2] // 10) + 0x10 *  (tm[1] % 10)          #day + month
			new_Buffer[0][10] = (tm[1] // 10) + 0x10 * ((tm[0] - 2000) % 10)  #month + year
			new_Buffer[0][11] = (tm[0] - 2000) // 10                          #year
			self.Regenerate = 1
			self.TimeSent = 1
			Buffer[0]=new_Buffer[0]
			Length = 0x0c
		return Length

	def buildConfigFrame(self,Buffer,Data):
		print "buildConfigFrame (not yet implemented)"
		Buffer[2] = 0x40;
		Buffer[3] = 0x64;
		#CWeatherStationConfig::write(Data, &(*Buffer)[4]);
		raise "buildConfigFrameCheckSumm: error... unimplemented"
		self.Regenerate = 0;
		self.TimeSent = 0;

	def buildACKFrame(self,Buffer, Action, CheckSum, HistoryIndex, ComInt):
		self.logger.debug("Action=%x, CheckSum=%x, HistoryIndex=%x, ComInt=%x" % (Action, CheckSum, HistoryIndex, ComInt))
		newBuffer = [0]
		newBuffer[0] = [0]*9
		for i in xrange(0,2):
			newBuffer[0][i] = Buffer[0][i]
		#CDataStore::TLastStat::TLastStat(&Stat);
#		if ( !Action && ComInt == 0xFFFFFFFF ):
#			v28 = 0;
#			if ( !Stat.LastCurrentWeatherTime.m_status ):
#			ATL::COleDateTime::operator_(&now, &ts, &Stat.LastCurrentWeatherTime);
#			if ( ATL::COleDateTimeSpan::GetTotalSeconds(&ts) >= 8.0 )
#				Action = 5;
#			v28 = -1;
		newBuffer[0][2] = Action & 0xF;
#		v21 = CDataStore::GetDeviceConfigCS(self.DataStore);
		if ( HistoryIndex >= 0x705 ):
			HistoryAddress = 0xffffff;
		else:
#			if ( !CDataStore.getBufferCheck(self.DataStore) ):
#				if ( !ATL::COleDateTime::GetStatus(&Stat.LastHistoryDataTime) ):
#				{
#					v9 = ATL::COleDateTime::operator_(&now, &result, &Stat.LastHistoryDataTime);
#					if ( ATL::COleDateTimeSpan::operator>(v9, &BUFFER_OVERFLOW_SPAN) )
#					{
#						val = 1;
#						CDataStore.setBufferCheck(self.DataStore, &val);
#					}
#				}
#			}
			if   ( CDataStore.getBufferCheck(self.DataStore) != 1
			  and CDataStore.getBufferCheck(self.DataStore) != 2 ):
				HistoryAddress = 18 * HistoryIndex + 0x1a0;
			else:
				if ( HistoryIndex ):
					HistoryAddress = 18 * (HistoryIndex - 1) + 0x1a0;
				else:
					HistoryAddress = 0x7fe8;
				CDataStore.setBufferCheck(self.DataStore, 2);
		newBuffer[0][3] = (CheckSum >> 8) &0xFF;
		newBuffer[0][4] = (CheckSum >> 0) &0xFF;
		if ( ComInt == 0xFFFFFFFF ):
			ComInt = CDataStore.getCommModeInterval(self.DataStore);
		newBuffer[0][5] = (ComInt >> 4) & 0xFF ;
		newBuffer[0][6] = (HistoryAddress >> 16) & 0x0F | 16 * (ComInt & 0xF);
		newBuffer[0][7] = (HistoryAddress >> 8 ) & 0xFF # BYTE1(HistoryAddress);
		newBuffer[0][8] = (HistoryAddress >> 0 ) & 0xFF

		#d5 00 09 f0 f0 03 00 32 00 3f ff ff
		Buffer[0]=newBuffer[0]
		self.Regenerate = 0;
		self.TimeSent = 0;
		return 9

	def handleWsAck(self,Buffer,Length):
		self.logger.debug("")
		#3 = ATL::COleDateTime::GetTickCount(&result);
		CDataStore.setLastSeen(self.DataStore, time.time());
		BatteryStat = (Buffer[0][2] & 0xF);
		CDataStore.setLastBatteryStatus(self.DataStore, BatteryStat);
		Quality = Buffer[0][3] & 0x7F;
		CDataStore.setLastLinkQuality(self.DataStore, Quality);
		ReceivedCS = (Buffer[0][4] << 8) + Buffer[0][5];
		rt = CDataStore.getRequestType(self.DataStore)
		#if ( rt == 3 ) #rtSetConfig
		#{
		#	v11 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
		#	v12 = CDataStore::GetFrontEndConfigCS(v11);
		#	if ( ReceivedCS == v12 )
		#	{
		#		v13 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
		#		CDataStore::getFrontEndConfig(v13, &c);
		#		v33 = 5;
		#		std::bitset<23>::bitset<23>((std::bitset<23> *)&v26, 0);
		#		v14 = CWeatherStationConfig::GetResetMinMaxFlags(&c);
		#		v14->_Array[0] = v26;
		#		v15 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
		#		CDataStore::setDeviceConfig(v15, &c);
		#		v16 = ATL::COleDateTime::GetTickCount((ATL::COleDateTime *)&v27);
		#		v17 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
		#		CDataStore::setLastConfigTime(v17, v16);
		#		v18 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
		#		CDataStore::setRequestState(v18, rsFinished);
		#		v19 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
		#		CDataStore::RequestNotify(v19);
		#		thisa->RepeatCount = 0;
		#		v33 = -1;
		#		CWeatherStationConfig::_CWeatherStationConfig(&c);
		#	}
		#}
		#else
		#{
		#	if ( rt == 4 ) #rtSetTime (unused)
		#	{
		#		if ( thisa->TimeSent )
		#		{
		#			v8 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
		#			CDataStore::setRequestState(v8, rsFinished);
		#			v9 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
		#			CDataStore::RequestNotify(v9);
		#			thisa->RepeatCount = 0;
		#			if ( thisa->TimeUpdate )
		#			{
		#				thisa->TimeUpdateComplete = 1;
		#				thisa->TimeUpdate = 0;
		#				ATL::CStringT<char_ATL::StrTraitATL<char_ATL::ChTraitsCRT<char>>>::CStringT<char_ATL::StrTraitATL<char_ATL::ChTraitsCRT<char>>>(
		#				    &FuncName,
		#				    "void __thiscall CCommunicationService::handleWsAck(unsigned char (*const )[300],unsigned int &)");
		#				v33 = 0;
		#				ATL::CStringT<char_ATL::StrTraitATL<char_ATL::ChTraitsCRT<char>>>::CStringT<char_ATL::StrTraitATL<char_ATL::ChTraitsCRT<char>>>(
		#				    &Name,
		#				    "DataStore->Request->Lock");
		#				LOBYTE(v33) = 1;
		#				v10 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
		#				CScopedLock::CScopedLock(&lock, &v10->Request->Lock, &Name, &FuncName);
		#				LOBYTE(v33) = 3;
		#				ATL::CStringT<char_ATL::StrTraitATL<char_ATL::ChTraitsCRT<char>>>::_CStringT<char_ATL::StrTraitATL<char_ATL::ChTraitsCRT<char>>>(&Name);
		#				LOBYTE(v33) = 4;
		#				ATL::CStringT<char_ATL::StrTraitATL<char_ATL::ChTraitsCRT<char>>>::_CStringT<char_ATL::StrTraitATL<char_ATL::ChTraitsCRT<char>>>(&FuncName);
		#				boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore)->Request->Type = 6;
		#				boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore)->Request->State = 8;
		#				v33 = -1;
		#				CScopedLock::_CScopedLock(&lock);
		#			}
		#			}
		#		}
		#	}
		#Length = 0;

	def handleConfig(self,Buffer,Length):
		self.logger.debug("")
		newBuffer=[0]
		newBuffer[0] = Buffer[0]
		newLength = [0]
		RecConfig = None
		diff = 0;
		t=[0]
		t[0]=[0]*300
		#j__memcpy(t, (char *)Buffer, *Length);
		for i in xrange(0,Length[0]):
			t[0][i]=newBuffer[0][i]
		c=CWeatherStationConfig()
		#CWeatherStationConfig.CWeatherStationConfig_buf(c, t,4);
		CWeatherStationConfig.CWeatherStationConfig_buf(self.DataStore.DeviceConfig, t,4); #for the moment I need the cs here
		#v73 = 0;
		#j__memset(t, -52, *Length);
		#t[0]=[0xcc]*Length[0]
		#CWeatherStationConfig::write(&c, &t[4]);
		USBHardware.ReverseByteOrder(t, 7, 4);
		USBHardware.ReverseByteOrder(t, 11, 5);
		USBHardware.ReverseByteOrder(t, 16, 5);
		USBHardware.ReverseByteOrder(t, 21, 2);
		USBHardware.ReverseByteOrder(t, 23, 2);
		USBHardware.ReverseByteOrder(t, 25, 4);
		USBHardware.ReverseByteOrder(t, 30, 3);
		USBHardware.ReverseByteOrder(t, 33, 5);
		USBHardware.ReverseByteOrder(t, 38, 5);
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
		#				#"Generated config differs from received in byte#: %02i generated = %04x rececived = %04x");
		#		diff = 1;
		#	}
		#}
		#if ( diff ):
			#v43 = *Length;
			#v42 = t;
			#v41.baseclass_0.m_pszData = (char *)v43;
			#v47 = &v41;
			#ATL::CStringT<char_ATL::StrTraitATL<char_ATL::ChTraitsCRT<char>>>::CStringT<char_ATL::StrTraitATL<char_ATL::ChTraitsCRT<char>>>(
			#		#&v41,
			#		#"Config_Gen");
			#v46 = v4;
			#rhs = v4;
			#LOBYTE(v73) = 1;
			#v5 = CTracer::Instance();
			#LOBYTE(v73) = 0;
			#CTracer::WriteDump(v5, 30, v41, v42, v43);
			#v43 = *Length;
			#v42 = (char *)Buffer;
			#v41.baseclass_0.m_pszData = (char *)v43;
			#v48 = &v41;
			#ATL::CStringT<char_ATL::StrTraitATL<char_ATL::ChTraitsCRT<char>>>::CStringT<char_ATL::StrTraitATL<char_ATL::ChTraitsCRT<char>>>(
			#		#&v41,
			#		#"Config_Rec");
			#v46 = v6;
			#rhs = v6;
			#LOBYTE(v73) = 2;
			#v7 = CTracer::Instance();
			#LOBYTE(v73) = 0;
			#CTracer::WriteDump(v7, 30, v41, v42, v43);
		#v73 = -1;
		#CWeatherStationConfig::_CWeatherStationConfig(&c);
		RecConfig = CWeatherStationConfig()
		confBuffer=[0]
		confBuffer[0]=[0]*0x111
		#CWeatherStationConfig.CWeatherStationConfig_buf(RecConfig, confBuffer, 4);
		#v73 = 3;
		if 1==1: #hack ident
		#if ( CWeatherStationConfig::operator bool(&RecConfig) ):
			rt = CDataStore.getRequestType(self.DataStore);
			#ATL::COleDateTime::GetTickCount(&now);
			#v43 = (CDataStore::ERequestState)&now;
			#v9 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
			#CDataStore::setLastSeen(self.DataStore, (ATL::COleDateTime *)v43);
			BatteryStat = (newBuffer[0][2] & 0xF);
			CDataStore.setLastBatteryStatus(self.DataStore, BatteryStat);
			Quality = newBuffer[0][3] & 0x7F
			CDataStore.setLastLinkQuality(self.DataStore, Quality)
			#FrontCS = CDataStore::GetFrontEndConfigCS(self.DataStore);
			HistoryIndex = CDataStore.getLastHistoryIndex(self.DataStore);
			#v46 = (CWeatherStationConfig *)rt;
			if 1==1: #hack ident
				if   rt == 3:
					print "handleConfig rt==3 rtSetConfig"
					#v43 = (CDataStore::ERequestState)&result;
					#v14 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
					#v46 = CDataStore::getFrontEndConfig(v14, (CWeatherStationConfig *)v43);
					#rhs = v46;
					#LOBYTE(v73) = 4;
					#v51 = CWeatherStationConfig::operator__(&RecConfig, v46);
					#LOBYTE(v73) = 3;
					#CWeatherStationConfig::_CWeatherStationConfig(&result);
					#if ( v51 ):
						#*Length = CCommunicationService::buildACKFrame(thisa, Buffer, 0, &FrontCS, &HistoryIndex, 0xFFFFFFFFu);
						#v43 = (CDataStore::ERequestState)&now;
						#v15 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
						#CDataStore::setLastConfigTime(v15, (ATL::COleDateTime *)v43);
						#v43 = (CDataStore::ERequestState)&RecConfig;
						#v16 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
						#CDataStore::setDeviceConfig(v16, (CWeatherStationConfig *)v43);
						#CDataStore.setRequestState(self.DataStore, ERequestState.rsFinished); #2
						#v18 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
						#CDataStore::RequestNotify(v18);
					#else:
					#	CheckSum = CWeatherStationConfig::GetCheckSum(&RecConfig);
					#	*Length = CCommunicationService::buildACKFrame(thisa, Buffer, 2, &CheckSum, &HistoryIndex, 0xFFFFFFFFu);
					#	CDataStore.setRequestState(self.DataStore, ERequestState.rsRunning); #1
				elif rt == 2:
					print "handleConfig rt==2 rtGetConfig"
					#v43 = (CDataStore::ERequestState)&now;
					#v20 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
					#CDataStore::setLastConfigTime(v20, (ATL::COleDateTime *)v43);
					#v43 = (CDataStore::ERequestState)&RecConfig;
					#v21 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
					#CDataStore::setDeviceConfig(v21, (CWeatherStationConfig *)v43);
					#v54 = CWeatherStationConfig::GetCheckSum(&RecConfig);
					#*Length = CCommunicationService::buildACKFrame(thisa, Buffer, 0, &v54, &HistoryIndex, 0xFFFFFFFF);
					CDataStore.setRequestState(self.DataStore, ERequestState.rsFinished); #2
					CDataStore.RequestNotify(self.DataStore);
				elif rt == 0:
					print "handleConfig rt==0 rtGetCurrent"
					#v43 = (CDataStore::ERequestState)&now;
					#v24 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
					#CDataStore::setLastConfigTime(v24, (ATL::COleDateTime *)v43);
					#v43 = (CDataStore::ERequestState)&RecConfig;
					#v25 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
					#CDataStore::setDeviceConfig(v25, (CWeatherStationConfig *)v43);
					v55 = CWeatherStationConfig.GetCheckSum(RecConfig);
					newLength[0] = self.buildACKFrame(newBuffer, 5, v55, HistoryIndex, 0xFFFFFFFF);
					CDataStore.setRequestState(self.DataStore, ERequestState.rsRunning); #1
				elif rt == 1:
					print "handleConfig rt==1 rtGetHistory"
					#v43 = (CDataStore::ERequestState)&now;
					#v27 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
					#CDataStore::setLastConfigTime(v27, (ATL::COleDateTime *)v43);
					#v43 = (CDataStore::ERequestState)&RecConfig;
					#v28 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
					#CDataStore::setDeviceConfig(v28, (CWeatherStationConfig *)v43);
					#v56 = CWeatherStationConfig::GetCheckSum(&RecConfig);
					#*Length = CCommunicationService::buildACKFrame(thisa, Buffer, 4, &v56, &HistoryIndex, 0xFFFFFFFFu);
					CDataStore.setRequestState(self.DataStore, ERequestState.rsRunning); #1
				elif rt == 4:
					print "handleConfig rt==4 rtSetTime"
					#v43 = (CDataStore::ERequestState)&now;
					#v30 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
					#CDataStore::setLastConfigTime(v30, (ATL::COleDateTime *)v43);
					#v43 = (CDataStore::ERequestState)&RecConfig;
					#v31 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
					#CDataStore::setDeviceConfig(v31, (CWeatherStationConfig *)v43);
					#v57 = CWeatherStationConfig::GetCheckSum(&RecConfig);
					#*Length = CCommunicationService::buildACKFrame(thisa, Buffer, 1, &v57, &HistoryIndex, 0xFFFFFFFFu);
					CDataStore.setRequestState(self.DataStore, ERequestState.rsRunning); #1
				elif rt == 5:
					print "handleConfig rt==5 rtFirstConfig"
					#v43 = (CDataStore::ERequestState)&now;
					#CDataStore.setLastConfigTime(self.DataStore, (ATL::COleDateTime *)v43);
					#v43 = (CDataStore::ERequestState)&RecConfig;
					#CDataStore.setDeviceConfig(self.DataStore, (CWeatherStationConfig *)v43);
					v58 = CWeatherStationConfig.GetCheckSum(RecConfig);
					newLength[0] = self.buildACKFrame(newBuffer, 0, v58, HistoryIndex, 0xFFFFFFFF);
					CDataStore.setRequestState(self.DataStore, ERequestState.rsFinished); #2
					CDataStore.RequestNotify(self.DataStore);
				elif rt == 6:
					print "handleConfig rt==6 rtINVALID"
					#v43 = (CDataStore::ERequestState)&now;
					#CDataStore::setLastConfigTime(self.DataStore, (ATL::COleDateTime *)v43);
					#v43 = (CDataStore::ERequestState)&RecConfig;
					#CDataStore.setDeviceConfig(self.DataStore, (CWeatherStationConfig *)v43);
					v59 = CWeatherStationConfig.GetCheckSum(RecConfig);
					newLength[0] = self.buildACKFrame(newBuffer, 0, v59, HistoryIndex, 0xFFFFFFFF);
		else:
			newLength[0] = 0
		#v73 = -1;
		#CWeatherStationConfig::_CWeatherStationConfig(&RecConfig);
		Buffer[0] = newBuffer[0]
		Length[0] = newLength[0]

	def handleCurrentData(self,Buffer,Length):
		self.logger.debug("")

		newBuffer = [0]
		newBuffer[0] = Buffer[0]
		newLength = [0]
		Data = CCurrentWeatherData.CCurrentWeatherData()
		Data.CCurrentWeatherData_buf(newBuffer, 6);
		#print "CurrentData", Buffer[0] #//fixme
		CDataStore.setLastSeen(self.DataStore, time.time());
		CDataStore.setLastCurrentWeatherTime(self.DataStore, time.time())
		BatteryStat = (Buffer[0][2] & 0xF);
		CDataStore.setLastBatteryStatus(self.DataStore, BatteryStat);
		Quality = Buffer[0][3] & 0x7F;
		CDataStore.setLastLinkQuality(self.DataStore, Quality);
		CDataStore.setCurrentWeather(self.DataStore, Data);
		#self.setCurrentWeather(self.DataStore,Data)

		rt = CDataStore.getRequestType(self.DataStore);
		DeviceCS = CDataStore.GetDeviceConfigCS(self.DataStore)
		HistoryIndex = CDataStore.getLastHistoryIndex(self.DataStore);

		if   rt == 0: #rtGetCurrent
			CDataStore.setRequestState(self.DataStore, ERequestState.rsFinished); #2
			CDataStore.RequestNotify(self.DataStore);
			newLength[0] = self.buildACKFrame(newBuffer, 0, DeviceCS, HistoryIndex, 0xFFFFFFFF);
		elif rt == 2: #rtGetConfig
			newLength[0] = self.buildACKFrame(newBuffer, 3, DeviceCS, HistoryIndex, 0xFFFFFFFF);
			CDataStore.setRequestState(self.DataStore, ERequestState.rsRunning); #1
		elif rt == 3: #rtSetConfig
			newLength[0] = self.buildACKFrame(newBuffer, 2, DeviceCS, HistoryIndex, 0xFFFFFFFF);
			CDataStore.setRequestState(self.DataStore, ERequestState.rsRunning); #1
		elif rt == 1: #rtGetHistory
			newLength[0] = self.buildACKFrame(newBuffer, 4, DeviceCS, HistoryIndex, 0xFFFFFFFF);
			CDataStore.setRequestState(self.DataStore, ERequestState.rsRunning); #1
		elif rt == 4: #rtSetTime
			newLength[0] = self.buildACKFrame(newBuffer, 1, DeviceCS, HistoryIndex, 0xFFFFFFFF);
			CDataStore.setRequestState(self.DataStore, ERequestState.rsRunning); #1
		elif rt == 5 or rt == 6: #rtFirstConfig || #rtINVALID
			newLength[0] = self.buildACKFrame(newBuffer, 0, DeviceCS, HistoryIndex, 0xFFFFFFFF);

		Length[0] = newLength[0]
		Buffer[0] = newBuffer[0]

	def handleHistoryData(self,Buffer,Length):
		self.logger.debug("")
		newBuffer = [0]
		newBuffer[0] = Buffer[0]
		newLength = [0]
		#CHistoryDataSet::CHistoryDataSet(&Data, &(*Buffer)[12]);
		#ATL::COleDateTime::GetTickCount(&now);
		#v3 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
		CDataStore.setLastSeen(self.DataStore, time.time());
		BatteryStat = (Buffer[0][2] & 0xF);
		CDataStore.setLastBatteryStatus(self.DataStore, BatteryStat);
		Quality = Buffer[0][3] & 0x7F;
		CDataStore.setLastLinkQuality(self.DataStore, Quality);
		LatestHistoryAddres = ((((Buffer[0][6] & 0xF) << 8) | Buffer[0][7]) << 8) | Buffer[0][8];
		ThisHistoryAddres = ((((Buffer[0][9] & 0xF) << 8) | Buffer[0][10]) << 8) | Buffer[0][11];
		ThisHistoryIndex = (ThisHistoryAddres - 415) / 0x12;
		LatestHistoryIndex = (LatestHistoryAddres - 415) / 0x12;
		#v6 = CTracer::Instance();
		#CTracer::WriteTrace(v6, 40, "ThisAddress: %X\tLatestAddress: %X");
		#v7 = CTracer::Instance();
		#CTracer::WriteTrace(v7, 40, "ThisIndex: %X\tLatestIndex: %X");
		#v38 = CDataStore::getBufferCheck(self.DataStore);
		#    if ( CDataStore.getBufferCheck(self.DataStore) != 2 ):
		#      j___wassert(
		#        L"false",
		#        L"c:\\svn\\heavyweather\\trunk\\applications\\backend\\communicationservice.cpp",
		#        __LINE__Var + 85);
		#    v9 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
		#v10 = CTracer::Instance();
		#CTracer::WriteTrace(v10, 40, "getLastHistoryIndex(): %X",CDataStore::getLastHistoryIndex(v9));
		if ( ThisHistoryIndex == CDataStore.getLastHistoryIndex(self.DataStore)):
		#      CDataStore::getLastHistTimeStamp(self.DataStore, &LastHistTs);
		#      if ( !ATL::COleDateTime::GetStatus(&LastHistTs) )
		#      {
		#        v14 = CHistoryDataSet::GetTime(&Data);
		#        if ( !ATL::COleDateTime::GetStatus(v14) )
		#        {
		#          v15 = CHistoryDataSet::GetTime(&Data);
		#          if ( ATL::COleDateTime::operator__(v15, &LastHistTs) )
		#          {
		#            CDataStore::setOutsatndingHistorySets(self.DataStore, 0xFFFFFFFFu);
		#             CDataStore.setLastHistoryIndex(self.DataStore, 0xFFFFFFFF);
		#            ThisHistoryIndex = -1;
		#            ATL::COleDateTime::COleDateTime(&InvalidDateTime);
		#            ATL::COleDateTime::SetStatus(&InvalidDateTime, partial);
		#            v18 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
		#            CDataStore::setLastHistTimeStamp(v18, &InvalidDateTime);
		#          }
		#          else
		#          {
		#            v19 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
		#            CDataStore::setLastHistoryDataTime(v19, &now);
		#          }
		#        }
		#      }
		#    }
			CDataStore.setBufferCheck(self.DataStore, 0)
		else:
			#v21 = CHistoryDataSet::GetTime(&Data);
			#CDataStore::setLastHistTimeStamp(self.DataStore, v21);
			#CDataStore::addHistoryData(self.DataStore, &Data);
			CDataStore.setLastHistoryIndex(self.DataStore, ThisHistoryIndex);
			if ( LatestHistoryIndex >= ThisHistoryIndex ): #unused
				CDataStore.setOutsatndingHistorySets(self.DataStore, LatestHistoryIndex - ThisHistoryIndex) #unused
			else:
				CDataStore.setOutsatndingHistorySets(self.DataStore, LatestHistoryIndex + 18 - ThisHistoryIndex) #unused

		rt = CDataStore.getRequestType(self.DataStore)
		DeviceCS = CDataStore.GetDeviceConfigCS(self.DataStore)
		if   rt == 0: #rtGetCurrent
		      newLength[0] = self.buildACKFrame(Buffer, 5, DeviceCS, ThisHistoryIndex, 0xFFFFFFFF);
		      CDataStore.setRequestState(self.DataStore, ERequestState.rsRunning);
		elif rt == 2: #rtGetConfig
		      newLength[0] = self.buildACKFrame(Buffer, 3, DeviceCS, ThisHistoryIndex, 0xFFFFFFFF);
		      CDataStore.setRequestState(self.DataStore, ERequestState.rsRunning);
		elif rt == 3: #rtSetConfig
		      newLength[0] = self.buildACKFrame(Buffer, 2, DeviceCS, ThisHistoryIndex, 0xFFFFFFFF);
		      CDataStore.setRequestState(self.DataStore, ERequestState.rsRunning);
		elif rt == 1: #rtGetHistory
			CDataStore.setRequestState(self.DataStore, ERequestState.rsFinished);
			CDataStore.RequestNotify(self.DataStore)
			newLength[0] = self.buildACKFrame(Buffer, 0, DeviceCS, ThisHistoryIndex, 0xFFFFFFFF);
		elif rt == 4: #rtSetTime
		      newLength[0] = self.buildACKFrame(Buffer, 1, DeviceCS, ThisHistoryIndex, 0xFFFFFFFF);
		      CDataStore.setRequestState(self.DataStore, ERequestState.rsRunning);
		elif rt == 5 or rt == 6: #rtFirstConfig || #rtINVALID
			newLength[0] = self.buildACKFrame(Buffer, 0, DeviceCS, ThisHistoryIndex, 0xFFFFFFFF);

		Length[0] = newLength[0]
		Buffer[0] = newBuffer[0]

	def handleNextAction(self,Buffer,Length):
		self.logger.debug("")
		newBuffer = [0]
		newBuffer[0] = Buffer[0]
		newLength = [0]
		newLength[0] = Length[0]
		print "handleNextAction:: Buffer[0] %x" % Buffer[0][0]
		print "handleNextAction:: Buffer[1] %x" % Buffer[0][1]
		print "handleNextAction:: Buffer[2] %x (CWeatherStationConfig *)" % (Buffer[0][2] & 0xF)
		rt = CDataStore.getRequestType(self.DataStore)
		HistoryIndex = CDataStore.getLastHistoryIndex(self.DataStore);
		DeviceCS = CDataStore.GetDeviceConfigCS(self.DataStore);
		CDataStore.setLastSeen(self.DataStore, time.time());
		Quality = Buffer[0][3] & 0x7F;
		CDataStore.setLastLinkQuality(self.DataStore, Quality);
		if (Buffer[0][2] & 0xF) == 2: #(CWeatherStationConfig *)
			self.logger.debug("handleNextAction Buffer[2] == 2")
		#	v16 = CDataStore::getFrontEndConfig(self.DataStore, &result);
		#	Data = v16;
		#	[0]v24 = 0;
			newLength[0] = self.buildConfigFrame(newBuffer, v16);
		#	v24 = -1;
		#	CWeatherStationConfig::_CWeatherStationConfig(&result);
		else:
			if (Buffer[0][2] & 0xF) == 3: #(CWeatherStationConfig *)
				self.logger.debug("handleNextAction Buffer[2] == 3")
				newLength[0] = self.buildTimeFrame(newBuffer, 1);
			else:
				self.logger.debug("handleNextAction Buffer[2] == %x" % (Buffer[0][2] & 0xF))
				if   rt == 0: #rtGetCurrent
					newLength[0] = self.buildACKFrame(newBuffer, 5, DeviceCS, HistoryIndex, 0xFFFFFFFF);
					CDataStore.setRequestState(self.DataStore, ERequestState.rsRunning);
				elif rt == 1: #rtGetHistory
					newLength[0] = self.buildACKFrame(newBuffer, 4, DeviceCS, HistoryIndex, 0xFFFFFFFF);
					CDataStore.setRequestState(self.DataStore, ERequestState.rsRunning);
				elif rt == 2: #rtGetConfig
					newLength[0] = self.buildACKFrame(newBuffer, 3, DeviceCS, HistoryIndex, 0xFFFFFFFF);
					CDataStore.setRequestState(self.DataStore, ERequestState.rsRunning);
				elif rt == 3: #rtSetConfig
					newLength[0] = self.buildACKFrame(newBuffer, 2, DeviceCS, HistoryIndex, 0xFFFFFFFF);
					CDataStore.setRequestState(self.DataStore, ERequestState.rsRunning);
				elif rt == 4: #rtSetTime
					newLength[0] = self.buildACKFrame(newBuffer, 1, DeviceCS, HistoryIndex, 0xFFFFFFFF);
					CDataStore.setRequestState(self.DataStore, ERequestState.rsRunning);
				else:
					if ( CDataStore.getFlag_FLAG_FAST_CURRENT_WEATHER(self.DataStore) ):
						newLength[0] = self.buildACKFrame(newBuffer, 5, DeviceCS, HistoryIndex, 0xFFFFFFFF);
					else:
						newLength[0] = self.buildACKFrame(newBuffer, 0, DeviceCS, HistoryIndex, 0xFFFFFFFF);
		Length[0] = newLength[0]
		Buffer[0] = newBuffer[0]

	def CCommunicationService(self):
		self.logger.debug("")
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

		self.logger.debug("start doRFCommunication thread...")
		child = threading.Thread(target=self.doRFCommunication)
		child.start()

	def caluculateFrequency(self,Frequency):
		self.logger.debug("")
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

	def GenerateResponse(self,Buffer,Length):
		self.logger.debug("Length=%x" % Length[0])
		
		newBuffer = [0]
		newBuffer[0] = Buffer[0]
		newLength = [0]
		newLength[0] = Length[0]
		if Length[0] != 0:
			RequestType = CDataStore.getRequestType(self.DataStore)
			#self.logger.debug("RequestType=%x",RequestType)
			if CDataStore.getDeviceRegistered(self.DataStore):

				RegisterdID = CDataStore.getDeviceId(self.DataStore)
				ID = (Buffer[0][0] <<8)| Buffer[0][1]
				self.logger.debug("ID:%x" % ID)

				if ID == RegisterdID:
					#print ((Buffer[0][2] & 0xE0) - 0x20)
					responseType = (Buffer[0][2] & 0xE0) - 0x20
					self.logger.debug("Length %x RegisteredID x%x responseType: x%x" % (Length[0], RegisterdID, responseType))
					if responseType == 0x00:
						#    00000000: 00 00 06 00 32 20
						if Length[0] == 0x06:
							self.handleWsAck(newBuffer, newLength);
						else:
							newLength[0] = 0
					elif responseType == 0x20:
						#    00000000: 00 00 30 00 32 40
						if Length[0] == 0x30:
							self.handleConfig(newBuffer, newLength);
						else:
							newLength[0] = 0
					elif responseType == 0x40:
						#    00000000: 00 00 d7 00 32 60
						if Length[0] == 0xd7: #215
							self.handleCurrentData(newBuffer, newLength);
						else:
							newLength[0] = 0
					elif responseType == 0x60:
						#    00000000: 00 00 1e 00 32 80
						if Length[0] == 0x1e:
							self.handleHistoryData(newBuffer, newLength);
						else:
							newLength[0] = 0
					elif responseType == 0x80:
						#    00000000: 00 00 06 f0 f0 a1
						#    00000000: 00 00 06 00 32 a3
						#    00000000: 00 00 06 00 32 a2
						if Length[0] == 0x06:
							self.handleNextAction(newBuffer, newLength);
						else:
							newLength[0] = 0
					else:
						newLength[0] = 0
				else:
					newLength[0] = 0
			else:
				if RequestType == 5:
					buffer = [None]
					sHID.ReadConfigFlash(0x1fe, 2, buffer);
					#    00000000: dd 0a 01 fe 18 f6 aa 01 2a a2 4d 00 00 87 16 
					TransceiverID = buffer[0][0] << 8;
					TransceiverID += buffer[0][1];
					#print "GenerateResponse: TransceiverID", TransceiverID
					#print "GenerateResponse: Length[0]",Length[0]
					#print "Buffer[0]", Buffer[0]
					if (    Length[0]            !=    6
					    or  Buffer[0][0]         != 0xf0
					    or  Buffer[0][1]         != 0xf0
					    or (Buffer[0][2] & 0xe0) != 0xa0
					    or (Buffer[0][2] & 0x0f) != 1 ):
						ReceivedId  = Buffer[0][0] <<8;
						ReceivedId += Buffer[0][1];
						if ( Length[0] != 6 or ReceivedId != TransceiverID or (Buffer[0][2] & 0xE0) != 0xa0 or (Buffer[0][2] & 0xF) != 3 ):
							#print "#1"
							if ( Length[0] != 48
							 or ReceivedId != TransceiverID
							 or (Buffer[0][2] & 0xE0) != 0x40
							 or CDataStore.getRequestState(self.DataStore) != ERequestState.rsWaitConfig): #5
								newLength[0] = 0;
								#print "#2"
							else:
								#print "#3"
								self.handleConfig(newBuffer, newLength); #temporary commented out
								if Length[0] == 9:
									#print "#4"
									CDataStore.setDeviceId(self.DataStore,TransceiverID);
									CDataStore.setDeviceRegistered(self.DataStore, True);
						else:
							#print "#5"
							newLength[0] = self.buildTimeFrame(newBuffer,0);

					else:
						if RequestType == 5:
							#print "#6"
							HistoryIndex = 0xfffff
							newLength[0] = self.buildACKFrame(newBuffer,3,TransceiverID,HistoryIndex,0xFFFFFFFF)
							self.RepeatCount = 0
							CDataStore.setRequestState(self.DataStore,ERequestState.rsWaitConfig)
						else:
							newLength[0] = 0
				else:
					newLength[0] = 0
		else: #Length[0] == 0
			if self.RepeatCount:
				if (datetime.now() - self.RepeatTime).seconds >1:
					if self.Regenerate:
						newLength[0] = self.buildTimeFrame(newBuffer,1);
					#else:
					#	self.logger.debug("implementami - copia data su buffer")
					#	newBuffer[0] = self.RepeatData, self.RepeatSize
					#newLength[0] = self.RepeatSize;

		Buffer[0] = newBuffer[0]
		Length[0] = newLength[0]
		if newLength[0] == 0:
			return 0
		return 1

	def TransceiverInit(self):
		self.logger.debug("")

		t=self.DataStore.TransceiverSettings
		self.caluculateFrequency(t.Frequency);

		buffer = [None]
		if ( sHID.ReadConfigFlash(0x1F9, 7, buffer) ):
			ID  = buffer[0][5] << 8;
			ID += buffer[0][6];
			self.logger.debug("ID=0x%x" % ID)

			SN  = str("%02d"%(buffer[0][0]))
			SN += str("%02d"%(buffer[0][1]))
			SN += str("%02d"%(buffer[0][2]))
			SN += str("%02d"%(buffer[0][3]))
			SN += str("%02d"%(buffer[0][4]))
			SN += str("%02d"%(buffer[0][5]))
			SN += str("%02d"%(buffer[0][6]))
			CDataStore.setTransceiverSerNo(self.DataStore,SN)

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
		self.logger.debug("")
		import usb

		CDataStore.setFlag_FLAG_TRANSCEIVER_SETTING_CHANGE(self.DataStore,1)

		TransceiverSettings=self.DataStore.TransceiverSettings
		device = sHID.Find(TransceiverSettings.VendorId,TransceiverSettings.ProductId,TransceiverSettings.VersionNo)
		if device:
			self.TransceiverInit()
			CDataStore.setFlag_FLAG_TRANSCEIVER_PRESENT(self.DataStore, 1);
			sHID.SetRX()
		else:
			raise "ws-28xx not present"

		while True:
			RequestType = CDataStore.getRequestType(self.DataStore)
			if RequestType == ERequestType.rtFirstConfig: # ==5
				RequestState = CDataStore.getRequestState(self.DataStore)
				self.logger.debug("RequestState #1 = %d" % RequestState)
				if RequestState:
					#RequestState<>ERequestState.rsQueued
					if RequestState == ERequestState.rsWaitDevice: # == 4
						self.logger.debug("self.getRequestState == 4")
						if DeviceWaitEndTime <= datetime.now():
							print "now=",datetime.now()
							print "DeviceWaitEndTime=",DeviceWaitEndTime
							print "DeviceWaitEndTime < now"
							CDataStore.setRequestState(self.DataStore,ERequestState.rsError);
							CDataStore.RequestNotify(self.DataStore);
				else:
					#RequestState=ERequestState.rsQueued
					sHID.SetPreamblePattern(0xaa)
					sHID.SetState(0x1e)
					CDataStore.setRequestState(self.DataStore,ERequestState.rsPreamble)
					PreambleDuration = CDataStore.getPreambleDuration(self.DataStore);
					PreambleEndTime = datetime.now() + timedelta(milliseconds=PreambleDuration)
					while True:
						if not ( PreambleEndTime >= datetime.now() ):
							break
						if RequestType != CDataStore.getRequestType(self.DataStore):
							break
						CDataStore.RequestTick(self.DataStore);
						time.sleep(0.001) #(thread
						CDataStore.setFlag_FLAG_SERVICE_RUNNING(self.DataStore, True);

					if RequestType == CDataStore.getRequestType(self.DataStore):
						CDataStore.setRequestState(self.DataStore,ERequestState.rsWaitDevice)
						RegisterWaitTime = CDataStore.getRegisterWaitTime(self.DataStore)
						DeviceWaitEndTime = datetime.now() + timedelta(milliseconds=RegisterWaitTime)
						print "DeviceWaitEndTime=",DeviceWaitEndTime
					ret = sHID.SetRX(); #make state from 14 to 15

			DataLength = [0]
			DataLength[0] = 0
			StateBuffer = [None]
			ret = sHID.GetState(StateBuffer);
			self.logger.debug("sHID.GetState=%x" % StateBuffer[0][0])
			if ret == 1:
				FrameBuffer=[0]
				FrameBuffer[0]=[0]*0x03
				ReceiverState = StateBuffer[0][0];
				if ReceiverState == 0x16:
					ret = sHID.GetFrame(FrameBuffer, DataLength);
					if ret == None:
						raise ws28xxError("USBDevice->GetFrame returned false")
					if DataLength[0]:
						strbuf = ""
						for i in xrange(0,DataLength[0]):
							strbuf += str("%.2x" % (FrameBuffer[0][i]))
						#CTracer::WriteDump((CTracer *)td, 50, v22, v23, v24);
						self.logger.debug("CTracer::WriteDump %s" % strbuf) #simulate CTracer::WriteDump
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
					#print "GenerateResp",FrameBuffer[0]
					#print "GenerateResp",DataLength[0]
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
					#print "entro nell'while stronzo"
					while True:
						ret = sHID.GetState(StateBuffer);
						CDataStore.RequestTick(self.DataStore);
						if ret == 0:
							raise "USBDevice->GetState returned false" #it shouldn't be blocking
						ReceiverState = StateBuffer[0];
						if ( not StateBuffer[0]) or (ReceiverState == 0x15 ):
#LABEL_42	
							#while (timeout >= 0) and self.RepeatCount:
							#	self.RepeatCount -= 1;
						#		#*(_QWORD *)&v23 = self.RepeatInterval;
						#		#a delay until I get 0x15
						#		time.sleep(0.0001)
						#		timeout -= 1;
						#if timeout == 0:
							self.RepeatTime = datetime.now()
							time.sleep(0.2)
						break;
						timeout -= 1
						#if ( !timeout )
							#goto label_42
#LABEL_49
					#print "sono fuori dall'while stronzo"
				if ReceiverState != 0x15:
					ret = sHID.SetRX(); #make state from 14 to 15
					#time.sleep(0.5)
				
				#if ReceiverState == 0x15:
				#	if CDataStore.getRequestType(self.DataStore) == 6:
				#		#CDataStore.GetCurrentWeather(self.DataStore)
				#		CDataStore.FirstTimeConfig(self.DataStore)

			if not ret:
				CDataStore.setFlag_FLAG_TRANSCEIVER_PRESENT(self.DataStore, 0)
				pass
			time.sleep(0.001)


#filehandler = open("WV5DataStore", 'w')
#pickle.dump(CDataStore.TransceiverSettings, filehandler)

#myCCommunicationService.getInstance()
#myCCommunicationService.doRFCommunication()

#t = ThreadClass()
#t.start()

if __name__ == "__main__":
	import logging
#CRITICAL 50 
#ERROR 40 
#WARNING 30 
#INFO 20 
#DEBUG 10 
#NOTSET 0 
#	logging.basicConfig(format='%(asctime)s %(name)s %(message)s',filename="HeavyWeatherService.log",level=logging.DEBUG)
	logging.basicConfig(format='%(asctime)s %(name)s.%(funcName)s %(message)s',filename="HeavyWeatherService.log",level=logging.DEBUG)

	print "Press [v] key on Weather Station"
	myCCommunicationService = CCommunicationService()
	CDataStore.setCommModeInterval(myCCommunicationService.DataStore,3) #move me to setfrontendalive
	time.sleep(5)

	TimeOut = CDataStore.getPreambleDuration(myCCommunicationService.DataStore) + CDataStore.getRegisterWaitTime(myCCommunicationService.DataStore)
	print "FirstTimeConfig Timeout=%d" % TimeOut
	ID=[0]
	ID[0]=0
	CDataStore.FirstTimeConfig(myCCommunicationService.DataStore,ID,TimeOut)

	CDataStore.setDeviceRegistered(myCCommunicationService.DataStore, True); #temp hack
	CDataStore.setDeviceId(myCCommunicationService.DataStore, 0x32); #temp hack

	Weather = [0]
	Weather[0]=[0]

	TimeOut = CDataStore.getPreambleDuration(myCCommunicationService.DataStore) + CDataStore.getRegisterWaitTime(myCCommunicationService.DataStore)
	CDataStore.GetCurrentWeather(myCCommunicationService.DataStore,Weather,TimeOut)
	time.sleep(1)

	while True:
		if CDataStore.getRequestState(myCCommunicationService.DataStore) == ERequestState.rsFinished \
		   or CDataStore.getRequestState(myCCommunicationService.DataStore) == ERequestState.rsINVALID:
			TimeOut = CDataStore.getPreambleDuration(myCCommunicationService.DataStore) + CDataStore.getRegisterWaitTime(myCCommunicationService.DataStore)
			CDataStore.GetCurrentWeather(myCCommunicationService.DataStore,Weather,TimeOut)
			#print "done"
		time.sleep(10)

