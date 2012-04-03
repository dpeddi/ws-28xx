#!/usr/bin/python

import logging
import CWeatherTraits

CWeatherTraits = CWeatherTraits.CWeatherTraits()

class USBHardware(object):
	def __init__(self):
		self.logger = logging.getLogger('ws28xx.USBHardware')

	def IsOFL2(self, buffer, start, startOnLowNibble):
		if ( startOnLowNibble ):
			result =   (buffer[0][start+0] & 0xF) == 15 \
				or (buffer[0][start+0] >>  4) == 15
		else:
			result =   (buffer[0][start+0] >>  4) == 15 \
				or (buffer[0][start+1] & 0xF) == 15
		return result

	def IsOFL5(self, buffer, startOnLowNibble):
		if ( startOnLowNibble ):
			result =     (buffer[0][0] & 0xF) == 15 \
				  or (buffer[0][0] >>  4) == 15 \
				  or (buffer[0][1] & 0xF) == 15 \
				  or (buffer[0][1] >>  4) == 15 \
				  or (buffer[0][2] & 0xF) == 15
		else:
			result =     (buffer[0][0] >>  4) == 15 \
				  or (buffer[0][1] & 0xF) == 15 \
				  or (buffer[0][1] >>  4) == 15 \
				  or (buffer[0][2] & 0xF) == 15 \
				  or (buffer[0][2] >>  4) == 15
		return result

	def IsErr2(self,buffer,start,startOnLowNibble):
		if ( startOnLowNibble ):
			result =    (buffer[0][start+0] & 0xF) >= 10 \
				and (buffer[0][start+0] & 0xF) != 15 \
				 or (buffer[0][start+0] >>  4) >= 10 \
				and (buffer[0][start+0] >>  4) != 15
		else:
			result = (buffer[0][start+0] >> 4) >= 10 and buffer[0][start+0] >> 4 != 15 or (buffer[0][start+1] & 0xF) >= 10 and (buffer[0][start+1] & 0xF) != 15;
		return result

	def IsErr5(self,buffer,startOnLowNibble):
		if ( startOnLowNibble ):
			result =     (buffer[0][0] & 0xF) >= 10 \
				 and (buffer[0][0] & 0xF) != 15 \
				  or (buffer[0][0] >>  4) >= 10 \
				 and (buffer[0][0] >>  4) != 15 \
				  or (buffer[0][1] & 0xF) >= 10 \
				 and (buffer[0][1] & 0xF) != 15 \
				  or (buffer[0][1] >>  4) >= 10 \
				 and (buffer[0][1] >>  4) != 15 \
				  or (buffer[0][2] & 0xF) >= 10 \
				 and (buffer[0][2] & 0xF) != 15
		else:
			result =     (buffer[0][0] >>  4) >= 10 \
				 and (buffer[0][0] >>  4) != 15 \
				  or (buffer[0][1] & 0xF) >= 10 \
				 and (buffer[0][1] & 0xF) != 15 \
				  or (buffer[0][1] >>  4) >= 10 \
				 and (buffer[0][1] >>  4) != 15 \
				  or (buffer[0][2] & 0xF) >= 10 \
				 and (buffer[0][2] & 0xF) != 15 \
				  or (buffer[0][2] >>  4) >= 10 \
				 and (buffer[0][2] >>  4) != 15
		return result

	def ToCurrentTempBytes(self,bufer,c, d):
		self.logger.debug("")

	def To2Pre(self,buffer, start, startOnLowNibble):
		self.logger.debug("")
		if startOnLowNibble:
			rawpre  = (buffer[0][start+0] & 0xf)*  1 \
				+ (buffer[0][start+0]  >> 4)* 10
		else:
			rawpre  = (buffer[0][start+0]  >> 4)*  1 \
				+ (buffer[0][start+1] & 0xf)* 10
		return rawpre

	def ToPressureInhg(buffer, startOnLowNibble):
		self.logger.debug("")

	def ToRainAlarmBytes(buffer,alarm):
		self.logger.debug("")

	def ToDateTime(result, buffer, startOnLowNibble):
		self.logger.debug("")

	def ToHumidity(self,buffer,start,startOnLowNibble):
		self.logger.debug("")
		if ( self.IsErr2(buffer, 0, startOnLowNibble) ):
			result = CWeatherTraits.HumidityNP();
		else:
			if ( self.IsOFL2(buffer, 0, startOnLowNibble) ):
				result = CWeatherTraits.HumidityOFL()
			else:
				result = self.To2Pre(buffer, start, startOnLowNibble);
		return result;

	def ToTemperature(self,buffer, start, startOnLowNibble):
		self.logger.debug("")
		if ( self.IsErr5(buffer, startOnLowNibble) ):
			result = CWeatherTraits.TemperatureNP()
		else:
			if ( self.IsOFL5(buffer, startOnLowNibble) ):
				result = CWeatherTraits.TemperatureOFL()
			else:
				if startOnLowNibble:
					rawtemp = (buffer[0][start+0] & 0xf)*  0.001 \
						+ (buffer[0][start+0] >> 4 )*  0.01  \
						+ (buffer[0][start+1] & 0xf)*  0.1   \
						+ (buffer[0][start+1] >>  4)*  1     \
						+ (buffer[0][start+2] & 0xf)* 10
				else:
					rawtemp = (buffer[0][start+0] >> 4 )*  0.001 \
						+ (buffer[0][start+1] & 0xf)*  0.01  \
						+ (buffer[0][start+1] >>  4)*  0.1   \
						+ (buffer[0][start+2] & 0xf)*  1     \
						+ (buffer[0][start+2] >>  4)* 10
				result = rawtemp - CWeatherTraits.TemperatureOffset()
		return result;

	def To4Pre2Post(self,buffer):
		self.logger.debug("")
		if ( self.IsErr2(buffer,0,1) or self.IsErr2(buffer,1, 1) or self.IsErr2(buffer,2, 1) ):
			result = CWeatherTraits.RainNP();
		else:
			if ( self.IsOFL2(buffer,0, 1) or self.IsOFL2(buffer, 1, 1) or self.IsOFL2(buffer, 2, 1) ):
				result = CWeatherTraits.RainOFL()
			else:
				result  = (buffer[0][0] & 0xf)* 1     \
					+ (buffer[0][0] >>  4)* 0.01  \
					+ (buffer[0][1] & 0xf)* 0.1   \
					+ (buffer[0][1] >>  4)*  1    \
					+ (buffer[0][2] & 0xf)* 10    \
					+ (buffer[0][2] >>  4)*100
		return result

	def ToWindspeed(self,buffer,start): #m/s
		self.logger.debug("")
		val = self.ByteToFloat(buffer, start, 1, 16, 6);
		val = val / 256.0;
		val = val / 100.0;             #km/h
		val = val / 3.599999904632568; #m/s
		return val

	def ByteToFloat(self,buffer, start,startOnLowNibble, base, pre):
		self.logger.debug("")
		lowNibble = startOnLowNibble;
		val = 0;
		byteCounter = 0;
		i = 0;
		#for i in xrange(0,pre):
		while i < pre:
			if ( pre > 0 ):
				digit = 0;
				if ( lowNibble ):
					digit = buffer[0][start+byteCounter] & 0xF;
				else:
					digit = buffer[0][start+byteCounter] >> 4;
				if ( not lowNibble ):
					byteCounter += 1
				if lowNibble == 0:
					lowNibble=1
				else:
					lowNibble=0
				power = base**i
				val += digit * power
			i += 1
		return val

	def ToDateTime(self,buffer,startOnLowNibble):
		pass
#  ATL::COleDateTime::COleDateTime(&invalidDate);
#  ATL::COleDateTime::SetStatus(&invalidDate, partial);
#  if ( USBHardware::IsErr2(buffer, startOnLowNibble)
#    || USBHardware::IsErr2(buffer + 1, startOnLowNibble)
#    || USBHardware::IsErr2(buffer + 2, startOnLowNibble)
#    || USBHardware::IsErr2(buffer + 3, startOnLowNibble)
#    || USBHardware::IsErr2(buffer + 4, startOnLowNibble) )
#  {
#    *(_QWORD *)&result->m_dt = (_QWORD)invalidDate.m_dt;
#    result->m_status = invalidDate.m_status;
#  }
#  else
#  {
#    v3 = USBHardware::To2Pre(buffer, startOnLowNibble);
#    minutes = j___ftol2_sse(v3);
#    v4 = USBHardware::To2Pre(buffer + 1, startOnLowNibble);
#    hours = j___ftol2_sse(v4);
#    v5 = USBHardware::To2Pre(buffer + 2, startOnLowNibble);
#    days = j___ftol2_sse(v5);
#    v6 = USBHardware::To2Pre(buffer + 3, startOnLowNibble);
#    month = j___ftol2_sse(v6);
#    v7 = USBHardware::To2Pre(buffer + 4, startOnLowNibble);
#    year = j___ftol2_sse(v7) + 2000;
#    ATL::COleDateTime::COleDateTime(&dt, year, month, days, hours, minutes, 0);
#    *(_QWORD *)&result->m_dt = (_QWORD)dt.m_dt;
#    result->m_status = dt.m_status;
#  }
#  _RTC_CheckStackVars(&v18, &stru_55ADA8);
#  j___RTC_CheckEsp(v8);
#  return v9;

	def ReverseByteOrder(self,buf,start,Count):
		self.logger.debug("")
		nbuf=buf[0]
		#print nbuf
		for i in xrange(0, Count >> 1):
			tmp = nbuf[start + i]
			nbuf[start + i] = nbuf[start + Count - i - 1]
			nbuf[start + Count - i - 1 ] = tmp
		buf[0]=nbuf

	def ReadWindDirectionShared(self,buffer,start):
		return (buffer[0][0+start] & 0xf, buffer[0][0+start] >> 4)

#void __cdecl USBHardware::ReadPressureShared(const char *buffer, float *a, float *b)
#  int v3; // ecx@1
#  char v4; // [sp+Ch] [bp-D8h]@1
#  char bBuffer[3]; // [sp+D0h] [bp-14h]@1
#  char aBuffer[3]; // [sp+DCh] [bp-8h]@1
#  int v7; // [sp+E4h] [bp+0h]@1
#
#  j__memcpy(aBuffer, (char *)buffer, 3u);
#  *a = USBHardware::ToPressure(aBuffer, 1);
#  j__memcpy(bBuffer, (char *)buffer + 2, 3u);
#  *b = USBHardware::ToPressureInhg(bBuffer, 0);

#def ToPressure(buffer,startOnLowNibble):
#	if ( USBHardware::IsErr5(buffer, startOnLowNibble) ):
#		result = CWeatherTraits::PressureNP();
#	else:
#		if ( USBHardware::IsOFL5(buffer, startOnLowNibble) ):
#			result = CWeatherTraits::PressureOFL();
#		else:
#      if ( startOnLowNibble )
#      {
#        v4 = *buffer >> 4;
#        v5 = buffer[1] & 0xF;
#        v6 = buffer[1] >> 4;
#        v7 = std::basic_ostream<char_std::char_traits<char>>::operator<<(
#               (std::basic_ostream<char,std::char_traits<char> > *)this.___u0.baseclass_0.___u0.baseclass_0.gap8,
#               buffer[2] & 0xF);
#        v8 = std::basic_ostream<char_std::char_traits<char>>::operator<<(v7, v6);
#        v9 = std::basic_ostream<char_std::char_traits<char>>::operator<<(v8, v5);
#        std::basic_ostream<char_std::char_traits<char>>::operator<<(v9, v4);
#        if ( &this )
#          _Ostr = (std::basic_ostream<char,std::char_traits<char> > *)this.___u0.baseclass_0.___u0.baseclass_0.gap8;
#        else
#          _Ostr = 0;
#        v10 = *buffer & 0xF;
#        v11 = std::operator<<<std::char_traits<char>>(_Ostr, ".");
#        std::basic_ostream<char_std::char_traits<char>>::operator<<(v11, v10);
#      }
#      else
#      {
#        v12 = buffer[1] & 0xF;
#        v13 = buffer[1] >> 4;
#        v14 = buffer[2] & 0xF;
#        v15 = std::basic_ostream<char_std::char_traits<char>>::operator<<(
#                (std::basic_ostream<char,std::char_traits<char> > *)this.___u0.baseclass_0.___u0.baseclass_0.gap8,
#                buffer[2] >> 4);
#        v16 = std::basic_ostream<char_std::char_traits<char>>::operator<<(v15, v14);
#        v17 = std::basic_ostream<char_std::char_traits<char>>::operator<<(v16, v13);
#        std::basic_ostream<char_std::char_traits<char>>::operator<<(v17, v12);
##        if ( &this )
#          _Ostr = (std::basic_ostream<char,std::char_traits<char> > *)this.___u0.baseclass_0.___u0.baseclass_0.gap8;
#        else
#          _Ostr = 0;
#        v18 = *buffer >> 4;
#        v19 = std::operator<<<std::char_traits<char>>(_Ostr, ".");
#        std::basic_ostream<char_std::char_traits<char>>::operator<<(v19, v18);
#      }
#      _Ostr = (std::basic_ostream<char,std::char_traits<char> > *)std::basic_stringstream<char_std::char_traits<char>_std::allocator<char>>::str(
#                                                                    &this,
#                                                                    &result);
#      v24 = _Ostr;
#      LOBYTE(v29) = 1;
#      v20 = std::basic_string<char_std::char_traits<char>_std::allocator<char>>::c_str((std::basic_string<char,std::char_traits<char>,std::allocator<char> > *)_Ostr);
#      v26 = j__atof(v20);
#      LOBYTE(v29) = 0;
#      std::basic_string<char_std::char_traits<char>_std::allocator<char>>::_basic_string<char_std::char_traits<char>_std::allocator<char>>(&result);
#      v29 = -1;
#      std::basic_stringstream<char_std::char_traits<char>_std::allocator<char>>::_vbase_destructor(&this);
#      result = v26;
#    }
#  }
#  v21 = v2;
#  _RTC_CheckStackVars(&v30, &stru_55AB2C);
#  j___RTC_CheckEsp(v23, v21);
#  LODWORD(v22) = LODWORD(v3);
#  return result;
#}

#	def ToPressureInhg(buffer,startOnLowNibble):
#		if ( USBHardware::IsErr5(buffer, startOnLowNibble) ):
#			v3 = CWeatherTraits::PressureNP();
#		else:
#			if ( USBHardware::IsOFL5(buffer, startOnLowNibble) ):
#				v3 = CWeatherTraits::PressureOFL()
#			else:
#      if ( startOnLowNibble )
#      {
#        v4 = buffer[1] & 0xF;
#        v5 = buffer[1] >> 4;
#        v6 = std::basic_ostream<char_std::char_traits<char>>::operator<<(
#               (std::basic_ostream<char,std::char_traits<char> > *)this.___u0.baseclass_0.___u0.baseclass_0.gap8,
#               buffer[2] & 0xF);
#        v7 = std::basic_ostream<char_std::char_traits<char>>::operator<<(v6, v5);
#        v8 = std::basic_ostream<char_std::char_traits<char>>::operator<<(v7, v4);
#        std::operator<<<std::char_traits<char>>(v8, ".");
#        v9 = *buffer & 0xF;
#        v10 = std::basic_ostream<char_std::char_traits<char>>::operator<<(
#                (std::basic_ostream<char,std::char_traits<char> > *)this.___u0.baseclass_0.___u0.baseclass_0.gap8,
#                *buffer >> 4);
#        std::basic_ostream<char_std::char_traits<char>>::operator<<(v10, v9);
#      }
#      else
#      {
#        v11 = buffer[1] >> 4;
#        v12 = buffer[2] & 0xF;
#        v13 = std::basic_ostream<char_std::char_traits<char>>::operator<<(
#                (std::basic_ostream<char,std::char_traits<char> > *)this.___u0.baseclass_0.___u0.baseclass_0.gap8,
#                buffer[2] >> 4);
#        v14 = std::basic_ostream<char_std::char_traits<char>>::operator<<(v13, v12);
#        v15 = std::basic_ostream<char_std::char_traits<char>>::operator<<(v14, v11);
#        std::operator<<<std::char_traits<char>>(v15, ".");
#        v16 = *buffer >> 4;
#        v17 = std::basic_ostream<char_std::char_traits<char>>::operator<<(
#                (std::basic_ostream<char,std::char_traits<char> > *)this.___u0.baseclass_0.___u0.baseclass_0.gap8,
#                buffer[1] & 0xF);
#        std::basic_ostream<char_std::char_traits<char>>::operator<<(v17, v16);
#      }
#      v23 = std::basic_stringstream<char_std::char_traits<char>_std::allocator<char>>::str(&this, &result);
#      v22 = v23;
#      LOBYTE(v27) = 1;
#      v18 = std::basic_string<char_std::char_traits<char>_std::allocator<char>>::c_str(v23);
#      v24 = j__atof(v18);
#      LOBYTE(v27) = 0;
#      std::basic_string<char_std::char_traits<char>_std::allocator<char>>::_basic_string<char_std::char_traits<char>_std::allocator<char>>(&result);
#      v27 = -1;
#      std::basic_stringstream<char_std::char_traits<char>_std::allocator<char>>::_vbase_destructor(&this);
#      v3 = v24;
#    }
#  }
#  v19 = v2;
#  _RTC_CheckStackVars(&v28, &stru_55A7E8);
#  j___RTC_CheckEsp(v21, v19);
#  LODWORD(v20) = LODWORD(v3);
#  return v20;
#}

