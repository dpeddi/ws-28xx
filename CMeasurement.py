#!/usr/bin/python

## This driver is based is based on reverse engineering of HeavyWeather 2800 v 1.54
## All copyright goes to La Crosse Technology (c) 2008

## Python port by Eddi De Pieri <eddi@depieri.net>
## Use this software as your own risk.
## Me and La Crosse Technology is not responsable for any damage using this software

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
