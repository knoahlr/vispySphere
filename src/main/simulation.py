import sys
from vispy import scene, app
from vispy.visuals.transforms import STTransform
from vispy.visuals.filters import Clipper, Alpha, ColorFilter
from vispy.util.quaternion import Quaternion


from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from random import randrange

import numpy as np

import copy

from pathlib import Path

import cv2

class Simulation(QObject):

    changePixmap = pyqtSignal()

    def __init__(self, n, index):
        
        super().__init__()
        self.canvas = scene.SceneCanvas(keys='interactive', bgcolor='white', size=(800, 600), show=False)

        self.elementCount = n

        self.view = self.canvas.central_widget.add_view()
    
        self.view.camera = 'turntable'
        self.index = index

        self.elementList = dict()

        self.frameList = list()

        self.create_elements()
        
        self.plane = scene.visuals.Plane(edge_color='blue', parent=self.view.scene, width=0.5, height=0.5)
        self.plane.transform = STTransform(translate=[0, 0, 0])
        self.axis = scene.visuals.XYZAxis(parent=self.view.scene)



    def randomize(self, range=None, event=None):

        ''' 
            Range: 
                    list for range of randomly generated value, integer or float.
        '''

        if event == 'radius':
            radius = randrange(range[0], range[1], 1) /11
            if radius > 1.8: radius -= 1
            # print(radius, end='\n\r')
            return radius

        if event == 'velocity' or event == "elementCount":
            value = randrange(range[0], range[1], 1)
            return value/15

        if event == 'pos':
            x = '{0:.2}'.format(randrange(-50, 50, 1)/ 11)
            y = '{0:.2}'.format(randrange(-50, 50, 1)/ 11) 
            z = '{0:.2}'.format(randrange(-50, 50, 1)/ 11) 

            return(x, y, z)

    def create_elements(self):

        for i in range(self.elementCount):

            if True:

                type = 'sphere'

                if self.elementList:

                    objectCount = len(list(self.elementList.keys()))
                    name = "{0}{1}".format('sphere', objectCount+1)
                    dimension = self.randomize((1,5), event='radius')
                    # print(dimension)
                    
                    self.elementList[name] = element()
                    self.elementList[name].type = 'sphere'
                    self.elementList[name].name = name
                    self.elementList[name].visual = scene.visuals.Sphere(radius=dimension, method='latitude', parent=self.view.scene, edge_color='blue', name=name)
                    self.elementList[name].dimension = dimension
                    self.setPosition(name)
                    self.setVelocity(name)

                else:

                    name = 'sphere1'
                    dimension = self.randomize((1,45), event='radius')
                    self.elementList[name] = element()
                    self.elementList[name].type = 'sphere'
                    self.elementList[name].name = name
                    self.elementList[name].visual = scene.visuals.Sphere(radius=dimension, method='latitude', parent=self.view.scene, edge_color='blue', name=name)
                    self.elementList[name].dimension = dimension
                    self.setPosition(name)
                    self.setVelocity(name)
                    


    def setPosition(self, name):

        x, y, z = self.randomize(event='pos')
        self.elementList[name].visual.transform = STTransform(translate=[x, y, z])
        self.elementList[name].pos = list((x, y, z))

    def setVelocity(self, name):

        vx = self.randomize((-12,12), event='velocity')
        vy = self.randomize((-5,5), event='velocity')
        vz = self.randomize((-9,9), event='velocity')

        self.elementList[name].velocity = (vx, vy, vz)




    def motionControl(self, dt):
        
        dt = dt/1000

        for name, elem in self.elementList.items():

            x, y, z = elem.pos
            vx, vy, vz = elem.velocity
            x = float(x)
            y = float(y)
            z = float(z)


            if abs((x + vx*dt)) > 7: 

                elem.velocity = (-vx, vy, vz)
                x -=  vx*dt

            else: x +=  vx*dt
            
            if abs((y + vy*dt)) > 10: 

                elem.velocity = (vx, -vy, vz)
                y -=  vy*dt

            else: y +=  vy*dt
            
            if abs((z + vz*dt)) > 5:

                elem.velocity = (vx, vy, -vz) 
                z -=  vz*dt
                
            else: z +=  vz*dt

            elem.pos = list((x, y, z))
            elem.translate()

        self.changePixmap.emit()


class element():

    def __init__(self):

        self.type = None
        self.visual = None

        self.dimension = None

        self.pos = list()

        self.velocity = None

        self.name = None

    def translate(self):

        if self.pos != None:
            self.visual.transform = STTransform(translate=[self.pos[0],self.pos[1], self.pos[2]])


class FrameData():

    def __init__(self, imageArray, elementList, scaleFactor, canvasSize, index):

        self.imageArray  = imageArray
        self.elementList = elementList.copy()
        self.elementPosition = dict( (name, elem.pos) for name, elem in self.elementList.items())
        self.index = index
        self.scale_factor = scaleFactor
        self.canvasSize = canvasSize

        self.velocityMatrix = np.full((self.canvasSize[1], self.canvasSize[0], 3), 255)
        self.depthMatrix = np.empty((self.canvasSize[1], self.canvasSize[0]))


    def createMatrix(self, event='velocity'):

        if event == "velocity": matrix = self.velocityMatrix
        else: matrix = self.depthMatrix
        # print('\n\n\n')
        for name, element in self.elementList.items():
            # print(self.elementPosition[name], end='\n')
            center_x = round( (self.elementPosition[name][1] * (self.canvasSize[1] / self.scale_factor)) + self.canvasSize[0]/2 ) #center[0]
            center_y = round( (-1*self.elementPosition[name][2] * (self.canvasSize[1] / self.scale_factor)) +  self.canvasSize[1]/2 )

            d_pixels = round(2* element.dimension * (self.canvasSize[1] / self.scale_factor))

            for pixelLine in range(d_pixels):

                if (center_y - pixelLine) > 0 and (center_y + pixelLine) < self.canvasSize[1]:

                    yPixelsPlus = matrix[center_y - pixelLine]
                    yPixelsMinus = matrix[center_y + pixelLine]

                    new_d_pixels = d_pixels - 2*pixelLine
                    startPixel = round(center_x - (new_d_pixels/2))

                    if startPixel < 0: startPixel = 0
                

                    for pixelNumber in range(new_d_pixels):

                        xPixel = startPixel + pixelNumber

                        if (xPixel) < self.canvasSize[0]:

                            if event == "velocity":
                                yPixelsMinus[xPixel] = [element.velocity[0] * 200, element.velocity[1] * 200, element.velocity[2]* 200]
                                yPixelsPlus[xPixel] = [element.velocity[0]* 200, element.velocity[1]* 200, element.velocity[2]* 200]
                            if event == "depth":
                                yPixelsMinus[xPixel] = (self.elementPosition[name][0] + 8) * 15
                                yPixelsPlus[xPixel] = (self.elementPosition[name][0] + 8) * 15




            



if __name__ == "__main__":


    ''' class Debugger '''

    imageArray = np.empty((600,800))

    for i in range(5):

        center_x = randrange(0, 600, 1)
        center_y = randrange(0, 800, 1)
        center= (center_x, center_y)
        print(center)

        d_pixels = randrange(20, 100, 1)

        imageArray = createMatrix()

    logFile = open(Path(r"../../logs/mainLog.log"), 'w')
    sys.stdout = logFile
    np.set_printoptions(threshold=np.inf)

    print(imageArray, end='\n\n\n')

    cv2.imwrite('..\..\logs\pic_vel.jpg', imageArray)





















