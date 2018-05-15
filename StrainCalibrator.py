import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
import time, datetime
import numpy as np
import os
np.seterr(all='raise')

class StrainCalibrator(QtGui.QMainWindow):
    '''
    UI for the callibration of phidget strain sensors.
    '''

    def __init__(self,sensor,parent=None):
        '''
        Constructor for callibration app. Takes sensor to be callibrated as
        an argument.
        '''
        self.iconPath = self.iconPath = os.path.join(os.path.abspath(os.path.dirname(__file__)),"UI_Icons")
        self.ownXData = [ ]
        self.ownYData = [ ]
        QtGui.QMainWindow.__init__(self,parent)
        self.setWindowIcon(QtGui.QIcon(os.path.join(self.iconPath,"strainLogo.png")))
        self.sensor = sensor
        self.masses = []
        self.voltages = []
        self.currentMean = 0
        self.gradient = 0
        self.intercept = 0
        self.generateDataPlotterUI()

    def generateDataPlotterUI(self):
        '''
        Constructs and combines the plottng and UI elements of the aplication
        '''
        self.mainWidget = QtGui.QWidget()
        self.mainLayout = QtGui.QGridLayout()
        self.constructPlottingWidget()
        self.constructUIWidgets()
        #Add layouts together
        self.mainLayout.addWidget(self.plotWidget,0,1,10,10)
        self.mainLayout.addLayout(self.UILayout,0,0)
        #Set  final layout
        self.mainWidget.setLayout(self.mainLayout)
        self.showPlotterUI()

    def constructPlottingWidget(self):
        '''
        Defines the plotting areas used for callibration
        '''
        #definewidget and layout
        self.plotWidget = QtGui.QWidget()
        self.plotLayout = QtGui.QGridLayout()

        #define plotting widgets
        self.topPlot = pg.PlotWidget()
        self.topPlot.setXRange(0,self.sensor.refreshPeriod/1000.0)
        self.bottomPlot = pg.PlotWidget()

        #Add curve to top plot
        self.topCurve = pg.PlotCurveItem(pen=(90,200,255))
        self.topPlot.addItem(self.topCurve)

        #Add lables
        self.bottomPlot.setLabels(bottom="Voltage V/V")
        self.bottomPlot.setLabels(left = "Mass (Kg)")
        self.topPlot.setLabels(bottom="time(s)")
        self.topPlot.setLabels(left="voltage (V/V)")

        #Set up highlighted reigon on top plot
        self.hReigon = pg.LinearRegionItem([5,10],movable=False)
        self.topPlot.addItem(self.hReigon)

        #Set up live ploting on top graph
        self.livePlotTimer = QtCore.QTimer()
        self.livePlotTimer.timeout.connect(self.onUpdate)
        self.livePlotTimer.start(45)

        #Add widgets to window
        self.plotLayout.addWidget(self.topPlot,0,0)
        self.plotLayout.addWidget(self.bottomPlot,1,0)

        #Add layout to widget
        self.plotWidget.setLayout(self.plotLayout)

    def constructUIWidgets(self):
        '''
        Defines and constructs all UI elements for the callibration UI
        '''
        #Define layout
        self.UILayout = QtGui.QVBoxLayout()

        #Define UI for selecting mass
        self.massLabel = QtGui.QLabel("Enter Mass (Kg)")
        self.massSpinBox = QtGui.QDoubleSpinBox()
        self.massSpinBox.setDecimals(4)

        #Add buttons for adding points to table
        self.addPointButton = QtGui.QPushButton("Add point")
        self.addPointButton.setIcon(QtGui.QIcon(os.path.join(self.iconPath,"AddPoint.png")))
        self.addPointButton.setIconSize(QtCore.QSize(24,24))

        #Add button for removing last point from table
        self.removePointButton = QtGui.QPushButton("Remove point")
        self.removePointButton.setIcon(QtGui.QIcon(os.path.join(self.iconPath,"RemovePoint.png")))
        self.removePointButton.setIconSize(QtCore.QSize(24,24))
        self.averageLabel = QtGui.QLabel("Current average:")
        self.averageLabel.setToolTip("Average of data in highlighted reigon on top left plot.")

        #Add table to store data points
        self.dataTable = QtGui.QTableWidget()
        self.dataTable.setRowCount(10)
        self.dataTable.setColumnCount(2)
        self.dataTable.setHorizontalHeaderLabels(["Mass (Kg)","Voltage (V/V)"])
        self.dataTable.setSizePolicy(QtGui.QSizePolicy.Fixed,QtGui.QSizePolicy.Fixed)
        self.dataTable.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)

        #Add labels for calculated gradient and intercept
        self.gradientLabel = QtGui.QLabel("Gradient: ")
        self.interceptLabel = QtGui.QLabel("Intercept: ")

        #Save callibration
        self.saveCalBtn = QtGui.QPushButton("Save Callibration")
        self.saveCalBtn.setIcon(self.style().standardIcon(QtGui.QStyle.SP_DialogSaveButton))
        self.saveCalBtn.setIconSize(QtCore.QSize(24,24))

        #connect widgets
        self.addPointButton.clicked.connect(self.onAddPointPress)
        self.removePointButton.clicked.connect(self.onRemovePointPress)
        self.saveCalBtn.clicked.connect(self.onSaveCalPress)
        self.dataTable.cellChanged.connect(self.onTableEdit)

        #Add widgets to layout

        #groub boxes for data entry
        dataEntryBox = QtGui.QGroupBox("Data entry")
        dataEntryLayout = QtGui.QVBoxLayout()
        dataEntryLayout.addWidget(self.massLabel)
        dataEntryLayout.addWidget(self.massSpinBox)
        dataEntryLayout.addWidget(self.addPointButton)
        dataEntryLayout.addWidget(self.removePointButton)
        dataEntryLayout.addWidget(self.averageLabel)
        dataEntryBox.setLayout(dataEntryLayout)
        self.UILayout.addWidget(dataEntryBox)
        self.UILayout.addWidget(self.dataTable)

        #Group box for displaying computed gradient and intercepy
        outputDataBox = QtGui.QGroupBox("Ouput values")
        outputDataLayout = QtGui.QVBoxLayout()
        outputDataLayout.addWidget(self.gradientLabel)
        outputDataLayout.addWidget(self.interceptLabel)
        outputDataBox.setLayout(outputDataLayout)
        self.UILayout.addWidget(outputDataBox)

        self.UILayout.addWidget(self.saveCalBtn)

    def showPlotterUI(self):
        '''
        Shows the callibration window and sets title and size of window
        '''
        self.setWindowTitle("Strain sensor callibration")
        self.resize(800,600)
        self.setCentralWidget(self.mainWidget)
        self.show()

    def onUpdate(self):
        '''
        Defines the function used to update the live plot necessary for callibration
        '''
        x, y, plotX, plotY = self.sensor.getData()
        for i in range(len(x)):
            if len(self.ownXData) > 0:
                if (x[i] - self.ownXData[0]) >= self.sensor.refreshPeriod/1000:
                    self.ownXData.pop(0)
                    self.ownYData.pop(0)
            self.ownXData.append(x[i])
            self.ownYData.append(y[i])
        actualPlotXData = np.asarray(self.ownXData)-self.ownXData[0]
        actualPlotYData = np.asarray(self.ownYData)
        self.topCurve.setData(actualPlotXData,actualPlotYData)

        #Average area in highlighted reigon
        minX,maxX = self.hReigon.getRegion()
        if actualPlotXData[-1] >= minX:
            self.currentMean = np.mean(actualPlotYData[np.where((actualPlotXData>minX) & (actualPlotXData < maxX))])
            self.averageLabel.setText("Avrage value: {0:1.4E}".format(self.currentMean))

    def onAddPointPress(self):
        '''
        Adds data point to the table. Data ponts are made from user set x value
        and y value obtained from average of highlighted reigon on live plot.
        '''
        self.dataTable.disconnect()
        mass = self.massSpinBox.value()
        voltage = self.currentMean
        self.masses.append(mass)
        self.voltages.append(voltage)
        self.writeToTable()
        self.replotCallCurve()
        self.dataTable.cellChanged.connect(self.onTableEdit)

    def onRemovePointPress(self):
        '''
        Removes the latest point from the table
        '''
        if len(self.masses)>0:
            self.dataTable.disconnect()
            self.dataTable.clearContents()
            self.masses.pop()
            self.voltages.pop()
            self.writeToTable()
            self.replotCallCurve()
            self.dataTable.cellChanged.connect(self.onTableEdit)

    def onTableEdit(self):
        '''
        Resets the callibration curve and table if user edits table entries
        '''
        self.masses = []
        self.voltages = []
        nRows = self.dataTable.rowCount()
        for row in range(nRows):
                mass = self.dataTable.item(row,0)
                volts = self.dataTable.item(row,1)
                if mass != None and volts != None:
                    self.masses.append(float(mass.text()))
                    self.voltages.append(float(volts.text()))
        if len(self.masses) >1:
            self.replotCallCurve()

    def writeToTable(self):
        '''
        Writes stored values to table
        '''
        for i in range(len(self.masses)):
            self.dataTable.setItem(i,0, QtGui.QTableWidgetItem(str(self.masses[i])))
            self.dataTable.setItem(i,1, QtGui.QTableWidgetItem(str(self.voltages[i])))

    def replotCallCurve(self):
        '''
        Replots the callibration curve using data from the table
        '''
        self.bottomPlot.clear()
        self.bottomPlot.plot(self.voltages,self.masses,pen=None ,symbols='o',symbolSize=10)
        #Fit best line through points
        if len(self.masses) > 1:
            try:
                p = np.polyfit(self.voltages,self.masses,1)
                self.gradient = p[0]
                self.intercept = p[1]
                x = np.linspace(min(self.voltages),max(self.voltages),100)
                y = self.gradient*x + self.intercept
                self.bottomPlot.plot(x,y,pen=(90,200,255))
                self.gradientLabel.setText("Gradient: {0:1.4E}".format(self.gradient))
                self.interceptLabel.setText("Intercept: {0:1.4E}".format(self.intercept))
            except Exception:
                pass

    def onSaveCalPress(self):
        '''
        Saves the calculated gradient and interept to a plain text .cal file
        '''
        fileName, filter = QtGui.QFileDialog.getSaveFileName(parent=self,
                caption='Select output file', filter='*.cal')
        if fileName != "":
            fileHandle = open(fileName,"w+")
            fileHandle.write("#Callibration data for strain sensor\n")
            timeStamp = time.time()
            timeStamp = datetime.datetime.fromtimestamp(timeStamp)
            timeStamp = timeStamp.strftime('%d/%m/%Y__%H:%M:%S')
            fileHandle.write("#Callibration performed on {}\n".format(timeStamp))
            fileHandle.write("#Callibration in form mass(Kg) = gradient*voltage(v/v) + intercept\n")
            fileHandle.write("#Data listed: gradient,intercept\n")
            fileHandle.write("{} , {}".format(self.gradient,self.intercept))

    def closeEvent(self,event):
        '''
        Overrides the defualt event which triggers on window close
        '''
        self.deleteLater()
        event.accept()
