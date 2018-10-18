import sys
from vispy import scene, app
from vispy.visuals.transforms import STTransform
from vispy.visuals.filters import Clipper, Alpha, ColorFilter

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import QWidget, QFormLayout, QMainWindow, QGroupBox, QVBoxLayout, QHBoxLayout, \
QLabel, QTextEdit, QLineEdit, QPushButton, QFrame

from defaultMenuBar import DefaultMenuBar

from pathlib import Path
import numpy as np


ICON = Path(r'..\articles\atom.png')

DATA = r"..\data"

class SceneWindow(QMainWindow):

    '''
    Windows for presenting Canvas in real time. Show only one view
    To be Implemented -- Stereo views
    '''


    def __init__(self):

        super().__init__()

        '''Fields'''

        self.rangeIndex = 0



        ''' Window Properties'''

        self.Icon = QtGui.QIcon(str(ICON))
        self.setMinimumSize(self.sizeHint())
        self.resize(1200, 800)
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

        self.canvasWidget = QWidget()
        self.canvasWidget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        
        '''Labels'''

        self.setFunctionLabel = QLabel("Set Function")
        self.setFunctionBox = QLineEdit() #placeholder="input Function in Cartesian Co-ordSinates"SSS

        self.controlFrameLayout.setWidget(0, QFormLayout.LabelRole, self.setFunctionLabel)
        self.controlFrameLayout.setWidget(0, QFormLayout.FieldRole, self.setFunctionBox)


        # self.canvasFrameLayout.addWidget(self.canvasWidget)
        self.addCanvas()






        self.verticalLayout.addWidget(self.canvasFrame)
        self.verticalLayout.addWidget(self.controlFrame)

        self.setCentralWidget(self.centralwidget)


    def addCanvas(self):

        self.canvas = scene.SceneCanvas(keys='interactive', bgcolor='white',
                           size=(800, 600), show=False)

        view = self.canvas.central_widget.add_view()
        view.camera = 'arcball'

        self.sphere1 = scene.visuals.Sphere(radius=.3, method='latitude', parent=view.scene,
                                    edge_color='blue')

        self.sphere2 = scene.visuals.Sphere(radius=.2, method='ico', parent=view.scene,
                                    edge_color='blue')

        self.sphere3 = scene.visuals.Sphere(radius=.3, rows=10, cols=10, depth=10,
                                    method='cube', parent=view.scene,
                                    edge_color='blue')

        self.plane = scene.visuals.Plane(edge_color='blue', parent=view.scene, width=10, height=10)
        self.plane.transform = STTransform(translate=[-2.5, -2.5, -2.5])


        self.sphere1.transform = STTransform(translate=[-2.5, 0, 0])
        self.sphere3.transform = STTransform(translate=[1.5, 2, 1])

        

        view.camera.set_range(x=[-3, 3], y=[-3,3], z=[-3,3])

        self.canvas.create_native()
        self.canvasWidget = self.canvas.native

        self.canvasFrameLayout.addWidget(self.canvasWidget)
        self.sphereRanges = list(np.linspace(-2.5,2.5,100))

        self.transform()

    def transform(self):

        ''' Function to transform '''

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(0.1)
        # timer = app.Timer(interval = 0.1, connect=self.update, start=True)
        # app.run()


           

    def update(self):
        
        cord = self.sphereRanges[self.rangeIndex]
        self.sphere1.transform = STTransform(translate=[-2.5, 0, cord])
        self.sphere3.transform = STTransform(translate=[cord, -2.5, 1])
        
        self.rangeIndex += 1

        if self.rangeIndex == len(self.sphereRanges)-1:
            self.sphereRanges = [elem*-1 for elem in self.sphereRanges]
            self.rangeIndex = 0

        






        
