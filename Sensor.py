from Phidget22.PhidgetException import *
from Phidget22.Phidget import *
import numpy as np
from time import sleep
import time
import queue

class Sensor():
    '''
    Base class for all types of phidget sensors
    '''

    noOfSensors = 0

    def __init__(self,deviceSN,dataInterval,refreshPeriod,sensorName=None):
        '''
        Constructor for base sensor class

        Arguments
        ---------
        deviceSN: Serial number for the desired phidget sensor.
        All sensors require a serial number either directly or for the hub they are connected to

        dataInterval: Delay between sequential readings ofthe sensor in ms.
        Should be multiple of 8

        refreshPeriod: Used for plotting.
        Time in seconds data will be plotted for before the graph is refreshed.

        sensorName: Human readable string used to ID sensors
        '''
        Sensor.noOfSensors += 1
        self.deviceSN = deviceSN
        self.dataInterval = dataInterval
        self.refreshPeriod = refreshPeriod*1000.0
        if sensorName == None:
            self.sensorName = "Sensor {}".format(str(self.noOfSensors))
        else:
            self.sensorName = sensorName
        self.attached = False
        self.dataQ = queue.Queue()
        self.data =  np.asarray([0.0]*round(self.refreshPeriod/self.dataInterval))
        self.times = np.asarray([0.0]*round(self.refreshPeriod/self.dataInterval))
        self.arrayIndex = 0
        self.attachSensor()
        self.activateDisconnectListener()
        self.activateDataListener()

    def attachSensor(self):
        '''
        Attatches the sensor to the application. This is different for differnet
        kinds of sensors and so is overwritten in each sensor class
        '''
        pass

    def activateDisconnectListener(self):
        '''
        Activates an event to listen for the disconnection of the sensor.
        '''
        def detachHandler(channelObject):
            self.attached = False
            print("\n***** {} detached *****".format(self.sensorName))
        self.channel.setOnDetachHandler(detachHandler)

    def getData(self):
        '''
        Method called externally to access sensor data. Returns the most recent
        time and sensor data values logged since last call. Also returns all time
        and data values since last refresh for use in plotting.
        '''
        newData = []
        newTimes = []
        newRawTimes = []
        while not self.dataQ.empty():
            datum = self.dataQ.get()
            newData.append(datum[0])
            newTimes.append(datum[1])
            newRawTimes.append(datum[2])
        currentTime = time.time() - self.startTime
        if len(newData) > 0:
            for i in range(len(newData)):
                self.data[self.arrayIndex] = newData[i]
                self.times[self.arrayIndex] = newTimes[i]
                self.arrayIndex = self.arrayIndex + 1
                if currentTime > self.refreshPeriod/1000.0:
                    self.arrayIndex = 0
                    self.startTime = time.time()
                else:
                    if self.arrayIndex >= len(self.data):
                        self.data = np.append(self.data,0)
                        self.times = np.append(self.times,0)
        return (np.asarray(newRawTimes), np.asarray(newData),
                    self.times[0:self.arrayIndex], self.data[0:self.arrayIndex])
