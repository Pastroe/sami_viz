from PyQt5 import QtWidgets
from viz_GUI import My_Main_window

import sys, os, gc
import warnings
warnings.filterwarnings("ignore")

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main_window = My_Main_window()
    main_window.show()
    app.exec()
