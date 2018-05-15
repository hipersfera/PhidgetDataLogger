from Phidget22.Devices.VoltageRatioInput import *
from Phidget22.PhidgetException import *
from Phidget22.Phidget import *
from PhidgetDataLogger import Sensor
import numpy as np
from time import sleep
import time
import queue

class StrainSensor(Sensor):
    '''Class used to handle load cell type sensors. Extends Sensor class '''

    def __init__(self, deviceSN,channelNo,dataInterval,refreshPeriod,
                sensorName=None):
        '''
        Constructor for strain sensor phidgets. Takes standard Sensor arguments
        '''
        self.channelNo = channelNo
        self.sensorUnits = "Kg"
        self.useCallibration = False
        self.gradient = 1
        self.intercept = 0
        Sensor.__init__(self,deviceSN,dataInterval,refreshPeriod,sensorName)

    def attachSensor(self):
        '''
        Connects the strain sensor to the application
        '''
        self.channel = VoltageRatioInput()
        self.channel.setDeviceSerialNumber(self.deviceSN)
        self.channel.setChannel(self.channelNo)
        self.channel.openWaitForAttachment(100)
        print("\n***** {} Sensor Attached *****".format(self.sensorName))
        self.attached = True
        self.channel.setDataInterval(self.dataInterval)
        self.channel.setBridgeGain(0x8)

    def activateDataListener(self):
        '''
        Sets up the event which triggers when the sensor updates its utput values
        '''
        self.startTime = time.time()
        def onSensorValueChange(channelObject,voltageRatio):
            rawTime = time.time()
            deltaTime = rawTime- self.startTime
            if self.useCallibration:
                voltageRatio = voltageRatio*self.gradient + self.intercept
            self.dataQ.put([voltageRatio,deltaTime,rawTime])
        self.channel.setOnVoltageRatioChangeHandler(onSensorValueChange)

    def setCallibration(self,gradient,intercept):
        '''
        Used to give the sensor callibration values.
        '''
        self.gradient = gradient
        self.intercept = intercept
        self.useCallibration = True
