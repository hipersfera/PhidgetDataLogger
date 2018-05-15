from Phidget22.Devices.DigitalOutput import *
from Phidget22.PhidgetException import *
from Phidget22.Phidget import *
import time

class DigitalOutputChannel():
    '''
    Class used to set high or low voltages on Digital Output channels on IO boards
    '''

    def __init__(self, deviceSN,channelNo):
        '''
        Constructor for Digital Output channels.
        '''
        #Attempt to attach tochannel
        self.deviceSN = deviceSN
        self.channelNo = channelNo
        self.attachChannel()

    def attachChannel(self):
        '''
        Connect to Digital output channel testing
        '''
        self.channel = DigitalOutput()
        self.channel.setDeviceSerialNumber(self.deviceSN)
        self.channel.setChannel(self.channelNo)
        self.channel.openWaitForAttachment(100)
        self.channel.setState(False)

    def setState(self,state):
        '''
        Changes the output state of the channel between high and low using True
        and False
        '''
        self.channel.setState(state)
