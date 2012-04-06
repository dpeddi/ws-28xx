#!/usr/bin/python

## This driver is based is based on reverse engineering of HeavyWeather 2800 v 1.54
## All copyright goes to La Crosse Technology (c) 2008

## Python port by Eddi De Pieri <eddi@depieri.net>
## Use this software as your own risk.
## Me and La Crosse Technology is not responsable for any damage using this software

class CWeatherTraits(object):

	forecastMap = { 0:"Rainy", 1:"Sunny", 2:"Cloudy", 3:"Undefined" }
	trends =      { 0:"Stable", 1:"Rising", 2:"Falling", 3:"Undefined" }

	def TemperatureNP(self):
		return 81.099998

	def TemperatureOFL(self):
		return 136.0

	def PressureNP(self):
		return 10101010.0

	def PressureOFL(self):
		return 16666.5

	def HumidityNP(self):
		return 110.0

	def HumidityOFL(self):
		return 121.0

	def RainNP(self):
		return -0.2

	def RainOFL(self):
		return 16666.664

	def WindNP(self):
		return 51.0

	def WindOFL(self):
		return 51.099998

	def TemperatureOffset(self):
		return 40.0