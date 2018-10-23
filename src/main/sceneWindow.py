import sys, os
from vispy import scene, app
from vispy.visuals.transforms import STTransform
from vispy.visuals.filters import Clipper, Alpha, ColorFilter
from vispy.util.quaternion import Quaternion

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import QWidget, QFormLayout, QMainWindow, QGroupBox, QVBoxLayout, QHBoxLayout, \
QLabel, QTextEdit, QLineEdit, QPushButton, QFrame, QGridLayout

from defaultMenuBar import DefaultMenuBar
from simulation import Simulation, FrameData
from errorWindow import ErrorWindow

from pathlib import Path
import numpy as np

from PIL import Image
import cv2
import time

import copy

ICON = Path(r'..\..\articles\atom.png')

class SceneWindow(QMainWindow):

    '''
    Windows for presenting Canvas in real time. Show only one view
    To be Implemented -- Stereo views
    '''
    pixmapChanged = QtCore.pyqtSignal(int)

    def __init__(self):

        super().__init__()

        '''Fields'''

        self.simLimit = None
        self.simulationNo = None
        self.elementCount = None
        self.simLength = 0
        self.simulation = None
        self.frameList = []

        self.timer = QtCore.QElapsedTimer()



        ''' Window Properties'''

        self.Icon = QtGui.QIcon(str(ICON))
        self.setMinimumSize(self.sizeHint())
        self.resize(1600, 800)
        self.setWindowTitle('Vispy 3D')
        self.setWindowIcon(self.Icon)
    
        self.setMenuBar(DefaultMenuBar(self))

        ''' Setting window layout and central widget '''
        self.centralwidget = QtWidgets.QWidget()
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setAlignment(QtCore.Qt.AlignCenter)


        ''' Frames'''
        self.canvasFrame = QGroupBox("Canvas Frame")
        self.controlFrame = QGroupBox("Control Frame")
        self.renderFrame = QGroupBox()

        self.canvasFrameLayout  = QVBoxLayout(self.canvasFrame)
        self.controlFrameLayout = QGridLayout(self.controlFrame)
        self.renderFrameLayout = QHBoxLayout()

        self.canvasWidget = QWidget()
        self.canvasWidget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.canvasWidgetLayout = QHBoxLayout()

        ''' Rendered Video of Scene'''
        self.canvasHolder = QWidget() #QtWidgets.QGraphicsView()#
        self.canvasHolder.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.canvasHolderLayout = QVBoxLayout()
        self.canvasHolder.setLayout(self.canvasHolderLayout)

        ''' 'Image' Video of scene'''
        self.twoVideoWidget = QWidget()
        self.twoVideoWidget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.twoVideoWidgetLayout = QVBoxLayout()
        


        self.video1Widget = QtWidgets.QGraphicsView()
        self.video2Widget = QtWidgets.QGraphicsView()

        self.twoVideoWidgetLayout.addWidget(self.video1Widget)
        self.twoVideoWidgetLayout.addWidget(self.video2Widget)
        
        self.twoVideoWidget.setLayout(self.twoVideoWidgetLayout)

        '''Simulation parameters'''
        self.elementCount = QLabel("Elements")
        self.elementCount.setMaximumSize(150,50)
        self.elementCountBox = QLineEdit()
        self.elementCountBox.setMaximumSize(350,50)
        self.elementCountBox.setPlaceholderText('element count')
        self.elementCountBox.setText('10')


        self.setFunctionLabel = QLabel("Set Function")
        self.setFunctionLabel.setMaximumSize(150,50)
        self.setFunctionBox = QLineEdit()
        self.setFunctionBox.setMaximumSize(350,50)
        self.setFunctionBox.setPlaceholderText("input Function in Cartesian Co-ordSinates")

        self.zoomLevel = QPushButton("Zoom")
        self.zoomLevel.setMaximumSize(150,50)
        self.zoomInput = QLineEdit()
        self.zoomLevel.clicked.connect(self.setZoom)
        self.zoomInput.setPlaceholderText('Adjust zoom for camera - default scale is 10.')
        self.zoomInput.setMaximumSize(350,50)

        self.simulationLengthLabel = QLabel('Simulation Length')
        self.simulationLengthLabel.setMaximumSize(150,50)
        self.simulationLengthBox = QLineEdit()
        self.simulationLengthBox.setMaximumSize(350,50)
        self.simulationLengthBox.setPlaceholderText('No. of Frames - default is 100')
        self.simulationLengthBox.setText('500')

        self.simulationsLabel = QLabel('Simulations')
        self.simulationsLabel.setMaximumSize(150, 50)
        self.simulationsBox = QLineEdit()
        self.simulationsBox.setMaximumSize(350,50)
        self.simulationsBox.setPlaceholderText('No. of simulations')

        ''' Render Button'''
        self.renderButton = QPushButton('Render')
        self.renderButton.clicked.connect(self.handleRender)
        self.renderButton.setMaximumSize(250,50)
        # self.renderButton.setAlignment(QtCore.Qt.AlignCenter)

        self.controlFrameLayout.addWidget(self.elementCount, 0, 0 )
        self.controlFrameLayout.addWidget(self.elementCountBox, 0, 1)

        self.controlFrameLayout.addWidget(self.zoomLevel, 0, 2)
        self.controlFrameLayout.addWidget(self.zoomInput, 0, 3)

        self.controlFrameLayout.addWidget(self.setFunctionLabel,0, 4)
        self.controlFrameLayout.addWidget(self.setFunctionBox,0, 5)
        self.controlFrameLayout.addWidget(self.simulationLengthLabel, 0, 6)
        self.controlFrameLayout.addWidget(self.simulationLengthBox, 0, 7)
        self.controlFrameLayout.addWidget(self.simulationsLabel, 0, 8)
        self.controlFrameLayout.addWidget(self.simulationsBox, 0, 9)

        self.renderFrameLayout.addWidget(self.renderButton)
        # self.controlFrameLayout.setAlignment(self.canvasWidget, QtCore.Qt.AlignCenter)
        # self.canvasFrameLayout.addWidget(self.canvasWidget)
        
        self.renderFrame.setLayout(self.renderFrameLayout)
        self.canvasWidget.setLayout(self.canvasWidgetLayout)
        self.canvasFrameLayout.addWidget(self.canvasWidget)
        
        # self.canvasFrame.setLayout(self.canvasFrameLayout)

        self.verticalLayout.addWidget(self.canvasFrame)
        self.verticalLayout.addWidget(self.controlFrame)
        self.verticalLayout.addWidget(self.renderFrame)

        self.setCentralWidget(self.centralwidget)

    def setZoom(self):

        zoomFactor = self.zoomInput.text()

        try:
            zoomFactor = int(zoomFactor)
            if zoomFactor > 100 or zoomFactor  == 0:
                self.error = ErrorWindow("element count can`t be greater than 100 or equal to 0", self.Icon)
                self.error.show()
                return

        except Exception as e:

            self.error = ErrorWindow("Element count has to be an Integer", self.Icon)
            self.error.show()
            return
        self.simulation.view.camera.scale_factor = zoomFactor

    def handleRender(self):

        n = self.elementCountBox.text()
        simulationLength = self.simulationLengthBox.text()
        simulations = self.simulationsBox.text()

        if simulationLength:

            try:
                simulationLength = int(simulationLength)
                self.simLimit = simulationLength
            except Exception as e:

                self.error = ErrorWindow("Simulation length has to be an Integer, default -- 100 has been used", self.Icon)
                self.error.show()

        else: self.simLimit = 100
        
        if simulations:

            try:
                simulations = int(simulations)
                self.simulationNo = simulations
            except Exception as e:
                self.error = ErrorWindow("No of simulations has to be an integer - only one simulation will be ran", self.Icon)
                self.error.show()

        else: self.simulationNo = 1
                
        try:

            n = int(n)
            if n > 100:
                self.error = ErrorWindow("element count can`t be greater than 100", self.Icon)
                self.error.show()

                return

            else: self.elementCount = n

        except Exception as e:

            print(e)

            self.error = ErrorWindow("Element count has to be an Integer", self.Icon)
            self.error.show()

            return

        self.create_simulation(self.elementCount, 1)




    def create_simulation(self, elementCount, sim_index):

        
        self.th = QtCore.QThread()

        self.simulation = Simulation(elementCount, sim_index)
        self.simulation.moveToThread(self.th)
        self.simulation.changePixmap.connect(self.update)
        self.pixmapChanged.connect(self.simulation.motionControl)

        self.th.start()

        self.simulation.canvas.create_native()
        self.native = self.simulation.canvas.native
        self.canvasHolderLayout.addWidget(self.native)

        # print(self.simulation.canvas.size)
        # self.canvasHolderLayout.addWidget(self.simulation.canvas.native)
        self.canvasWidgetLayout.addWidget(self.canvasHolder)
        self.canvasWidgetLayout.addWidget(self.twoVideoWidget)

    

        self.pixmapChanged.emit(100)



    def setImage(self):

        'Return camera to neutral x position after rendering the two images'

        self.simulation.view.camera.scale_factor = 10

        self.simulation.canvas.size = 800,600

        self.simulation.view.camera.elevation = 20
        self.simulation.view.camera.azimuth = 85
        
        imageArray = self.simulation.canvas.render()
        rgbImage = cv2.cvtColor(imageArray, cv2.COLOR_BGR2RGB)
        image = QtGui.QImage(rgbImage.data, imageArray.shape[1], imageArray.shape[0], QtGui.QImage.Format_RGB888)
        

        scene1 = QtWidgets.QGraphicsScene()
        pixmapItem = QtWidgets.QGraphicsPixmapItem(QtGui.QPixmap.fromImage(image))
        scene1.addItem(pixmapItem)


        self.simulation.view.camera.elevation = 20
        self.simulation.view.camera.azimuth = 95

        imageArray = self.simulation.canvas.render()
        rgbImage = cv2.cvtColor(imageArray, cv2.COLOR_BGR2RGB)
        image = QtGui.QImage(rgbImage.data, imageArray.shape[1], imageArray.shape[0], QtGui.QImage.Format_RGB888)
        

        scene2 = QtWidgets.QGraphicsScene()
        pixmapItem = QtWidgets.QGraphicsPixmapItem(QtGui.QPixmap.fromImage(image))
        scene2.addItem(pixmapItem)

        self.video1Widget.setScene(scene1)
        self.video2Widget.setScene(scene2)

        'Return camera to neutral x position after rendering the two images'
        self.simulation.view.camera.elevation = 20
        self.simulation.view.camera.azimuth = 90

        self.simulation.canvas.render()
    
        np.set_printoptions(threshold=np.inf)

        self.simulation.frameList.append(FrameData(self.simulation.canvas.render(), self.simulation.elementList, self.simulation.view.camera.scale_factor, (800, 600), len(self.frameList)+1))
 

    def update(self):
        
        self.simLength += 1
        self.timer.start()
        self.setImage()
        dt = self.timer.elapsed()
        self.timer.restart()

        self.pixmapChanged.emit(dt)

        if self.simLength == self.simLimit:

            self.pixmapChanged.disconnect()
            self.simulation.changePixmap.disconnect()

            currSim = self.simulation.index
            self.writeData()

            if currSim < self.simulationNo: 

                self.th.exit()
                while not self.th.isFinished(): time.sleep(0.5)

                self.simLength = 0  
                self.canvasHolderLayout.removeWidget(self.native)
                self.create_simulation(self.elementCount, currSim + 1)
            
            else: self.close()

    def writeData(self):
        
        index = 0
        
        if not Path(r'..\..\logs\simulations\originalImages\simulation_{0}'.format(self.simulation.index)).is_dir(): os.makedirs(r'..\..\logs\simulations\originalImages\simulation_{0}'.format(self.simulation.index))
        if not Path(r'..\..\logs\simulations\velocityImages\simulation_{0}'.format(self.simulation.index)).is_dir(): os.makedirs(r'..\..\logs\simulations\velocityImages\simulation_{0}'.format(self.simulation.index))
        if not Path(r'..\..\logs\simulations\depthMatrix\simulation_{0}'.format(self.simulation.index)).is_dir(): os.makedirs(r'..\..\logs\simulations\depthMatrix\simulation_{0}'.format(self.simulation.index))
        

        for frameData in self.simulation.frameList:

            frameData.createMatrix()
            frameData.createMatrix(event='depth')

            filenameO = r'..\..\logs\simulations\originalImages\simulation_{0}\frame{1}.jpg'.format(self.simulation.index, index)
            filenameV = r'..\..\logs\simulations\velocityImages\simulation_{0}\frame{1}.jpg'.format(self.simulation.index, index)
            filenameD = r'..\..\logs\simulations\depthMatrix\simulation_{0}\frame{1}.jpg'.format(self.simulation.index, index)
            cv2.imwrite(filenameO, frameData.imageArray)
            cv2.imwrite(filenameV, frameData.velocityMatrix)
            cv2.imwrite(filenameD, frameData.depthMatrix)

            index  += 1

        



