from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget, QPushButton, QLabel, QInputDialog, QTextBrowser
from PyQt5 import QtCore, QtWidgets,QtGui

from viz_getdata import get_data
from viz_plot import plot_

import re

import configparser

import sys, os, gc
import warnings
warnings.filterwarnings("ignore")

class My_Main_window(QtWidgets.QMainWindow):
    def getconfig(self):
        config = configparser.ConfigParser(allow_no_value = True)

        config.read("./config.ini")
        self.com_view = True
        self.HSC_bkg = False
        self.component = 1
        self.map = config.get('DEFAULT', 'map', fallback = "gasv")
        self.pos_x = 25
        self.pos_y = 25
        self.wav_min_max = [3000, 9000]
        self.flux = config.get('DEFAULT', 'flux', fallback = './sami/dr3/ifs')
        self.gasv = config.get('DEFAULT', 'gasv', fallback = './sami/dr3/ifs')
        self.gasd = config.get('DEFAULT', 'gasd', fallback = './sami/dr3/ifs')
        self.stev = config.get('DEFAULT', 'stev', fallback = './sami/dr3/ifs')
        self.sted = config.get('DEFAULT', 'sted', fallback = './sami/dr3/ifs')
        self.line_flux = config.get('DEFAULT', 'line_flux', fallback = './sami/dr3/ifs')
        self.hsc_image = config.get('DEFAULT', 'hsc_image', fallback = './sami/dr3/ifs')
        self.cube = config.get('DEFAULT', 'cube', fallback = './sami/dr3/ifs')
        self.sami_id = config.getint('DEFAULT', 'sami_id', fallback = 0)
        self.line_set = [['Hα', 6562.8],
                    ['Hβ', 4861.33],
                    ['OIII', 5006.843],
                    ['NII', 6583.454],
                    ['SII', 6731],
                    ['SII', 6716],
                    ['OII', [3727, 3729]],]
    def setconfig(self):
        config = configparser.SafeConfigParser()
        
        config.read("./config.ini")
        config.set('DEFAULT', 'map', self.map)

        config.set('DEFAULT', 'flux', self.flux)
        config.set('DEFAULT', 'gasv', self.gasv)
        config.set('DEFAULT', 'gasd', self.gasd)
        config.set('DEFAULT', 'stev', self.stev)
        config.set('DEFAULT', 'sted', self.sted)
        config.set('DEFAULT', 'line_flux', self.line_flux)
        config.set('DEFAULT', 'hsc_image', self.hsc_image)
        config.set('DEFAULT', 'cube', self.cube)
        config.set('DEFAULT', 'sami_id', str(self.sami_id))
        config.write(open("config.ini", "w"))
        
    
    def __init__(self,parent=None):
        super(My_Main_window,self).__init__(parent)
        self.nofig = True
        self.getconfig()
        self.setWindowTitle('SAMI viz')
        self.get_data = get_data
        self.plot_ = plot_

        # Add menu for maps
        self.menu_maps = QtWidgets.QMenu("Maps")
        self.maps_actions = []
        self.maps_actions.append(QtWidgets.QAction("Flux",self.menu_maps))
        self.maps_actions.append(QtWidgets.QAction("Gas Velocity",self.menu_maps))
        self.maps_actions.append(QtWidgets.QAction("Stellar Velocity",self.menu_maps))
        self.maps_actions.append(QtWidgets.QAction("Gas Velocity Dispersion",self.menu_maps))
        self.maps_actions.append(QtWidgets.QAction("Stellar Velocity Dispersion",self.menu_maps))
        self.maps_actions.append(QtWidgets.QAction("BPT diagram",self.menu_maps))
        self.maps_actions.append(QtWidgets.QAction("Line Wing Map",self.menu_maps))
        self.maps_actions.append(QtWidgets.QAction("Component",self.menu_maps))
        
        for action in self.maps_actions:
            self.menu_maps.addAction(action)
        self.menuBar().addMenu(self.menu_maps) 
        
        # Add menu for settings
        self.menu_setting = QtWidgets.QMenu("Settings")
        self.setting_actions = []
        self.setting_actions.append(QtWidgets.QAction("Path to cube",self.menu_setting))
        self.setting_actions.append(QtWidgets.QAction("Path to total flux",self.menu_setting))
        self.setting_actions.append(QtWidgets.QAction("Path to gas velocity",self.menu_setting))
        self.setting_actions.append(QtWidgets.QAction("Path to gas dispersion",self.menu_setting))
        self.setting_actions.append(QtWidgets.QAction("Path to stellar velocity",self.menu_setting))
        self.setting_actions.append(QtWidgets.QAction("Path to stellar dispersion",self.menu_setting))
        self.setting_actions.append(QtWidgets.QAction("Path to line flux",self.menu_setting))
        self.setting_actions.append(QtWidgets.QAction("SAMI id",self.menu_setting))
        for action in self.setting_actions:
            self.menu_setting.addAction(action)
        self.menuBar().addMenu(self.menu_setting)

        # Add menu for modes
        self.menu_modes = QtWidgets.QMenu("Modes")
        self.modes_actions = []
        self.modes_actions.append(QtWidgets.QAction("Multi-component velocity view",self.menu_modes))
        self.modes_actions.append(QtWidgets.QAction("HSC background",self.menu_modes))
        for action in self.modes_actions:
            self.menu_modes.addAction(action)
        self.menuBar().addMenu(self.menu_modes)
        

        # Add events
        for action in self.maps_actions:
            action.triggered.connect(self.menu_maps_func)
        
        for action in self.setting_actions:
            action.triggered.connect(self.menu_setting_func)
            
        for action in self.modes_actions:
            action.triggered.connect(self.menu_mode_func)
        
        #Plot()
        self.get_data(self)
        self.plot_(self)

    def focus(self, event):
        if self.com_view:
            if event.inaxes in self.axes[7:11]:
                self.pos_x = round(event.xdata)
                self.pos_y = round(event.ydata)
                print(self.snr[self.pos_x, self.pos_y])
                self.plot_(self)
            elif event.inaxes in self.axes[0:7]:
                self.wav_min_max.pop(0)
                self.wav_min_max.append(event.xdata)
                self.plot_(self)
        else:
            if event.inaxes == self.axes[7]:
                self.pos_x = round(event.xdata)
                self.pos_y = round(event.ydata)
                self.plot_(self)

            elif event.inaxes in self.axes[0:7]:
                self.wav_min_max.pop(0)
                self.wav_min_max.append(event.xdata)
                self.plot_(self)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Up:
            self.pos_y = self.pos_y + 1
        if event.key() == QtCore.Qt.Key_Down:
            self.pos_y = self.pos_y - 1
        if event.key() == QtCore.Qt.Key_Right:
            self.pos_x = self.pos_x + 1
        if event.key() == QtCore.Qt.Key_Left:
            self.pos_x = self.pos_x - 1
        self.plot_(self)

    def menu_setting_func(self):
        sender = self.sender()
        if sender.text() == "Path to cube":
            text, ok = QInputDialog.getText(self, 'Path to cube', 'Enter path here:')
            if ok and text:
                self.cube = text
        elif sender.text() == "Path to total flux":
            text, ok = QInputDialog.getText(self, 'Path to total flux', 'Enter path here:')
            if ok and text:
                self.flux = text
        elif sender.text() == "Path to gas velocity":
            text, ok = QInputDialog.getText(self, 'Path to gas velocity', 'Enter path here:')
            if ok and text:
                self.gasv = text      
        elif sender.text() == "Path to stellar velocity":
            text, ok = QInputDialog.getText(self, 'Path to stellar velocity', 'Enter path here:')
            if ok and text:
                self.stev = text
        elif sender.text() == "Path to gas dispersion":
            text, ok = QInputDialog.getText(self, 'Path to gas dispersion', 'Enter path here:')
            if ok and text:
                self.gasd = text
        elif sender.text() == "Path to stellar dispersion":
            text, ok = QInputDialog.getText(self, 'Path to stellar dispersion', 'Enter path here:')
            if ok and text:
                self.sted = text
        elif sender.text() == "Path to line flux":
            text, ok = QInputDialog.getText(self, 'Path to line flux', 'Enter path here:')
            if ok and text:
                self.lineflux = text
        elif sender.text() == "SAMI id":
            text, ok = QInputDialog.getText(self, 'SAMI id', 'Enter SAMI id here:')
            pattern = re.compile(r'\d+')
            if ok and len(pattern.findall(text)):
                self.sami_id = pattern.findall(text)[0]
        else:
            ok = None
        
        if ok and text:
            self.get_data(self)
            gc.collect()
            self.plot_(self)
            self.setconfig()
    
    def menu_maps_func(self):
        sender = self.sender()
        ok = True
        if sender.text() == "Flux":
            self.map = 'flux'
        elif sender.text() == "Gas Velocity":
            self.map = 'gasv'
        elif sender.text() == "Stellar Velocity":
            self.map = 'stev'     
        elif sender.text() == "Gas Velocity Dispersion":
            self.map = 'gasd'
        elif sender.text() == "Stellary Velocity Dispersion":
            self.map = 'sted'
        elif sender.text() == "BPT diagram":
            self.map = 'BPT'
        elif sender.text() == "Line Wing Map":
            self.map = 'LWM'
        elif sender.text() == "Component":
            text, ok = QInputDialog.getItem(self, 'Which component', 'Enter # of component here:', ['1', '2', '3'], 0, False)
            self.component = int(text)
        else:
            ok = None
        if ok:
            self.plot_(self)
        
    def menu_mode_func(self):
        sender = self.sender()
        if sender.text() == "Multi-component velocity view":
            self.com_view = 1 - self.com_view
            self.HSC_bkg = False
        elif sender.text() == "HSC background":
            self.HSC_bkg  = 1 - self.HSC_bkg
            self.com_view = False
        self.setconfig()

        self.plot_(self)


