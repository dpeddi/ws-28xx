## Copyright 2012 Eddi De Pieri <eddi@depieri.net>
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

##  To use this module you need to install somewhere 
##  the library available at https://github.com/dpeddi/ws-28xx.git
##  Before you start wfrog you need to export path to ws-28xx module
##  export PYTHONPATH=$PYTHONPATH:/path/to/ws-28xx-module
##  then you can start wfrog.

##  The ws-28xx at github and driver are still under heavy
##  development. Feel free to contribute.

##  2012-04-27: my station stopped working. I've imported a US unit
##              while I live in EU. I've asked support for my unit
##              both to lacrossetechnology.com and lacrossetecnhology.fr
##
##              Now I'm in the situation that both give email support
##              but I can't get my station back to repair.


import time
import logging

def detect():
	try:
		station = WS28xxStation()
	except:
		print "ws28xx: failed loading modules"
		station = None
	return station

class WS28xxStation(object):

	logger = logging.getLogger('station.ws28xx')

	name = "LaCrosse WS28xx"
	
	def run(self, generate_event, send_event, context={}):

		import CCommunicationService
		import CWeatherTraits
		import EConstants

		ERequestState=EConstants.ERequestState()
		CWeatherTraits = CWeatherTraits.CWeatherTraits()

		myCCommunicationService = CCommunicationService.CCommunicationService()
		myCCommunicationService.DataStore.setCommModeInterval(3) #move me to setfrontendalive
		
		if myCCommunicationService.DataStore.getTransmissionFrequency() == 1:
			self.logger.info("Set Frequency to EU")
			myCCommunicationService.DataStore.TransceiverSettings.Frequency = 868300000
		else:
			self.logger.info("Set Frequency to US(Default)")

		while True:
			time.sleep(0.5)
			if myCCommunicationService.DataStore.getFlag_FLAG_TRANSCEIVER_PRESENT():
				break

		if myCCommunicationService.DataStore.getDeviceId() == -1:
			TimeOut = myCCommunicationService.DataStore.getPreambleDuration() + myCCommunicationService.DataStore.getRegisterWaitTime()
			ID=[0]
			ID[0]=0
			print "Press [v] key on Weather Station"
			myCCommunicationService.DataStore.FirstTimeConfig(ID,TimeOut)

		myCCommunicationService.DataStore.setDeviceRegistered( True);	#temp hack

		Weather = [0]
		Weather[0]=[0]

		#TimeOut = myCCommunicationService.DataStore.getPreambleDuration() + myCCommunicationService.DataStore.getRegisterWaitTime()
		#print TimeOut
		#myCCommunicationService.DataStore.GetCurrentWeather(Weather,TimeOut)
		#time.sleep(1)

		LastTimeStamp = None
		while True:
			#if myCCommunicationService.DataStore.getRequestState() == ERequestState.rsFinished \
			#       or myCCommunicationService.DataStore.getRequestState() == ERequestState.rsINVALID:
			#		TimeOut = myCCommunicationService.DataStore.getPreambleDuration() + myCCommunicationService.DataStore.getRegisterWaitTime()
			#		myCCommunicationService.DataStore.GetCurrentWeather(Weather,TimeOut)

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

				if abs(CWeatherTraits.PressureNP() - myCCommunicationService.DataStore.CurrentWeather._PressureRelative_hPa ) > 0.001:
					e = generate_event('press')
					e.value = myCCommunicationService.DataStore.CurrentWeather._PressureRelative_hPa
					send_event(e)

				if CWeatherTraits.RainNP() != myCCommunicationService.DataStore.CurrentWeather._RainTotal:
					e = generate_event('rain')
					e.rate = myCCommunicationService.DataStore.CurrentWeather._Rain1H
					e.total = myCCommunicationService.DataStore.CurrentWeather._RainTotal
					send_event(e)

				if abs(CWeatherTraits.WindNP() - myCCommunicationService.DataStore.CurrentWeather._WindSpeed) > 0.001:
					e = generate_event('wind')
					e.create_child('mean')
					e.mean.speed = myCCommunicationService.DataStore.CurrentWeather._WindSpeed
					e.mean.dir = myCCommunicationService.DataStore.CurrentWeather._WindDirection * 360 / 16
					e.create_child('gust')
					e.gust.speed = myCCommunicationService.DataStore.CurrentWeather._Gust
					e.gust.dir = myCCommunicationService.DataStore.CurrentWeather._GustDirection * 360 / 16
					send_event(e)


				#history records...
				History = myCCommunicationService.DataStore.getHistoryData(1)
				if History.m_Time != LastTimeStamp:
					if abs(CWeatherTraits.TemperatureNP() - History.m_IndoorTemp ) > 0.001:
						self.logger.info("ts=%s indoor_temp %d"%(History.m_Time,History.m_IndoorTemp))
						e = generate_event('temp')
						e.sensor = 0
						e.value = History.m_IndoorTemp
						e.timestamp = History.m_Time
						send_event(e)

					if abs(CWeatherTraits.HumidityNP() - History.m_IndoorHumidity ) > 0.001:
						self.logger.info("ts=%s indoor_hum %d"%(History.m_Time,History.m_IndoorHumidity))
						e = generate_event('hum')
						e.sensor = 0
						e.value = History.m_IndoorHumidity
						e.timestamp = History.m_Time
						send_event(e)

					if abs(CWeatherTraits.TemperatureNP() - History.m_OutdoorTemp ) > 0.001:
						self.logger.info("ts=%s Outdoor_temp %d"%(History.m_Time,History.m_OutdoorTemp))
						e = generate_event('temp')
						e.sensor = 1
						e.value = History.m_OutdoorTemp
						e.timestamp = History.m_Time
						send_event(e)

					if abs(CWeatherTraits.HumidityNP() - History.m_OutdoorHumidity ) > 0.001:
						self.logger.info("ts=%s Outdoor_hum %d"%(History.m_Time,History.m_OutdoorHumidity))
						e = generate_event('hum')
						e.sensor = 1
						e.value = History.m_OutdoorHumidity
						e.timestamp = History.m_Time
						send_event(e)

					if abs(CWeatherTraits.PressureNP() - History.m_PressureRelative ) > 0.001:
						self.logger.info("ts=%s Pressure %d"%(History.m_Time,History.m_PressureRelative))
						e = generate_event('press')
						e.value = History.m_PressureRelative
						e.timestamp = History.m_Time
						send_event(e)

				#History.m_RainCounterRaw = 0
					if abs(CWeatherTraits.WindNP() - History.m_WindSpeed) > 0.001:
						self.logger.info("ts=%s Wind %d %d"%(History.m_Time,History.m_WindSpeed,History.m_WindDirection))
						self.logger.info("ts=%s Gust %d %d"%(History.m_Time,History.m_Gust,History.m_WindDirection))
						e = generate_event('wind')
						e.create_child('mean')
						e.mean.speed = History.m_WindSpeed
						e.mean.dir = History.m_WindDirection * 360 / 16
						e.create_child('gust')
						e.gust.speed = History.m_Gust
						#we don't have gust dir... we take wind dir... :-(
						e.gust.dir = History.m_WindDirection * 360 / 16
						e.timestamp = History.m_Time
						send_event(e)

					LastTimeStamp = History.m_Time

			except Exception, e:
				self.logger.error(e)

			time.sleep(1)

name = WS28xxStation.name
