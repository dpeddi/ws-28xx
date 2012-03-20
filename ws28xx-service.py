import sHID
import time

usbWait = 0.5

#placeholder to start hacking with hardware  //FIXME
#remove next class TransceiverSettings and 
#rename xTransceiverSettings to TransceiverSettings
class TransceiverSettings:
	VendorId	= 0x6666
	ProductId	= 0x5555
	VersionNo	= 1
	Frequency	= 905000000
	manufacturer	= "LA CROSSE TECHNOLOGY"
	product		= "Weather Direct Light Wireless Device"

#placeholder to start testing driver without hardware  //FIXME
#pls change next vars to match some hardware you have..
class xTransceiverSettings:
	VendorId	= 0x046d
	ProductId	= 0xc00e
	VersionNo	= 1	#seems unused
	Frequency	= 905000000
	manufacturer	= "Logitech"
	product		= "USB-PS/2 Optical Mouse"

lowlevel = sHID.sHID()

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
#FFFFFFFF ; enum EWindDirection (standard)
#FFFFFFFF wdN              = 0
#FFFFFFFF wdNNE            = 1
#FFFFFFFF wdNE             = 2
#FFFFFFFF wdENE            = 3
#FFFFFFFF wdE              = 4
#FFFFFFFF wdESE            = 5
#FFFFFFFF wdSE             = 6
#FFFFFFFF wdSSE            = 7
#FFFFFFFF wdS              = 8
#FFFFFFFF wdSSW            = 9
#FFFFFFFF wdSW             = 0Ah
#FFFFFFFF wdWSW            = 0Bh
#FFFFFFFF wdW              = 0Ch
#FFFFFFFF wdWNW            = 0Dh
#FFFFFFFF wdNW             = 0Eh
#FFFFFFFF wdNNW            = 0Fh
#FFFFFFFF wdERR            = 10h
#FFFFFFFF wdInvalid        = 11h
#FFFFFFFF ; enum EResetMinMaxFlags (standard)
#FFFFFFFF rmTempIndoorHi   = 0
#FFFFFFFF rmTempIndoorLo   = 1
#FFFFFFFF rmTempOutdoorHi  = 2
#FFFFFFFF rmTempOutdoorLo  = 3
#FFFFFFFF rmWindchillHi    = 4
#FFFFFFFF rmWindchillLo    = 5
#FFFFFFFF rmDewpointHi     = 6
#FFFFFFFF rmDewpointLo     = 7
#FFFFFFFF rmHumidityIndoorLo  = 8
#FFFFFFFF rmHumidityIndoorHi  = 9
#FFFFFFFF rmHumidityOutdoorLo  = 0Ah
#FFFFFFFF rmHumidityOutdoorHi  = 0Bh
#FFFFFFFF rmWindspeedHi    = 0Ch
#FFFFFFFF rmWindspeedLo    = 0Dh
#FFFFFFFF rmGustHi         = 0Eh
#FFFFFFFF rmGustLo         = 0Fh
#FFFFFFFF rmPressureLo     = 10h
#FFFFFFFF rmPressureHi     = 11h
#FFFFFFFF rmRain1hHi       = 12h
#FFFFFFFF rmRain24hHi      = 13h
#FFFFFFFF rmRainLastWeekHi  = 14h
#FFFFFFFF rmRainLastMonthHi  = 15h
#FFFFFFFF rmRainTotal      = 16h
#FFFFFFFF rmInvalid        = 17h
#FFFFFFFF

#		class ERequestType:
#			rtGetCurrent     = 0
#			rtGetHistory     = 1
#			rtGetConfig      = 2
#			rtSetConfig      = 3
#			rtSetTime        = 4
#			rtFirstConfig    = 5
#			rtINVALID        = 6


#class CDataStore(object):

#	class ERequestState:
#FFFFFFFF ; enum CDataStore::ERequestState (standard)
#FFFFFFFF rsQueued         = 0
#FFFFFFFF rsRunning        = 1
#FFFFFFFF rsFinished       = 2
#FFFFFFFF rsPreamble       = 3
#FFFFFFFF rsWaitDevice     = 4
#FFFFFFFF rsWaitConfig     = 5
#FFFFFFFF rsError          = 6
#FFFFFFFF rsChanged        = 7
#FFFFFFFF rsINVALID        = 8


class CCommunicationService(object):

	Regenerate = 0
	TimeSent = 0
	
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

	def getRequestType(self):
		print "getRequestType() (temporary wrapper)"
		return 0

	def getInstance(self):
		print "getInstance (partially implemented)"
		self.CCommunicationService();

	def buildACKFrame(Buffer, Action, CheckSum, HistoryIndex, ComInt):
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
#				HistoryAddress = 18 * *HistoryIndex + 416;
#				}
#				else
#				{
#				if ( *HistoryIndex )
#					HistoryAddress = 18 * (*HistoryIndex - 1) + 416;
#				else
#					HistoryAddress = 32744;
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

	def handleConfig():
		print "handleConfig (not yet implemented)"

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

	def handleNextAction():
		print "handleNextAction (not yet implemented)"

	def buildTimeFrame():
		print "buildTimeFrame (not yet implemented)"

	def CCommunicationService(self):
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

	def caluculateFrequency(self,Frequency):
		print "CCommunicationService::caluculateFrequency"
		FreqVal =  long(Frequency / 16000000.0 * 16777216.0);
		FreqCorrection = [None]
		if lowlevel.ReadConfigFlash(0x1F5, 4, FreqCorrection):
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
		print "CCommunicationService::caluculateFrequency - end"

	def GenerateResponse(self,Buffer,Length):
		print "CCommunicationService::GenerateResponse (not implemented yet)"
		print "CCommunicationService->Length=",Length
		if Length == 0:
		    print "CCommunicationService->Buffer=[None]"
		else:
		    print "CCommunicationService->Buffer=",Buffer
		
		if ((Buffer[2] & 0xE0) - 0x20) == 0x40:
			if Length == 215:
				self.handleCurrentData(Buffer, Length);
			else:
				Length = 0


	#_RTC_CheckStackVars();
	#return j___RTC_CheckEsp();

	def TransceiverInit(self):
		#print "CCommunicationService::TransceiverInit"
		print "CCommunicationService::TransceiverInit (partially implemented)"

		self.caluculateFrequency(TransceiverSettings.Frequency);

		buffer = [None]
		if ( lowlevel.ReadConfigFlash(0x1F9, 7, buffer) ):
			ID  = buffer[0][5] << 8;
			ID += buffer[0][6];
			print "CCommunicationService::TransceiverInit TransceiverID 0x%x" % ID

			SN  = buffer[0][0] << 24;
			SN += buffer[0][1] << 16;
			SN += buffer[0][2] << 8;
			SN += buffer[0][3];
			print "CCommunicationService::TransceiverInit TransceiverSN %d - ????" % SN

			for i, Register in enumerate(self.AX5051RegisterNames_map):
				lowlevel.WriteReg(Register,self.AX5051RegisterNames_map[Register])

			if lowlevel.Execute(5):
				lowlevel.SetPreamblePattern(0xaa)
				if lowlevel.SetState(0):
					#print "fixme: subsecond duration" //fixme
					if lowlevel.SetRX():
						v67 = 1  #//fixme:and so?
						v78 = -1 #//fixme:and so?

		#raise NotImplementedError()
		#raise ws28xxError("not implemented yet")

		#security_check_cookie

	def doRFCommunication(self):
		import usb
		print "CCommunicationService::doRFCommunication"

		device = lowlevel.Find(TransceiverSettings.VendorId,TransceiverSettings.ProductId,TransceiverSettings.VersionNo)
		if device:
			self.TransceiverInit()
			lowlevel.SetRX()
		else:
			raise "no ws"
		#while True:
		if 1 == 1:
			RequestType = self.getRequestType()
			print "RequestType = %d" % RequestType
			if RequestType == 5: #ERequestState.rtFirstConfig
				if self.getRequestState() == 4: # waitdevice
					print "self.getRequestState == 4"
					#sleep....
					#se e' scaduto il tempo di sleep... (DeviceWaitEndTime)
					#setRequestState(ERequestState.rsError)
				else:
					if lowlevel.SetPreamblePattern(0xaa):
						if lowlevel.SetState(0x1e):
							print "lowlevel.SetState(0x1e)"
						#self.setRequestState(ERequestState.rsPreamble)
						#self.getPreambleDuration()
						#while True:
						#	if RequestType != self.getRequestType():
						#		break
						#	#RequestTick
						#	#setFlag
						#if RequestType == self.getRequestType():
						#	setRequestState(rsWaitDevice)
						#	
						#	SetRx()

			DataLength = 0
			StateBuffer = [None]
			ret = lowlevel.GetState(StateBuffer);
			if ret == 1:
				FrameBuffer=[None]*0x200 #//FIXME
	
				ReceiverState = StateBuffer[0][0];
				print "DEBUG: ReceivedState:0x%x" % ReceiverState
				if ReceiverState == 0x16:
					ret = lowlevel.GetFrame(FrameBuffer, DataLength);
					if ret == None:
						raise ws28xxError("USBDevice->GetFrame returned false")
					if DataLength:
						print "Receiverstate = 22 - I don't understand what do do..."
						v24 = DataLength;
						v23 = FrameBuffer;
						#v22.baseclass_0.m_pszData = FrameBuffer;
						#v43 = &v22;
						#CTracer::WriteDump((CTracer *)td, 50, v22, v23, v24);
				self.GenerateResponse(FrameBuffer, DataLength); #// return 0 no error, return 1 runtime error
																# this one prepare the ackframe  
				if DataLength:
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
				lowlevel.SetState(0);
				ret = lowlevel.SetFrame(FrameBuffer, DataLength); # send the ackframe prepared by GenerateResponse
				if ret == None:
					print "USBDevice->SetFrame returned false"  #it shouldn't be blocking
					#goto LABEL_49
				ret = lowlevel.SetTX();
				if ret == None:
					print ws28xxError("USBDevice->SetTX returned false")  #it shouldn't be blocking
					#goto LABEL_49
				ReceiverState = 0xc8;
				timeout = 1000;
				while True:
					ret = lowlevel.GetState(StateBuffer);
					if ret == None:
						raise "USBDevice->GetState returned false" #it shouldn't be blocking
					ReceiverState = StateBuffer[0];
					if ( not StateBuffer[0]) or (ReceiverState == 0x15 ):
#LABEL_42
						#if timeout and RepeatCount:
						#	--RepeatCount;
							#*(_QWORD *)&v23 = thisa->RepeatInterval;
							#a delay until I get 0x15
						#break;
						a=1

					--timeout;
					#if ( !timeout )
						#goto label_42
#LABEL_49
				if ReceiverState != 0x15:
					ret = lowlevel.SetRX();
				
				#if not ret:

myCCommunicationService = CCommunicationService()
myCCommunicationService.getInstance()
myCCommunicationService.doRFCommunication()

