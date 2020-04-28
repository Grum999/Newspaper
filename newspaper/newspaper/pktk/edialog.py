#-----------------------------------------------------------------------------
# PyKritaToolKit
# Copyright (C) 2019 - Grum999
#
# A toolkit to make pykrita plugin coding easier :-)
# -----------------------------------------------------------------------------
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.
# If not, see https://www.gnu.org/licenses/
# -----------------------------------------------------------------------------



# -----------------------------------------------------------------------------
from .pktk import PkTk

import PyQt5.uic
from PyQt5.QtCore import (
        pyqtSignal
    )
from PyQt5.QtWidgets import (
        QDialog
    )

# -----------------------------------------------------------------------------
PkTk.setModuleInfo(
    'edialog',
    '1.0.0',
    'PyKrita Toolkit EDialog',
    'Extent QDialog to simplify signas/event management for ui interface'
)


# -----------------------------------------------------------------------------

class EDialog(QDialog):
    """Extended QDialog provides some signals and event to manage ui"""

    dialogShown = pyqtSignal()

    def __init__(self, parent=None):
        super(EDialog, self).__init__(parent)
        self.__eventCallBack = {}

    @staticmethod
    def loadUi(fileName):
        """Create an EDialog object from given XML .ui file"""
        return PyQt5.uic.loadUi(fileName, EDialog())

    def showEvent(self, event):
        """Event trigerred when dialog is shown

           At this time, all widgets are initialised and size/visiblity is known



           Example
           =======
                # define callback function
                def my_callback_function():
                    print("EDialog shown!")

                # initialise a dialog from an xml .ui file
                dlgMain = EDialog.loadUi(uiFileName)

                # execute my_callback_function() when dialog became visible
                dlgMain.dialogShown.connect(my_callback_function)
        """
        super(EDialog, self).showEvent(event)
        self.dialogShown.emit()

    def eventFilter(self, object, event):
        """Manage event filters for dialog"""
        if object in self.__eventCallBack.keys():
            return self.__eventCallBack[object](event)

        return super(EDialog, self).eventFilter(object, event)

    def setEventCallback(self, object, method):
        """Add an event callback method for given object


           Example
           =======
                # define callback function
                def my_callback_function(event):
                    if event.type() == QEvent.xxxx:
                        print("Event!")
                        return True
                    return False


                # initialise a dialog from an xml .ui file
                dlgMain = EDialog.loadUi(uiFileName)

                # define callback for widget from ui
                dlgMain.setEventCallback(dlgMain.my_widget, my_callback_function)
        """
        if object is None:
            return False

        self.__eventCallBack[object] = method
        object.installEventFilter(self)



