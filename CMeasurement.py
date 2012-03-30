import time

class CMeasurement:
	_Value = 0.0
	_ResetFlag = 23
	_IsError = 1
	_IsOverflow = 1
	_Time = time.time()	#ATL::COleDateTime::COleDateTime(&thisa->_Time);
				#ATL::COleDateTime::SetStatus(&thisa->_Time, partial);

	def Reset(self):
		self._Value = 0.0
		self._ResetFlag = 23
		self._IsError = 1
		self._IsOverflow = 1
