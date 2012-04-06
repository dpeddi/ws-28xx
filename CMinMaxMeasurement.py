#!/usr/bin/python

## This driver is based is based on reverse engineering of HeavyWeather 2800 v 1.54
## All copyright goes to La Crosse Technology (c) 2008

## Python port by Eddi De Pieri <eddi@depieri.net>
## Use this software as your own risk.
## Me and La Crosse Technology is not responsable for any damage using this software

import CMeasurement

class CMinMaxMeasurement(object):

	def __init__(self):
		self._Min = CMeasurement.CMeasurement()
		self._Max = CMeasurement.CMeasurement()

