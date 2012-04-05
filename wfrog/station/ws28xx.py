##
##  This file is part of wfrog
##
##  wfrog is free software: you can redistribute it and/or modify
##  it under the terms of the GNU General Public License as published by
##  the Free Software Foundation, either version 3 of the License, or
##  (at your option) any later version.
##
##  This program is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##  GNU General Public License for more details.
##
##  You should have received a copy of the GNU General Public License
##  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import time
import logging

def detect():
	station = WS28xxStation()
	return station

class WS28xxStation(object):

	logger = logging.getLogger('station.ws28xx')

	name = "LaCrosse WS28xx"
	
	def run(self, generate_event, send_event, context={}):

		from ws28xxgit import HeavyWeatherService
		from ws28xxgit import CWeatherTraits

		#import HeavyWeatherService
		#print(dir(HeavyWeatherService))
		
		CWeatherTraits = CWeatherTraits.CWeatherTraits()

		myCCommunicationService = HeavyWeatherService.CCommunicationService()
		HeavyWeatherService.CDataStore.setCommModeInterval(myCCommunicationService.DataStore,3) #move me to setfrontendalive
		time.sleep(5)

		TimeOut = HeavyWeatherService.CDataStore.getPreambleDuration(myCCommunicationService.DataStore) + HeavyWeatherService.CDataStore.getRegisterWaitTime(myCCommunicationService.DataStore)
		print "FirstTimeConfig Timeout=%d" % TimeOut
		ID=[0]
		ID[0]=0
		HeavyWeatherService.CDataStore.FirstTimeConfig(myCCommunicationService.DataStore,ID,TimeOut)

		HeavyWeatherService.CDataStore.setDeviceRegistered(myCCommunicationService.DataStore, True); #temp hack
		HeavyWeatherService.CDataStore.setDeviceId(myCCommunicationService.DataStore, 0x32); #temp hack

		Weather = [0]
		Weather[0]=[0]

		TimeOut = HeavyWeatherService.CDataStore.getPreambleDuration(myCCommunicationService.DataStore) + HeavyWeatherService.CDataStore.getRegisterWaitTime(myCCommunicationService.DataStore)
		HeavyWeatherService.CDataStore.GetCurrentWeather(myCCommunicationService.DataStore,Weather,TimeOut)
		time.sleep(1)

		while True:
			if HeavyWeatherService.CDataStore.getRequestState(myCCommunicationService.DataStore) == HeavyWeatherService.ERequestState.rsFinished \
			       or HeavyWeatherService.CDataStore.getRequestState(myCCommunicationService.DataStore) == HeavyWeatherService.ERequestState.rsINVALID:
					TimeOut = HeavyWeatherService.CDataStore.getPreambleDuration(myCCommunicationService.DataStore) + HeavyWeatherService.CDataStore.getRegisterWaitTime(myCCommunicationService.DataStore)
					HeavyWeatherService.CDataStore.GetCurrentWeather(myCCommunicationService.DataStore,Weather,TimeOut)

			try:
				if abs(CWeatherTraits.TemperatureNP() - myCCommunicationService.DataStore.CurrentWeather._IndoorTemp ) > 0.001:
					e = generate_event('temp')
					e.sensor = 0
					e.value = myCCommunicationService.DataStore.CurrentWeather._IndoorTemp
					send_event(e)

				if abs(CWeatherTraits.HumidityNP() - myCCommunicationService.DataStore.CurrentWeather._IndoorHumidity ) > 0.001:
					e = generate_event('hum')
					e.sensor = 0
					e.value = myCCommunicationService.DataStore.CurrentWeather._IndoorHumidity
					send_event(e)

				#if abs(CWeatherTraits.HumidityNP() - myCCommunicationService.DataStore.CurrentWeather._IndoorHumidity ) > 0.001:
				#	e = generate_event('press')
				#	e.sensor = 0
				#	e.value = myCCommunicationService.DataStore.CurrentWeather._IndoorHumidity
				#	send_event(e)

				if abs(CWeatherTraits.TemperatureNP() - myCCommunicationService.DataStore.CurrentWeather._OutdoorTemp ) > 0.001:
					e = generate_event('temp')
					e.sensor = 1
					e.value = myCCommunicationService.DataStore.CurrentWeather._OutdoorTemp
					send_event(e)

				if abs(CWeatherTraits.HumidityNP() - myCCommunicationService.DataStore.CurrentWeather._OutdoorHumidity ) > 0.001:
					e = generate_event('hum')
					e.sensor = 1
					e.value = myCCommunicationService.DataStore.CurrentWeather._OutdoorHumidity
					send_event(e)

				if abs(CWeatherTraits.HumidityNP() - myCCommunicationService.DataStore.CurrentWeather._OutdoorHumidity ) > 0.001:
					e = generate_event('press')
					e.sensor = 1
					e.value = myCCommunicationService.DataStore.CurrentWeather._OutdoorHumidity
					send_event(e)

				if CWeatherTraits.WindNP() != myCCommunicationService.DataStore.CurrentWeather._WindSpeed:
					e = generate_event('wind')
					e.create_child('mean')
					e.mean.speed = myCCommunicationService.DataStore.CurrentWeather._WindSpeed
					e.mean.dir = myCCommunicationService.DataStore.CurrentWeather._WindDirection * 360 / 16
					#if CWeatherTraits.WindNP() == myCCommunicationService.DataStore.CurrentWeather._Gust:
					e.create_child('gust')
					e.gust.speed = myCCommunicationService.DataStore.CurrentWeather._Gust
					e.gust.dir = myCCommunicationService.DataStore.CurrentWeather._GustDirection * 360 / 16
				send_event(e)

			except Exception, e:
				self.logger.error(e)

			time.sleep(5)

name = WS28xxStation.name
