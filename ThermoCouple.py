from Phidget22.Devices.TemperatureSensor import *
from Phidget22.PhidgetException import *
from Phidget22.Phidget import *
from PhidgetDataLogger import Sensor
import numpy as np
from time import sleep
import time
import queue

class ThermoCouple(Sensor):
    '''Class used to handle any thermcouple data '''

    def __init__(self, deviceSN,channelNo,dataInterval,refreshPeriod,sensorType,
                sensorName=None):
        '''
        Constructor for creating thermcouple sensors. Takes standard sensor
        arguments. Sensor type here is enum for different thermcouples. J,K,E and
        T types are represented by 1,2,3,4. 
        '''
        self.channelNo = channelNo
        self.sensorType = sensorType
        self.sensorUnits = None
        Sensor.__init__(self,deviceSN,dataInterval,refreshPeriod,sensorName)

    def attachSensor(self):
        '''
        Connects the sensor to the application
        '''
        self.channel = TemperatureSensor()
        self.channel.setDeviceSerialNumber(self.deviceSN)
        self.channel.setChannel(self.channelNo)
        self.channel.openWaitForAttachment(100)
        print("\n***** {} Sensor Attached *****".format(self.sensorName))
        self.attached = True
        self.channel.setThermocoupleType(self.sensorType)
        self.channel.setDataInterval(self.dataInterval)
        self.sensorUnits= "degrees C"

    def activateDataListener(self):
        '''
        Sets up the event which triggers when the sensor updates its outputs
        '''
        self.startTime = time.time()
        def onTempChange(channelObject,temp):
            rawTime = time.time()
            deltaTime = rawTime- self.startTime
            self.dataQ.put([temp,deltaTime,rawTime])
        self.channel.setOnTemperatureChangeHandler(onTempChange)
