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

from enum import Enum
import re

from .pktk import (
        PkTk,
        EInvalidType
    )

from krita import (
        Document,
        Node
    )

from PyQt5.QtCore import (
        QByteArray,
        QPoint,
        QRect
    )
from PyQt5.QtGui import (
        QImage,
        QPixmap
    )




# -----------------------------------------------------------------------------
PkTk.setModuleInfo(
    'ekrita',
    '1.0.0',
    'PyKrita Toolkit EKrita',
    'Extent Krita API to simplify some commons'
)

# -----------------------------------------------------------------------------





class EKritaDocument:
    """Provides methods to manage Krita Documents"""

    @staticmethod
    def findFirstLayerByName(searchFrom, layerName):
        """Find a layer by name in document
        If more than one layer is found in document layers tree, will return the first layer found
        If no layer is found, return None

        The `searchFrom` parameter can be:
        - A Krita Layer (in this case, search in made in sub-nodes)
        - A Krita Document (in this case, search is made from document root node)

        The `layerName` can be a regular expression; just provide layer name with the following form:
        - "re://my_regular_expression

        """
        def find(layerName, isRegex, parentLayer):
            """sub function called recursively to search layer in document tree"""
            for layer in reversed(parentLayer.childNodes()):
                if isRegex == False and layerName == layer.name():
                    return layer
                elif isRegex == True and (reResult := re.match(layerName, layer.name())):
                    return layer
                elif len(layer.childNodes()) > 0:
                    returned = find(layerName, isRegex, layer)
                    if not returned is None:
                        return returned
            return None

        if not (isinstance(searchFrom, Document) or isinstance(searchFrom, Layer)):
            raise EInvalidType("Given `searchFrom` must be a Krita <Layer> or a Krita <Document> type")
        elif not isinstance(layerName, str):
            raise EInvalidType("Given `layerName` must be a valid <str>")

        parentLayer = searchFrom
        if isinstance(searchFrom, Document):
            # a document has been provided, use document root layer
            parentLayer = searchFrom.rootNode()

        if (reResult := re.match("^re://(.*)", layerName)):
            # retrieve given regular expression
            layerName = reResult.group(1)
            return find(layerName, True, parentLayer)
        else:
            return find(layerName, False, parentLayer)

        return None


    @staticmethod
    def findLayersByName(searchFrom, layerName):
        """Find layer(s) by name
        Return a list of all layers for which name is matching given layer name
        If no layer is found, return empty list

        The `searchFrom` parameter can be:
        - A Krita Layer (in this case, search in made in sub-nodes)
        - A Krita Document (in this case, search is made from document root node)

        The `layerName` can be a regular expression; just provide layer name with the following form:
        - "re://my_regular_expression
        """
        def find(layerName, isRegex, parentLayer):
            """sub function called recursively to search layer in document tree"""
            returned=[]
            for layer in reversed(parentLayer.childNodes()):
                if isRegex == False and layerName == layer.name():
                    returned.append(layer)
                elif isRegex == True and (reResult := re.match(layerName, layer.name())):
                    returned.append(layer)
                elif len(layer.childNodes()) > 0:
                    found = find(layerName, isRegex, layer)
                    if not found is None:
                        returned+=found
            return returned


        if not (isinstance(searchFrom, Document) or isinstance(searchFrom, Layer)):
            raise EInvalidType("Given `searchFrom` must be a Krita <Layer> or a Krita <Document> type")
        elif not isinstance(layerName, str):
            raise EInvalidType("Given `layerName` must be a valid <str> (current: {0})".format(type(layerName)))

        parentLayer = searchFrom
        if isinstance(searchFrom, Document):
            # a document has been provided, use document root layer
            parentLayer = searchFrom.rootNode()

        if (reResult := re.match("^re://(.*)", layerName)):
            # retrieve given regular expression
            layerName = reResult.group(1)
            return find(layerName, True, parentLayer)
        else:
            return find(layerName, False, parentLayer)

        return []


    @staticmethod
    def getLayers(searchFrom, recursiveSubLayers=False):
        """Return a list of all layers

        The `searchFrom` parameter can be:
        - A Krita Layer (in this case, return all sub-nodes from given layer)
        - A Krita Document (in this case, return all sub-nodes from document root node)

        If `recursiveSubLayers` is True, also return all subLayers
        """
        def find(recursiveSubLayers, parentLayer):
            """sub function called recursively to search layer in document tree"""
            returned=[]
            for layer in reversed(parentLayer.childNodes()):
                returned.append(layer)
                if recursiveSubLayers and len(layer.childNodes()) > 0:
                    found = find(recursiveSubLayers, layer)
                    if not found is None:
                        returned+=found
            return returned

        if not (isinstance(searchFrom, Document) or isinstance(searchFrom, Layer)):
            raise EInvalidType("Given `searchFrom` must be a Krita <Layer> or a Krita <Document> type")
        elif not isinstance(recursiveSubLayers, bool):
            raise EInvalidType("Given `recursiveSubLayers` must be a <bool>")

        parentLayer = searchFrom
        if isinstance(searchFrom, Document):
            # a document has been provided, use document root layer
            parentLayer = searchFrom.rootNode()

        return find(recursiveSubLayers, parentLayer)


    @staticmethod
    def getLayerFromPath(searchFrom, path):
        """Return a layer from given path
        If no layer is found, return None

        The `searchFrom` parameter can be:
        - A Krita Document (in this case, return all sub-nodes from document root node)
        """
        def find(pathNodes, level, parentLayer):
            """sub function called recursively to search layer in document tree"""
            for layer in reversed(parentLayer.childNodes()):
                if layer.name() == pathNodes[level]:
                    if level == len(pathNodes) - 1:
                        return layer
                    elif len(layer.childNodes()) > 0:
                        return find(pathNodes, level + 1, layer)
            return None

        if not isinstance(searchFrom, Document):
            raise EInvalidType("Given `searchFrom` must be a Krita <Document> type")
        elif not isinstance(path, str):
            raise EInvalidType("Given `path` must be a <str>")

        pathNodes = re.findall(r'(?:[^/"]|"(?:\\.|[^"])*")+', path)

        if not pathNodes is None:
            pathNodes = [re.sub(r'^"|"$', '', pathNode) for pathNode in pathNodes]

        return find(pathNodes, 0, searchFrom.rootNode())



class EKritaNode:
    """Provides methods to manage Krita Nodes"""

    class ProjectionMode(Enum):
        """Projection modes for toQImage(), toQPixmap()"""
        FALSE = 0
        TRUE = 1
        AUTO = 2


    __projectionMode = ProjectionMode.AUTO


    @staticmethod
    def path(layerNode):
        """Return `layerNode` path in tree

        Example
        =======
            rootnode
             +-- groupLayer1
                 +-- groupLayer2
                     +-- theNode
                     +-- theNode with / character

            return '/groupLayer1/groupLayer2/theNode'
            return '/groupLayer1/groupLayer2/"theNode with / character"'
        """
        def parentPath(layerNode):
            if layerNode.parentNode() is None or layerNode.parentNode().parentNode() is None:
                return ''
            else:
                if '/' in layerNode.name():
                    return f'{parentPath(layerNode.parentNode())}/"{layerNode.name()}"'
                else:
                    return f'{parentPath(layerNode.parentNode())}/{layerNode.name()}'

        if not isinstance(layerNode, Node):
            raise EInvalidType("Given `layerNode` must be a valid Krita <Node> ")

        return parentPath(layerNode)


    @staticmethod
    def toQImage(layerNode, rect=None):
        """Return `layerNode` content as a QImage (as ARGB32)

        The `rect` value can be:
        - None, in this case will return all `layerNode` content
        - A QRect() object, in this case return `layerNode` content reduced to given rectangle bounds
        - A Krita document, in this case return `layerNode` content reduced to document bounds
        """
        if not isinstance(layerNode, Node):
            raise EInvalidType("Given `layerNode` must be a valid Krita <Node> ")

        if rect is None:
            rect = layerNode.bounds()
        elif isinstance(rect, Document):
            rect = rect.bounds()
        elif not isinstance(rect, QRect):
            raise EInvalidType("Given `rect` must be a valid Krita <Document>, a <QRect> or None")

        projectionMode = EKritaNode.__projectionMode
        if projectionMode == EKritaNode.ProjectionMode.AUTO:
            if len(layerNode.childNodes()) == 0:
                projectionMode = EKritaNode.ProjectionMode.FALSE
            else:
                projectionMode = EKritaNode.ProjectionMode.TRUE

        if projectionMode == EKritaNode.ProjectionMode.TRUE:
            return QImage(layerNode.projectionPixelData(rect.left(), rect.top(), rect.width(), rect.height()), rect.width(), rect.height(), QImage.Format_ARGB32)
        else:
            return QImage(layerNode.pixelData(rect.left(), rect.top(), rect.width(), rect.height()), rect.width(), rect.height(), QImage.Format_ARGB32)


    @staticmethod
    def toQPixmap(layerNode, rect=None):
        """Return `layerNode` content as a QPixmap (as ARGB32)

        If the `projection` value is True, returned :


        The `rect` value can be:
        - None, in this case will return all `layerNode` content
        - A QRect() object, in this case return `layerNode` content reduced to given rectangle bounds
        - A Krita document, in this case return `layerNode` content reduced to document bounds
        """
        return QPixmap.fromImage(EKritaNode.toQImage(layerNode, rect))


    @staticmethod
    def fromQImage(layerNode, image, position=None):
        """Paste given `image` to `position` in '`layerNode`

        The `position` value can be:
        - None, in this case, pixmap will be pasted at position (0, 0)
        - A QPoint() object, pixmap will be pasted at defined position
        """
        if not isinstance(layerNode, Node):
            raise EInvalidType("Given `layerNode` must be a valid Krita <Node> ")
        elif not isinstance(image, QImage):
            raise EInvalidType("Given `image` must be a valid <QImage> ")

        if position is None:
            position = QPoint(0, 0)

        if not isinstance(position, QPoint):
            raise EInvalidType("Given `position` must be a valid <QPoint> ")

        ptr = image.bits()
        ptr.setsize(image.byteCount())

        layerNode.setPixelData(QByteArray(ptr.asstring()), position.x(), position.y(), image.width(), image.height())


    @staticmethod
    def fromQPixmap(layerNode, pixmap, position=None):
        """Paste given `pixmap` to `position` in '`layerNode`

        The `position` value can be:
        - None, in this case, pixmap will be pasted at position (0, 0)
        - A QPoint() object, pixmap will be pasted at defined position
        """
        if not isinstance(pixmap, QPixmap):
            raise EInvalidType("Given `pixmap` must be a valid <QPixmap> ")

        if position is None:
            position = QPoint(0, 0)

        EKritaNode.fromQImage(layerNode, pixmap.toImage(), position)


    @staticmethod
    def above(layerNode):
        """Return node above given `layerNode`

        If there's no node above given layer, return None"""

        if layerNode is None:
            return None

        if not isinstance(layerNode, Node):
            raise EInvalidType("Given `layerNode` must be a valid Krita <Node> ")

        returnNext = False
        for layer in layerNode.parentNode().childNodes():
            if returnNext:
                return layer
            elif layer == layerNode:
                returnNext = True

        return None


    @staticmethod
    def below(layerNode):
        """Return node below given `layerNode`

        If there's no node below given layer, return None"""

        if layerNode is None:
            return None

        if not isinstance(layerNode, Node):
            raise EInvalidType("Given `layerNode` must be a valid Krita <Node> ")

        prevNode = None
        for layer in layerNode.parentNode().childNodes():
            if layer == layerNode:
                return prevNode
            prevNode = layer

        return None



