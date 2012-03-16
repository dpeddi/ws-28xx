import array
import sHID

#placeholder to start hacking with hardware  //FIXME
#remove next class TransceiverSettings and 
#rename xTransceiverSettings to TransceiverSettings
class xTransceiverSettings:
	VendorId	= 0x6666
	ProductId	= 0x5555
	VersionNo	= 1
	Frequency	= 905000000
	manufacturer	= "LA CROSSE TECHNOLOGY"
	product		= "Weather Direct Light Wireless Device"

#placeholder to start testing driver without hardware  //FIXME
#pls change next vars to match some hardware you have..
class TransceiverSettings:
	VendorId	= 0x046d
	ProductId	= 0xc00e
	VersionNo	= 1	#seems unused
	Frequency	= 905000000
	manufacturer	= "Logitech"
	product		= "USB-PS/2 Optical Mouse"

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

	AX5051RegisterNames_map = dict()

	def getInstance(self):
		print "getInstance(partially implemented)"
		self.CCommunicationService();

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

	def GenerateResponse(self,FrameBuffer,DataLength):
		print "CCommunicationService::GenerateResponse (not implemented yet)"

	def TransceiverInit(self):
		#print "CCommunicationService::TransceiverInit"
		print "CCommunicationService::TransceiverInit (partially implemented)"

		self.caluculateFrequency(TransceiverSettings.Frequency);

		buffer = [None]
		if ( lowlevel.ReadConfigFlash(0x1F9, 7, buffer) ):
			ID  = buffer[0][5] << 8;
			ID += buffer[0][6];
			print "CCommunicationService::TransceiverInit TransceiverID %d" % ID

			SN  = buffer[0][0] << 24;
			SN += buffer[0][1] << 16;
			SN += buffer[0][2] << 8;
			SN += buffer[0][3];
			print "CCommunicationService::TransceiverInit TransceiverSN %d - ????" % SN

			for i, Register in enumerate(self.AX5051RegisterNames_map):
				lowlevel.WriteReg(Register,self.AX5051RegisterNames_map[Register])

			if lowlevel.Execute(5):
				lowlevel.SetPreamblePattern(0xaa)



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
		print ret
		if ret == 1:
			FrameBuffer=[None]*0x200 #//FIXME
			DataLength = 0 #//FIXME
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
				print ws28xxError("GenerateResponse Failed...")
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

