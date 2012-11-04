class EHistoryInterval:
	hi01Min          = 0
	hi05Min          = 1
	hi10Min          = 2
	hi15Min          = 3
	hi20Min          = 4
	hi30Min          = 5
	hi60Min          = 6
	hi02Std          = 7
	hi04Std          = 8
	hi06Std          = 9
	hi08Std          = 0xA
	hi12Std          = 0xB
	hi24Std          = 0xC

class EWindspeedFormat:
	wfMs             = 0
	wfKnots          = 1
	wfBFT            = 2
	wfKmh            = 3
	wfMph            = 4

class ERainFormat:
	rfMm             = 0
	rfInch           = 1

class EPressureFormat:
	pfinHg           = 0
	pfHPa            = 1

class ETemperatureFormat:
	tfFahrenheit     = 0
	tfCelsius        = 1

class EClockMode:
	ct24H            = 0
	ctAmPm           = 1

class  EWeatherTendency:
	TREND_NEUTRAL    = 0
	TREND_UP         = 1
	TREND_DOWN       = 2
	TREND_ERR        = 3

class EWeatherState:
	WEATHER_BAD      = 0
	WEATHER_NEUTRAL  = 1
	WEATHER_GOOD     = 2
	WEATHER_ERR      = 3

class EWindDirection:
	 wdN              = 0
	 wdNNE            = 1
	 wdNE             = 2
	 wdENE            = 3
	 wdE              = 4
	 wdESE            = 5
	 wdSE             = 6
	 wdSSE            = 7
	 wdS              = 8
	 wdSSW            = 9
	 wdSW             = 0x0A
	 wdWSW            = 0x0B
	 wdW              = 0x0C
	 wdWNW            = 0x0D
	 wdNW             = 0x0E
	 wdNNW            = 0x0F
	 wdERR            = 0x10
	 wdInvalid        = 0x11

class EResetMinMaxFlags:
	 rmTempIndoorHi   = 0
	 rmTempIndoorLo   = 1
	 rmTempOutdoorHi  = 2
	 rmTempOutdoorLo  = 3
	 rmWindchillHi    = 4
	 rmWindchillLo    = 5
	 rmDewpointHi     = 6
	 rmDewpointLo     = 7
	 rmHumidityIndoorLo  = 8
	 rmHumidityIndoorHi  = 9
	 rmHumidityOutdoorLo  = 0x0A
	 rmHumidityOutdoorHi  = 0x0B
	 rmWindspeedHi    = 0x0C
	 rmWindspeedLo    = 0x0D
	 rmGustHi         = 0x0E
	 rmGustLo         = 0x0F
	 rmPressureLo     = 0x10
	 rmPressureHi     = 0x11
	 rmRain1hHi       = 0x12
	 rmRain24hHi      = 0x13
	 rmRainLastWeekHi  = 0x14
	 rmRainLastMonthHi  = 0x15
	 rmRainTotal      = 0x16
	 rmInvalid        = 0x17

class ERequestType:
	rtGetCurrent     = 0
	rtGetHistory     = 1
	rtGetConfig      = 2
	rtSetConfig      = 3
	rtSetTime        = 4
	rtFirstConfig    = 5
	rtINVALID        = 6

class ERequestState:
	rsQueued         = 0
	rsRunning        = 1
	rsFinished       = 2
	rsPreamble       = 3
	rsWaitDevice     = 4
	rsWaitConfig     = 5
	rsError          = 6
	rsChanged        = 7
	rsINVALID        = 8

class ETransmissionFrequency:
	tfUS             = 0
	tfEuropean       = 1
