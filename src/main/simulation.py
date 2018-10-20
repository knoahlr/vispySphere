import sys
from vispy import scene, app
from vispy.visuals.transforms import STTransform
from vispy.visuals.filters import Clipper, Alpha, ColorFilter
from vispy.util.quaternion import Quaternion

from random import randrange



class Simulation():


    def __init__(self, n):

        self.canvas = scene.SceneCanvas(keys='interactive', bgcolor='white', size=(600, 800), show=False)

        self.elementCount = n

        self.view = self.canvas.central_widget.add_view()
    
        self.view.camera = 'turntable'

        self.elementList = dict()

        self.create_elements()
        
        self.plane = scene.visuals.Plane(edge_color='blue', parent=self.view.scene, width=10, height=10)
        self.plane.transform = STTransform(translate=[-2.5, -2.5, -2.5])
        self.axis = scene.visuals.XYZAxis(parent=self.view.scene)



    def randomize(self, range=None, event=None):

        ''' 
            Range: 
                    tuple for range of randomly generated value, integer or float.
        '''

        if event == 'radius':
            radius = randrange(range[0], range[1], 1) /11
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
                    print(dimension)
                    
                    self.elementList[name] = element()
                    self.elementList[name].type = 'sphere'
                    self.elementList[name].name = name
                    self.elementList[name].visual = scene.visuals.Sphere(radius=dimension, method='latitude', parent=self.view.scene, edge_color='blue', name=name)
                    self.setPosition(name)
                    self.setVelocity(name)

                else:

                    name = 'sphere1'
                    dimension = self.randomize((1,45), event='radius')
                    self.elementList[name] = element()
                    self.elementList[name].type = 'sphere'
                    self.elementList[name].name = name
                    self.elementList[name].visual = scene.visuals.Sphere(radius=dimension, method='latitude', parent=self.view.scene, edge_color='blue', name=name)
                    self.setPosition(name)
                    self.setVelocity(name)
                    


    def setPosition(self, name):

        x, y, z = self.randomize(event='pos')
        self.elementList[name].visual.transform = STTransform(translate=[x, y, z])
        self.elementList[name].pos = (x, y, z)

    def setVelocity(self, name):

        vx = self.randomize((-12,12), event='velocity')
        vy = self.randomize((-5,5), event='velocity')
        vz = self.randomize((-9,9), event='velocity')

        self.elementList[name].velocity = (vx, vy, vz)




    def motionControl(self):

        for elem in self.elementList.values():

            x, y, z = elem.pos
            vx, vy, vz = elem.velocity
            x = float(x)
            y = float(y)
            z = float(z)


            if abs((x + vx*0.1)) > 7: 

                elem.velocity = (-vx, vy, vz)
                x -=  vx*0.1

            else: x +=  vx*0.1
            
            if abs((y + vy*0.1)) > 10: 

                elem.velocity = (vx, -vy, vz)
                y -=  vy*0.1

            else: y +=  vy*0.1
            
            if abs((z + vz*0.1)) > 5:

                elem.velocity = (vx, vy, -vz) 
                z -=  vz*0.1
                
            else: z +=  vz*0.1

            elem.pos = (x, y, z)
            elem.translate()










class element():

    def __init__(self):

        self.type = None
        self.visual = None

        self.pos = None

        self.velocity = None

        self.name = None

    def translate(self):

        if self.pos != None:
            self.visual.transform = STTransform(translate=[self.pos[0],self.pos[1], self.pos[2]])



















