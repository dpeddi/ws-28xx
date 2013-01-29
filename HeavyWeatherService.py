#!/usr/bin/python

## This driver is based is based on reverse engineering of HeavyWeather 2800 v 1.54
## All copyright goes to La Crosse Technology (c) 2008

## Python port by Eddi De Pieri <eddi@depieri.net>
## Use this software as your own risk.
## Me and La Crosse Technology is not responsable for any damage using this software

## Really thanks tfa-dostmann.de to allow me to go forward with development

#from datetime import datetime
#from datetime import timedelta

import os

import logging
#import time
import threading
import traceback

#import shelve 
#import mmap #http://docs.python.org/library/mmap.html

#import USBHardware
#import CWeatherTraits
#import CHistoryDataSet
#import CDataStore
import CCommunicationService
#import CCurrentWeatherData
import EConstants
#import sHID
from CWeatherStationConfig import CWeatherStationConfig


def handleError(self, record):
	traceback.print_stack()
logging.Handler.handleError = handleError

#sHID = sHID.sHID()
#USBHardware = USBHardware.USBHardware()
#CCurrentWeatherData = CCurrentWeatherData.CCurrentWeatherData()
#CWeatherStationConfig = CWeatherStationConfig.CWeatherStationConfig()

#CCommunicationService = CCommunicationService.CCommunicationService()
#CWeatherTraits = CWeatherTraits.CWeatherTraits()
ERequestState=EConstants.ERequestState()


#def equal(a, b):
    #return abs(a - b) < 1e-6
#
#if equal(f1, f2):

class ws28xxError(IOError):
	"Used to signal an error condition"

#filehandler = open("WV5DataStore", 'w')
#pickle.dump(CDataStore.TransceiverSettings, filehandler)

if __name__ == "__main__":
	import logging
	import sys
	
	#http://rosettacode.org/wiki/Keyboard_input/Keypress_check
	import thread
	import time

	try:
	    from msvcrt import getch
	except ImportError:
	    def getch():
	        import sys, tty, termios
	        fd = sys.stdin.fileno()
	        old_settings = termios.tcgetattr(fd)
	        try:
	            tty.setraw(sys.stdin.fileno())
	            ch = sys.stdin.read(1)
	        finally:
	            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
	        return ch

	char = None


	def keypress():
	    global char
	    char = getch()

	thread.start_new_thread(keypress, ())


#CRITICAL 50 
#ERROR 40 
#WARNING 30 
#INFO 20 
#DEBUG 10 
#NOTSET 0 
#	logging.basicConfig(format='%(asctime)s %(name)s %(message)s',filename="HeavyWeatherService.log",level=logging.DEBUG)
#	logging.basicConfig(format='%(asctime)s %(name)s.%(funcName)s %(message)s',filename="HeavyWeatherService.log",level=logging.DEBUG)
	logging.basicConfig(format='%(asctime)s %(name)s.%(funcName)s %(message)s',filename="HeavyWeatherService.log",level=logging.INFO)

	os.system( [ 'clear', 'cls' ][ os.name == 'nt' ] )

	print "Initializing ws28xx...\r"
	myCCommunicationService = CCommunicationService.CCommunicationService()
	myCCommunicationService.DataStore.setCommModeInterval(3) #move me to setfrontendalive

	Freq = 915
	if myCCommunicationService.DataStore.getTransmissionFrequency() == 1:
		myCCommunicationService.DataStore.TransceiverSettings.Frequency = 868300000
		Freq = 868

	def infoscreen(TransceiverSerNo,Freq):
		os.system( [ 'clear', 'cls' ][ os.name == 'nt' ] )
		print "ws28xx python driver\r"
		print "====================\r"
		
		print "Transceiver With SerNo %s at %d Mhz\r" % (TransceiverSerNo,Freq)
		print "\r"
		print "0: Current\r"
		print "1: History\r"
		print "2: GetConfig\r"
		print "3: SetConfig\r"
		print "4: SetTime\r"
		print "5: Syncronize - press [v] key on Display then choose this option\r"
		print "\r"
		print "f: switch operating frequency (and exit)\r"
		print "o: switch to old rainsensor (and exit)\r"
		print "\r"
		print "x: exit\r"
		print "esc: exit\r"
		print "\r"

	sys.stdout.write("waiting until transceiver initialized")
	while True:
		sys.stdout.write(".")
		time.sleep(0.5)
		if myCCommunicationService.DataStore.getFlag_FLAG_TRANSCEIVER_PRESENT():
			print "\r"
			break


	myCCommunicationService.DataStore.setDeviceRegistered(True); #temp hack

	infoscreen(myCCommunicationService.DataStore.getTransceiverSerNo(),Freq)

	try:
	    while True:
		if char is not None:
			print "Key pressed is %s\r" % char
		#print "GetRequestType %d GetRequestState %d\r" % (myCCommunicationService.DataStore.getRequestType(), myCCommunicationService.DataStore.getRequestState())
		if   char == "0":
			char = None
			Weather = [0]
			Weather[0]=[0]
			if myCCommunicationService.DataStore.getRequestState() == ERequestState.rsFinished \
			    or myCCommunicationService.DataStore.getRequestState() == ERequestState.rsINVALID:
				print "getRequestState == rsFinished or rsInvalid... ask for current weather again :-)\r"
				TimeOut = myCCommunicationService.DataStore.getPreambleDuration() + myCCommunicationService.DataStore.getRegisterWaitTime()
				myCCommunicationService.DataStore.GetCurrentWeather(Weather,TimeOut)
		elif char == "1":
			char = None
		elif char == "2":
			char = None
		elif char == "3":
			char = None
		elif char == "4":
			char = None
		elif char == "5":
			char = None
			#if myCCommunicationService.DataStore.getDeviceId() == -1:
			if True: #hack ident
				print "TransceiverSerNo will be overwritten", myCCommunicationService.DataStore.getTransceiverSerNo()
				print "DeviceID will be overwritten", myCCommunicationService.DataStore.getDeviceId()
				TimeOut = myCCommunicationService.DataStore.getPreambleDuration() + myCCommunicationService.DataStore.getRegisterWaitTime()
				print "FirstTimeConfig Timeout=%d" % TimeOut
				ID=[0]
				ID[0]=0
				myCCommunicationService.DataStore.FirstTimeConfig(ID,TimeOut)
				print ID[0]
		elif char == "F" or char == "f":
			char = None
			FreqID = myCCommunicationService.DataStore.getTransmissionFrequency()
			if FreqID == 1:
				FreqID = 0
			else:
				FreqID = 1
			FreqID = myCCommunicationService.DataStore.setTransmissionFrequency(FreqID)
			myCCommunicationService.kill_received = True
			break
		elif char == "O" or char == "o":
			char = None
			myCCommunicationService.kill_received = True
			break
		elif char==chr(27) or char == "x":
			char = None
			myCCommunicationService.kill_received = True
			#os._exit(12)
			break
		else:
			char = None
			Weather = [0]
			Weather[0]=[0]
			if myCCommunicationService.DataStore.getRequestState() == ERequestState.rsFinished \
			   or myCCommunicationService.DataStore.getRequestState() == ERequestState.rsINVALID:
				print "getRequestState == rsFinished or rsInvalid... ask for current weather again :-)\r"
				TimeOut = myCCommunicationService.DataStore.getPreambleDuration() + myCCommunicationService.DataStore.getRegisterWaitTime()
				myCCommunicationService.DataStore.GetCurrentWeather(Weather,TimeOut)
		time.sleep(1)

	except KeyboardInterrupt:
		print "Ctrl-c received! Sending kill to threads..."
		myCCommunicationService.kill_received = True
		raise

