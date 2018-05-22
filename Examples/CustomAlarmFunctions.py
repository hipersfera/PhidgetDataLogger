# Example showing how to add custom alarm functions to the application
# Uses dummy sensors so no Phidget devices required

if __name__ == "__main__":
    #Only need the following 2 lines in examples you wont need these elsewhere
    import sys
    sys.path.insert(0, '../../')
    #Import phidget package
    import PhidgetDataLogger as PDL

    #Define 2 dummy sensors
    S1 = PDL.DummySensor(1,15,"sensor 1")
    S2 = PDL.DummySensor(2,15,"Sensor 2")

    #Create lists of sensor and data ranges
    sensorList = [S1,S2]
    yDataRanges = [ [-1,1] , [-1,1] ]

    #Define main application object
    PDA = PDL.PhidgetDisplayApp(sensorList,yDataRanges=yDataRanges)

    #create alarm function
    def alarmFunction(*message):
        print(message)

    #Load function and arguments to application
    PDA.loadAlarmFunction(alarmFunction,"Alarm has been sounded")
    #Start application
    PDA.run()
