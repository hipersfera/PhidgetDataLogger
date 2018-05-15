from Phidget22.PhidgetException import *
from Phidget22.Phidget import *
from PhidgetDataLogger import Sensor
import numpy as np
from time import sleep
import time
import queue

class DummySensor(Sensor):
    ''' Class derived from Sensor to simulte a phidget sensor by outputting
    sin waves. Used for testing application without phidgets.'''

    def __init__(self, omega,refreshPeriod,sensorName=None):
        '''
        Constructor for dummy sensor. omega is used to change frquency of output sin wave.
        '''
        self.refreshPeriod = refreshPeriod*1000.0
        self.sensorName = sensorName
        self.omega = omega
        self.sensorUnits = "N/A"
        self.times =[ ]
        self.data = []
        self.startTime = time.time()

    def getData(self):
        '''
        Overrides getData method from Sensor. Returns time and dummy sensor values
        as well as all values logged since last refresh period
        '''
        if time.time()- self.startTime > 15:
            self.data = []
            self.times = []
            self.startTime =time.time()
        y = np.sin(self.omega*time.time())
        x= time.time()-self.startTime
        self.times.append(x)
        self.data.append(y)
        return([time.time()],[y],self.times,self.data )
