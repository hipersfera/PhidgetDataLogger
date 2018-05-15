# Example showing how to start the application with 2 dummy sensors
# Requires no phidgets to get started 

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

    #Define main application object and start application
    PDA = PDL.PhidgetDisplayApp(sensorList,yDataRanges=yDataRanges)
    PDA.run()
