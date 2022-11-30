# -----------------------------------------------------------------------------
# Newspaper
# Copyright (C) 2019-2002 - Grum999
# -----------------------------------------------------------------------------
# SPDX-License-Identifier: GPL-3.0-or-later
#
# https://spdx.org/licenses/GPL-3.0-or-later.html
# -----------------------------------------------------------------------------
# A Krita plugin designed to apply a "newspaper" style to a layer
# . Monochrome
# . Four color (CMYK)
# -----------------------------------------------------------------------------

from krita import Krita
from .newspaper import Newspaper

# And add the extension to Krita's list of extensions:
app = Krita.instance()
# Instantiate your class:
extension = Newspaper(parent=app)
app.addExtension(extension)
