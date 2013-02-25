

from datetime import datetime
from datetime import timedelta
from configobj import ConfigObj

import EConstants
import BitHandling
import CWeatherStationConfig
import threading
import logging
import CCurrentWeatherData
import CHistoryDataSet

BitHandling = BitHandling.BitHandling()
ERequestType = EConstants.ERequestType()
ERequestState=EConstants.ERequestState()

class CDataStore(object):

	class TBufferCheck:
		eBufferCheckInactive = 0
		eBufferCheckRequired = 1
		eBufferCheckRunning = 2

	class TTransceiverSettings(object): 
		# void __thiscall CDataStore::TTransceiverSettings::TTransceiverSettings(CDataStore::TTransceiverSettings *this);
		def __init__(self):
			self.VendorId	= 0x6666
			self.ProductId	= 0x5555
			self.VersionNo	= 1
			self.Frequency	= 905000000
			self.TransmissionFrequency = 0
			self.manufacturer	= "LA CROSSE TECHNOLOGY"
			self.product		= "Weather Direct Light Wireless Device"

	class TRequest(object):
		# void __thiscall CDataStore::TRequest::TRequest(CDataStore::TRequest *this);
		def __init__(self):
			self.Type = 6
			self.State = ERequestState.rsError
			self.TTL = 90000
			self.Lock = threading.Lock()
			self.CondFinish = threading.Condition()

	class TLastStat(object):
		# void __thiscall CDataStore::TLastStat::TLastStat(CDataStore::TLastStat *this);
		def __init__(self):
			self.LastBatteryStatus = [0]
			self.LastLinkQuality = 0
			self.OutstandingHistorySets = -1
			self.WeatherClubTransmissionErrors = 0
			self.LastCurrentWeatherTime = datetime(1900, 01, 01, 00, 00)
			self.LastHistoryDataTime = datetime(1900, 01, 01, 00, 00)
			self.LastConfigTime = datetime(1900, 01, 01, 00, 00)
			self.LastWeatherClubTransmission = None
			self.LastSeen = None

			filename= "/tmp/WV5Datastore.cfg"
			config = ConfigObj(filename)
			config.filename = filename
			try:
				self.LastHistoryIndex = int(config['LastStat']['LastHistoryIndex'])
			except:
				self.LastHistoryIndex = 0xffff
				pass

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
		self.Flags = 0;
		self.Settings = 0;
		self.TransceiverSettings = 0;
		self.WeatherClubSettings = 0;
		self.HistoryData = CHistoryDataSet.CHistoryDataSet();
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

		self.DeviceConfig = CWeatherStationConfig.CWeatherStationConfig()

		self.TransceiverSerNo = None
		self.TransceiveID = None

		#ShelveDataStore=shelve.open("WV5DataStore",writeback=True)

		#if ShelveDataStore.has_key("Settings"):
		#	self.DataStore.Settings = ShelveDataStore["Settings"]
		#else:
		#	print ShelveDataStore.keys()
		if self.Request:
		    self.logger.debug("ok")
		    
		    

	def writeLastStat(self):
		filename= "/tmp/WV5Datastore.cfg"
		config = ConfigObj(filename)
		config.filename = filename
		config['LastStat'] = {}
		config['LastStat']['LastLinkQuality'] = str(self.LastStat.LastLinkQuality)
		config['LastStat']['LastSeen'] = str(self.LastStat.LastSeen)
		config['LastStat']['LastHistoryIndex'] = str(self.LastStat.LastHistoryIndex)
		config['LastStat']['LastCurrentWeatherTime'] = str(self.LastStat.LastCurrentWeatherTime)
		config['LastStat']['LastHistoryDataTime'] = str(self.LastStat.LastHistoryDataTime)
		config['LastStat']['LastConfigTime'] = str(self.LastStat.LastConfigTime)
		config.write()

	def writeSettings(self):
		filename= "/etc/WV5Datastore.cfg"
		config = ConfigObj(filename)
		config.filename = filename
		config['Settings'] = {}
		config['Settings']['DeviceID'] = str(self.Settings.DeviceId)
		
		config.write()

	def writeDataStore(self):
		filename= "/etc/WV5Datastore.cfg"
		config = ConfigObj(filename)
		config.filename = filename
		config['DataStore'] = {}
		config['DataStore']['TransceiverSerNo'] = self.TransceiverSerNo
		config.write()

	def getDeviceConfig(self,result):
		self.logger.debug("")

	def getTransmissionFrequency(self):
		filename= "/etc/WV5Datastore.cfg"
		config = ConfigObj(filename)
		config.filename = filename
		try:
			self.TransceiverSettings.TransmissionFrequency = int(config['TransceiverSettings']['TransmissionFrequency'])
		except:
			pass
		self.logger.debug("TransceiverSettings.TransmissionFrequency=%x" % self.TransceiverSettings.TransmissionFrequency)
		#print "TransceiverSettings.TransmissionFrequency=%x" % self.TransceiverSettings.TransmissionFrequency
		return self.TransceiverSettings.TransmissionFrequency

	def setTransmissionFrequency(self,val):
		filename= "/etc/WV5Datastore.cfg"
		config = ConfigObj(filename)
		config.filename = filename
		config['TransceiverSettings'] = {}
		config['TransceiverSettings']['TransmissionFrequency'] = val
		config.write()

	def getDeviceId(self):
		filename= "/etc/WV5Datastore.cfg"
		config = ConfigObj(filename)
		config.filename = filename
		try:
			self.Settings.DeviceId = int(config['Settings']['DeviceID'])
		except:
			pass
		self.logger.debug("Settings.DeviceId=%x" % self.Settings.DeviceId)
		#print "Settings.DeviceId=%x" % self.Settings.DeviceId
		return self.Settings.DeviceId

	def setDeviceId(self,val):
		self.logger.debug("val=%x" % val)
		self.Settings.DeviceId = val
		self.writeSettings()

	def getFlag_FLAG_TRANSCEIVER_SETTING_CHANGE(self):	# <4>
		self.logger.debug("")
		#return self.Flags_FLAG_TRANSCEIVER_SETTING_CHANGE
		#std::bitset<5>::at(thisa->Flags, &result, 4u);
		return BitHandling.testBit(self.Flags, 4)

	def getFlag_FLAG_FAST_CURRENT_WEATHER(self):		# <2>
		self.logger.debug("")
		#return self.Flags_FLAG_SERVICE_RUNNING
		#std::bitset<5>::at(thisa->Flags, &result, 2u);
		return BitHandling.testBit(self.Flags, 2)

	def getFlag_FLAG_TRANSCEIVER_PRESENT(self):		# <0>
		Flag = BitHandling.testBit(self.Flags, 0)
		self.logger.debug("getFlag_FLAG_TRANSCEIVER_PRESENT=%d" % Flag)
		#return self.Flags_FLAG_TRANSCEIVER_PRESENT
		return Flag

	def getFlag_FLAG_SERVICE_RUNNING(self):			# <3>
		self.logger.debug("")
		#return self.Flags_FLAG_SERVICE_RUNNING
		return BitHandling.testBit(self.Flags, 3)

	def setFlag_FLAG_TRANSCEIVER_SETTING_CHANGE(self,val):	# <4>
		self.logger.debug("")
		#std::bitset<5>::set(thisa->Flags, 4u, val);
		self.Flags = BitHandling.setBitVal(self.Flags,4,val)

	def setFlag_FLAG_FAST_CURRENT_WEATHER(self,val):	# <2>
		self.logger.debug("")
		#std::bitset<5>::set(thisa->Flags, 2u, val);
		self.Flags = BitHandling.setBitVal(self.Flags,2,val)

	def setFlag_FLAG_TRANSCEIVER_PRESENT(self,val):		# <0>
		self.logger.debug("")
		#std::bitset<5>::set(thisa->Flags, 0, val);
		self.Flags_FLAG_TRANSCEIVER_PRESENT = val
		self.Flags = BitHandling.setBitVal(self.Flags,0,val)

	def setFlag_FLAG_SERVICE_RUNNING(self,val):		# <3>
		self.logger.debug("")
		#std::bitset<5>::set(thisa->Flags, 3u, val);
		self.Flags_FLAG_SERVICE_RUNNING = val
		self.Flags = BitHandling.setBitVal(self.Flags,3,val)

	def setLastLinkQuality(self,Quality):
		self.logger.debug("Quality=%d",Quality)
		self.LastStat.LastLinkQuality = Quality
		self.writeLastStat()

	def setLastSeen(self,time):
		self.logger.debug("time=%s",time)
		self.LastStat.LastSeen = time
		self.writeLastStat()

	def getLastSeen(self):
		self.logger.debug("LastSeen=%d",self.LastStat.LastSeen)
		return self.LastStat.LastSeen

	def setLastBatteryStatus(self, BatteryStat):
		self.logger.debug("")
		self.logger.info("Battery 3=%d 0=%d 1=%d 2=%d" % (BitHandling.testBit(BatteryStat,3),BitHandling.testBit(BatteryStat,0),BitHandling.testBit(BatteryStat,1),BitHandling.testBit(BatteryStat,2)))
		self.LastStat.LastBatteryStatus = BatteryStat

	def setCurrentWeather(self,Data):
		self.logger.debug("")
		self.CurrentWeather = Data

	def addHistoryData(self,Data):
		self.logger.debug("")
		self.HistoryData = Data

	def getHistoryData(self,clear):
		self.logger.debug("")
		
		import copy
		
		self.Request.Lock.acquire()
		History = copy.copy(self.HistoryData)
		self.Request.Lock.release()
		return History

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
		self.logger.debug("time=%s" % time)
		self.LastStat.LastCurrentWeatherTime = time
		self.writeLastStat()

	def setLastHistoryDataTime(self,time):
		self.logger.debug("time=%s" % time)
		self.LastStat.LastHistoryDataTime = time
		self.writeLastStat()

	def setLastConfigTime(self,time):
		self.logger.debug("time=%s" % time)
		self.LastStat.LastConfigTime = time
		self.writeLastStat()

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
		self.writeDataStore()

	def getTransceiverSerNo(self):
		self.logger.debug("getTransceiverSerNo=%s" % self.TransceiverSerNo)
		return self.TransceiverSerNo

	def setLastHistoryIndex(self,val):
		self.LastStat.LastHistoryIndex = val
		self.logger.debug("self.LastStat.LastHistoryIndex=%x" % self.LastStat.LastHistoryIndex)
		self.writeLastStat()

	def getLastHistoryIndex(self):
		self.logger.debug("LastHistoryIndex=%x" % self.LastStat.LastHistoryIndex)
		#print "CDataStore::getLastHistoryIndex %x" % self.LastStat.LastHistoryIndex
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
		self.logger.critical("FirstTimeConfig")
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
		else:
			self.logger.debug("FirstTimeConfig: self.getFlag_FLAG_TRANSCEIVER_PRESENT ko")
			print "FirstTimeConfig: self.getFlag_FLAG_TRANSCEIVER_PRESENT ko"


	def GetCurrentWeather(self,Weather,TimeOut):
		self.logger.debug("timeout=%d DeviceRegistered=%d" % (TimeOut, self.getDeviceRegistered() ) )
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
		else:
			print "GetCurrentWeather - warning: flag False or getDeviceRegistered false"

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
		return self.DeviceConfig.GetCheckSum()

	def RequestTick(self):
		self.logger.debug("")
		if self.Request.Type != 6:
			self.Request.TTL -= 1
			if not self.Request.TTL:
				self.Request.Type = 6
				self.Request.State = 8
				print "internal timeout, request aborted"

