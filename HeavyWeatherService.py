#!/usr/bin/python

## This driver is based is based on reverse engineering of HeavyWeather 2800 v 1.54
## All copyright goes to La Crosse Technology (c) 2008

## Python port by Eddi De Pieri <eddi@depieri.net>
## Use this software as your own risk.
## Me and La Crosse Technology is not responsable for any damage using this software

## Really thanks tfa-dostmann.de to allow me to go forward with development

from datetime import datetime
from datetime import timedelta

import os

import logging
import time
import threading
import traceback

#import shelve 
#import mmap #http://docs.python.org/library/mmap.html

import USBHardware
import CWeatherTraits
import CHistoryDataSet
import CDataStore
import CCommunicationService
import CCurrentWeatherData
import sHID
from CWeatherStationConfig import CWeatherStationConfig

def handleError(self, record):
	traceback.print_stack()
logging.Handler.handleError = handleError

sHID = sHID.sHID()
USBHardware = USBHardware.USBHardware()
#CCurrentWeatherData = CCurrentWeatherData.CCurrentWeatherData()
#CWeatherStationConfig = CWeatherStationConfig.CWeatherStationConfig()

#CCommunicationService = CCommunicationService.CCommunicationService()
CWeatherTraits = CWeatherTraits.CWeatherTraits()

#def equal(a, b):
    #return abs(a - b) < 1e-6
#
#if equal(f1, f2):

class ws28xxError(IOError):
	"Used to signal an error condition"

#filehandler = open("WV5DataStore", 'w')
#pickle.dump(CDataStore.TransceiverSettings, filehandler)

#myCCommunicationService.getInstance()
#myCCommunicationService.doRFCommunication()

#t = ThreadClass()
#t.start()

if __name__ == "__main__":
	import logging
#CRITICAL 50 
#ERROR 40 
#WARNING 30 
#INFO 20 
#DEBUG 10 
#NOTSET 0 
#	logging.basicConfig(format='%(asctime)s %(name)s %(message)s',filename="HeavyWeatherService.log",level=logging.DEBUG)
#	logging.basicConfig(format='%(asctime)s %(name)s.%(funcName)s %(message)s',filename="HeavyWeatherService.log",level=logging.DEBUG)
	logging.basicConfig(format='%(asctime)s %(name)s.%(funcName)s %(message)s',filename="HeavyWeatherService.log",level=logging.CRITICAL)

	myCCommunicationService = CCommunicationService.CCommunicationService()
	myCCommunicationService.DataStore.setCommModeInterval(3) #move me to setfrontendalive

	print "zzzzz"
	time.sleep(10)

	if myCCommunicationService.DataStore.getDeviceId() == -1:
		print "Press [v] key on Weather Station"
		TimeOut = myCCommunicationService.DataStore.getPreambleDuration() + myCCommunicationService.DataStore.getRegisterWaitTime()
		print "FirstTimeConfig Timeout=%d" % TimeOut
		ID=[0]
		ID[0]=0
		myCCommunicationService.DataStore.FirstTimeConfig(ID,TimeOut)

	#time.sleep(60+60+30)
	#os._exit(12)
	
	myCCommunicationService.DataStore.setDeviceRegistered( True); #temp hack

	Weather = [0]
	Weather[0]=[0]

	TimeOut = myCCommunicationService.DataStore.getPreambleDuration() + myCCommunicationService.DataStore.getRegisterWaitTime()
	myCCommunicationService.DataStore.GetCurrentWeather(Weather,TimeOut)
	time.sleep(1)

	while True:
		if myCCommunicationService.DataStore.getRequestState() == ERequestState.rsFinished \
		   or myCCommunicationService.DataStore.getRequestState() == ERequestState.rsINVALID:
			TimeOut = myCCommunicationService.DataStore.getPreambleDuration() + myCCommunicationService.DataStore.getRegisterWaitTime()
			myCCommunicationService.DataStore.GetCurrentWeather(Weather,TimeOut)
			#print "done"
		time.sleep(10)

