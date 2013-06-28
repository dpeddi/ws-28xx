#!/usr/bin/python

#define BYTE3(v) ((u8)((u32)(v) >> 24))

from datetime import datetime
from datetime import timedelta
import logging
import time
import threading
import CDataStore
import sHID

import EConstants

from CWeatherStationConfig import CWeatherStationConfig
import CCurrentWeatherData
import CHistoryDataSet
import USBHardware

ERequestType=EConstants.ERequestType()
ERequestState=EConstants.ERequestState()

USBHardware=USBHardware.USBHardware()

sHID = sHID.sHID()

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

		self.DataStore = CDataStore.CDataStore(1)
		self.Instance = self.CCommunicationService()
		
		self.kill_received = False

	def getInstance(self):
		self.logger.debug("partially implemented")
		self.CCommunicationService();

	def buildTimeFrame(self,Buffer,checkMinuteOverflow):
		self.logger.debug("checkMinuteOverflow=%x" % checkMinuteOverflow)

		DeviceCheckSum = self.DataStore.GetDeviceConfigCS()
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
			HistoryIndex = self.DataStore.getLastHistoryIndex();
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

#(newBuffer,3,TransceiverID,HistoryIndex,0xFFFFFFFF)
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
#				ATL::COleDateTime::operator_(&now, &ts, &Stat.LastCurrentWeatherTime);
#			if ( ATL::COleDateTimeSpan::GetTotalSeconds(&ts) >= 8.0 )
#				Action = 5;
			if datetime.now() - self.DataStore.LastStat.LastCurrentWeatherTime >= timedelta(seconds=8):
				Action = 5
#			v28 = -1;
		newBuffer[0][2] = Action & 0xF;
#		v21 = CDataStore::GetDeviceConfigCS();
		if ( HistoryIndex >= 0x705 ):
			HistoryAddress = 0xffffff;
		else:
#			if ( !self.DataStore.getBufferCheck() ):
#				if ( !ATL::COleDateTime::GetStatus(&Stat.LastHistoryDataTime) ):
#				{
#					v9 = ATL::COleDateTime::operator_(&now, &result, &Stat.LastHistoryDataTime);
#					if ( ATL::COleDateTimeSpan::operator>(v9, &BUFFER_OVERFLOW_SPAN) )
#					{
#						val = 1;
#						self.DataStore.setBufferCheck( &val);
#					}
#				}
#			}
			if   ( self.DataStore.getBufferCheck() != 1
			  and self.DataStore.getBufferCheck() != 2 ):
				HistoryAddress = 18 * HistoryIndex + 0x1a0;
			else:
				if ( HistoryIndex != 0xffff ):
					HistoryAddress = 18 * (HistoryIndex - 1) + 0x1a0;
				else:
					HistoryAddress = 0x7fe8;
				self.DataStore.setBufferCheck( 2);
		newBuffer[0][3] = (CheckSum >> 8) &0xFF;
		newBuffer[0][4] = (CheckSum >> 0) &0xFF;
		if ( ComInt == 0xFFFFFFFF ):
			ComInt = self.DataStore.getCommModeInterval();
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
		self.DataStore.setLastSeen( datetime.now());
		BatteryStat = (Buffer[0][2] & 0xF);
		self.DataStore.setLastBatteryStatus( BatteryStat);
		Quality = Buffer[0][3] & 0x7F;
		self.DataStore.setLastLinkQuality( Quality);
		ReceivedCS = (Buffer[0][4] << 8) + Buffer[0][5];
		rt = self.DataStore.getRequestType()
		#if ( rt == ERequestType.rtSetConfig ) #rtSetConfig
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
		#	if ( rt == ERequestType.rtSetTime ) #rtSetTime (unused)
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
		#v73 = -1;
		#CWeatherStationConfig::_CWeatherStationConfig(&RecConfig);
		Length[0] = 0

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
			rt = self.DataStore.getRequestType();
			#ATL::COleDateTime::GetTickCount(&now);
			#v43 = (CDataStore::ERequestState)&now;
			#v9 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
			#CDataStore::setLastSeen( (ATL::COleDateTime *)v43);
			BatteryStat = (newBuffer[0][2] & 0xF);
			self.DataStore.setLastBatteryStatus( BatteryStat);
			Quality = newBuffer[0][3] & 0x7F
			self.DataStore.setLastLinkQuality( Quality)
			#FrontCS = CDataStore::GetFrontEndConfigCS();
			HistoryIndex = self.DataStore.getLastHistoryIndex();
			#v46 = (CWeatherStationConfig *)rt;
			if 1==1: #hack ident
				if   rt == ERequestType.rtSetConfig:
					print "handleConfig rt==3 rtSetConfig"
					#v43 = (CDataStore::ERequestState)&result;
					#rhs = v46;
					#LOBYTE(v73) = 4;
					#v51 = CWeatherStationConfig::operator__(&RecConfig, CDataStore::getFrontEndConfig( (CWeatherStationConfig *)v43))
					#LOBYTE(v73) = 3;
					#CWeatherStationConfig::_CWeatherStationConfig(&result);
					#if ( v51 ):
						#*Length = CCommunicationService::buildACKFrame(thisa, Buffer, 0, &FrontCS, &HistoryIndex, 0xFFFFFFFFu);
						#self.DataStore.setLastConfigTime( datetime.now())
						#v43 = (CDataStore::ERequestState)&RecConfig;
						#v16 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
						#CDataStore::setDeviceConfig(v16, (CWeatherStationConfig *)v43);
						#self.DataStore.setRequestState( ERequestState.rsFinished); #2
						#v18 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
						#CDataStore::RequestNotify(v18);
					#else:
					#	CheckSum = CWeatherStationConfig::GetCheckSum(&RecConfig);
					#	*Length = CCommunicationService::buildACKFrame(thisa, Buffer, 2, &CheckSum, &HistoryIndex, 0xFFFFFFFFu);
					#	self.DataStore.setRequestState( ERequestState.rsRunning); #1
				elif rt == ERequestType.rtGetConfig:
					print "handleConfig rt==2 rtGetConfig"
					self.DataStore.setLastConfigTime( datetime.now())
					#v43 = (CDataStore::ERequestState)&RecConfig;
					#v21 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
					#CDataStore::setDeviceConfig(v21, (CWeatherStationConfig *)v43);
					#v54 = CWeatherStationConfig::GetCheckSum(&RecConfig);
					#*Length = CCommunicationService::buildACKFrame(thisa, Buffer, 0, &v54, &HistoryIndex, 0xFFFFFFFF);
					self.DataStore.setRequestState( ERequestState.rsFinished); #2
					self.DataStore.RequestNotify();
				elif rt == ERequestType.rtGetCurrent:
					print "handleConfig rt==0 rtGetCurrent"
					self.DataStore.setLastConfigTime( datetime.now())
					#v43 = (CDataStore::ERequestState)&RecConfig;
					#v25 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
					#CDataStore::setDeviceConfig(v25, (CWeatherStationConfig *)v43);
					v55 = CWeatherStationConfig.GetCheckSum(RecConfig);
					newLength[0] = self.buildACKFrame(newBuffer, 5, v55, HistoryIndex, 0xFFFFFFFF);
					self.DataStore.setRequestState( ERequestState.rsRunning); #1
				elif rt == ERequestType.rtGetHistory:
					print "handleConfig rt==1 rtGetHistory"
					self.DataStore.setLastConfigTime( datetime.now())
					#v43 = (CDataStore::ERequestState)&RecConfig;
					#v28 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
					#CDataStore::setDeviceConfig(v28, (CWeatherStationConfig *)v43);
					#v56 = CWeatherStationConfig::GetCheckSum(&RecConfig);
					#*Length = CCommunicationService::buildACKFrame(thisa, Buffer, 4, &v56, &HistoryIndex, 0xFFFFFFFFu);
					self.DataStore.setRequestState( ERequestState.rsRunning); #1
				elif rt == ERequestType.rtSetTime:
					print "handleConfig rt==4 rtSetTime"
					self.DataStore.setLastConfigTime( datetime.now())
					#v43 = (CDataStore::ERequestState)&RecConfig;
					#v31 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
					#CDataStore::setDeviceConfig(v31, (CWeatherStationConfig *)v43);
					#v57 = CWeatherStationConfig::GetCheckSum(&RecConfig);
					#*Length = CCommunicationService::buildACKFrame(thisa, Buffer, 1, &v57, &HistoryIndex, 0xFFFFFFFFu);
					self.DataStore.setRequestState( ERequestState.rsRunning); #1
				elif rt == ERequestType.rtFirstConfig:
					print "handleConfig rt==5 rtFirstConfig"
					self.DataStore.setLastConfigTime( datetime.now())
					#v43 = (CDataStore::ERequestState)&RecConfig;
					#self.DataStore.setDeviceConfig( (CWeatherStationConfig *)v43);
					v58 = CWeatherStationConfig.GetCheckSum(RecConfig);
					newLength[0] = self.buildACKFrame(newBuffer, 0, v58, HistoryIndex, 0xFFFFFFFF);
					self.DataStore.setRequestState( ERequestState.rsFinished); #2
					self.DataStore.RequestNotify();
				elif rt == ERequestType.rtINVALID:
					print "handleConfig rt==6 rtINVALID"
					self.DataStore.setLastConfigTime( datetime.now())
					#v43 = (CDataStore::ERequestState)&RecConfig;
					#self.DataStore.setDeviceConfig( (CWeatherStationConfig *)v43);
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
		self.DataStore.setLastSeen( datetime.now());
		self.DataStore.setLastCurrentWeatherTime( datetime.now())
		BatteryStat = (Buffer[0][2] & 0xF);
		self.DataStore.setLastBatteryStatus( BatteryStat);
		Quality = Buffer[0][3] & 0x7F;
		self.DataStore.setLastLinkQuality( Quality);
		self.DataStore.setCurrentWeather( Data);
		#self.setCurrentWeather(Data)

		rt = self.DataStore.getRequestType();
		DeviceCS = self.DataStore.GetDeviceConfigCS()
		HistoryIndex = self.DataStore.getLastHistoryIndex();

		if   rt == ERequestType.rtGetCurrent: #rtGetCurrent
			self.DataStore.setRequestState( ERequestState.rsFinished); #2
			self.DataStore.RequestNotify();
			newLength[0] = self.buildACKFrame(newBuffer, 0, DeviceCS, HistoryIndex, 0xFFFFFFFF);
		elif rt == ERequestType.rtGetConfig: #rtGetConfig
			newLength[0] = self.buildACKFrame(newBuffer, 3, DeviceCS, HistoryIndex, 0xFFFFFFFF);
			self.DataStore.setRequestState( ERequestState.rsRunning); #1
		elif rt == ERequestType.rtSetConfig: #rtSetConfig
			newLength[0] = self.buildACKFrame(newBuffer, 2, DeviceCS, HistoryIndex, 0xFFFFFFFF);
			self.DataStore.setRequestState( ERequestState.rsRunning); #1
		elif rt == ERequestType.rtGetHistory: #rtGetHistory
			newLength[0] = self.buildACKFrame(newBuffer, 4, DeviceCS, HistoryIndex, 0xFFFFFFFF);
			self.DataStore.setRequestState( ERequestState.rsRunning); #1
		elif rt == ERequestType.rtSetTime: #rtSetTime
			newLength[0] = self.buildACKFrame(newBuffer, 1, DeviceCS, HistoryIndex, 0xFFFFFFFF);
			self.DataStore.setRequestState( ERequestState.rsRunning); #1
		elif rt == ERequestType.rtFirstConfig or rt == ERequestType.rtINVALID: #rtFirstConfig || #rtINVALID
			newLength[0] = self.buildACKFrame(newBuffer, 0, DeviceCS, HistoryIndex, 0xFFFFFFFF);

		Length[0] = newLength[0]
		Buffer[0] = newBuffer[0]

	def handleHistoryData(self,Buffer,Length):
		self.logger.debug("")
		newBuffer = [0]
		newBuffer[0] = Buffer[0]
		newLength = [0]
		Data = CHistoryDataSet.CHistoryDataSet() #similar to currentwheather as it works ;-)
		Data.CHistoryDataSet_buf(newBuffer, 12)
		#ATL::COleDateTime::GetTickCount(&now);
		self.DataStore.setLastSeen( datetime.now());
		BatteryStat = (Buffer[0][2] & 0xF);
		self.DataStore.setLastBatteryStatus( BatteryStat);
		Quality = Buffer[0][3] & 0x7F;
		self.DataStore.setLastLinkQuality( Quality);
		LatestHistoryAddres = ((((Buffer[0][6] & 0xF) << 8) | Buffer[0][7]) << 8) | Buffer[0][8];
		ThisHistoryAddres = ((((Buffer[0][9] & 0xF) << 8) | Buffer[0][10]) << 8) | Buffer[0][11];
		ThisHistoryIndex = (ThisHistoryAddres - 415) / 0x12;
		LatestHistoryIndex = (LatestHistoryAddres - 415) / 0x12;
		#v6 = CTracer::Instance();
		#CTracer::WriteTrace(v6, 40, "ThisAddress: %X\tLatestAddress: %X");
		#v7 = CTracer::Instance();
		#CTracer::WriteTrace(v7, 40, "ThisIndex: %X\tLatestIndex: %X");
		#v38 = CDataStore::getBufferCheck();
		#    if ( self.DataStore.getBufferCheck() != 2 ):
		#      j___wassert(
		#        L"false",
		#        L"c:\\svn\\heavyweather\\trunk\\applications\\backend\\communicationservice.cpp",
		#        __LINE__Var + 85);
		#    v9 = boost::shared_ptr<CDataStore>::operator_>(&thisa->DataStore);
		#v10 = CTracer::Instance();
		#CTracer::WriteTrace(v10, 40, "getLastHistoryIndex(): %X",self.DataStore.getLastHistoryIndex());
		if ( ThisHistoryIndex == self.DataStore.getLastHistoryIndex()):
		#	CDataStore::getLastHistTimeStamp( &LastHistTs);
			if 1 == 1:
		#	if ( !ATL::COleDateTime::GetStatus(&LastHistTs) )
				if 1 == 1:
		#		if ( !ATL::COleDateTime::GetStatus(CHistoryDataSet::GetTime(&Data)) ):
					if 1 == 1:
		#			if ( ATL::COleDateTime::operator__(CHistoryDataSet::GetTime(&Data), &LastHistTs) ):
		#				CDataStore::setOutsatndingHistorySets( 0xFFFFFFFFu);
		#				self.DataStore.setLastHistoryIndex( 0xFFFFFFFF);
		#				ThisHistoryIndex = -1;
		#				ATL::COleDateTime::COleDateTime(&InvalidDateTime);
		#				ATL::COleDateTime::SetStatus(&InvalidDateTime, partial);
		#				CDataStore::setLastHistTimeStamp( &InvalidDateTime);
		#			else:
						self.DataStore.setLastHistoryDataTime( datetime.now())
			self.DataStore.setBufferCheck( 0)
		else:
			#CDataStore::setLastHistTimeStamp( CHistoryDataSet::GetTime(&Data));
			#CDataStore::addHistoryData( &Data);
			self.DataStore.addHistoryData(Data);
			self.DataStore.setLastHistoryIndex( ThisHistoryIndex);
			if ( LatestHistoryIndex >= ThisHistoryIndex ): #unused
				self.DataStore.setOutsatndingHistorySets( LatestHistoryIndex - ThisHistoryIndex) #unused
			else:
				self.DataStore.setOutsatndingHistorySets( LatestHistoryIndex + 18 - ThisHistoryIndex) #unused

		rt = self.DataStore.getRequestType()
		DeviceCS = self.DataStore.GetDeviceConfigCS()
		if   rt == ERequestType.rtGetCurrent: #rtGetCurrent
			newLength[0] = self.buildACKFrame(Buffer, 5, DeviceCS, ThisHistoryIndex, 0xFFFFFFFF);
			self.DataStore.setRequestState( ERequestState.rsRunning);
		elif rt == ERequestType.rtGetConfig: #rtGetConfig
			newLength[0] = self.buildACKFrame(Buffer, 3, DeviceCS, ThisHistoryIndex, 0xFFFFFFFF);
			self.DataStore.setRequestState( ERequestState.rsRunning);
		elif rt == ERequestType.rtSetConfig: #rtSetConfig
			newLength[0] = self.buildACKFrame(Buffer, 2, DeviceCS, ThisHistoryIndex, 0xFFFFFFFF);
			self.DataStore.setRequestState( ERequestState.rsRunning);
		elif rt == ERequestType.rtGetHistory: #rtGetHistory
			self.DataStore.setRequestState( ERequestState.rsFinished);
			self.DataStore.RequestNotify()
			newLength[0] = self.buildACKFrame(Buffer, 0, DeviceCS, ThisHistoryIndex, 0xFFFFFFFF);
		elif rt == ERequestType.rtSetTime: #rtSetTime
			newLength[0] = self.buildACKFrame(Buffer, 1, DeviceCS, ThisHistoryIndex, 0xFFFFFFFF);
			self.DataStore.setRequestState( ERequestState.rsRunning);
		elif rt == ERequestType.rtFirstConfig or rt == ERequestType.rtINVALID: #rtFirstConfig || #rtINVALID
			newLength[0] = self.buildACKFrame(Buffer, 0, DeviceCS, ThisHistoryIndex, 0xFFFFFFFF);

		Length[0] = newLength[0]
		Buffer[0] = newBuffer[0]

	def handleNextAction(self,Buffer,Length):
		self.logger.debug("")
		newBuffer = [0]
		newBuffer[0] = Buffer[0]
		newLength = [0]
		newLength[0] = Length[0]
		#print "handleNextAction:: Buffer[0] %x" % Buffer[0][0]
		#print "handleNextAction:: Buffer[1] %x" % Buffer[0][1]
		#print "handleNextAction:: Buffer[2] %x (CWeatherStationConfig *)" % (Buffer[0][2] & 0xF)
		rt = self.DataStore.getRequestType()
		HistoryIndex = self.DataStore.getLastHistoryIndex();
		DeviceCS = self.DataStore.GetDeviceConfigCS();
		self.DataStore.setLastSeen( datetime.now());
		Quality = Buffer[0][3] & 0x7F;
		self.DataStore.setLastLinkQuality( Quality);
		if (Buffer[0][2] & 0xF) == 2: #(CWeatherStationConfig *)
			self.logger.debug("handleNextAction Buffer[2] == 2")
		#	v16 = CDataStore::getFrontEndConfig( &result);
		#	Data = v16;
			newLength[0] = self.buildConfigFrame(newBuffer, v16);
		#	CWeatherStationConfig::_CWeatherStationConfig(&result);
		else:
			if (Buffer[0][2] & 0xF) == 3: #(CWeatherStationConfig *)
				self.logger.debug("handleNextAction Buffer[2] == 3")
				newLength[0] = self.buildTimeFrame(newBuffer, 1);
			else:
				self.logger.debug("handleNextAction Buffer[2] == %x" % (Buffer[0][2] & 0xF))
				if   rt == ERequestType.rtGetCurrent: #rtGetCurrent
					newLength[0] = self.buildACKFrame(newBuffer, 5, DeviceCS, HistoryIndex, 0xFFFFFFFF);
					self.DataStore.setRequestState( ERequestState.rsRunning);
				elif rt == ERequestType.rtGetHistory: #rtGetHistory
					newLength[0] = self.buildACKFrame(newBuffer, 4, DeviceCS, HistoryIndex, 0xFFFFFFFF);
					self.DataStore.setRequestState( ERequestState.rsRunning);
				elif rt == ERequestType.rtGetConfig: #rtGetConfig
					newLength[0] = self.buildACKFrame(newBuffer, 3, DeviceCS, HistoryIndex, 0xFFFFFFFF);
					self.DataStore.setRequestState( ERequestState.rsRunning);
				elif rt == ERequestType.rtSetConfig: #rtSetConfig
					newLength[0] = self.buildACKFrame(newBuffer, 2, DeviceCS, HistoryIndex, 0xFFFFFFFF);
					self.DataStore.setRequestState( ERequestState.rsRunning);
				elif rt == ERequestType.rtSetTime: #rtSetTime
					newLength[0] = self.buildACKFrame(newBuffer, 1, DeviceCS, HistoryIndex, 0xFFFFFFFF);
					self.DataStore.setRequestState( ERequestState.rsRunning);
				else:
					if ( self.DataStore.getFlag_FLAG_FAST_CURRENT_WEATHER() ):
						newLength[0] = self.buildACKFrame(newBuffer, 5, DeviceCS, HistoryIndex, 0xFFFFFFFF);
					else:
						newLength[0] = self.buildACKFrame(newBuffer, 0, DeviceCS, HistoryIndex, 0xFFFFFFFF);
		Length[0] = newLength[0]
		Buffer[0] = newBuffer[0]

	def CCommunicationService(self):
		self.logger.debug("")
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.IFMODE]     = 0x00;
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.MODULATION] = 0x41; #fsk
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.ENCODING]   = 0x07;
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.FRAMING]    = 0x84; #1000:0100 ##?hdlc? |1000 010 0
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
			self.logger.debug("CorVal: %x" % CorVal) #0x184e8
			FreqVal += CorVal;

		#print "try to tune sensors"
		#Frequency = 915450000
		#FreqVal =  long(Frequency / 16000000.0 * 16777216.0);

		if ( not (FreqVal % 2) ):
			FreqVal+=1;
			#FreqVal = 949060841 0x389184e9
			#print "Freq:",CorVal,(CorVal / 16777216 * 16000000 + 1)
			#FreqVal= 915450000 / 16000000 * 16777216 + 1
			#print "experiment:",FreqVal,CorVal
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.FREQ3] = (FreqVal >>24) & 0xFF;
		#print "dd %x" % (self.AX5051RegisterNames_map[self.AX5051RegisterNames.FREQ3])
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.FREQ2] = (FreqVal >>16) & 0xFF;
		#print "dd %x" % (self.AX5051RegisterNames_map[self.AX5051RegisterNames.FREQ2])
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.FREQ1] = (FreqVal >>8)  & 0xFF;
		#print "dd %x" % (self.AX5051RegisterNames_map[self.AX5051RegisterNames.FREQ1])
		self.AX5051RegisterNames_map[self.AX5051RegisterNames.FREQ0] = (FreqVal >>0)  & 0xFF;
		#print "dd %x" % (self.AX5051RegisterNames_map[self.AX5051RegisterNames.FREQ0])
		self.logger.debug("FreqVal: %x" % FreqVal)

	def GenerateResponse(self,Buffer,Length):
		self.logger.debug("Length=%x" % Length[0])
		
		newBuffer = [0]
		newBuffer[0] = Buffer[0]
		newLength = [0]
		newLength[0] = Length[0]
		if Length[0] != 0:
			RequestType = self.DataStore.getRequestType()
			#self.logger.debug("RequestType=%x",RequestType)
			if self.DataStore.getDeviceRegistered():

				RegisterdID = self.DataStore.getDeviceId()
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
					#print "Unrecognized TransceiverID=%x" % ID
					self.logger.critical("Unrecognized ID=%x" % ID)
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
							 or self.DataStore.getRequestState() != ERequestState.rsWaitConfig): #5
								newLength[0] = 0;
								#print "#2"
							else:
								#print "#3"
								self.handleConfig(newBuffer, newLength);
								if newLength[0] == 9:
									#print "#4"
									self.DataStore.setDeviceId(TransceiverID);
									self.DataStore.setDeviceRegistered( True);
						else:
							#print "#5"
							newLength[0] = self.buildTimeFrame(newBuffer,0);

					else:
						if RequestType == 5:
							#print "#6"
							HistoryIndex = 0xffff
##FIXME 
##here should fail the linux first config .... our tranceiverid is tored thru ack frame
							newLength[0] = self.buildACKFrame(newBuffer,3,TransceiverID,HistoryIndex,0xFFFFFFFF)
							self.RepeatCount = 0
							self.DataStore.setRequestState(ERequestState.rsWaitConfig)
						else:
							newLength[0] = 0
				else:
					newLength[0] = 0
		else: #Length[0] == 0
			self.logger.debug("DEBUG: repeatcount %d" %  self.RepeatCount)
			newBuffer[0]=[0]*0x0c
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
			self.DataStore.setTransceiverSerNo(SN)

			for i, Register in enumerate(self.AX5051RegisterNames_map):
				sHID.WriteReg(Register,self.AX5051RegisterNames_map[Register])

			if sHID.Execute(5):
				sHID.SetPreamblePattern(0xaa)
				if sHID.SetState(0):
					#time.sleep(1) #//fixme
					threading.Event().wait(1)
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

		self.DataStore.setFlag_FLAG_TRANSCEIVER_SETTING_CHANGE(1)

		TransceiverSettings=self.DataStore.TransceiverSettings
		device = sHID.Find(TransceiverSettings.VendorId,TransceiverSettings.ProductId,TransceiverSettings.VersionNo)
		if device:
			self.TransceiverInit()
			self.DataStore.setFlag_FLAG_TRANSCEIVER_PRESENT( 1);
			sHID.SetRX()
		else:
			raise "ws-28xx not present"

		#while True:
		while not self.kill_received:
			RequestType = self.DataStore.getRequestType()
			if RequestType == ERequestType.rtFirstConfig:
				RequestState = self.DataStore.getRequestState()
				self.logger.critical("RequestState #1 = %d" % RequestState)
				if RequestState:
					#RequestState<>ERequestState.rsQueued
					if RequestState == ERequestState.rsWaitDevice: # == 4
						self.logger.debug("self.getRequestState == 4 (rsWaitDevice)")
						if datetime.now() >= DeviceWaitEndTime :
							print "now=",datetime.now()
							print "DeviceWaitEndTime=",DeviceWaitEndTime
							print "now => DeviceWaitEndTime"
							self.DataStore.setRequestState(ERequestState.rsError);
							self.DataStore.RequestNotify();
				else:
					#RequestState=ERequestState.rsQueued
					sHID.SetPreamblePattern(0xaa)
					sHID.SetState(0x1e)
					self.DataStore.setRequestState(ERequestState.rsPreamble)
					PreambleDuration = self.DataStore.getPreambleDuration() ;
					print "now=",datetime.now()
					print "PreambleDuration", PreambleDuration
					PreambleEndTime = datetime.now() + timedelta(milliseconds=PreambleDuration)
					print "PreambleEndTime", PreambleEndTime
					while True:
						if not ( PreambleEndTime >= datetime.now() ):
							print "!PreambleEndTime >= datetime.now()"
							break
						if RequestType != self.DataStore.getRequestType():
							print "RequestType != self.DataStore.getRequestType()"
							break
						self.DataStore.RequestTick();
						#time.sleep(0.001)
						threading.Event().wait(0.001)
						self.DataStore.setFlag_FLAG_SERVICE_RUNNING(True);
					#time.sleep(6)

					if RequestType == self.DataStore.getRequestType():
						self.DataStore.setRequestState(ERequestState.rsWaitDevice)
						RegisterWaitTime = self.DataStore.getRegisterWaitTime() 
						DeviceWaitEndTime = datetime.now() + timedelta(milliseconds=RegisterWaitTime)
						print "DeviceWaitEndTime=",DeviceWaitEndTime
					ret = sHID.SetRX(); #make state from 14 to 15
			#endif RequestType == ERequestType.rtFirstConfig:

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
					#print FrameBuffer #---fixme
					if ret == None:
						raise ws28xxError("USBDevice->GetFrame returned false")
					if DataLength[0]:
						strbuf = ""
						for i in xrange(0,DataLength[0]):
							strbuf += str("%.2x" % (FrameBuffer[0][i]))
						#CTracer::WriteDump((CTracer *)td, 50, v22, v23, v24);
						self.logger.debug("CTracer::WriteDump %s" % strbuf) #simulate CTracer::WriteDump
				rel_time = self.GenerateResponse(FrameBuffer, DataLength);	#// return 0 no error, return 1 runtime error
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
					self.logger.debug("entro nell'while stronzo")
					#print "entro nell'while stronzo"
					while True:
						ret = sHID.GetState(StateBuffer);
						self.DataStore.RequestTick();
						if ret == 0:
							raise "USBDevice->GetState returned false" #it shouldn't be blocking
						ReceiverState = StateBuffer[0];
						if ( not ReceiverState) or (ReceiverState == 0x15 ):
#LABEL_42	
							#self.RepeatCount -= 1;
							#while (timeout >= 0) and self.RepeatCount:
							#	self.RepeatCount -= 1;
						#		#*(_QWORD *)&v23 = self.RepeatInterval;
						#		#a delay until I get 0x15
						#		time.sleep(0.0001)
						#		timeout -= 1;
						#if timeout == 0:
							self.RepeatTime = datetime.now()
							#time.sleep(0.2)
							threading.Event().wait(0.2)
						break;
						timeout -= 1
						#if ( not timeout ):
						#	break
#LABEL_49
					#print "sono fuori dall'while stronzo"
				if ReceiverState != 0x15:
					ret = sHID.SetRX(); #make state from 14 to 15
				
				#if ReceiverState == 0x15:
				#	if self.DataStore.getRequestType() == 6:
				#		#self.DataStore.GetCurrentWeather()
				#		self.DataStore.FirstTimeConfig()

			if not ret:
				self.DataStore.setFlag_FLAG_TRANSCEIVER_PRESENT( 0)
				pass
			#time.sleep(0.5) # original driver value was time.sleep(0.001)
			threading.Event().wait(0.5)

