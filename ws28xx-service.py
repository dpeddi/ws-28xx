import array
import sHID

class Animal:
	DOG=1
	CAT=2

x = Animal.DOG

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
	def caluculateFrequency(self,Frequency):
		print "CCommunicationService::caluculateFrequency (not implemented yet)"

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

