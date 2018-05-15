from Phidget22.PhidgetException import *
from Phidget22.Phidget import *
from Phidget22.Devices.TemperatureSensor import *
from PhidgetDataLogger import Sensor
import numpy as np
from time import sleep
import time
import queue

class IRTemperatureSensor(Sensor):
    '''
    Class for connecting to Phidget IR temperature sensors. Extends base Sensor class
    '''

    def __init__(self,deviceSN,dataInterval,refreshPeriod,sensorName=None):
        '''
        Constructor for IR Temp class. Takes same arguments as Sensor
        '''
        Sensor.__init__(self,deviceSN,dataInterval,refreshPeriod,sensorName)
        self.sensorUnits = "Degrees C"

    def attachSensor(self):
        '''
        Connects sensor to application. Sets the "channel" parameter which is the
        handle to the phidget
        '''
        self.channel = TemperatureSensor()
        self.channel.setDeviceSerialNumber(self.deviceSN)
        self.channel.setChannel(0)
        self.channel.openWaitForAttachment(5000)
        print("***** {} Sensor Attached *****".format(self.sensorName))
        self.attached = True
        self.channel.setDataInterval(self.dataInterval)

    def activateDataListener(self):
        '''
        Sets up the event which triggers when the sensor updates its output values
        '''
        self.startTime = time.time()
        def onTemperatureChange(channelObject,temperature):
            # logs time and sensor value to the thread safe dataQ
            rawTime = time.time()
            deltaTime = rawTime-self.startTime
            self.dataQ.put([temperature,deltaTime,rawTime])
        self.channel.setOnTemperatureChangeHandler(onTemperatureChange  )
