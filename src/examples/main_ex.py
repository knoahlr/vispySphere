 
import sys
from vispy import scene, app
from vispy.visuals.transforms import STTransform
from vispy.visuals.filters import Clipper, Alpha, ColorFilter

canvas = scene.SceneCanvas(keys='interactive', bgcolor='white',
                           size=(800, 600), show=True)

view = canvas.central_widget.add_view()
view.camera = 'arcball'

sphere1 = scene.visuals.Sphere(radius=.01, method='latitude', parent=view.scene,
                               edge_color='blue')

sphere2 = scene.visuals.Sphere(radius=0.02, method='ico', parent=view.scene,
                               edge_color='blue')

sphere3 = scene.visuals.Sphere(radius=.03, rows=10, cols=10, depth=10,
                               method='cube', parent=view.scene,
                               edge_color='blue')
cube = scene.visuals.Box(width=10, height=10, depth=10, parent=view.scene,edge_color='black')

sphere1.transform = STTransform(translate=[-2.5, 0, 0])
sphere3.transform = STTransform(translate=[1.5, 2, 1])

cube.transform = STTransform(translate=[0,0,0])
cube.attach(Alpha(0))

view.camera.set_range(x=[-3, 3], y=[-3,3], z=[-3,3])

x1, y1, z1 =  -2.5, 0, 0
x2, y2, z2 =  1.5, 2, 1

def update(ev):

    global x1, y1, z1, x2, y2, z2
    
    sphere1.transform = STTransform(translate=[x1, y1, z1])
    sphere3.transform = STTransform(translate=[x2, y2, z2])

    y1 -= 0.4
    z2 -= 0.4
    view.camera.fov = view.camera.fov + 1

timer = app.Timer(interval=0.1, connect=update, start=True)

    


if __name__ == '__main__' and sys.flags.interactive == 0:
    app.run()
    dir(sphere1)



