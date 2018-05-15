import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
import numpy as np
import os

class StoredDataPlotter(QtGui.QMainWindow):
    '''
    Class defines and controls UI for user viewing of saved data files.
    '''

    def __init__(self,filePath,parent=None):
        ''' Class constructor. Takes path to data file as main argument '''
        QtGui.QMainWindow.__init__(self,parent)
        self.iconPath = os.path.join(os.path.abspath(os.path.dirname(__file__)),"UI_Icons")
        self.setWindowIcon(QtGui.QIcon(os.path.join(self.iconPath,"dataPlotterLogo.png")))
        self.filePath = filePath
        self.generateDataPlotterUI()

    def generateDataPlotterUI(self):
        '''
        Constructs the plotting and UI elements and brings them together into
        a single widget
        '''
        #Attempt to read data from file.
        try:
            self.dataLabels,self.xDatas,self.yDatas=self.getDataFromFile()
        except Exception:
            #Display error dialouge if problem encountered reading data from file
            self.msg = QtGui.QMessageBox()
            self.msg.setIcon(QtGui.QMessageBox.Warning)
            self.msg.setText("Uh Oh! ")
            self.msg.setInformativeText("Bad file or not correct format.")
            self.msg.setWindowTitle("Error")
            self.msg.show()
            return

        self.mainWidget = QtGui.QWidget()
        self.mainLayout = QtGui.QGridLayout()
        #If file read succesfully and  is not empty
        if len(self.dataLabels) > 0:
            #Set up plotting elements
            self.constructPlottingWidget()
            self.setUpCrossHairs()
            self.constructUIWidgets()

            #Add layouts together
            self.mainLayout.addWidget(self.plotWidget,0,1,10,10)
            self.mainLayout.addLayout(self.UILayout,0,0)

            #Set  final layout
            self.mainWidget.setLayout(self.mainLayout)
            self.showPlotterUI()
        else:
            #Display error dialouge if file was empty
            self.msg = QtGui.QMessageBox()
            self.msg.setIcon(QtGui.QMessageBox.Warning)
            self.msg.setText("Uh Oh! ")
            self.msg.setInformativeText("It looks liks that file was empty.")
            self.msg.setWindowTitle("Error")
            self.msg.show()

    def constructPlottingWidget(self):
        '''
        Sets up both plotting views for the data viewer.
        '''
        #Plot widget
        self.plotWidget = QtGui.QWidget()
        self.topPlot = pg.PlotWidget()
        self.plotLayout = QtGui.QGridLayout()
        self.bottomPlot = pg.PlotWidget()
        self.legend = self.topPlot.addLegend()
        for i in range(len(self.dataLabels)):
            self.topPlot.plot(self.xDatas[i],self.yDatas[i],
                    pen=(i,len(self.dataLabels)),name=self.dataLabels[i])
            self.bottomPlot.plot(self.xDatas[i],self.yDatas[i],
                    pen=(i,len(self.dataLabels)),name=self.dataLabels[i])
        self.bottomPlot.showGrid(x=True,y=True)
        #Set up highlighted reigon on top plot for zooming in on bottom plot
        self.hReigon = pg.LinearRegionItem([max(max(self.xDatas))*0.25,max(max(self.xDatas))*0.75])
        self.hReigon.setBounds([0,max(max(self.xDatas))])
        self.hReigon.sigRegionChanged.connect(self.onHReigonMove)

        #Add widgets for x,y values
        self.topPlot.addItem(self.hReigon)
        self.topPlot.setLabels(left=('Sensor units'))
        self.topPlot.setLabels(bottom=('Time (S)'))
        self.topPlot.setLabels(top=('Plot from: {}'.format(self.filePath)))
        self.plotLayout.addWidget(self.topPlot,0,0,1,2)
        self.plotLayout.addWidget(self.bottomPlot,2,0,1,2)
        self.plotWidget.setLayout(self.plotLayout)

    def constructUIWidgets(self):
        '''
        Sets up all UI elements for the data plotter
        '''
        UIWidget = QtGui.QWidget()
        self.UILayout = QtGui.QVBoxLayout()
        #Checkbox widgets for graph
        self.checkWidgets = []
        for i in range(len(self.dataLabels)):
            self.checkWidgets.append(QtGui.QCheckBox(self.dataLabels[i]))
            self.checkWidgets[-1].setChecked(True)

        #Button to average highlighted reigon
        self.getAverageButton = QtGui.QPushButton("Average")
        self.getAverageButton.setIcon(QtGui.QIcon(os.path.join(self.iconPath,"Average.png")))
        self.getAverageButton.setIconSize(QtCore.QSize(24,24))

        #Label to display results of averaging
        self.averageResult = QtGui.QLabel("Average Value:\n {0:1.3E}".format(0.0))
        self.averageResult.setFrameShape(QtWidgets.QFrame.Panel)
        self.averageResult.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.averageResult.setWordWrap(True)

        #Check box for toggling showing points on lower graph
        self.showPointsToggle = QtGui.QCheckBox("Show Points?")
        self.showPointsToggle.clicked.connect(self.onCheckBoxPress)

        #Check box for toggling snap to points
        self.snapToPointsToggle = QtGui.QCheckBox("Snap to points?")
        self.saveSelectedRegionBtn = QtGui.QPushButton("Save selection")
        self.saveSelectedRegionBtn.setIcon(self.style().standardIcon(QtGui.QStyle.SP_DialogSaveButton))
        self.saveSelectedRegionBtn.setIconSize(QtCore.QSize(24,24))

        #Add widgets to UI layout and connect their funtions

        #Add channel selection box layout to UI
        channelBox = QtGui.QGroupBox("Channel selection")
        channelLayout = QtGui.QVBoxLayout()
        for i in range(len(self.checkWidgets)):
            self.checkWidgets[i].clicked.connect(self.onCheckBoxPress)
            channelLayout.addWidget(self.checkWidgets[i])
        channelBox.setLayout(channelLayout)
        self.UILayout.addWidget(channelBox)

        #Add plot options box to UI
        optionsBox = QtGui.QGroupBox("Plot options")
        optionsLayout = QtGui.QVBoxLayout()
        optionsLayout.addWidget(self.showPointsToggle)
        optionsLayout.addWidget(self.snapToPointsToggle)
        optionsLayout.addWidget(self.saveSelectedRegionBtn)
        optionsBox.setLayout(optionsLayout)
        self.UILayout.addWidget(optionsBox)

        #Add average button and output to UI
        averageBox = QtGui.QGroupBox("Average selection")
        averageLayout = QtGui.QVBoxLayout()
        self.getAverageButton.clicked.connect(self.onAverageButtonPress)
        self.saveSelectedRegionBtn.clicked.connect(self.onSaveSelectedRegionPress)
        averageLayout.addWidget(self.getAverageButton)
        averageLayout.addWidget(self.averageResult)
        averageBox.setLayout(averageLayout)
        self.UILayout.addWidget(averageBox)

        #Define and add mouse coordinates labels to UI
        self.coordsBox = QtGui.QGroupBox("Mouse Coordinates")
        self.coordsLayout = QtGui.QVBoxLayout()
        self.xValueLabel = QtGui.QLabel("x = ???")
        self.yValueLabel = QtGui.QLabel("y= ???")
        self.coordsLayout.addWidget(self.xValueLabel)
        self.coordsLayout.addWidget(self.yValueLabel)
        self.coordsBox.setLayout(self.coordsLayout)
        self.UILayout.addWidget(self.coordsBox)
        self.UIWidget = UIWidget

    def showPlotterUI(self):
        '''
        Show the window contaiing the data plotter.
        '''
        self.setWindowTitle("Phidget Stroed Data Plotter")
        self.resize(800,600)
        self.setCentralWidget(self.mainWidget)
        self.show()

    def onCheckBoxPress(self):
        '''
        Redraws the plots when different data channels are selected
        '''
        self.topPlot.clear()
        self.bottomPlot.clear()
        for i in range(len(self.dataLabels)):
            self.legend.removeItem(self.dataLabels[i])
        for i in range(len(self.checkWidgets)):
            if self.checkWidgets[i].isChecked():
                self.topPlot.plot(self.xDatas[i],self.yDatas[i],
                        pen=(i,len(self.dataLabels)),name=self.dataLabels[i])
                if self.showPointsToggle.isChecked():
                    self.bottomPlot.plot(self.xDatas[i],self.yDatas[i],
                    symbols='o',symbolSize=3,pen=(i,len(self.dataLabels)),
                    name=self.dataLabels[i])
                else:
                    self.bottomPlot.plot(self.xDatas[i],self.yDatas[i],
                    pen=(i,len(self.dataLabels)),name=self.dataLabels[i])
        self.topPlot.addItem(self.hReigon)
        self.bottomPlot.addItem(self.vLine)
        self.bottomPlot.addItem(self.hLine)

    def onHReigonMove(self):
        '''
        Updates view on the bottom plot when the user moves highlighted reigon
        on the top plot
        '''
        x1,x2 = self.hReigon.getRegion()
        self.bottomPlot.setXRange(x1,x2,padding=0)

    def onAverageButtonPress(self):
        '''
        Average data in highlighted reigon and display result to user
        '''
        for i in range(len(self.checkWidgets)):
            if self.checkWidgets[i].isChecked():
                yData = np.asarray(self.yDatas[i])
                xData = np.asarray(self.xDatas[i])
                minX,maxX = self.hReigon.getRegion()
                average = np.mean(yData[np.where((xData>minX) & (xData < maxX))])
                self.averageResult.setText("Average Value:\n {0:1.3E}".format(average))
                break

    def onSaveSelectedRegionPress(self):
        '''
        Brings up dialoug to allow the user to save data in the highlighted reigon
        to a new file by itself.
        '''
        fileName, filter = QtGui.QFileDialog.getSaveFileName(parent=self,
                caption='Select output file', filter='*.csv')
        if fileName != "":
            fileHandle = open(fileName,"w+")
            x1,x2 = self.hReigon.getRegion()
            for k,widget in enumerate(self.checkWidgets):
                if widget.isChecked():
                    for i in range(len(self.xDatas[k])):
                        if self.xDatas[k][i] >= x1 and self.xDatas[k][i] <= x2:
                            fileHandle.write("{}\t,\t{}\t,\t{}\t\n".format(
                            self.dataLabels[k],self.xDatas[k][i],self.yDatas[k][i]))

    def setUpCrossHairs(self):
        '''
        Draws cross hairs to the bottom plot. And sets up events to redraw them
        whenever the mouse is moved.
        '''
        self.vLine = pg.InfiniteLine(angle=90,movable=False)
        self.hLine = pg.InfiniteLine(angle=0,movable=False)
        self.bottomPlot.addItem(self.vLine,ignoreBounds=True)
        self.bottomPlot.addItem(self.hLine,ignoreBounds=True)

        def mouseMoved(event):
            '''
            Update the mouse coordinate labels when the mouse is moved. Handles snaping
            to point functionallity also.
            '''
            index = None
            position = event[0]
            if self.bottomPlot.sceneBoundingRect().contains(position):
                mousePoint = self.bottomPlot.plotItem.vb.mapSceneToView(position)

                for i in range(len(self.checkWidgets)):
                    if self.snapToPointsToggle.isChecked():
                        if self.checkWidgets[i].isChecked():
                            index = np.abs(np.asarray(self.xDatas[i])-mousePoint.x()).argmin()
                            self.vLine.setPos(self.xDatas[i][index])
                            self.hLine.setPos(self.yDatas[i][index])
                            self.xValueLabel.setText("x = {0:1.4E}".format(self.xDatas[i][index]))
                            self.yValueLabel.setText("y = {0:1.4E}".format(self.yDatas[i][index]))
                            break
                    if index == None:
                        self.vLine.setPos(mousePoint.x())
                        self.hLine.setPos(mousePoint.y())
                        self.xValueLabel.setText("x = {0:1.4E}".format(mousePoint.x()))
                        self.yValueLabel.setText("y = {0:1.4E}".format(mousePoint.y()))
        self.proxy = pg.SignalProxy(self.bottomPlot.scene().sigMouseMoved,rateLimit=30,slot=mouseMoved)

    def getDataFromFile(self):
        '''
        Read data from CSV file and store it in lists for plotting
        '''
        nameArray = []
        timeArray = []
        dataArray = []
        dataFile = open(self.filePath)
        for line in dataFile:
            if not line.startswith("#"):
                strippedLine = line.rstrip().split("\t,\t")
                nameArray.append((strippedLine[0]))
                timeArray.append(float(strippedLine[1]))
                dataArray.append(float(strippedLine[2]))

        sensorNames = list(set(nameArray))
        xs = []
        ys = []
        for i in range(len(sensorNames)):
            xs.append([])
            ys.append([])
            for j in range(len(timeArray)):
                if sensorNames[i] == nameArray[j]:
                    xs[i].append(timeArray[j])
                    ys[i].append(dataArray[j])

        for i in range(len(sensorNames)):
            start = xs[i][0]
            for j in range(len(xs[i])):
                xs[i][j] = xs[i][j]-start

        return sensorNames, xs,ys
