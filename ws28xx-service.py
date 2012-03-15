import array
import sHID

class xTransceiverSettings:
	VendorId	= 0x6666
	ProductId	= 0x5555
	VersionNo	= 1
	Frequency	= 905000000
	manufacturer	= "LA CROSSE TECHNOLOGY"
	product		= "Weather Direct Light Wireless Device"

class TransceiverSettings:
	VendorId	= 0x046d
	ProductId	= 0xc00e
	VersionNo	= 1	#seems unused
	Frequency	= 905000000
	manufacturer	= "LA CROSSE TECHNOLOGY"
	product		= "Weather Direct Light Wireless Device"

#print(dir(sHID))

lowlevel = sHID.sHID()

class ws28xxError(IOError):
	"Used to signal an error condition"

class CCommunicationService(object):

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
	
#	x = AX5051RegisterNames.RXMISC
#	print x
	
	AX5051RegisterNames_map = dict()
#	print AX5051RegisterNames_map[AX5051RegisterNames.RXMISC]
	AX5051RegisterNames_map[AX5051RegisterNames.RXMISC]=5
	print AX5051RegisterNames_map[AX5051RegisterNames.RXMISC]

	def caluculateFrequency(self,Frequency):
		print "CCommunicationService::caluculateFrequency"
		FreqVal =  (Frequency / 16000000.0 * 16777216.0);
		FreqCorrection = 0
		if lowlevel.ReadConfigFlash(0x1F5, 4, FreqCorrection):
			CorVal = FreqCorrection[0] << 8;
			CorVal |= FreqCorrection[1];
			CorVal <<= 8;
			CorVal |= FreqCorrection[2];
			CorVal <<= 8;
			CorVal |= FreqCorrection[3];
			FreqVal += CorVal;
		if ( not (FreqVal % 2) ):
			print "caluculateFrequency fixme"
			++FreqVal;
#			*std::map<enum__CCommunicationService::AX5051RegisterNames_unsigned_char_std::less
#				 <enum__CCommunicationService::AX5051RegisterNames>_std::allocator
#				 <std::pair<enum__CCommunicationService::AX5051RegisterNames_const_unsigned_char>>>::operator__(
#			    	    &thisa->TransceiverSettings,
#			    	    &_Keyval) = BYTE3(FreqVal);
#			v5 = 33;
#			*std::map<enum__CCommunicationService::AX5051RegisterNames_unsigned_char_std::less<enum__CCommunicationService::AX5051RegisterNames>_std::allocator<std::pair<enum__CCommunicationService::AX5051RegisterNames_const_unsigned_char>>>::operator__(
#			        &thisa->TransceiverSettings,
#			(CCommunicationService::AX5051RegisterNames *)&v5) = FreqVal >> 16;
#			v6 = 34;
#			*std::map<enum__CCommunicationService::AX5051RegisterNames_unsigned_char_std::less<enum__CCommunicationService::AX5051RegisterNames>_std::allocator<std::pair<enum__CCommunicationService::AX5051RegisterNames_const_unsigned_char>>>::operator__(
#			        &thisa->TransceiverSettings,
#			(CCommunicationService::AX5051RegisterNames *)&v6) = BYTE1(FreqVal);
#			v7 = 35;
#			*std::map<enum__CCommunicationService::AX5051RegisterNames_unsigned_char_std::less<enum__CCommunicationService::AX5051RegisterNames>_std::allocator<std::pair<enum__CCommunicationService::AX5051RegisterNames_const_unsigned_char>>>::operator__(
#                           &thisa->TransceiverSettings,
#			(CCommunicationService::AX5051RegisterNames *)&v7) = FreqVal;
#                }
#		http://docs.python.org/tutorial/datastructures.html
#		>>> questions = ['name', 'quest', 'favorite color']
#		>>> answers = ['lancelot', 'the holy grail', 'blue']
#		>>> for q, a in zip(questions, answers):
#		...     print 'What is your {0}?  It is {1}.'.format(q, a)
#		                                                                                    


	def GenerateResponse(self,FrameBuffer,DataLength):
		print "CCommunicationService::GenerateResponse (not implemented yet)"

	def TransceiverInit(self):
		#print "CCommunicationService::TransceiverInit"
		print "CCommunicationService::TransceiverInit (not implemented yet)"

		self.caluculateFrequency(TransceiverSettings.Frequency);
		#if ( lowlevel.ReadConfigFlash(v2, 0x1F9u, 7u, buffer) ) #if ( sHID::ReadConfigFlash(v2, 0x1F9u, 7u, buffer) )
			
			#while enum AX5051
			#	lowlevel.WriteReg(reg,value)
		#raise NotImplementedError()
		#raise ws28xxError("not implemented yet")

		#security_check_cookie

	def doRFCommunication(self):
		print "CCommunicationService::doRFCommunication"
		device = lowlevel.Find(TransceiverSettings.VendorId,TransceiverSettings.ProductId,TransceiverSettings.VersionNo)
		if device == None:
			raise ws28xxError("USB ws28xx not found (%04X %04X)" % (vendor_id, product_id))
		self.TransceiverInit()
		#rel_time = (boost::posix_time::ptime *)boost::shared_ptr<sHID>::operator_>(&thisa->USBDevice);
		#rel_time = 0
		lowlevel.SetRX()
		
		#while 1
			#RequestType = getRequestType
			#if RequestType = 5

		StateBuffer = array.array("h",range(0x200))
		ret = lowlevel.GetState(StateBuffer);
		if ret == 1:
			ReceiverState = StateBuffer[0];
			if ReceiverState == 22:
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
			rel_time = self.GenerateResponse(FrameBuffer, DataLength);
			if rel_time == None:
				raise ws28xxError("GenerateResponse Failed...")
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
			ret = lowlevel.SetFrame(FrameBuffer, DataLength);
			if ret == None:
				raise "USBDevice->SetFrame returned false"  #it shouldn't be blocking
				#goto LABEL_49
			ret = lowlevel.SetTX();
			if ret == None:
				raise ws28xxError("USBDevice->SetTX returned false")  #it shouldn't be blocking
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
					if timeout and RepeatCount:
						--RepeatCount;
						#*(_QWORD *)&v23 = thisa->RepeatInterval;
						#a delay until I get 0x15
					break;

				--timeout;
				#if ( !timeout )
					#goto label_42
#LABEL_49
			if ReceiverState != 0x15:
				ret = lowlevel.SetRX();
			
			#if not ret:
			



myCCommunicationService = CCommunicationService()
myCCommunicationService.doRFCommunication()

