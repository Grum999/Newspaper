#-----------------------------------------------------------------------------
# Newspaper
# Copyright (C) 2019 - Grum999
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
# A Krita plugin designed to apply a "newspaper" style to a layer
# . Monochrome
# . Four color (CMYK)
# -----------------------------------------------------------------------------

from math import (
        ceil,
        cos,
        radians,
        sin,
        sqrt
    )
import os
import random
import re
import sys
import time

import PyQt5.uic

from krita import (
        Extension,
        InfoObject,
        Node,
        Selection
    )

from PyQt5.Qt import *
from PyQt5 import QtCore
from PyQt5.QtCore import (
        pyqtSlot,
        QByteArray,
        QRect,
        QStandardPaths,
        QObject
    )
from PyQt5.QtGui import (
        QColor,
        QImage,
        QPixmap,
        QPolygonF
    )
from PyQt5.QtWidgets import (
        QApplication,
        QCheckBox,
        QColorDialog,
        QComboBox,
        QDialog,
        QDialogButtonBox,
        QFormLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QMessageBox,
        QProgressBar,
        QProgressDialog,
        QVBoxLayout,
        QWidget
    )

if __name__ != '__main__':
    # script is executed from Krita, loaded as a module
    from .pktk.edialog import (
            EDialog
        )

    from .pktk.ekrita import (
            EKritaNode
        )

    PLUGIN_EXEC_FROM = 'KRITA'
else:
    # Execution from 'Scripter' plugin?

    # Reload or Import
    if 'newspaper.pktk.edialog' in sys.modules:
        from importlib import reload
        reload(sys.modules['newspaper.pktk.edialog'])
    else:
        import newspaper.pktk.edialog

    from newspaper.pktk.edialog import (
            EDialog
        )

    if 'newspaper.pktk.ekrita' in sys.modules:
        from importlib import reload
        reload(sys.modules['newspaper.pktk.ekrita'])
    else:
        import newspaper.pktk.ekrita

    from newspaper.pktk.ekrita import (
            EKritaDocument,
            EKritaNode
        )

    PLUGIN_EXEC_FROM = 'SCRIPTER_PLUGIN'


PLUGIN_VERSION = '1.2.0'
EXTENSION_ID = 'pykrita_newspaper'
PLUGIN_MENU_ENTRY = 'Newspaper'
PLUGIN_DIALOG_TITLE = "{0} - {1}".format('Newspaper', PLUGIN_VERSION)

# Define DialogBox types
DBOX_INFO = 'i'
DBOX_WARNING ='w'


# Define Output modes
OUTPUT_MODE_MONO = i18n('Monochrome')
OUTPUT_MODE_CMY = i18n('Three color (CMY - Pictures)')
OUTPUT_MODE_CMYK = i18n('Four color (CMYK - Pictures)')
OUTPUT_MODE_CMYrK = i18n('Four color (CMY+K - Pictures)')
OUTPUT_MODE_CMYpK1 = i18n('Four color (CMY+K - Comics #1)')
OUTPUT_MODE_CMYpK2 = i18n('Four color (CMY+K - Comics #2)')

# define precision method to calculate current dot size
OUTPUT_SAMPLING_LOW = i18n('Low')
OUTPUT_SAMPLING_MEDIUM = i18n('Medium')
OUTPUT_SAMPLING_HIGH = i18n('High')

OUTPUT_ANTIALIASING_NONE = i18n('None')
OUTPUT_ANTIALIASING_NORMAL = i18n('Normal')
OUTPUT_ANTIALIASING_SOFT = i18n('Soft')

OUTPUT_DOT_STYLE_CIRCLE = i18n('Circle')
OUTPUT_DOT_STYLE_DIAMOND = i18n('Diamond')
OUTPUT_DOT_STYLE_SQUARE = i18n('Square')
OUTPUT_DOT_STYLE_LINEFLAT = i18n('Flat line')
OUTPUT_DOT_STYLE_LINEROUND = i18n('Rounded line')

OUTPUT_4C_SCREENANGLE_US = "Standard 4/C U.S. (15/75/0/45)"
OUTPUT_4C_SCREENANGLE_EU = "Standard 4/C European (15/45/0/75)"

OUTPUT_MONO_DESMODE_LIGHTNESS = i18n('Lightness')
OUTPUT_MONO_DESMODE_LUMINOSITY709 = i18n('Luminosity (ITU-R BT.709)')
OUTPUT_MONO_DESMODE_LUMINOSITY601 = i18n('Luminosity (ITU-R BT.601)')
OUTPUT_MONO_DESMODE_AVERAGE = i18n('Average')
OUTPUT_MONO_DESMODE_MINIMUM = i18n('Minimum')
OUTPUT_MONO_DESMODE_MAXIMUM = i18n('Maximum')


# Define original layer action
ORIGINAL_LAYER_KEEPUNCHANGED = i18n('Unchanged')
ORIGINAL_LAYER_KEEPVISIBLE = i18n('Visible')
ORIGINAL_LAYER_KEEPHIDDEN = i18n('Hidden')
ORIGINAL_LAYER_REMOVE = i18n('Remove')


# define dialog option minimum dimension
DOPT_MIN_WIDTH = 1024
DOPT_MIN_HEIGHT = 480


OUTPUT_PREDEF_VALUES = {
    OUTPUT_4C_SCREENANGLE_US: {
        'C': 15,
        'M': 75,
        'Y': 0,
        'K': 45
    },
    OUTPUT_4C_SCREENANGLE_EU: {
        'C': 15,
        'M': 45,
        'Y': 0,
        'K': 75
    },
    '4CCOLORS': {
        'C': QColor(Qt.cyan),
        'M': QColor(Qt.magenta),
        'Y': QColor(Qt.yellow),
        'K': QColor(Qt.black)
    }
}

# note: same processing base than "Channels To Layers" plugin
OUTPUT_MODE_NFO = {
    (OUTPUT_MODE_MONO+'0') : {
        'description' : 'Convert image to monochrome halftone',
        'groupLayerName' : 'Newspaper (Monochrome)',
        'layers' : [
                    {
                        'color' : 'Mono',
                        'process': [
                                {
                                    'action' : 'duplicate',
                                    'value' : '@original'
                                },
                                {
                                    'action' : 'filter',
                                    'value' : 'name=desaturate;type=0'
                                },
                                {
                                    'action' : 'newspaper',
                                    'value' : None                      # automatically use right configuration
                                }
                            ]
                    }
                ]
    },
    (OUTPUT_MODE_MONO+'1') : {
        'description' : 'Convert image to monochrome halftone',
        'groupLayerName' : 'Newspaper (Monochrome)',
        'layers' : [
                    {
                        'color' : 'Mono',
                        'process': [
                                {
                                    'action' : 'duplicate',
                                    'value' : '@original'
                                },
                                {
                                    'action' : 'filter',
                                    'value' : 'name=desaturate;type=1'
                                },
                                {
                                    'action' : 'newspaper',
                                    'value' : None                      # automatically use right configuration
                                }
                            ]
                    }
                ]
    },
    (OUTPUT_MODE_MONO+'2') : {
        'description' : 'Convert image to monochrome halftone',
        'groupLayerName' : 'Newspaper (Monochrome)',
        'layers' : [
                    {
                        'color' : 'Mono',
                        'process': [
                                {
                                    'action' : 'duplicate',
                                    'value' : '@original'
                                },
                                {
                                    'action' : 'filter',
                                    'value' : 'name=desaturate;type=2'
                                },
                                {
                                    'action' : 'newspaper',
                                    'value' : None                      # automatically use right configuration
                                }
                            ]
                    }
                ]
    },
    (OUTPUT_MODE_MONO+'3') : {
        'description' : 'Convert image to monochrome halftone',
        'groupLayerName' : 'Newspaper (Monochrome)',
        'layers' : [
                    {
                        'color' : 'Mono',
                        'process': [
                                {
                                    'action' : 'duplicate',
                                    'value' : '@original'
                                },
                                {
                                    'action' : 'filter',
                                    'value' : 'name=desaturate;type=3'
                                },
                                {
                                    'action' : 'newspaper',
                                    'value' : None                      # automatically use right configuration
                                }
                            ]
                    }
                ]
    },
    (OUTPUT_MODE_MONO+'4') : {
        'description' : 'Convert image to monochrome halftone',
        'groupLayerName' : 'Newspaper (Monochrome)',
        'layers' : [
                    {
                        'color' : 'Mono',
                        'process': [
                                {
                                    'action' : 'duplicate',
                                    'value' : '@original'
                                },
                                {
                                    'action' : 'filter',
                                    'value' : 'name=desaturate;type=4'
                                },
                                {
                                    'action' : 'newspaper',
                                    'value' : None                      # automatically use right configuration
                                }
                            ]
                    }
                ]
    },
    (OUTPUT_MODE_MONO+'5') : {
        'description' : 'Convert image to monochrome halftone',
        'groupLayerName' : 'Newspaper (Monochrome)',
        'layers' : [
                    {
                        'color' : 'Mono',
                        'process': [
                                {
                                    'action' : 'duplicate',
                                    'value' : '@original'
                                },
                                {
                                    'action' : 'filter',
                                    'value' : 'name=desaturate;type=5'
                                },
                                {
                                    'action' : 'newspaper',
                                    'value' : None                      # automatically use right configuration
                                }
                            ]
                    }
                ]
    },

    OUTPUT_MODE_CMY : {
        'description' : 'Decompose image a into 3 primary colors (CMY) and apply halftone. The black value is obtained as a pure coombination of Cyan, Magenta and Yellow',
        'groupLayerName' : 'Newspaper (CMY)',
        'layers' : [
                    {
                        'color' : 'Y',
                        'process': [
                                {
                                    'action' : 'duplicate',
                                    'value' : '@original'
                                },
                                {
                                    'action' : 'new',
                                    'value' : {
                                                'type' : 'filllayer',
                                                'color' :  QColor(Qt.yellow)
                                            }
                                },
                                {
                                    'action' : 'blending mode',
                                    'value' : 'add'
                                },
                                {
                                    'action' : 'merge down',
                                    'value' : None
                                },
                                {
                                    'action' : 'blending mode',
                                    'value' : 'multiply'
                                },
                                {
                                    'action' : 'filter',
                                    'value' : 'name=desaturate;type=4'  # desaturate method = min
                                },
                                {
                                    'action' : 'newspaper',
                                    'value' : None                      # automatically use right configuration
                                }
                            ]
                    },
                    {
                        'color' : 'M',
                        'process': [
                                {
                                    'action' : 'duplicate',
                                    'value' : '@original'
                                },
                                {
                                    'action' : 'new',
                                    'value' : {
                                                'type' : 'filllayer',
                                                'color' :  QColor(Qt.magenta)
                                            }
                                },
                                {
                                    'action' : 'blending mode',
                                    'value' : 'add'
                                },
                                {
                                    'action' : 'merge down',
                                    'value' : None
                                },
                                {
                                    'action' : 'blending mode',
                                    'value' : 'multiply'
                                },
                                {
                                    'action' : 'filter',
                                    'value' : 'name=desaturate;type=4'  # desaturate method = min
                                },
                                {
                                    'action' : 'newspaper',
                                    'value' : None                      # automatically use right configuration
                                }
                            ]
                    },
                    {
                        'color' : 'C',
                        'process': [
                                {
                                    'action' : 'duplicate',
                                    'value' : '@original'
                                },
                                {
                                    'action' : 'new',
                                    'value' : {
                                                'type' : 'filllayer',
                                                'color' :  QColor(Qt.cyan)
                                            }
                                },
                                {
                                    'action' : 'blending mode',
                                    'value' : 'add'
                                },
                                {
                                    'action' : 'merge down',
                                    'value' : None
                                },
                                {
                                    'action' : 'blending mode',
                                    'value' : 'multiply'
                                },
                                {
                                    'action' : 'filter',
                                    'value' : 'name=desaturate;type=4'  # desaturate method = min
                                },
                                {
                                    'action' : 'newspaper',
                                    'value' : None                      # automatically use right configuration
                                }
                            ]
                    }
                ]
    },
    OUTPUT_MODE_CMYK : {
        'description' : 'Decompose image a into four color CMYK halftone, as used in color printing (optmised for pictures)',
        'groupLayerName' : 'Newspaper (CMYK)',
        'layers' : [
                    {
                        'color' : 'K',
                        'process': [
                                {
                                    'action' : 'duplicate',
                                    'value' : '@original'
                                },
                                {
                                    'action' : 'filter',
                                    'value' : 'name=desaturate;type=5'  # desaturate method = max
                                },
                                {
                                    'action' : 'newspaper',
                                    'value' : None                      # automatically use right configuration
                                }
                            ]
                    },
                    {
                        'color' : 'Y',
                        'process': [
                                {
                                    'action' : 'duplicate',
                                    'value' : '@original'
                                },
                                {
                                    'action' : 'new',
                                    'value' : {
                                                'type' : 'filllayer',
                                                'color' :  QColor(Qt.yellow)
                                            }
                                },
                                {
                                    'action' : 'blending mode',
                                    'value' : 'add'
                                },
                                {
                                    'action' : 'merge down',
                                    'value' : None
                                },
                                {
                                    'action' : 'duplicate',
                                    'value' : '@K'
                                },
                                {
                                    'action' : 'blending mode',
                                    'value' : 'divide'
                                },
                                {
                                    'action' : 'merge down',
                                    'value' : None
                                },
                                {
                                    'action' : 'blending mode',
                                    'value' : 'multiply'
                                },
                                {
                                    'action' : 'filter',
                                    'value' : 'name=desaturate;type=4'  # desaturate method = min
                                },
                                {
                                    'action' : 'newspaper',
                                    'value' : None                      # automatically use right configuration
                                }
                            ]
                    },
                    {
                        'color' : 'M',
                        'process': [
                                {
                                    'action' : 'duplicate',
                                    'value' : '@original'
                                },
                                {
                                    'action' : 'new',
                                    'value' : {
                                                'type' : 'filllayer',
                                                'color' :  QColor(Qt.magenta)
                                            }
                                },
                                {
                                    'action' : 'blending mode',
                                    'value' : 'add'
                                },
                                {
                                    'action' : 'merge down',
                                    'value' : None
                                },
                                {
                                    'action' : 'duplicate',
                                    'value' : '@K'
                                },
                                {
                                    'action' : 'blending mode',
                                    'value' : 'divide'
                                },
                                {
                                    'action' : 'merge down',
                                    'value' : None
                                },
                                {
                                    'action' : 'blending mode',
                                    'value' : 'multiply'
                                },
                                {
                                    'action' : 'filter',
                                    'value' : 'name=desaturate;type=4'  # desaturate method = min
                                },
                                {
                                    'action' : 'newspaper',
                                    'value' : None                      # automatically use right configuration
                                }
                            ]
                    },
                    {
                        'color' : 'C',
                        'process': [
                                {
                                    'action' : 'duplicate',
                                    'value' : '@original'
                                },
                                {
                                    'action' : 'new',
                                    'value' : {
                                                'type' : 'filllayer',
                                                'color' :  QColor(Qt.cyan)
                                            }
                                },
                                {
                                    'action' : 'blending mode',
                                    'value' : 'add'
                                },
                                {
                                    'action' : 'merge down',
                                    'value' : None
                                },
                                {
                                    'action' : 'duplicate',
                                    'value' : '@K'
                                },
                                {
                                    'action' : 'blending mode',
                                    'value' : 'divide'
                                },
                                {
                                    'action' : 'merge down',
                                    'value' : None
                                },
                                {
                                    'action' : 'blending mode',
                                    'value' : 'multiply'
                                },
                                {
                                    'action' : 'filter',
                                    'value' : 'name=desaturate;type=4'  # desaturate method = min
                                },
                                {
                                    'action' : 'newspaper',
                                    'value' : None                      # automatically use right configuration
                                }
                            ]
                    }
                ]
    },
    OUTPUT_MODE_CMYrK : {
        'description' : 'Decompose image a into 4 colors (CMYK) and apply halftone. The <a href="https://en.wikipedia.org/wiki/Rich_black">Registration Black</a> value is obtained as a coombination of Cyan, Magenta and Yellow with additional black',
        'groupLayerName' : 'Newspaper (CMY+rK)',
        'layers' : [
                    {
                        'color' : 'K',
                        'process': [
                                {
                                    'action' : 'duplicate',
                                    'value' : '@original'
                                },
                                {
                                    'action' : 'filter',
                                    'value' : 'name=desaturate;type=5'  # desaturate method = max
                                },
                                {
                                    'action' : 'newspaper',
                                    'value' : None                      # automatically use right configuration
                                }
                            ]
                    },
                    {
                        'color' : 'Y',
                        'process': [
                                {
                                    'action' : 'duplicate',
                                    'value' : '@original'
                                },
                                {
                                    'action' : 'new',
                                    'value' : {
                                                'type' : 'filllayer',
                                                'color' :  QColor(Qt.yellow)
                                            }
                                },
                                {
                                    'action' : 'blending mode',
                                    'value' : 'add'
                                },
                                {
                                    'action' : 'merge down',
                                    'value' : None
                                },
                                {
                                    'action' : 'blending mode',
                                    'value' : 'multiply'
                                },
                                {
                                    'action' : 'filter',
                                    'value' : 'name=desaturate;type=4'  # desaturate method = min
                                },
                                {
                                    'action' : 'newspaper',
                                    'value' : None                      # automatically use right configuration
                                }
                            ]
                    },
                    {
                        'color' : 'M',
                        'process': [
                                {
                                    'action' : 'duplicate',
                                    'value' : '@original'
                                },
                                {
                                    'action' : 'new',
                                    'value' : {
                                                'type' : 'filllayer',
                                                'color' :  QColor(Qt.magenta)
                                            }
                                },
                                {
                                    'action' : 'blending mode',
                                    'value' : 'add'
                                },
                                {
                                    'action' : 'merge down',
                                    'value' : None
                                },
                                {
                                    'action' : 'blending mode',
                                    'value' : 'multiply'
                                },
                                {
                                    'action' : 'filter',
                                    'value' : 'name=desaturate;type=4'  # desaturate method = min
                                },
                                {
                                    'action' : 'newspaper',
                                    'value' : None                      # automatically use right configuration
                                }
                            ]
                    },
                    {
                        'color' : 'C',
                        'process': [
                                {
                                    'action' : 'duplicate',
                                    'value' : '@original'
                                },
                                {
                                    'action' : 'new',
                                    'value' : {
                                                'type' : 'filllayer',
                                                'color' :  QColor(Qt.cyan)
                                            }
                                },
                                {
                                    'action' : 'blending mode',
                                    'value' : 'add'
                                },
                                {
                                    'action' : 'merge down',
                                    'value' : None
                                },
                                {
                                    'action' : 'blending mode',
                                    'value' : 'multiply'
                                },
                                {
                                    'action' : 'filter',
                                    'value' : 'name=desaturate;type=4'  # desaturate method = min
                                },
                                {
                                    'action' : 'newspaper',
                                    'value' : None                      # automatically use right configuration
                                }
                            ]
                    }
                ]
    },

    OUTPUT_MODE_CMYpK1: {
        'description' : 'Decompose image a into four color CMYK halftone (optmised for comics style pictures, method #1)',
        'groupLayerName' : 'Newspaper (CMY+K #1)',
        'layers' : [
                    {
                        'color' : 'KT',
                        'process': [
                                {
                                    'action' : 'duplicate',
                                    'value' : '@original'
                                },
                                {
                                    'action' : 'filter',
                                    'value' : 'name=desaturate;type=5'  # desaturate method = max
                                }
                            ]
                    },
                    {
                        'color' : 'K',
                        'process': [
                                {
                                    'action' : 'duplicate',
                                    'value' : '@KT'
                                }
                            ]
                    },
                    {
                        'color' : 'Y',
                        'process': [
                                {
                                    'action' : 'duplicate',
                                    'value' : '@original'
                                },
                                {
                                    'action' : 'new',
                                    'value' : {
                                                'type' : 'filllayer',
                                                'color' :  QColor(Qt.yellow)
                                            }
                                },
                                {
                                    'action' : 'blending mode',
                                    'value' : 'add'
                                },
                                {
                                    'action' : 'merge down',
                                    'value' : None
                                },
                                {
                                    'action' : 'duplicate',
                                    'value' : '@KT'
                                },
                                {
                                    'action' : 'blending mode',
                                    'value' : 'divide'
                                },
                                {
                                    'action' : 'merge down',
                                    'value' : None
                                },
                                {
                                    'action' : 'blending mode',
                                    'value' : 'multiply'
                                },
                                {
                                    'action' : 'filter',
                                    'value' : 'name=desaturate;type=4'  # desaturate method = min
                                },
                                {
                                    'action' : 'newspaper',
                                    'value' : None                      # automatically use right configuration
                                }
                            ]
                    },
                    {
                        'color' : 'M',
                        'process': [
                                {
                                    'action' : 'duplicate',
                                    'value' : '@original'
                                },
                                {
                                    'action' : 'new',
                                    'value' : {
                                                'type' : 'filllayer',
                                                'color' :  QColor(Qt.magenta)
                                            }
                                },
                                {
                                    'action' : 'blending mode',
                                    'value' : 'add'
                                },
                                {
                                    'action' : 'merge down',
                                    'value' : None
                                },
                                {
                                    'action' : 'duplicate',
                                    'value' : '@KT'
                                },
                                {
                                    'action' : 'blending mode',
                                    'value' : 'divide'
                                },
                                {
                                    'action' : 'merge down',
                                    'value' : None
                                },
                                {
                                    'action' : 'blending mode',
                                    'value' : 'multiply'
                                },
                                {
                                    'action' : 'filter',
                                    'value' : 'name=desaturate;type=4'  # desaturate method = min
                                },
                                {
                                    'action' : 'newspaper',
                                    'value' : None                      # automatically use right configuration
                                }
                            ]
                    },
                    {
                        'color' : 'C',
                        'process': [
                                {
                                    'action' : 'duplicate',
                                    'value' : '@original'
                                },
                                {
                                    'action' : 'new',
                                    'value' : {
                                                'type' : 'filllayer',
                                                'color' :  QColor(Qt.cyan)
                                            }
                                },
                                {
                                    'action' : 'blending mode',
                                    'value' : 'add'
                                },
                                {
                                    'action' : 'merge down',
                                    'value' : None
                                },
                                {
                                    'action' : 'duplicate',
                                    'value' : '@KT'
                                },
                                {
                                    'action' : 'blending mode',
                                    'value' : 'divide'
                                },
                                {
                                    'action' : 'merge down',
                                    'value' : None
                                },
                                {
                                    'action' : 'blending mode',
                                    'value' : 'multiply'
                                },
                                {
                                    'action' : 'filter',
                                    'value' : 'name=desaturate;type=4'  # desaturate method = min
                                },
                                {
                                    'action' : 'newspaper',
                                    'value' : None                      # automatically use right configuration
                                }
                            ]
                    },
                    {
                        'color' : 'KT',
                        'process': [
                                {
                                    'action' : 'remove',
                                    'value' : None
                                }
                            ]
                    },

                ]
    },
    OUTPUT_MODE_CMYpK2: {
        'description' : 'Decompose image a into four color CMYK halftone (optmised for comics style pictures, method #2)',
        'groupLayerName' : 'Newspaper (CMY+K #2)',
        'layers' : [
                    {
                        'color' : 'KT',
                        'process': [
                                {
                                    'action' : 'duplicate',
                                    'value' : '@original'
                                },
                                {
                                    'action' : 'filter',
                                    'value' : 'name=desaturate;type=5'  # desaturate method = max
                                },
                                {
                                    'action' : 'duplicate',
                                    'value' : '@original'
                                },
                                {
                                    'action' : 'filter',
                                    'value' : 'name=desaturate;type=5'  # desaturate method = max
                                },
                                {
                                    'action' : 'blending mode',
                                    'value' : 'add'
                                },
                                {
                                    'action' : 'merge down',
                                    'value' : None
                                }
                            ]
                    },
                    {
                        'color' : 'K',
                        'process': [
                                {
                                    'action' : 'duplicate',
                                    'value' : '@KT'
                                }
                            ]
                    },
                    {
                        'color' : 'Y',
                        'process': [
                                {
                                    'action' : 'duplicate',
                                    'value' : '@original'
                                },
                                {
                                    'action' : 'new',
                                    'value' : {
                                                'type' : 'filllayer',
                                                'color' :  QColor(Qt.yellow)
                                            }
                                },
                                {
                                    'action' : 'blending mode',
                                    'value' : 'add'
                                },
                                {
                                    'action' : 'merge down',
                                    'value' : None
                                },
                                {
                                    'action' : 'duplicate',
                                    'value' : '@KT'
                                },
                                {
                                    'action' : 'blending mode',
                                    'value' : 'divide'
                                },
                                {
                                    'action' : 'merge down',
                                    'value' : None
                                },
                                {
                                    'action' : 'duplicate',
                                    'value' : '@KT'
                                },
                                {
                                    'action' : 'blending mode',
                                    'value' : 'converse'
                                },
                                {
                                    'action' : 'opacity',
                                    'value' : 128
                                },
                                {
                                    'action' : 'merge down',
                                    'value' : None
                                },
                                {
                                    'action' : 'blending mode',
                                    'value' : 'multiply'
                                },
                                {
                                    'action' : 'filter',
                                    'value' : 'name=desaturate;type=4'  # desaturate method = min
                                },
                                {
                                    'action' : 'newspaper',
                                    'value' : None                      # automatically use right configuration
                                }
                            ]
                    },
                    {
                        'color' : 'M',
                        'process': [
                                {
                                    'action' : 'duplicate',
                                    'value' : '@original'
                                },
                                {
                                    'action' : 'new',
                                    'value' : {
                                                'type' : 'filllayer',
                                                'color' :  QColor(Qt.magenta)
                                            }
                                },
                                {
                                    'action' : 'blending mode',
                                    'value' : 'add'
                                },
                                {
                                    'action' : 'merge down',
                                    'value' : None
                                },
                                {
                                    'action' : 'duplicate',
                                    'value' : '@KT'
                                },
                                {
                                    'action' : 'blending mode',
                                    'value' : 'divide'
                                },
                                {
                                    'action' : 'merge down',
                                    'value' : None
                                },
                                {
                                    'action' : 'duplicate',
                                    'value' : '@KT'
                                },
                                {
                                    'action' : 'blending mode',
                                    'value' : 'converse'
                                },
                                {
                                    'action' : 'opacity',
                                    'value' : 128
                                },
                                {
                                    'action' : 'merge down',
                                    'value' : None
                                },
                                {
                                    'action' : 'blending mode',
                                    'value' : 'multiply'
                                },
                                {
                                    'action' : 'filter',
                                    'value' : 'name=desaturate;type=4'  # desaturate method = min
                                },
                                {
                                    'action' : 'newspaper',
                                    'value' : None                      # automatically use right configuration
                                }
                            ]
                    },
                    {
                        'color' : 'C',
                        'process': [
                                {
                                    'action' : 'duplicate',
                                    'value' : '@original'
                                },
                                {
                                    'action' : 'new',
                                    'value' : {
                                                'type' : 'filllayer',
                                                'color' :  QColor(Qt.cyan)
                                            }
                                },
                                {
                                    'action' : 'blending mode',
                                    'value' : 'add'
                                },
                                {
                                    'action' : 'merge down',
                                    'value' : None
                                },
                                {
                                    'action' : 'duplicate',
                                    'value' : '@KT'
                                },
                                {
                                    'action' : 'blending mode',
                                    'value' : 'divide'
                                },
                                {
                                    'action' : 'merge down',
                                    'value' : None
                                },
                                {
                                    'action' : 'duplicate',
                                    'value' : '@KT'
                                },
                                {
                                    'action' : 'blending mode',
                                    'value' : 'converse'
                                },
                                {
                                    'action' : 'opacity',
                                    'value' : 128
                                },
                                {
                                    'action' : 'merge down',
                                    'value' : None
                                },
                                {
                                    'action' : 'blending mode',
                                    'value' : 'multiply'
                                },
                                {
                                    'action' : 'filter',
                                    'value' : 'name=desaturate;type=4'  # desaturate method = min
                                },
                                {
                                    'action' : 'newspaper',
                                    'value' : None                      # automatically use right configuration
                                }
                            ]
                    },
                    {
                        'color' : 'KT',
                        'process': [
                                {
                                    'action' : 'remove',
                                    'value' : None
                                }
                            ]
                    },

                ]
    }
}

TRANSLATIONS_DICT = {
    'colorDepth' : {
        'U8' : '8bits',
        'U16' : '16bits',
        'F16' : '16bits floating point',
        'F32' : '32bits floating point'
    },
    'colorModel' : {
        'A' : 'Alpha mask',
        'RGBA' : 'RGB with alpha channel',
        'XYZA' : 'XYZ with alpha channel',
        'LABA' : 'LAB with alpha channel',
        'CMYKA' : 'CMYK with alpha channel',
        'GRAYA' : 'Gray with alpha channel',
        'YCbCrA' : 'YCbCr with alpha channel'
    },
    'layerType' : {
        'paintlayer' : 'Paint layer',
        'grouplayer' : 'Group layer',
        'filelayer' : 'File layer',
        'filterlayer' : 'Filter layer',
        'filllayer' : 'Fill layer',
        'clonelayer' : 'Clone layer',
        'vectorlayer' : 'Vector layer',
        'transparencymask' : 'Transparency mask',
        'filtermask' : 'Filter mask',
        'transformmask': 'Transform mask',
        'selectionmask': 'Selection mask',
        'colorizemask' : 'Colorize mask'
    }
}


class Newspaper(Extension):

    def __init__(self, parent):
        # Default options
        self.__outputOptions = {
                'originalLayerAction': ORIGINAL_LAYER_KEEPHIDDEN,
                'layerGroupName': '{mode}-{source:name}',
                'layerColorName': '{mode}[{color:short}]-{source:name}',

                'outputMode': OUTPUT_MODE_MONO,
                'outputDotStyle': OUTPUT_DOT_STYLE_CIRCLE,
                'outputSize': 8,
                'outputAdjustment': 0,
                'outputSteadiness': 10,
                'outputSampling': OUTPUT_SAMPLING_MEDIUM,
                'outputAntialasing': OUTPUT_ANTIALIASING_NORMAL,

                'outputMonoDesaturateMode': OUTPUT_MONO_DESMODE_AVERAGE,
                'outputMonoRotation': 45,
                'outputMonoFg': QColor(0xFF000000),
                'outputMonoBg': QColor(0xFFFFFFFF),
                'outputMonoBgTransparent': False,

                'output4CScreenAngle': OUTPUT_4C_SCREENANGLE_US
            }

        self.__sourceDocument = None
        self.__sourceLayer = None

        self.__checkerBoardBrush = QBrush()
        self.__pixmapStylePreviewBlack = {
                'mono': None,
                '4c': None
            }
        self.__pixmapStylePreviewCMYK = {
                'mono': None,
                '4c': None
            }
        self.__stylePreviewModel = {
                'mono': 'black',
                '4c': 'cmyk'
            }
        self.__iconSizeStylePreview = None
        self.__pixmapStylePreviewApplied = None
        self.__stylePreviewModelNeedRefresh = False

        self.createCheckerBoard()

        # Always initialise the superclass.
        # This is necessary to create the underlying C++ object
        super().__init__(parent)
        self.parent = parent


    def createCheckerBoard(self):
        tmpPixmap = QPixmap(32,32)
        tmpPixmap.fill(QColor(255,255,255))
        brush = QBrush(QColor(220,220,220))

        canvas = QPainter()
        canvas.begin(tmpPixmap)
        canvas.setPen(Qt.NoPen)

        canvas.setRenderHint(QPainter.Antialiasing, False)
        canvas.fillRect(QRect(0, 0, 16, 16), brush)
        canvas.fillRect(QRect(16, 16, 16, 16), brush)
        canvas.end()

        self.__checkerBoardBrush = QBrush(tmpPixmap)


    def setup(self):
        """Is executed at Krita's startup"""
        pass


    def createActions(self, window):
        action = window.createAction(EXTENSION_ID, PLUGIN_MENU_ENTRY, "tools/scripts")
        action.triggered.connect(self.action_triggered)


    def dBoxMessage(self, msgType, msg):
        """Simplified function for DialogBox 'OK' message"""
        if msgType == DBOX_WARNING:
            QMessageBox.warning(
                    QWidget(),
                    PLUGIN_DIALOG_TITLE,
                    msg
                )
        else:
            QMessageBox.information(
                    QWidget(),
                    PLUGIN_DIALOG_TITLE,
                    msg
                )


    def action_triggered(self):
        """Action called when script is executed from Kitra menu"""
        if self.checkCurrentLayer():
            if self.openDialogOptions():
                self.run()


    def translateDictKey(self, key, value):
        """Translate key from dictionnary (mostly internal Krita internal values) to human readable values"""
        returned = i18n('Unknown')

        if key in TRANSLATIONS_DICT.keys():
            if value in TRANSLATIONS_DICT[key].keys():
                returned = i18n(TRANSLATIONS_DICT[key][value])

        return returned


    def checkCurrentLayer(self):
        """Check if current layer is valid
           - A document must be opened
           - Active layer properties must be:
             . Layer type:  a paint layer
             . Color model: RGBA
             . Color depth: 8bits
        """
        self.__sourceDocument = Application.activeDocument()
        # Check if there's an active document
        if self.__sourceDocument is None:
            self.dBoxMessage(DBOX_WARNING, "There's no active document!")
            return False

        self.__sourceLayer = self.__sourceDocument.activeNode()

        # Check if current layer can be processed
        if self.__sourceLayer.type() != "paintlayer" or self.__sourceLayer.colorModel() != "RGBA" or self.__sourceLayer.colorDepth() != "U8":
            self.dBoxMessage(DBOX_WARNING, i18n("Selected layer must be a 8bits RGBA Paint Layer!"
                                                "\n\nCurrent layer '{0}' properties:"
                                                "\n- Layer type: {1}"
                                                "\n- Color model: {2} ({3})"
                                                "\n- Color depth: {4}"
                                                "\n\n> Action is cancelled".format(self.__sourceLayer.name(),
                                                                                   self.translateDictKey('layerType', self.__sourceLayer.type()),
                                                                                   self.__sourceLayer.colorModel(), self.translateDictKey('colorModel', self.__sourceLayer.colorModel()),
                                                                                   self.translateDictKey('colorDepth', self.__sourceLayer.colorDepth())
                                            )
                            ))
            return False

        return True


    def openDialogOptions(self):
        """Open dialog box to let user define channel extraction options"""

        self.inSizeEvent=False
        previewBaSrc = QByteArray()
        inInit=True


        # ----------------------------------------------------------------------
        def uiSetBtColor(button, color):
            """Set button color (ie: might be foreground/background buttons)"""
            iconSize = QSize(button.frameSize().width() - 8, button.frameSize().height() - 8)
            iconImg = QImage(iconSize, QImage.Format_ARGB32)
            iconImg.fill(color)
            button.setIcon(QIcon(QPixmap.fromImage(iconImg)))
            button.setIconSize(iconSize)

        def uiColorDialog(currentColor, colorName):
            """Open color dialog box with given dialog title and preselected color"""
            returnedColor = QColorDialog.getColor(currentColor, None, colorName, QColorDialog.DontUseNativeDialog)
            if returnedColor.isValid():
                return returnedColor
            return currentColor

        def uiBuildStylePreview():
            """Generate style preview"""
            if inInit:
                return

            outputWidth = dlgMain.btStylePreview.frameSize().width() - 8
            outputHeight = dlgMain.btStylePreview.frameSize().height() - 8
            iconSizeStylePreview = QSize(outputWidth, outputHeight)

            currentMode = '4c'
            if self.__outputOptions['outputMode'] == OUTPUT_MODE_MONO:
                currentMode = 'mono'


            # build preview model if needed
            if self.__pixmapStylePreviewBlack[currentMode] is None:
                gradient = QLinearGradient(QPointF(10, 0), QPointF(outputWidth - 10, outputHeight));
                gradient.setColorAt(0, Qt.black);
                gradient.setColorAt(1, Qt.white);

                self.__pixmapStylePreviewBlack[currentMode] = QPixmap(outputWidth,outputHeight)

                canvas = QPainter()
                canvas.begin(self.__pixmapStylePreviewBlack[currentMode])
                canvas.fillRect(QRect(0,0,outputWidth, outputHeight), gradient);
                canvas.end()

            if self.__pixmapStylePreviewCMYK[currentMode] is None:
                gradient = QLinearGradient(QPointF(10, 0), QPointF(outputWidth - 10, outputHeight));
                gradient.setColorAt(0, Qt.black);
                gradient.setColorAt(0.125, Qt.white);
                gradient.setColorAt(0.25, Qt.red);
                gradient.setColorAt(0.375, Qt.yellow);
                gradient.setColorAt(0.5, Qt.green);
                gradient.setColorAt(0.625, Qt.cyan);
                gradient.setColorAt(0.75, Qt.blue);
                gradient.setColorAt(0.875, Qt.magenta);
                gradient.setColorAt(1, Qt.red);

                self.__pixmapStylePreviewCMYK[currentMode] = QPixmap(outputWidth,outputHeight)

                path = QPainterPath(QPointF(0, outputHeight/2))
                path.cubicTo(QPointF(outputWidth * 0.125, outputHeight * 0.25), QPointF(outputWidth * 0.375, outputHeight * 0.25), QPointF(outputWidth/2, outputHeight/2))
                path.cubicTo(QPointF(outputWidth * 0.625, outputHeight * 0.75), QPointF(outputWidth * 0.875, outputHeight * 0.75), QPointF(outputWidth, outputHeight/2))
                path.cubicTo(QPointF(outputWidth * 0.625, outputHeight * 0.65), QPointF(outputWidth * 0.875, outputHeight * 0.65), QPointF(outputWidth/2, outputHeight/2))
                path.cubicTo(QPointF(outputWidth * 0.125, outputHeight * 0.35), QPointF(outputWidth * 0.375, outputHeight * 0.35), QPointF(0, outputHeight/2))
                path.closeSubpath()

                canvas = QPainter()
                canvas.begin(self.__pixmapStylePreviewCMYK[currentMode])
                canvas.fillRect(QRectF(0,0,outputWidth, outputHeight), gradient);
                canvas.setBrush(QBrush(QColor(Qt.black), Qt.SolidPattern))
                canvas.setPen(QPen(Qt.NoPen))
                canvas.setRenderHint(QPainter.Antialiasing, True)
                canvas.fillPath(path, QBrush(QColor(Qt.black), Qt.SolidPattern))

                canvas.end()



            if self.__stylePreviewModel[currentMode] == 'black':
                srcPixmap = self.__pixmapStylePreviewBlack[currentMode]
            else:
                srcPixmap = self.__pixmapStylePreviewCMYK[currentMode]


            # create a temporary document to work; work on visible part of preview only
            tmpDocument = Application.createDocument(outputWidth, outputHeight, "tmp", "RGBA", "U8", "", self.__sourceDocument.resolution())

            # create a layer used as original layer
            tmpLayer = tmpDocument.createNode("tmpLayer", "paintlayer")
            tmpDocument.rootNode().addChildNode(tmpLayer, None)
            # and set original image content
            EKritaNode.fromQPixmap(tmpLayer, srcPixmap)

            # execute process
            tmpGroupLayer = self.process(tmpDocument, tmpLayer, None)

            if self.__outputOptions['outputMonoBgTransparent']:
                self.__pixmapStylePreviewApplied = QPixmap(outputWidth, outputHeight)
                canvas = QPainter()
                canvas.begin(self.__pixmapStylePreviewApplied)
                canvas.fillRect(QRect(0, 0, outputWidth, outputHeight), self.__checkerBoardBrush)
                canvas.drawPixmap(0, 0, EKritaNode.toQPixmap(tmpGroupLayer))
                canvas.end()
            else:
                #self.__pixmapStylePreviewApplied = QPixmap.fromImage( QImage(tmpGroupLayer.projectionPixelData(0, 0, outputWidth, outputHeight), outputWidth, outputHeight, QImage.Format_ARGB32))
                self.__pixmapStylePreviewApplied = EKritaNode.toQPixmap(tmpGroupLayer)

            dlgMain.btStylePreview.setIcon(QIcon(self.__pixmapStylePreviewApplied))
            dlgMain.btStylePreview.setIconSize(iconSizeStylePreview)


            tmpDocument.close()

        def uiBuildPreview():
            # set size of progress bar identical to button to avoid preview being resized
            if not inInit:
                dlgMain.pbProgress.reset()
                dlgMain.pbProgress.setFixedHeight(dlgMain.btRefresh.height())
                dlgMain.btRefresh.setVisible(False)
                dlgMain.pbProgress.setVisible(True)

                # calculate viewport (top/left, width/height) for current preview
                viewPort = dlgMain.scraPreview.frameRect()
                viewPort.setLeft(dlgMain.scraPreview.horizontalScrollBar().value())
                viewPort.setTop(dlgMain.scraPreview.verticalScrollBar().value())
                # need to update width/height with top/left properties
                viewPort.setWidth(viewPort.left() + viewPort.width())
                viewPort.setHeight(viewPort.top() + viewPort.height())

                if viewPort.width() > self.__sourceDocument.width():
                    viewPort.setWidth(self.__sourceDocument.width())
                if viewPort.height() > self.__sourceDocument.height():
                    viewPort.setHeight(self.__sourceDocument.height())

                # create a temporary document to work; work on visible part of preview only
                tmpDocument = Application.createDocument(viewPort.width(), viewPort.height(), "tmp", "RGBA", "U8", "", 120.0)

                # create a layer used as original layer
                tmpLayer = tmpDocument.createNode("tmpLayer", "paintlayer")
                tmpDocument.rootNode().addChildNode(tmpLayer, None)

                # and set original image content
                tmpLayer.setPixelData(self.__sourceLayer.pixelData(viewPort.left(),
                                                                   viewPort.top(),
                                                                   viewPort.width(),
                                                                   viewPort.height()),
                                                                   0, 0,
                                                                   viewPort.width(),
                                                                   viewPort.height())

                # execute process
                tmpGroupLayer = self.process(tmpDocument, tmpLayer, dlgMain.pbProgress)

                #tmpLayer.setVisible(False)
                #tmpGroupLayer.setVisible(True)
                tmpDocument.refreshProjection()

                # prepare final rendered image
                # a) original image with 'empty' area from processed rect
                # b) final image image with checkerboard
                # c) paste original image
                # d) paste process result
                srcPixmap = EKritaNode.toQPixmap(self.__sourceLayer, self.__sourceDocument)
                canvas = QPainter()
                canvas.begin(srcPixmap)
                canvas.setCompositionMode(QPainter.CompositionMode_Clear)
                canvas.fillRect(QRect(viewPort.left(), viewPort.top(), tmpDocument.width(), tmpDocument.height()), QBrush(QColor(Qt.white)))
                canvas.end()

                previewResult = QPixmap(self.__sourceDocument.width(), self.__sourceDocument.height())
                canvas.begin(previewResult)
                canvas.fillRect(QRect(0, 0, self.__sourceDocument.width(), self.__sourceDocument.height()), self.__checkerBoardBrush)
                canvas.drawPixmap(0, 0, srcPixmap)
                canvas.drawPixmap(viewPort.left() + tmpGroupLayer.bounds().left(),
                                  viewPort.top() + tmpGroupLayer.bounds().top(),
                                  EKritaNode.toQPixmap(tmpGroupLayer))
                canvas.end()

                dlgMain.lblPreview.setPixmap(previewResult)

                tmpDocument.close()
                dlgMain.pbProgress.setVisible(False)
                dlgMain.btRefresh.setVisible(True)
            else:
                previewResult = QPixmap(self.__sourceDocument.width(), self.__sourceDocument.height())

                canvas = QPainter()
                canvas.begin(previewResult)
                canvas.fillRect(QRect(0, 0, self.__sourceDocument.width(), self.__sourceDocument.height()), self.__checkerBoardBrush)
                canvas.drawPixmap(0, 0, EKritaNode.toQPixmap(self.__sourceLayer, self.__sourceDocument))
                canvas.end()
                dlgMain.lblPreview.setPixmap(previewResult)

        # ----------------------------------------------------------------------
        # Define signal and slots for UI widgets
        def btStylePreviewEvent(event):

            currentMode = '4c'
            if self.__outputOptions['outputMode'] == OUTPUT_MODE_MONO:
                currentMode = 'mono'

            # mouse is over button
            if event.type() == QEvent.Enter:
                if self.__stylePreviewModel[currentMode] == 'black':
                    dlgMain.btStylePreview.setIcon(QIcon(self.__pixmapStylePreviewBlack[currentMode]))
                else:
                    dlgMain.btStylePreview.setIcon(QIcon(self.__pixmapStylePreviewCMYK[currentMode]))

                return True
            elif event.type() == QEvent.Leave:
                # mouse leaved button
                if self.__stylePreviewModelNeedRefresh:
                    self.__stylePreviewModelNeedRefresh = False
                    uiBuildStylePreview()
                dlgMain.btStylePreview.setIcon(QIcon(self.__pixmapStylePreviewApplied))
                return True
            return False

        @pyqtSlot('QString')
        def btStylePreview_Clicked(checked):
            currentMode = '4c'
            if self.__outputOptions['outputMode'] == OUTPUT_MODE_MONO:
                currentMode = 'mono'

            # switch model for color mode
            if self.__stylePreviewModel[currentMode] == 'black':
                self.__stylePreviewModel[currentMode] = 'cmyk'
                dlgMain.btStylePreview.setIcon(QIcon(self.__pixmapStylePreviewCMYK[currentMode]))
            else:
                self.__stylePreviewModel[currentMode] = 'black'
                dlgMain.btStylePreview.setIcon(QIcon(self.__pixmapStylePreviewBlack[currentMode]))

            self.__stylePreviewModelNeedRefresh = True

        @pyqtSlot('QString')
        def ledLayerGroupName_Changed(value):
            self.__outputOptions['layerGroupName'] = value

        @pyqtSlot('QString')
        def ledLayerColorName_Changed(value):
            self.__outputOptions['layerColorName'] = value

        @pyqtSlot('QString')
        def cmbMode_Changed(value):
            self.__outputOptions['outputMode'] = value

            if value == OUTPUT_MODE_MONO:
                isVisible = True
            else:
                isVisible = False

            dlgMain.lblMonoDesaturateMode.setVisible(isVisible)
            dlgMain.cmbMonoDesaturateMode.setVisible(isVisible)

            dlgMain.lblMonoRotation.setVisible(isVisible)
            dlgMain.wMonoRotation.setVisible(isVisible)

            dlgMain.lblMonoFgColor.setVisible(isVisible)
            dlgMain.btMonoFgColor.setVisible(isVisible)

            dlgMain.lblMonoFgColor.setVisible(isVisible)
            dlgMain.btMonoFgColor.setVisible(isVisible)

            dlgMain.lblMonoBgColor.setVisible(isVisible)
            dlgMain.wMonoBgColor.setVisible(isVisible)

            dlgMain.lblScreenAngle.setVisible(not isVisible)
            dlgMain.cmb4CScreenAngle.setVisible(not isVisible)

            uiBuildStylePreview()

        @pyqtSlot('QString')
        def cmbDotStyle_Changed(value):
            self.__outputOptions['outputDotStyle'] = value
            uiBuildStylePreview()

        @pyqtSlot('QString')
        def hsldAdjustment_Changed(value):
            self.__outputOptions['outputAdjustment'] = value
            uiBuildStylePreview()

        @pyqtSlot('QString')
        def hsldSteadiness_Changed(value):
            self.__outputOptions['outputSteadiness'] = value
            uiBuildStylePreview()

        @pyqtSlot('QString')
        def cmbSampling_Changed(value):
            self.__outputOptions['outputSampling'] = value
            uiBuildStylePreview()

        @pyqtSlot('QString')
        def cmbAntialiasing_Changed(value):
            self.__outputOptions['outputAntialasing'] = value
            uiBuildStylePreview()

        @pyqtSlot('QString')
        def cmbMonoDesaturateMode_Changed(value):
            self.__outputOptions['outputMonoDesaturateMode'] = value
            uiBuildStylePreview()

        @pyqtSlot('QString')
        def hsldMonoRotation_Changed(value):
            self.__outputOptions['outputMonoRotation'] = value
            uiBuildStylePreview()

        @pyqtSlot('QString')
        def btMonoFgColor_Clicked(checked):
            self.__outputOptions['outputMonoFg'] = uiColorDialog(self.__outputOptions['outputMonoFg'], "Foreground color")
            uiSetBtColor(dlgMain.btMonoFgColor, self.__outputOptions['outputMonoFg'])
            uiBuildStylePreview()

        @pyqtSlot('QString')
        def btMonoBgColor_Clicked(checked):
            self.__outputOptions['outputMonoBg'] = uiColorDialog(self.__outputOptions['outputMonoBg'], "Background color")
            uiSetBtColor(dlgMain.btMonoBgColor, self.__outputOptions['outputMonoBg'])
            uiBuildStylePreview()

        @pyqtSlot('QString')
        def cbxMonoBgTransparent_Changed(value):
            self.__outputOptions['outputMonoBgTransparent'] = value
            dlgMain.btMonoBgColor.setEnabled(not value)
            uiBuildStylePreview()

        @pyqtSlot('QString')
        def cmb4CScreenAngle_Changed(value):
            self.__outputOptions['output4CScreenAngle'] = value
            uiBuildStylePreview()

        @pyqtSlot('QString')
        def cmbOriginalLayer_Changed(value):
            self.__outputOptions['originalLayerAction'] = value

        @pyqtSlot('QString')
        def leNewLayerGroupName_Changed(value):
            self.__outputOptions['layerGroupName'] = value

        @pyqtSlot('QString')
        def leNewLayerColorName_Changed(value):
            self.__outputOptions['layerColorName'] = value



        @pyqtSlot('QString')
        def btRefresh_Clicked(checked):
            uiBuildPreview()


        def onDspbxSizeChanged(value):
            if self.inSizeEvent:
                return

            inSizeEvent = True
            dlgMain.hsldSize.setValue(int(value * 100))
            self.__outputOptions['outputSize'] = value
            uiBuildStylePreview()
            inSizeEvent = False


        def onHsldSizeChanged(value):
            if self.inSizeEvent:
                return
            inSizeEvent = True
            dlgMain.dspbxSize.setValue(value / 100)
            inSizeEvent = False


        def onDialogShown():
            """Called when dialog is shown"""
            dlgMain.grpbOptionsOutput.setMaximumSize(dlgMain.grpbOptionsOutput.size())
            dlgMain.grpbLayers.setMaximumSize(dlgMain.grpbOptionsOutput.size())
            uiBuildStylePreview()

        # ----------------------------------------------------------------------
        # Create dialog box
        uiFileName = os.path.join(os.path.dirname(__file__), 'mainwindow.ui')
        dlgMain = EDialog.loadUi(uiFileName)

        dlgMain.setWindowTitle(PLUGIN_DIALOG_TITLE)
        dlgMain.dialogShown.connect(onDialogShown)



        # ......................................................................
        # Define values & connectors

        dlgMain.cmbMode.addItems([
                OUTPUT_MODE_MONO,
                OUTPUT_MODE_CMY,
                OUTPUT_MODE_CMYK,
                OUTPUT_MODE_CMYrK,
                OUTPUT_MODE_CMYpK1,
                OUTPUT_MODE_CMYpK2
            ])
        dlgMain.cmbMode.setCurrentText(self.__outputOptions['outputMode'])
        dlgMain.cmbMode.currentTextChanged.connect(cmbMode_Changed)
        dlgMain.cmbMode.currentTextChanged.emit(self.__outputOptions['outputMode'])

        dlgMain.btStylePreview.setText("")
        uiSetBtColor(dlgMain.btMonoFgColor, self.__outputOptions['outputMonoFg'])
        dlgMain.btStylePreview.clicked.connect(btStylePreview_Clicked)
        dlgMain.setEventCallback(dlgMain.btStylePreview, btStylePreviewEvent)


        dlgMain.cmbDotStyle.addItems([
                OUTPUT_DOT_STYLE_CIRCLE,
                OUTPUT_DOT_STYLE_DIAMOND,
                OUTPUT_DOT_STYLE_SQUARE,
                OUTPUT_DOT_STYLE_LINEFLAT,
                OUTPUT_DOT_STYLE_LINEROUND
            ])
        dlgMain.cmbDotStyle.setCurrentText(self.__outputOptions['outputDotStyle'])
        dlgMain.cmbDotStyle.currentTextChanged.connect(cmbDotStyle_Changed)

        dlgMain.hsldSize.valueChanged.connect(lambda v: onHsldSizeChanged(v))
        dlgMain.dspbxSize.valueChanged[float].connect(lambda v: onDspbxSizeChanged(v))
        dlgMain.hsldSize.setValue(self.__outputOptions['outputSize'] * 100)


        dlgMain.hsldAdjustment.setValue(self.__outputOptions['outputAdjustment'])
        dlgMain.hsldAdjustment.valueChanged.connect(hsldAdjustment_Changed)

        dlgMain.hsldSteadiness.setValue(self.__outputOptions['outputSteadiness'])
        dlgMain.hsldSteadiness.valueChanged.connect(hsldSteadiness_Changed)


        dlgMain.cmbSampling.addItems([
                OUTPUT_SAMPLING_LOW,
                OUTPUT_SAMPLING_MEDIUM,
                OUTPUT_SAMPLING_HIGH
            ])
        dlgMain.cmbSampling.setCurrentText(self.__outputOptions['outputSampling'])
        dlgMain.cmbSampling.currentTextChanged.connect(cmbSampling_Changed)

        dlgMain.cmbAntialiasing.addItems([
                OUTPUT_ANTIALIASING_NONE,
                OUTPUT_ANTIALIASING_NORMAL,
                OUTPUT_ANTIALIASING_SOFT
            ])
        dlgMain.cmbAntialiasing.setCurrentText(self.__outputOptions['outputAntialasing'])
        dlgMain.cmbAntialiasing.currentTextChanged.connect(cmbAntialiasing_Changed)


        dlgMain.cmbMonoDesaturateMode.addItems([
            OUTPUT_MONO_DESMODE_LIGHTNESS,
            OUTPUT_MONO_DESMODE_LUMINOSITY709,
            OUTPUT_MONO_DESMODE_LUMINOSITY601,
            OUTPUT_MONO_DESMODE_AVERAGE,
            OUTPUT_MONO_DESMODE_MINIMUM,
            OUTPUT_MONO_DESMODE_MAXIMUM
        ])
        dlgMain.cmbMonoDesaturateMode.setCurrentText(self.__outputOptions['outputMonoDesaturateMode'])
        dlgMain.cmbMonoDesaturateMode.currentTextChanged.connect(cmbMonoDesaturateMode_Changed)


        dlgMain.hsldMonoRotation.setValue(self.__outputOptions['outputMonoRotation'])
        dlgMain.hsldMonoRotation.valueChanged.connect(hsldMonoRotation_Changed)


        dlgMain.btMonoFgColor.setText("")
        uiSetBtColor(dlgMain.btMonoFgColor, self.__outputOptions['outputMonoFg'])
        dlgMain.btMonoFgColor.setMaximumSize(dlgMain.btMonoFgColor.size())
        dlgMain.btMonoFgColor.clicked.connect(btMonoFgColor_Clicked)

        dlgMain.btMonoBgColor.setText("")
        uiSetBtColor(dlgMain.btMonoBgColor, self.__outputOptions['outputMonoBg'])
        dlgMain.btMonoBgColor.setMaximumSize(dlgMain.btMonoBgColor.size())
        dlgMain.btMonoBgColor.clicked.connect(btMonoBgColor_Clicked)

        dlgMain.cbxMonoBgTransparent.clicked.connect(cbxMonoBgTransparent_Changed)

        dlgMain.cmb4CScreenAngle.addItems([
                OUTPUT_4C_SCREENANGLE_US,
                OUTPUT_4C_SCREENANGLE_EU
            ])
        dlgMain.cmb4CScreenAngle.setCurrentText(self.__outputOptions['output4CScreenAngle'])
        dlgMain.cmb4CScreenAngle.currentTextChanged.connect(cmb4CScreenAngle_Changed)


        dlgMain.cmbOriginalLayer.addItems([
            ORIGINAL_LAYER_KEEPUNCHANGED,
            ORIGINAL_LAYER_KEEPVISIBLE,
            ORIGINAL_LAYER_KEEPHIDDEN,
            ORIGINAL_LAYER_REMOVE
        ])
        dlgMain.cmbOriginalLayer.setCurrentText(self.__outputOptions['originalLayerAction'])
        dlgMain.cmbOriginalLayer.currentTextChanged.connect(cmbOriginalLayer_Changed)

        dlgMain.leNewLayerGroupName.setText(self.__outputOptions['layerGroupName'])
        dlgMain.leNewLayerGroupName.textChanged.connect(leNewLayerGroupName_Changed)
        dlgMain.leNewLayerColorName.setText(self.__outputOptions['layerColorName'])
        dlgMain.leNewLayerColorName.textChanged.connect(leNewLayerColorName_Changed)


        dlgMain.lblPreview.resize(self.__sourceDocument.width(), self.__sourceDocument.height())
        dlgMain.scraWidgetContentsPreview.resize(self.__sourceDocument.width(), self.__sourceDocument.height())
        uiBuildPreview()




        dlgMain.btRefresh.clicked.connect(btRefresh_Clicked)

        dlgMain.pbProgress.setVisible(False)

        dlgMain.verticalLayout_options.addStretch()


        dlgMain.dbbxOkCancel.accepted.connect(dlgMain.accept)
        dlgMain.dbbxOkCancel.rejected.connect(dlgMain.reject)

        inInit = False
        returned = dlgMain.exec_()

        return returned


    def progressNext(self, pProgress):
        """Update progress bar"""
        if pProgress is not None:
            stepCurrent=pProgress.value()+1
            pProgress.setValue(stepCurrent)
            QApplication.instance().processEvents()


    def run(self):
        """Run process for current layer"""

        pdlgProgress = QProgressDialog(self.__outputOptions['outputMode'], None, 0, 100, Application.activeWindow().qwindow())
        pdlgProgress.setWindowTitle(PLUGIN_DIALOG_TITLE)
        pdlgProgress.setMinimumSize(640, 200)
        pdlgProgress.setModal(True)
        pdlgProgress.show()

        self.process(self.__sourceDocument, self.__sourceLayer, pdlgProgress)

        pdlgProgress.close()


    def process(self, pDocument, pOriginalLayer, pProgress):
        """Process given layer with current options"""

        self.layerNum = 0
        document = pDocument
        originalLayer = pOriginalLayer
        parentGroupLayer = None
        currentProcessedLayer = None
        originalLayerIsVisible = originalLayer.visible()

        def getLayerByName(parent, value):
            """search and return a layer by name, within given parent group"""
            if parent == None:
                return document.nodeByName(value)

            for layer in parent.childNodes():
                if layer.name() == value:
                    return layer

            return None


        def duplicateLayer(currentProcessedLayer, value):
            """Duplicate layer from given name
               New layer become active layer
            """

            newLayer = None
            srcLayer = None
            srcName = re.match("^@(.*)", value)

            if not srcName is None:
                # reference to a specific layer
                if srcName[1] == 'original':
                    # original layer currently processed
                    srcLayer = originalLayer
                else:
                    # a color layer previously built (and finished)
                    srcLayer = getLayerByName(parentGroupLayer, parseLayerName(self.__outputOptions['layerColorName'], srcName[1]))
            else:
                # a layer with a fixed name
                srcLayer = document.nodeByName(parseLayerName(value, ''))


            if not srcLayer is None:
                newLayer = srcLayer.duplicate()

                self.layerNum+=1
                newLayer.setName("np-d{0}".format(self.layerNum))

                parentGroupLayer.addChildNode(newLayer, currentProcessedLayer)

                return newLayer
            else:
                return None


        def newLayer(currentProcessedLayer, value):
            """Create a new layer of given type
               New layer become active layer
            """

            newLayer = None

            if value is None or not value['type'] in ['filllayer']:
                # given type for new layer is not valid
                # currently only one layer type is implemented
                return None

            if value['type'] == 'filllayer':
                infoObject = InfoObject();
                infoObject.setProperty("color", value['color'])
                selection = Selection();
                selection.select(0, 0, document.width(), document.height(), 255)

                newLayer = document.createFillLayer(value['color'].name(), "color", infoObject, selection)

            if newLayer:
                self.layerNum+=1
                newLayer.setName("np-n{0}".format(self.layerNum))

                parentGroupLayer.addChildNode(newLayer, currentProcessedLayer)

                # Need to force generator otherwise, information provided when creating layer seems to not be taken in
                # account
                newLayer.setGenerator("color", infoObject)

                return newLayer
            else:
                return None


        def removeLayer(currentProcessedLayer, value):
            """Remove layer"""
            currentProcessedLayer.remove()

            return None


        def mergeDown(currentProcessedLayer, value):
            """Merge current layer with layer below"""
            if currentProcessedLayer is None:
                return None

            newLayer = currentProcessedLayer.mergeDown()
            # note:
            #   when layer is merged down:
            #   - a new layer seems to be created (reference to 'down' layer does not match anymore layer in group)
            #   - retrieved 'newLayer' reference does not match to new layer resulting from merge
            #   - activeNode() in document doesn't match to new layer resulting from merge
            #   maybe it's normal, maybe not...
            #   but the only solution to be able to work on merged layer (with current script) is to consider that from
            #   parent node, last child match to last added layer and then, to our merged layer
            # (works if the merged layer was the last from parent node)
            currentProcessedLayer = parentGroupLayer.childNodes()[-1]
            # for an unknown reason, merged layer bounds are not corrects... :'-(
            currentProcessedLayer.cropNode(0, 0, document.width(), document.height())
            return currentProcessedLayer


        def applyBlendingMode(currentProcessedLayer, value):
            """Set blending mode for current layer"""
            if currentProcessedLayer is None or value is None or value == '':
                return False

            currentProcessedLayer.setBlendingMode(value)
            return True


        def applyOpacity(currentProcessedLayer, value):
            """Set opacity current layer"""
            if currentProcessedLayer is None or value is None or value == '':
                return False

            currentProcessedLayer.setOpacity(value)
            return True


        def applyFilter(currentProcessedLayer, value):
            """Apply filter to layer"""
            if currentProcessedLayer is None or value is None or value == '':
                return None

            filterName = re.match("name=([^;]+)", value)

            if filterName is None:
                return None

            filter = Application.filter(filterName.group(1))
            filterConfiguration = filter.configuration()

            for parameter in value.split(';'):
                parameterName = re.match("^([^=]+)=(.*)", parameter)

                if not parameterName is None and parameterName != 'name':
                    filterConfiguration.setProperty(parameterName.group(1), parameterName.group(2).replace('\;',';'))

            filter.setConfiguration(filterConfiguration)
            filter.apply(currentProcessedLayer, 0, 0, document.width(), document.height())

            return currentProcessedLayer


        def applyNewspaper(currentProcessedLayer, value, color):
            """Apply newspaper style to layer"""

            # note:
            # as python is slow, code in this function is made in a way that is
            # not intuitive for a python programmer
            # - use array instead of range (faster)
            # - work on bits array instead of pixel object (faster)
            # - use of many [configuration] variables instead of dictionnary (faster)
            # - ...
            def transform(x, y, matrix):
                """Calculate new coordinates according to given transformation matrix"""
                xt = x - matrix[0][2]
                yt = y - matrix[1][2]
                return (xt * matrix[0][0] + yt * matrix[0][1] + matrix[0][2],
                        xt * matrix[1][0] + yt * matrix[1][1] + matrix[1][2])

            #if not pProgress is None:
            #    print(f"Newspaper execution duration[{color}]: start")
            #    startTime = time.time()


            # define configuration
            # do not use hashtable (slower access than a variable)
            configBrush = QBrush(Qt.NoBrush)
            configPen = QPen(Qt.NoPen)
            configBgColor = QColor(Qt.white)
            configRotation = 0                                                  # in radians
            configRotationD = -self.__outputOptions['outputMonoRotation']        # in degree
            configSteadinessValue = self.__outputOptions['outputSteadiness']
            configSteadinessApplied = (self.__outputOptions['outputSteadiness'] < 10)
            configWidth = currentProcessedLayer.bounds().width()
            configHeight = currentProcessedLayer.bounds().height()
            configSampling = True
            configSamplingRange = []
            configDrawMode = 0 # Circle

            if self.__outputOptions['outputMode'] == OUTPUT_MODE_MONO:
                # In Monochrome mode, set background color as defined
                if self.__outputOptions['outputMonoBgTransparent']:
                    configBgColor=QColor(Qt.transparent)
                else:
                    configBgColor=self.__outputOptions['outputMonoBg']

                if self.__outputOptions['outputDotStyle'] == OUTPUT_DOT_STYLE_LINEFLAT:
                    # in line mode, use pen
                    configPen=QPen(self.__outputOptions['outputMonoFg'])
                    configPen.setCapStyle(Qt.FlatCap)
                    configPen.setJoinStyle(Qt.MiterJoin)
                elif self.__outputOptions['outputDotStyle'] == OUTPUT_DOT_STYLE_LINEROUND:
                    # in line mode, use pen
                    configPen=QPen(self.__outputOptions['outputMonoFg'])
                    configPen.setCapStyle(Qt.RoundCap)
                    configPen.setJoinStyle(Qt.MiterJoin)
                else:
                    # otherwise use brush
                    configBrush=QBrush(self.__outputOptions['outputMonoFg'], Qt.SolidPattern)

                if self.__outputOptions['outputMonoRotation'] != 90:
                    # when rotation = 90, do same process than rotation = 0
                    configRotation = radians(self.__outputOptions['outputMonoRotation'])
            else:
                appliedColor = QColor(Qt.black)
                # in CMYK mode, according to current processed layer:
                #   - set foreground color
                #   - set rotation
                appliedColor = OUTPUT_PREDEF_VALUES['4CCOLORS'][color]
                configRotationD = -OUTPUT_PREDEF_VALUES[self.__outputOptions['output4CScreenAngle']][color]
                configRotation = radians(OUTPUT_PREDEF_VALUES[self.__outputOptions['output4CScreenAngle']][color])


                # in CMYK mode, set white background color
                if self.__outputOptions['outputDotStyle'] == OUTPUT_DOT_STYLE_LINEFLAT:
                    # in line mode, use pen
                    configPen=QPen(appliedColor)
                    configPen.setCapStyle(Qt.FlatCap)
                    configPen.setJoinStyle(Qt.MiterJoin)
                elif self.__outputOptions['outputDotStyle'] == OUTPUT_DOT_STYLE_LINEROUND:
                    # in line mode, use pen
                    configPen=QPen(appliedColor)
                    configPen.setCapStyle(Qt.FlatCap)
                    configPen.setJoinStyle(Qt.MiterJoin)
                else:
                    configBrush=QBrush(appliedColor, Qt.SolidPattern)

            # use a number, faster to check than a string
            if self.__outputOptions['outputDotStyle'] == OUTPUT_DOT_STYLE_DIAMOND:
                configDrawMode = 1
            elif self.__outputOptions['outputDotStyle'] == OUTPUT_DOT_STYLE_SQUARE:
                configDrawMode = 2
            elif self.__outputOptions['outputDotStyle'] == OUTPUT_DOT_STYLE_LINEFLAT:
                configDrawMode = 3
            elif self.__outputOptions['outputDotStyle'] == OUTPUT_DOT_STYLE_LINEROUND:
                configDrawMode = 4



            # Calculate dot geometry
            dotSize = self.__outputOptions['outputSize']
            dotAdjustmentValue = dotSize * self.__outputOptions['outputAdjustment']/100
            dotOffset = dotSize + dotAdjustmentValue

            dotiSize=int(dotSize)
            dotHSize = dotSize  / 2
            dotiHSize = int(dotHSize)

            dotFullSizeFactor = 1
            if self.__outputOptions['outputDotStyle'] == OUTPUT_DOT_STYLE_CIRCLE:
                # Calculate factor for rendering 'circle dots' that fill 100% of cell
                #
                #   Cell: area for a 'dot'
                #           Inside square:
                #               W                   : Defined option size
                #               r = W/2             : Half width
                #                                     [=> dotHSize]
                #
                #           Outside circle:
                #               A 100% black dot
                #               When dot is 100% size, cell is full Black
                #               => Dot radius equals to hypotenuse of half-square
                #
                #               R = sqrt(2r²)       : full size radius
                #                                     [=> dotFullSizeFactor]
                #
                #           *******
                #         **+-----+**
                #        ** |   R/| **
                #       **  |   / |  **
                #       **  |  +--+--**
                #       **  |    r| R**
                #        ** |  W  | **
                #         **+-----+**
                #           *******
                #
                dotFullSizeFactor = sqrt( 2*dotHSize*dotHSize )
            elif self.__outputOptions['outputDotStyle'] == OUTPUT_DOT_STYLE_DIAMOND:
                # Calculate factor for rendering 'diamoond dots' that fill 100% of cell
                # These are calculated now to improve calculation performances
                #
                #   Cell: area for a 'dot'
                #           Inside square:
                #               W                   : Defined option size
                #               r = W/2             : Half width
                #                                     [=> fHSize]
                #
                #           Outside circle:
                #               A 100% black dot
                #               When dot is 100% size, cell is full Black
                #
                #               R = 3 * r           : full size radius
                #                                     [=> dotFullSizeFactor]
                #
                #              .
                #             / \
                #            /   \
                #           +-----+
                #          /|     |\
                #         / |     | \
                #        .  |  +--+--.
                #         \ |   r |R/
                #          \|     |/
                #           +-----+
                #            \   /
                #             \ /
                #              .
                #
                dotFullSizeFactor = 1.5 * dotHSize


            # Calculate ranges for on each pixel processing
            # (made now to avoid recalculation on each loop)
            if self.__outputOptions['outputSampling'] == OUTPUT_SAMPLING_HIGH:
                # sample made on ALL pixel
                configSamplingRange = [v for v in range(0, dotiSize, 1)]
            elif self.__outputOptions['outputSampling'] == OUTPUT_SAMPLING_MEDIUM:
                # sample made on one pixel on two
                configSamplingRange = [v for v in range(0, dotiSize, 2)]
            else: # (self.__outputOptions['outputSampling'] == OUTPUT_SAMPLING_LOW:
                # sample made on current pixel only
                configSampling = False


            # calculate bounds
            if configRotation == 0 or configRotation == 90:
                # no rotation, no calculation: bounds are image bounds :-)
                xLeft = -dotiHSize
                xRight = configWidth+dotiHSize

                yTop = -dotiHSize
                yBottom = configHeight+dotiHSize
            else:
                # When a rotation is applied, we need to determinate new bounds
                # Original bounds
                #   (0,0)   => origin coordinates
                #   (w,h)   => bottom/left coordinates
                #   (cx,cy) => rotation center (w/2, h/2)
                #
                # Intermediate calculations
                #   (0',0') => rotated origin coordinates
                #   (w',h') => rotated bottom/left coordinates
                #
                #       (left,top)       (w",0")       (right,top)
                #            *              +                *
                #                         .. ..
                #                       ..     ..
                #             (0,0)   ..         ..     (w,0)
                #               +---..-------------..-----+
                #               | ..                -..   |
                #               ..                     .. |
                #             ..|                        ..
                #     (0',0')+  |         (cx,cy)         |..
                #             ..|            o            |  +(w',h')
                #               ..                        |..
                #               | ..                     ..
                #               |   ..                 .. |
                #               |     ..             ..   |
                #               +-------..---------..-----+
                #             (0,h)       ..     ..     (w,h)
                #                           .. ..
                #            *                +              *
                #       (left,bottom)      (0",h")     (right,bottom)
                #
                #
                # New bounds are defined by:
                #   (left,top)      = (MIN(0, 0'), MIN(0, 0"))
                #   (right,bottom)  = (MAX(w, w'), MAX(h, h"))
                #
                # applied rotation do not rotate image, but rotate scanline angle

                # calculate sinus and cosinus
                rotCos = cos(-configRotation)
                rotSin = sin(-configRotation)


                xMiddle = configWidth / 2
                yMiddle = configHeight / 2

                transformMatrix = [[rotCos, -rotSin, xMiddle],
                                   [rotSin, rotCos, yMiddle]]

                xLeft, tmp = transform(0, 0, transformMatrix)
                xRight, tmp = transform(configWidth, configHeight, transformMatrix)

                tmp, yTop = transform(configWidth, 0, transformMatrix)
                tmp, yBottom = transform(0, configHeight, transformMatrix)

                xLeft = min(0, xLeft)
                xRight = max(configWidth, xRight)

                yTop = min(0, yTop)
                yBottom = max(configHeight, yBottom)

            # calculate positions
            xPositions = [(xLeft + dotOffset * v) for v in range(ceil((xRight - xLeft) / dotOffset))]
            yPositions = [(yTop + dotOffset * v) for v in range(ceil((yBottom - yTop) / dotOffset))]


            # Source is used to determinate pixels values
            imgSrc = EKritaNode.toQImage(currentProcessedLayer)
            srcPixmap = QPixmap.fromImage(imgSrc)

            # WorkingPixmap define pixmap on which newspaper effect will be built
            workingPixmap = QPixmap(configWidth, configHeight)
            workingPixmap.fill(configBgColor)

            canvas = QPainter()
            canvas.begin(workingPixmap)

            canvas.setPen(configPen)
            canvas.setBrush(configBrush)
            canvas.setRenderHint(QPainter.Antialiasing, (self.__outputOptions['outputAntialasing'] != OUTPUT_ANTIALIASING_NONE))

            # Calculate progress information
            totalLoop = len(xPositions) * len(yPositions)
            moduloStep = int(totalLoop / 20)             # 20 considers steps for progress bar
            currentStepnumber = 0
            stepInc = len(yPositions)


            mWidth = configWidth + dotiSize
            mHeight = configHeight + dotiSize


            # working on bits() is faster than working on pixels
            # pixel is stored on 4bytes:
            # Bits[index] = blue
            # Bits[index + 1] = green
            # Bits[index + 2] = red
            # Bits[index + 3] = alpha
            imgSrcBits = imgSrc.bits()
            imgSrcBits.setsize(imgSrc.byteCount())
            imgSrcBitsRowLength = configWidth << 2 # << 2 = *4 but faster

            # start processing image
            for x in xPositions:
                for y in yPositions:

                    if configRotation == 0:
                        # avoid heavy calculations...
                        iXSrc, iYSrc = int(x), int(y)
                        fXSrc, fYSrc = x, y
                    else:
                        fXSrc, fYSrc = transform(x, y, transformMatrix)

                        iXSrc = int(fXSrc)
                        iYSrc = int(fYSrc)

                    if (configSampling and
                        (iXSrc + dotiSize > mWidth or
                         iYSrc + dotiSize > mHeight or
                         iXSrc < -dotiSize or
                         iYSrc < -dotiSize) or
                        not configSampling and
                         (iXSrc < 0 or
                          iYSrc < 0 or
                          iXSrc >= configWidth or
                          iYSrc >= configHeight)):
                        # completely outside viewport, do not process
                        continue

                    # retrieve cell area pixels
                    if configSampling:
                        # do an average calculation of all pixels in area to determinate dot size
                        sumPx = 0
                        nbPx = 0
                        for tx in configSamplingRange:
                            gX = iXSrc + tx
                            if gX < 0 or gX >= configWidth:
                                continue

                            for ty in configSamplingRange:
                                gY = iYSrc + ty
                                if gY < 0 or gY >= configHeight:
                                    continue
                                # use 'x << 2' instead of 'x * 4'
                                # because bitwise operation is faster
                                imgSrcBitsIndex = gY * imgSrcBitsRowLength + (gX << 2)

                                alpha = ord(imgSrcBits[imgSrcBitsIndex + 3])
                                if alpha == 0xFF:
                                    # no alpha, get value
                                    # work on 1byte only (all RGB byte have same value)
                                    sumPx+=ord(imgSrcBits[imgSrcBitsIndex])
                                    nbPx+=1
                                elif alpha > 0:
                                    # alpha, get weighted value
                                    sumPx+=255 - int((255 - ord(imgSrcBits[imgSrcBitsIndex])) * alpha/255)
                                    nbPx+=1
                                # Else
                                #   fully transparent
                                #   do nothing

                        if nbPx > 0:
                            # some pixels have been processed
                            fRadius = (255-sumPx/nbPx)/255
                        else:
                            # nothing to process
                            continue
                    else:
                        # no sampling, only based on current pixel value

                        # use 'x << 2' instead of 'x * 4'
                        # because bitwise operation is faster
                        imgSrcBitsIndex = iYSrc * imgSrcBitsRowLength + (iXSrc << 2)

                        alpha = ord(imgSrcBits[imgSrcBitsIndex + 3])

                        if alpha == 0:
                            # completely transparent, do nothing and process next pixel
                            continue
                        elif alpha == 0xFF:
                            # no transparency, get current value
                            fRadius = (255 - ord(imgSrcBits[imgSrcBitsIndex])) / 255
                        else:
                            # with transparency, apply alpha weight
                            #fRadius2 = (255 - (255 - ord(imgSrcBits[imgSrcBitsIndex])) * alpha/255)/255
                            # factorized calculation
                            fRadius = (65025 + (ord(imgSrcBits[imgSrcBitsIndex]) - 255) * alpha)/65025

                    if dotFullSizeFactor != 1:
                        fRadius *= dotFullSizeFactor
                    else:
                        fRadius *= dotSize

                    if configSteadinessApplied:
                        fRadiusX = fRadius * (1 + ((random.random() - 0.5) / configSteadinessValue))
                        fRadiusY = fRadius * (1 + ((random.random() - 0.5) / configSteadinessValue))
                    else:
                        fRadiusX = fRadius
                        fRadiusY = fRadius

                    if configDrawMode == 0:
                        # circle
                        canvas.drawEllipse(QPointF(fXSrc, fYSrc), fRadiusX, fRadiusY)
                    elif configDrawMode == 1:
                        # diamond
                        canvas.drawPolygon(QPolygonF([QPointF(fXSrc, fYSrc - fRadiusY),
                                                      QPointF(fXSrc + fRadiusX, fYSrc),
                                                      QPointF(fXSrc, fYSrc + fRadiusY),
                                                      QPointF(fXSrc - fRadiusX, fYSrc)])
                                        )
                    elif configDrawMode == 2:
                        # square
                        canvas.fillRect(QRectF(fXSrc - fRadiusX, fYSrc - fRadiusY, fRadiusX, fRadiusY), configBrush)
                    elif configDrawMode == 3:
                        # line
                        configPen.setWidthF(fRadiusX)
                        canvas.setPen(configPen)

                        canvas.save()
                        canvas.translate(fXSrc, fYSrc)
                        canvas.rotate(configRotationD)
                        if configRotation == 0:
                            canvas.drawLine(QPointF(0, dotHSize), QPointF(dotSize, dotHSize))
                        else:
                            canvas.drawLine(QPointF(-0.5, dotHSize), QPointF(dotSize+0.5, dotHSize))
                        canvas.restore()
                    elif configDrawMode == 4:
                        # soft line
                        configPen.setWidthF(fRadiusX)
                        canvas.setPen(configPen)

                        canvas.save()
                        canvas.translate(fXSrc, fYSrc)
                        canvas.rotate(configRotationD)
                        canvas.drawLine(QPointF(0, dotHSize), QPointF(dotSize, dotHSize))
                        canvas.restore()

                if not pProgress is None:
                    currentStepnumber+=stepInc
                    if currentStepnumber >= moduloStep:
                        currentStepnumber = 0
                        self.progressNext(pProgress)

            canvas.end()

            # apply result to current processed layer
            EKritaNode.fromQPixmap(currentProcessedLayer, workingPixmap, QPoint(currentProcessedLayer.bounds().left(), currentProcessedLayer.bounds().top()) )

            if self.__outputOptions['outputAntialasing'] == OUTPUT_ANTIALIASING_SOFT:
                filter = Application.filter("gaussian blur")
                filterConfiguration = filter.configuration()
                filterConfiguration.setProperty("horizRadius", 0.67)
                filterConfiguration.setProperty("vertRadius", 0.67)
                filterConfiguration.setProperty("lockAspect", True)
                filter.setConfiguration(filterConfiguration)
                filter.apply(currentProcessedLayer, 0, 0, configWidth, configHeight)

            #if not pProgress is None:
            #    print(f"Newspaper execution duration[{color}]:", time.time() - startTime)



            return currentProcessedLayer


        def parseLayerName(value, color):
            """Parse layer name"""

            returned = value

            returned = returned.replace("{source:name}", originalLayer.name())
            returned = returned.replace("{mode}", OUTPUT_MODE_NFO[outputMode]['groupLayerName'])
            returned = returned.replace("{color:short}", color)
            if color == "C":
                returned = returned.replace("{color:long}", i18n("Cyan"))
            elif color == "M":
                returned = returned.replace("{color:long}", i18n("Magenta"))
            elif color == "Y":
                returned = returned.replace("{color:long}", i18n("Yellow"))
            elif color == "K":
                returned = returned.replace("{color:long}", i18n("Black"))
            elif color == "R":
                returned = returned.replace("{color:long}", i18n("Red"))
            elif color == "G":
                returned = returned.replace("{color:long}", i18n("Green"))
            elif color == "B":
                returned = returned.replace("{color:long}", i18n("Blue"))
            else:
                returned = returned.replace("{color:long}", "")

            return returned


        if document is None or originalLayer is None:
            # should not occurs, but...
            return

        outputMode = self.__outputOptions['outputMode']
        if outputMode == OUTPUT_MODE_MONO:
            if self.__outputOptions['outputMonoDesaturateMode'] == OUTPUT_MONO_DESMODE_LIGHTNESS:
                outputMode+='0'
            elif self.__outputOptions['outputMonoDesaturateMode'] == OUTPUT_MONO_DESMODE_LUMINOSITY709:
                outputMode+='1'
            elif self.__outputOptions['outputMonoDesaturateMode'] == OUTPUT_MONO_DESMODE_LUMINOSITY601:
                outputMode+='2'
            elif self.__outputOptions['outputMonoDesaturateMode'] == OUTPUT_MONO_DESMODE_AVERAGE:
                outputMode+='3'
            elif self.__outputOptions['outputMonoDesaturateMode'] == OUTPUT_MONO_DESMODE_MINIMUM:
                outputMode+='4'
            elif self.__outputOptions['outputMonoDesaturateMode'] == OUTPUT_MONO_DESMODE_MAXIMUM:
                outputMode+='5'

        if not pProgress is None:
            # determinate number of steps
            stepTotal = 4
            for layer in OUTPUT_MODE_NFO[outputMode]['layers']:
                stepTotal+=len(layer['process'])
                for process in layer['process']:
                    if process['action'] in ['newspaper', 'uncolorise']:
                        # arbitrary decompose a newspaper action to 20steps
                        # otherwise progress bar seems to be freezed during
                        # process
                        stepTotal+=20

            pProgress.setRange(0, stepTotal)

        if originalLayerIsVisible == False:
            originalLayer.setVisible(True)

        # ----------------------------------------------------------------------
        # Create new group layer
        parentGroupLayer = document.createGroupLayer(parseLayerName(self.__outputOptions['layerGroupName'], ''))
        originalLayer.parentNode().addChildNode(parentGroupLayer, originalLayer)

        self.progressNext(pProgress)

        currentProcessedLayer = None

        for layer in OUTPUT_MODE_NFO[outputMode]['layers']:
            currentProcessedLayer=getLayerByName(parentGroupLayer, parseLayerName(self.__outputOptions['layerColorName'], layer['color']))

            for process in layer['process']:
                if process['action'] == 'duplicate':
                    currentProcessedLayer = duplicateLayer(currentProcessedLayer, process['value'])
                elif process['action'] == 'new':
                    currentProcessedLayer = newLayer(currentProcessedLayer, process['value'])
                elif process['action'] == 'remove':
                    currentProcessedLayer = removeLayer(currentProcessedLayer, process['value'])
                elif process['action'] == 'merge down':
                    currentProcessedLayer = mergeDown(currentProcessedLayer, process['value'])
                elif process['action'] == 'blending mode':
                    applyBlendingMode(currentProcessedLayer, process['value'])
                elif process['action'] == 'opacity':
                    applyOpacity(currentProcessedLayer, process['value'])
                elif process['action'] == 'filter':
                    applyFilter(currentProcessedLayer, process['value'])
                elif process['action'] == 'newspaper':
                    applyNewspaper(currentProcessedLayer, process['value'], layer['color'])

                self.progressNext(pProgress)

            if not currentProcessedLayer is None:
                # rename currentProcessedLayer
                currentProcessedLayer.setName(parseLayerName(self.__outputOptions['layerColorName'], layer['color']))


        self.progressNext(pProgress)

        if self.__outputOptions['originalLayerAction'] == ORIGINAL_LAYER_KEEPVISIBLE:
            originalLayer.setVisible(True)
        elif self.__outputOptions['originalLayerAction'] == ORIGINAL_LAYER_KEEPHIDDEN:
            originalLayer.setVisible(False)
        elif self.__outputOptions['originalLayerAction'] == ORIGINAL_LAYER_REMOVE:
            originalLayer.remove()
        else:
            # ORIGINAL_LAYER_KEEPUNCHANGED
            originalLayer.setVisible(originalLayerIsVisible)


        self.progressNext(pProgress)

        document.refreshProjection()
        self.progressNext(pProgress)

        document.setActiveNode(parentGroupLayer)

        return parentGroupLayer




if PLUGIN_EXEC_FROM == 'SCRIPTER_PLUGIN':
    Newspaper(Krita.instance()).action_triggered()
