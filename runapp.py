# -*- coding: utf-8 -*-
"""
Created on Thu Nov  6 15:16:24 2025

@author: anais
"""

import sys
import os
import model_hexa
from PyQt5 import QtWidgets

app = QtWidgets.QApplication(sys.argv)
window = model_hexa.Window()
window.show()

sys.exit(app.exec_())
