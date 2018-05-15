from Phidget22.Devices.VoltageRatioInput import *
from Phidget22.PhidgetException import *
from Phidget22.Phidget import *
from PhidgetDataLogger import Sensor
import numpy as np
from time import sleep
import time
import queue

class VoltageRatioSensor(Sensor):
    '''Class used to handle any sensor which uses a ratiometric voltage input '''

    def __init__(self, deviceSN,channelNo,dataInterval,refreshPeriod,sensorType,
                sensorName=None):
        '''
        Connects the sensor to the application
        '''
        self.channelNo = channelNo
        self.sensorType = sensorType
        self.sensorUnits = None
        Sensor.__init__(self,deviceSN,dataInterval,refreshPeriod,sensorName)

    def attachSensor(self):
        '''
        Connects the sensor to the application
        '''
        self.channel = VoltageRatioInput()
        self.channel.setDeviceSerialNumber(self.deviceSN)
        self.channel.setChannel(self.channelNo)
        self.channel.openWaitForAttachment(100)
        print("\n***** {} Sensor Attached *****".format(self.sensorName))
        self.attached = True
        self.channel.setSensorType(self.sensorType)
        self.channel.setDataInterval(self.dataInterval)
        self.sensorUnits=self.channel.getSensorUnit().symbol

    def activateDataListener(self):
        '''
        Sets up the event which triggers when the sensor updates its outputs
        '''
        self.startTime = time.time()
        def onSensorValueChange(channelObject,sensorVlue,sensorUnit):
            rawTime = time.time()
            deltaTime = rawTime- self.startTime
            self.dataQ.put([channelObject.getSensorValue(),deltaTime,rawTime])
        self.channel.setOnSensorChangeHandler(onSensorValueChange)
