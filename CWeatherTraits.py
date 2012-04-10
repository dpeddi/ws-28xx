#!/usr/bin/python

## This driver is based is based on reverse engineering of HeavyWeather 2800 v 1.54
## All copyright goes to La Crosse Technology (c) 2008

## Python port by Eddi De Pieri <eddi@depieri.net>
## Use this software as your own risk.
## Me and La Crosse Technology is not responsable for any damage using this software

class CWeatherTraits(object):

	windDirMap = { 0:"N", 1:"NNE", 2:"NE", 3:"ENE", 4:"E", 5:"ESE", 6:"SE", 7:"SSE",
                       8:"S", 9:"SSW", 10:"SW", 11:"WSW", 12:"W", 13:"WNW", 14:"NW", 15:"NWN", 16:"err", 17:"inv" }

	forecastMap = { 0:"Rainy(Bad)", 1:"Cloudy(Neutral)", 2:"Sunny(Good)",  3:"Error" }
	trends =      { 0:"Stable(Neutral)", 1:"Rising(Up)", 2:"Falling(Down)", 3:"Error" }

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