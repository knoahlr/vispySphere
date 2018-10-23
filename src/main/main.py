import sys, time, ctypes, re, argparse
from sceneWindow import SceneWindow
# from secondaryWindow import secondaryWindow

from PyQt5 import QtCore
from PyQt5.QtWidgets import QCommonStyle, QApplication
# ICON = r'articles\atom.png'
import os, shutil

sys.path.append(os.path.abspath(r"../../"))

from pathlib import Path

if __name__ == "__main__":
    
    if not Path(r"../../logs").is_dir(): os.makedirs(r"../../logs")

    ''' Cleaning up simulation folder '''
    if not Path(r"../../logs/simulations/velocityImages").is_dir(): os.makedirs(r"../../logs/simulations/velocityImages")
    else:
        for filename in os.listdir(r"../../logs/simulations/velocityImages/"):
            shutil.rmtree(r"../../logs/simulations/velocityImages/{0}".format(filename))
    
    if not Path(r"../../logs/simulations/originalImages").is_dir(): os.makedirs(r"../../logs/simulations/originalImages")
    else: 
        for filename in os.listdir(r'../../logs/simulations/originalImages/'):
            shutil.rmtree(r'../../logs/simulations/originalImages/{0}'.format(filename))

    if not Path(r"../../logs/simulations/depthMatrix").is_dir(): os.makedirs(r"../../logs/simulations/depthMatrix")
    else: 
        for filename in os.listdir(r'../../logs/simulations/depthMatrix/'):
            shutil.rmtree(r'../../logs/simulations/depthMatrix/{0}'.format(filename))

        
    logFile = open(Path(r"../../logs/mainLog.log"), 'w')
    sys.stdout = logFile

    myappid = 'mycompany.myproduct.subproduct.version' # arbitrary string
    ''' https://stackoverflow.com/questions/1551605/how-to-set-applications-taskbar-icon-in-windows-7/1552105#1552105 '''
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    app = QApplication(sys.argv)

    styleSheetFile = QtCore.QFile(r"..\..\css\materialDesign.qss")
    styleSheetFile.open(QtCore.QFile.ReadOnly)
    
    styleSheetFileString = str(styleSheetFile.readAll(), "utf-8") 

    # app.setStyleSheet(styleSheetFileString)

    #app.setStyle(QCommonStyle())

    window =SceneWindow()
    window.show()
    sys.exit(app.exec_())