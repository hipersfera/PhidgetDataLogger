import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
from PyQt5.QtMultimedia import QSound
from pyqtgraph.ptime import time as ptime
from PhidgetDataLogger.StrainSensor import StrainSensor
from PhidgetDataLogger.StoredDataPlotter import StoredDataPlotter
from PhidgetDataLogger.StrainCalibrator import StrainCalibrator
from PhidgetDataLogger.aqua.qsshelper import QSSHelper
import time
import datetime
import os

class PhidgetDisplayApp(QtGui.QWidget):
    '''
    Main application window. Handles live plotting and allows access to data viewer
    and callibration UIs.
    '''

    def __init__(self,sensors,xDataRanges=None,yDataRanges=None,parent=None):
        '''
        Constructor for the entire Phidget application. Takes list of sensors as
        well as x and y data ranges as arguments.
        '''
        self.app = QtGui.QApplication([])
        #Define relative paths to asset files
        self.iconPath = os.path.join(os.path.abspath(os.path.dirname(__file__)),"UI_Icons")
        self.soundPath = os.path.join(os.path.abspath(os.path.dirname(__file__)),"Sounds")
        self.styleSheetPath =  os.path.join(os.path.abspath(os.path.dirname(__file__)),"aqua")
        QtGui.QWidget.__init__(self,parent)
        self.sensors = sensors
        self.yDataRanges = yDataRanges
        self.xDataRanges = xDataRanges
        #SDPs (Stored Data Plotters) are usd to plot data from files.
        self.SDPs = []
        self.loadSounds()
        self.setUpPlotWidget()
        self.setUpUIWidgets()
        self.setUpMainWidget()
        self.connectPlotUpdates()
        qss = QSSHelper.open_qss(os.path.join(self.styleSheetPath,"aqua.qss"))
        self.app.setStyleSheet(qss)
        self.show()


    def run(self):
        '''
        Starts the main application window. Is blocking.
        '''
        self.app.exec_()


    def setUpPlotWidget(self):
        '''
        Creates a grid of data plots based on a variable number of inputs.
        Handles most thigns to do with the graphing parts of the UI.
        '''
        #Set default background and foreground colors for plots
        pg.setConfigOption('background', (40,40,40))
        pg.setConfigOption('foreground', (220,220,220))
        # Generate grid of plots
        plotLayout = QtGui.QGridLayout()
        coords = self.getPlotCoords()
        plotWidgets = [pg.PlotWidget() for i in range(len(self.sensors))]
        self.curves = []
        self.plots = []
        for i in range(len(self.sensors)):
            plot = plotWidgets[i]
            curve = pg.PlotCurveItem(pen=(i,len(self.sensors)))
            plot.addItem(curve)
            #Set X and Y data ranges if given use refresh priod for x if not.
            if self.yDataRanges != None:
                plot.setYRange(self.yDataRanges[i][0],self.yDataRanges[i][1],padding=0)
            if self.xDataRanges != None:
                plot.setXRange(self.xDataRanges[i][0],self.xDataRanges[i][1],padding=0)
            else:
                plot.setXRange(0,self.sensors[i].refreshPeriod/1000.0,padding=0)
            #Add axis lables to plots
            plot.setLabels(left=('Sensor units', self.sensors[i].sensorUnits))
            plot.setLabels(bottom=('Time', 's'))
            plot.setLabels(top=str(self.sensors[i].sensorName))
            plot.showGrid(x=True,y=True)
            self.plots.append(plot)
            self.curves.append(curve)
            #Arrange plots on grid.
            if len(self.sensors)%2 != 0 and i == (len(self.sensors) - 1):
                plotLayout.addWidget(plot,coords[i][0],coords[i][1],1,2)
            else:
                plotLayout.addWidget(plot,coords[i][0],coords[i][1])
        self.plotLayout = plotLayout

    def setUpUIWidgets(self):
        '''
        Creates all not grpahing UI elements and adds them to the applicatiom
        '''
        UILayout = QtGui.QVBoxLayout()
        #Creates checkboxes for choosing the channel to record
        self.checkWidgets = []
        for i in range(len(self.sensors)):
            checkWidget = QtGui.QCheckBox("Record {}".format(self.sensors[i].sensorName))
            checkWidget.setChecked(True)
            self.checkWidgets.append(checkWidget)

        #File selection for output button and label to display output path
        self.selectOutFileBtn = QtGui.QPushButton("Save plots")
        self.selectOutFileBtn.setToolTip("Choose the file to which recordings will be saved.")
        self.selectOutFileBtn.setIcon(self.style().standardIcon(QtGui.QStyle.SP_DialogSaveButton))
        self.selectOutFileBtn.setIconSize(QtCore.QSize(24,24))
        self.outputFileText = QtGui.QLabel("")
        self.outputFileText.setFrameShape(QtWidgets.QFrame.Panel)
        self.outputFileText.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.outputFileText.setWordWrap(True)

        #Recording button
        self.recordingButton = QtGui.QPushButton("Start recording")
        self.recordingButton.setToolTip("Start the recording. Only available once an output file has been selected")
        self.recordingButton.setIcon(self.style().standardIcon(QtGui.QStyle.SP_MediaPlay))
        self.recordingButton.setIconSize(QtCore.QSize(24,24))
        self.recordingButton.setMinimumHeight(50)
        self.recordingButton.setCheckable(True)
        self.recordingButton.setEnabled(False)

        #Recording duration selection labels and spin boxes
        self.hoursLabel = QtGui.QLabel("Hours:")
        self.hoursInput = QtGui.QSpinBox()
        self.hoursInput.setMaximum(10000)
        self.minutesLabel = QtGui.QLabel("Minutes:")
        self.minutesInput = QtGui.QSpinBox()
        self.minutesInput.setMaximum(59)
        self.secondsLabel = QtGui.QLabel("Seconds:")
        self.secondsInput = QtGui.QSpinBox()
        self.secondsInput.setMaximum(59)

        #LCD clock for displaying remaining time for recording
        self.timerLabel = QtGui.QLabel("Reording duration")
        self.recordingDurationDisplay = QtGui.QLCDNumber()
        self.recordingDurationDisplay.setDigitCount(11)
        self.recordingDurationDisplay.display("00:00:00:00")
        self.recordingDurationDisplay.setSegmentStyle(2)
        self.recordingDurationDisplay.setMinimumHeight(40);

        #Open file button for viewing saved data
        self.openFileButton = QtGui.QPushButton("Open plots")
        self.openFileButton.setToolTip("View the output of a previous recording in a new window.")
        self.openFileButton.setIcon(self.style().standardIcon(QtGui.QStyle.SP_DialogOpenButton))
        self.openFileButton.setIconSize(QtCore.QSize(24,24))

        #Callibration box set up.
        self.chooseSensorLabel = QtGui.QLabel("Choose sensor to callibrate")
        self.chooseSensorMenu = QtGui.QComboBox()
        for i in range(len(self.sensors)):
            if isinstance(self.sensors[i],StrainSensor):
                self.chooseSensorMenu.addItem(self.sensors[i].sensorName)
        self.callibrateButton = QtGui.QPushButton("Callibrate sensor")
        self.callibrateButton.setIcon(QtGui.QIcon(os.path.join(self.iconPath,"CallIcon.png")))
        self.callibrateButton.setIconSize(QtCore.QSize(24,24))
        self.loadCallibrationBtn = QtGui.QPushButton("Load Callibration")
        self.loadCallibrationBtn.setIcon(self.style().standardIcon(QtGui.QStyle.SP_DialogOpenButton))
        self.loadCallibrationBtn.setIconSize(QtCore.QSize(24,24))
        self.reConnectBtn = QtGui.QPushButton("Reconnect live plots")
        self.reConnectBtn.setToolTip("Resets the live plotting to the main window. Use this after callibration has been completed.")
        self.reConnectBtn.setIcon(self.style().standardIcon(QtGui.QStyle.SP_BrowserReload))
        self.reConnectBtn.setIconSize(QtCore.QSize(24,24))
        self.reConnectBtn.setEnabled(False)

        #Connects UI elements with event handling functions
        self.selectOutFileBtn.clicked.connect(self.onSelectFile)
        self.recordingButton.clicked.connect(self.onRecordingPress)
        self.openFileButton.clicked.connect(self.onLoadFilePress)
        self.hoursInput.valueChanged.connect(self.onDuratinChange)
        self.minutesInput.valueChanged.connect(self.onDuratinChange)
        self.secondsInput.valueChanged.connect(self.onDuratinChange)
        self.callibrateButton.clicked.connect(self.onCallibrationPress)
        self.loadCallibrationBtn.clicked.connect(self.onLoadCalPress)
        self.reConnectBtn.clicked.connect(self.onReconnectPress)

        #Organises widgets into group boxes to tidy the UI

        #File Input and output Box
        fileIBox = QtGui.QGroupBox("File I/O")
        fileILayout = QtGui.QVBoxLayout()
        fileILayout.addWidget(self.selectOutFileBtn)
        fileILayout.addWidget(self.outputFileText)
        fileILayout.addWidget(self.openFileButton)
        fileIBox.setLayout(fileILayout)
        UILayout.addWidget(fileIBox)

        #Channel selections box
        channelBox = QtGui.QGroupBox("Select channels")
        channelLayout = QtGui.QVBoxLayout()
        for widget in self.checkWidgets:
            channelLayout.addWidget(widget)
        channelBox.setLayout(channelLayout)
        UILayout.addWidget(channelBox)

        #Clock/timer box
        clockBox = QtGui.QGroupBox("Set recording duration")
        clockLayout = QtGui.QVBoxLayout()
        clockLayout.addWidget(self.hoursLabel)
        clockLayout.addWidget(self.hoursInput)
        clockLayout.addWidget(self.minutesLabel)
        clockLayout.addWidget(self.minutesInput)
        clockLayout.addWidget(self.secondsLabel)
        clockLayout.addWidget(self.secondsInput)
        clockLayout.addWidget(self.timerLabel)
        clockLayout.addWidget(self.recordingDurationDisplay)
        clockBox.setLayout(clockLayout)
        UILayout.addWidget(clockBox)

        #Add recording button by itself
        UILayout.addWidget(self.recordingButton)

        #User controlled alarms for unsafe values control box.
        self.alarmFunc = None
        self.alarms = []
        alarmBox = QtGui.QGroupBox("Alarm settings")
        alarmLayout = QtGui.QGridLayout()
        alarmLayout.addWidget(QtGui.QLabel("Alarm active"),0,0)
        alarmLayout.addWidget(QtGui.QLabel("Low alarm"),0,1)
        alarmLayout.addWidget(QtGui.QLabel("High alarm"),0,2)
        for i in range(len(self.sensors)):
            alarmActive = QtGui.QCheckBox(self.sensors[i].sensorName)
            alarmHigh = QtGui.QDoubleSpinBox()
            alarmLow = QtGui.QDoubleSpinBox()
            alarmHigh.setSizePolicy(QtGui.QSizePolicy.Minimum ,QtGui.QSizePolicy.Minimum)
            alarmLow.setSizePolicy(QtGui.QSizePolicy.Minimum ,QtGui.QSizePolicy.Minimum)
            alarmHigh.setMinimumSize(0,0)
            alarmLow.setMinimumSize(0,0)
            alarmHigh.setDecimals(3)
            alarmLow.setDecimals(3)
            alarmHigh.setMinimum(-1000)
            alarmHigh.setMaximum(1000)
            alarmLow.setMinimum(-1000)
            alarmLow.setMaximum(1000)
            self.alarms.append([alarmActive,alarmHigh,alarmLow])
            self.alarms[-1][0].clicked.connect(self.onAlarmActivationChange)
            alarmLayout.addWidget(alarmActive,i+1,0)
            alarmLayout.addWidget(alarmHigh,i+1,1)
            alarmLayout.addWidget(alarmLow,i+1,2)
            alarmBox.setLayout(alarmLayout)
        UILayout.addWidget(alarmBox)

        #Callibration control box. Only add if there are sensors of type strain
        calBox = QtGui.QGroupBox("Load Cell Callibration")
        calLayout = QtGui.QVBoxLayout()
        for i in range(len(self.sensors)):
            if isinstance(self.sensors[i],StrainSensor):
                calLayout.addWidget(self.chooseSensorLabel)
                calLayout.addWidget(self.chooseSensorMenu)
                calLayout.addWidget(self.callibrateButton)
                calLayout.addWidget(self.loadCallibrationBtn)
                calLayout.addWidget(self.reConnectBtn)
                calBox.setLayout(calLayout)
                UILayout.addWidget(calBox)
                break
        UILayout.addStretch(0)
        self.UILayout = UILayout

    def setUpMainWidget(self):
        '''
        Combines the UI widgets and the plot widgets to build the final application.
        '''
        self.setWindowTitle('Phidget ReadOuts')
        self.setWindowIcon(QtGui.QIcon(os.path.join(self.iconPath,"logo.png")))

        #Define relative layout of plotting area and UI widgets
        self.resize(1600,900)
        mainLayout = QtGui.QGridLayout()
        mainLayout.setColumnStretch(0,2)
        mainLayout.setColumnStretch(1,10)
        mainLayout.addLayout(self.plotLayout,0,1,2,10)

        # Adds all UI widgets to a vertical scroll area.
        scrollWidget = QtGui.QWidget()
        scrollWidget.setLayout(self.UILayout)
        scrollWidget.setSizePolicy(QtGui.QSizePolicy.Ignored,QtGui.QSizePolicy.Minimum)
        scroll = QtGui.QScrollArea()
        scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        scroll.setWidget(scrollWidget)
        scroll.setSizePolicy(QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        scroll.setMinimumSize(200,200)
        scroll.setWidgetResizable(True)
        vLayout = QtGui.QVBoxLayout()
        vLayout.addWidget(scroll)

        mainLayout.addLayout(vLayout,0,0)
        self.setLayout(mainLayout)

    def connectPlotUpdates(self):
        '''
        Defines the function for replotting graphs in real time and handling user set alarms.
        '''
        #def function to be called to update live plots
        def update():
            for i in range(len(self.sensors)):
                #Update plots and write to file if recording
                x, y, plotX, plotY = self.sensors[i].getData()
                self.curves[i].setData(plotX,plotY)
                self.writeDataToFile(x,y,self.sensors[i],self.checkWidgets[i])
                #Handle alarms
                alarm = self.alarms[i]
                if alarm[0].isChecked() and len(y) > 0:
                    if y[-1] <= alarm[1].value() or y[-1] >= alarm[2].value():
                        self.plots[i].setBackground((128,10,10))
                        if self.alarmFunc != None:
                            self.alarmFunc(self.alarmFuncArgs)
                        if self.alarmSound.isFinished():
                            self.alarmSound.play()
                    else:
                        pass#self.plots[i].setBackground((40,40,40))

        #Connect function to timer. Will trigger every timeout.
        self.replotTimer = QtCore.QTimer()
        self.replotTimer.timeout.connect(update)
        self.replotTimer.start(45)

    def loadSounds(self):
        '''
        Loads any sounds required for the applicaiton and store them as QSound objects.
        '''
        self.alarmSound = QSound(os.path.abspath(os.path.join(self.soundPath,"shortAlarm.wav")))

    def getPlotCoords(self):
        '''
        Converts the number of plots into a list of coordinates used to arrange them neatly.
        '''
        nPlots = len(self.sensors)
        if nPlots < 4:
            return [[i,0] for i in range(nPlots)]
        else:
            if nPlots%2 ==0:
                return [[i,j] for i in range(nPlots//2) for j in range(2)]
            else:
                nPlots += 1
                return [[i,j] for i in range(nPlots//2) for j in range(2)]

    def onSelectFile(self):
        '''
        Handles the seletion of an output file.
        '''
        fileName, filter = QtGui.QFileDialog.getSaveFileName(parent=self,
                caption='Select output file', filter='*.csv')
        if fileName != "":
            self.recordingButton.setEnabled(True)
            if not fileName.endswith(".csv"):
                fileName = fileName + ".csv"
            self.currentOutputFile = fileName
            self.outputFileText.setText(fileName)

    def onCallibrationPress(self):
        '''
        Opens the callibration UI for the chosen sensor.
        '''
        #Stops live plotting on main window while sensor is being callibrated
        for i in range(len(self.sensors)):
            if self.sensors[i].sensorName == str(self.chooseSensorMenu.currentText()):
                self.sensors[i].useCallibration = False
                self.CallibrationWindow = StrainCalibrator(self.sensors[i])
                fun = lambda: self.reConnectBtn.setEnabled(True)
                self.CallibrationWindow.destroyed.connect(fun)
                try:
                    self.replotTimer.disconnect()
                except TypeError:
                    pass

    def onRecordingPress(self):
        '''
        Sets up the logging of data to a file on recoding button press.
        '''
        if self.recordingButton.isChecked():
            try:
                self.currentOutputFile
            except AttributeError:
                self.currentOutputFile = None
            if self.currentOutputFile != None:
                #Changge button text and Icon
                self.recordingButton.setText("Stop recording")
                self.recordingButton.setIcon(self.style().standardIcon(QtGui.QStyle.SP_MediaStop))
                #Deal with timer and countdown
                secs = self.secondsInput.value()
                mins = self.minutesInput.value()
                hours = self.hoursInput.value()
                timeStamp = time.time()
                self.recordingStartTime = timeStamp
                #start timer tickng
                if secs+mins+hours != 0:
                    self.startTimer()
                #Set up filename and header
                timeStamp = datetime.datetime.fromtimestamp(timeStamp)
                timeStamp = timeStamp.strftime('%d-%m-%Y__%H-%M-%S')
                fileName = self.currentOutputFile.split(".")
                fileName = "{}__{}__.{}".format(fileName[0],timeStamp,fileName[1])
                fileName = os.path.abspath(fileName)
                self.file = open(fileName,"w+")
                self.insertHeader()
        else:
            self.recordingButton.setText("Start recording")
            self.recordingButton.setIcon(self.style().standardIcon(QtGui.QStyle.SP_MediaPlay))

    def onReconnectPress(self):
        '''
        Reconnects the plots on the main window to the sensors resuming live plotting
        in the main window
        '''
        self.connectPlotUpdates()
        self.reConnectBtn.setEnabled(False)

    def insertHeader(self):
        '''
        Adds column headings to start of output file has header.
        '''
        headerString = ("# Channel name (units)"
                " \t,\t Time (S) \t,\t Sensor value ()")
        self.file.write(headerString)

    def writeDataToFile(self,xs,ys,sensor,widget):
        '''
        Writes output from selected channels to chosen output file
        '''
        if self.recordingButton.isChecked():
            if widget.isChecked():
                for i in range(len(xs)):
                    self.file.write("{}\t,\t{}\t,\t{}\t\n".format(
                                sensor.sensorName,xs[i],ys[i]))

    def onLoadFilePress(self):
        '''
        Opens the chosen file using the Stored Data Plotter window. Allows for
        manual inspection of saved data while still moitoring live data.
        '''
        filePath, filter = QtGui.QFileDialog.getOpenFileName(self,
                'Open File', './    ',filter="*.csv")
        if filePath != "":
            self.SDPs.append(StoredDataPlotter(filePath))

    def onLoadCalPress(self):
        '''
        Loads a saved callibration to a chosen sensor. Updates live plots accordingly.
        '''
        filePath, filter = QtGui.QFileDialog.getOpenFileName(self,
                'Open File', './    ',filter="*.cal")
        try:
            if filePath != "":
                fileHandle = open(filePath)
                lines = fileHandle.readlines()
                if len(lines) <= 0:
                    raise ValueError('Empty file')
                for line in lines:
                    if not line.startswith("#"):
                        lineArray = line.rstrip().split(",")
                        gradient = float(lineArray[0].rstrip())
                        intercept = float(lineArray[1].rstrip())
                        for i in range(len(self.sensors)):
                            if self.sensors[i].sensorName == str(self.chooseSensorMenu.currentText()):
                                self.sensors[i].setCallibration(gradient,intercept)
                                break
        except Exception:
            self.msg = QtGui.QMessageBox()
            self.msg.setIcon(QtGui.QMessageBox.Warning)
            self.msg.setText("Uh Oh! ")
            self.msg.setInformativeText("Bad file or not correct format.")
            self.msg.setWindowTitle("Error")
            self.msg.show()

    def onDuratinChange(self):
        '''
        Updates countdown clock display as user changes time inputs.
        '''
        duration = datetime.timedelta(seconds=self.secondsInput.value(),
        minutes=self.minutesInput.value(), hours=self.hoursInput.value())
        self.recordingDurationDisplay.display(self.timeDeltaToString(duration))
        self.timerTime = duration

    def onAlarmActivationChange(self):
        '''
        Resets the plot background colors if an alarm is deactivated.
        '''
        for i in range(len(self.alarms)):
            if not self.alarms[i][0].isChecked():
                self.plots[i].setBackground((40,40,40))

    def startTimer(self):
        '''
        Sets up a timer and associated function for updating timer as it ticks
        down during recording.
        '''
        self.secondsInput.setEnabled(False)
        self.minutesInput.setEnabled(False)
        self.hoursInput.setEnabled(False)
        def onTimeout():
            dt = datetime.timedelta(seconds=time.time()-self.recordingStartTime)
            newTime = self.timerTime - dt
            if dt.seconds >= self.timerTime.seconds or not self.recordingButton.isChecked():
                self.durationTimer.disconnect()
                self.recordingButton.setChecked(False)
                self.secondsInput.setEnabled(True)
                self.minutesInput.setEnabled(True)
                self.hoursInput.setEnabled(True)
                self.recordingButton.setIcon(self.style().standardIcon(QtGui.QStyle.SP_MediaPlay))
                self.recordingButton.setText("Start recording")
            else:
                self.recordingDurationDisplay.display(self.timeDeltaToString(newTime))
        self.durationTimer = QtCore.QTimer()
        self.durationTimer.timeout.connect(onTimeout)
        self.durationTimer.start(100)

    def timeDeltaToString(self,timeDelta):
        '''
        Converts a difference in time in miliseconds to a formatted string displaying
        time in days:hours:minutes:seconds
        '''
        days = timeDelta.days
        hours =timeDelta.seconds // 3600
        minutes = timeDelta.seconds //60 % 60
        seconds = timeDelta.seconds - datetime.timedelta(days=days,hours=hours,minutes=minutes).seconds
        return "{:02d}:{:02d}:{:02d}:{:02d}".format(days,hours,minutes,seconds)

    def loadAlarmFunction(self, func,*args):
        '''
        Sets up a custom user function to be called when the user defined alarms
        are triggered. Takes the function as first argument and arguments of that
        function as following arguments
        '''
        self.alarmFunc = func
        self.alarmFuncArgs = args
