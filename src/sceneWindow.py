import sys
from vispy import scene, app
from vispy.visuals.transforms import STTransform
from vispy.visuals.filters import Clipper, Alpha, ColorFilter
from vispy.util.quaternion import Quaternion

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import QWidget, QFormLayout, QMainWindow, QGroupBox, QVBoxLayout, QHBoxLayout, \
QLabel, QTextEdit, QLineEdit, QPushButton, QFrame

from defaultMenuBar import DefaultMenuBar

from pathlib import Path
import numpy as np

from PIL import Image
import cv2


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

        self.canvasWidget = QWidget()
        self.canvasWidget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.canvasWidgetLayout = QHBoxLayout()


        ''' Rendered Video of scene'''
        self.videoWidget = QtWidgets.QGraphicsView()
        self.videoWidget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        

        '''Labels'''

        self.setFunctionLabel = QLabel("Set Function")
        self.setFunctionBox = QLineEdit() #placeholder="input Function in Cartesian Co-ordSinates"SSS
        self.controlFrameLayout.setWidget(0, QFormLayout.LabelRole, self.setFunctionLabel)
        self.controlFrameLayout.setWidget(0, QFormLayout.FieldRole, self.setFunctionBox)


        # self.canvasFrameLayout.addWidget(self.canvasWidget)
        self.addCanvas()
        self.canvasWidget.setLayout(self.canvasWidgetLayout)
        self.canvasFrameLayout.addWidget(self.canvasWidget)
        
        self.verticalLayout.addWidget(self.canvasFrame)
        self.verticalLayout.addWidget(self.controlFrame)

        self.setCentralWidget(self.centralwidget)


    def addCanvas(self):

        self.canvas = scene.SceneCanvas(keys='interactive', bgcolor='white',
                           size=(800, 600), show=False)

        self.view = self.canvas.central_widget.add_view()
    
        self.view.camera = 'turntable'

        print(self.view, dir(self.view))
        print(self.view.camera, dir(self.view.camera))
        self.newCameraRotation = Quaternion()

        self.sphere1 = scene.visuals.Sphere(radius=.3, method='latitude', parent=self.view.scene,
                                    edge_color='blue')

        self.sphere2 = scene.visuals.Sphere(radius=.2, method='ico', parent=self.view.scene,
                                    edge_color='blue')

        self.sphere3 = scene.visuals.Sphere(radius=.3, rows=10, cols=10, depth=10,
                                    method='cube', parent=self.view.scene,
                                    edge_color='blue')
        self.axis = scene.visuals.XYZAxis(parent=self.view.scene)

        self.plane = scene.visuals.Plane(edge_color='blue', parent=self.view.scene, width=10, height=10)
        self.plane.transform = STTransform(translate=[-2.5, -2.5, -2.5])


        self.sphere1.transform = STTransform(translate=[-2.5, 0, 0])
        self.sphere3.transform = STTransform(translate=[1.5, 2, 1])

        

        self.view.camera.set_range(x=[-3, 3], y=[-3,3], z=[-3,3])
        self.view.camera.set_state({'center': [0.0, 0.0, 0.0]})

        self.canvas.create_native()

        self.canvasWidgetLayout.addWidget(self.canvas.native)
        self.canvasWidgetLayout.addWidget(self.videoWidget)

        self.sphereRanges = list(np.linspace(-2.5,2.5,100))

        self.transform()

    def transform(self):

        ''' Function to transform '''

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(0.1)
        # timer = app.Timer(interval = 0.1, connect=self.update, start=True)
        # app.run()

    def setImage(self):

        # self.view.camera.set_range(x=[-5, 1], y=[-5,1], z=[-3,3])
        # self.view.camera.set_state({'center': [0.0, 0.0, 0.0]})
        
        imageArray = self.canvas.render()

        rgbImage = cv2.cvtColor(imageArray, cv2.COLOR_BGR2RGB)
        
        image = QtGui.QImage(rgbImage.data, imageArray.shape[1], imageArray.shape[0], QtGui.QImage.Format_RGB888)
        

        scene = QtWidgets.QGraphicsScene()
        pixmapItem = QtWidgets.QGraphicsPixmapItem(QtGui.QPixmap.fromImage(image))
        scene.addItem(pixmapItem)

        self.videoWidget.setScene(scene)

           

    def update(self):
        

        cord = self.sphereRanges[self.rangeIndex]
        self.sphere1.transform = STTransform(translate=[-2.5, 0, cord])
        self.sphere3.transform = STTransform(translate=[cord, -2.5, 1])
        # print(self.canvas.render())
        print(self.view.camera.get_state(),self.view.camera.transform ,(self.view.camera._xlim, self.view.camera._ylim, self.view.camera._zlim,))

        self.newCameraRotation = Quaternion(1, 0, cord, 3)
        self.newCameraRotation =  self.newCameraRotation.create_from_euler_angles(0, 0, cord*36)

        # self.canvas.push_viewport((3,3, cord*36,3))
        
        # self.view.camera.set_range( x=[-cord,cord],z=[-cord,cord])
        # self.view.camera._quaternion = self.newCameraRotation
        # self.view.camera._rotate_tr()
        self.view.camera.elevation = 20
        self.view.camera.azimuth = cord *72

        
        self.setImage()
        
        self.rangeIndex += 1

        if self.rangeIndex == len(self.sphereRanges)-1:
            self.sphereRanges = [elem*-1 for elem in self.sphereRanges]
            self.rangeIndex = 0


