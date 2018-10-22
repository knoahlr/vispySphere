import sys
from vispy import scene, app
from vispy.visuals.transforms import STTransform
from vispy.visuals.filters import Clipper, Alpha, ColorFilter
from vispy.util.quaternion import Quaternion

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import QWidget, QFormLayout, QMainWindow, QGroupBox, QVBoxLayout, QHBoxLayout, \
QLabel, QTextEdit, QLineEdit, QPushButton, QFrame

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

        self.simLimit = 100
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

        self.canvasFrameLayout  = QVBoxLayout(self.canvasFrame)
        self.controlFrameLayout = QFormLayout(self.controlFrame)
        # print(dir(self.controlFrameLayout.formAlignment()))
        self.controlFrameLayout.setFormAlignment(QtCore.Qt.AlignCenter)
        self.controlFrameLayout.setFormAlignment(QtCore.Qt.AlignTop)
        

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

        '''Labels'''
        self.elementCount = QLabel("Elements")
        self.elementCountBox = QLineEdit()
        self.elementCountBox.setMaximumSize(250,50)
        self.elementCountBox.setPlaceholderText('element count')
        self.elementCountBox.setText('10')


        self.setFunctionLabel = QLabel("Set Function")
        self.setFunctionBox = QLineEdit()
        self.setFunctionBox.setMaximumSize(250,50)
        self.setFunctionBox.setPlaceholderText("input Function in Cartesian Co-ordSinates")

        self.zoomLevel = QPushButton("Zoom")
        self.zoomInput = QLineEdit()
        self.zoomLevel.clicked.connect(self.setZoom)
        self.zoomInput.setPlaceholderText('Adjust zoom for camera')
        self.zoomLevel.setMaximumSize(250,50)
        self.zoomInput.setMaximumSize(250,50)


        self.renderButton = QPushButton('Render')
        self.renderButton.clicked.connect(self.handleRender)
        self.renderButton.setMaximumSize(250,50)
        # self.renderButton.setAlignment(QtCore.Qt.AlignCenter)

        self.controlFrameLayout.setWidget(0, QFormLayout.LabelRole, self.elementCount)
        self.controlFrameLayout.setWidget(0, QFormLayout.FieldRole, self.elementCountBox)

        self.controlFrameLayout.setWidget(1, QFormLayout.LabelRole, self.zoomLevel)
        self.controlFrameLayout.setWidget(1, QFormLayout.FieldRole, self.zoomInput)

        self.controlFrameLayout.setWidget(2, QFormLayout.LabelRole, self.setFunctionLabel)
        self.controlFrameLayout.setWidget(2, QFormLayout.FieldRole, self.setFunctionBox)

        self.controlFrameLayout.addWidget(self.renderButton)
        # self.canvasFrameLayout.addWidget(self.canvasWidget)
        
        self.canvasWidget.setLayout(self.canvasWidgetLayout)
        self.canvasFrameLayout.addWidget(self.canvasWidget)
        # self.canvasFrame.setLayout(self.canvasFrameLayout)

        self.verticalLayout.addWidget(self.canvasFrame)
        self.verticalLayout.addWidget(self.controlFrame)

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

        try:
            n = int(n)
            if n > 100:
                self.error = ErrorWindow("element count can`t be greater than 100", self.Icon)
                self.error.show()

                return

            

        except Exception as e:

            print(e)

            self.error = ErrorWindow("Element count has to be an Integer", self.Icon)
            self.error.show()

            return
        self.addCanvas(n)



    def addCanvas(self, elementCount):

        
        self.th = QtCore.QThread()

        self.simulation = Simulation(elementCount)
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

        # self.canvasHolder.setScene(mainScene)
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

        if self.simLength == self.simLimit:
            self.pixmapChanged.disconnect()
            self.simulation.changePixmap.disconnect()

            self.writeData()


        self.pixmapChanged.emit(dt)

    def writeData(self):
        
        index = 0

        for frameData in self.simulation.frameList:

            frameData.createMatrix()

            print(frameData.imageArray.shape, frameData.velocityMatrix.shape)

            filenameO = r'..\..\logs\originalImages\frame{0}.jpg'.format(index)
            filenameV = r'..\..\logs\velocityImages\frame{0}.jpg'.format(index)
            cv2.imwrite(filenameO, frameData.imageArray)
            cv2.imwrite(filenameV, frameData.velocityMatrix)

            index  += 1

        self.close()



