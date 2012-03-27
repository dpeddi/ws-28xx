import logging

class USBHardware(object):
	def __init__(self):
		self.logger = logging.getLogger('ws28xx.USBHardware')

	def ToCurrentTempBytes(self,bufer,c, d):
		self.logger.debug("")

	def To2Pre(buffer,startOnLowNibble):
		self.logger.debug("")

	def ToPressureInhg(buffer, startOnLowNibble):
		self.logger.debug("")

	def ToRainAlarmBytes(buffer,alarm):
		self.logger.debug("")

	def ToDateTime(result, buffer, startOnLowNibble):
		self.logger.debug("")

	def ToTemperature(buffer, start, startOnLowNibble):
		self.logger.debug("")
		#if ( USBHardware::IsErr5(buffer, startOnLowNibble) ):
		#	v2 = CWeatherTraits::TemperatureNP();
		#else:
		#	if ( USBHardware::IsOFL5(buffer, startOnLowNibble) ):
		#		v2 = CWeatherTraits::TemperatureOFL();
		#	else:
		#		ATL::CStringT<char_ATL::StrTraitATL<char_ATL::ChTraitsCRT<char>>>::CStringT<char_ATL::StrTraitATL<char_ATL::ChTraitsCRT<char>>>(&strValue);
		#		v10 = 0;
		#		ATL::CStringT<char_ATL::StrTraitATL<char_ATL::ChTraitsCRT<char>>>::Format(&strValue, "%01d%01d.%01d%01d%01d");
		#		v3 = ATL::CSimpleStringT<char_0>::operator char_const__(&strValue.baseclass_0);
		#		v7 = j__atof(v3);
		#		v6 = v7;
		#		v8 = v7 - CWeatherTraits::TemperatureOffset();
		#		v10 = -1;
		#		ATL::CStringT<char_ATL::StrTraitATL<char_ATL::ChTraitsCRT<char>>>::_CStringT<char_ATL::StrTraitATL<char_ATL::ChTraitsCRT<char>>>(&strValue);
		#		v2 = v8;
		#LODWORD(result) = LODWORD(v2);
		#return result;

	def ReverseByteOrder(self,buf,start,Count):
		self.logger.debug("")
		nbuf=buf[0]
		#print nbuf
		for i in xrange(0, Count >> 1):
			tmp = nbuf[start + i]
			nbuf[start + i] = nbuf[start + Count - i - 1]
			nbuf[start + Count - i - 1 ] = tmp
		buf[0]=nbuf
