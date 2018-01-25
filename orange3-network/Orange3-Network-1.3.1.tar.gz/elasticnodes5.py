
import numpy as np

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QLineF, QPointF, QRectF, Qt
from PyQt4.QtGui import qApp, QBrush, QPen, QPolygonF, QStyle, QColor

from orangecontrib.network._fr_layout import fruchterman_reingold_layout

import pyqtgraph as pg


class QGraphicsEdge(QtGui.QGraphicsLineItem):
    def __init__(self, source, dest, view=None):
        super().__init__()
        self.setAcceptedMouseButtons(Qt.NoButton)
        self.setFlags(self.ItemIgnoresTransformations |
                      self.ItemIgnoresParentOpacity)
        self.setZValue(1)
        self.setPen(QPen(Qt.darkGray, .5))

        source.addEdge(self)
        dest.addEdge(self)
        self.source = source
        self.dest = dest
        self.__transform = view.transform
        # Add text labels
        label = self.label = QtGui.QGraphicsSimpleTextItem('', self)
        label.setVisible(False)
        label.setBrush(Qt.gray)
        label.setZValue(2)
        label.setFlags(self.ItemIgnoresParentOpacity |
                       self.ItemIgnoresTransformations)
        view.scene().addItem(label)

        self.adjust()

    def adjust(self):
        line = QLineF(self.mapFromItem(self.source, 0, 0),
                      self.mapFromItem(self.dest, 0, 0))
        self.label.setPos(line.pointAt(.5))
        self.setLine(self.__transform().map(line))


class Edge(QGraphicsEdge):
    def __init__(self, source, dest, view=None):
        super().__init__(source, dest, view)
        self.setSize(.5)

    def setSize(self, size):
        self.setPen(QPen(self.pen().color(), size))

    def setText(self, text):
        if text: self.label.setText(text)
        self.label.setVisible(bool(text))

    def setColor(self, color):
        self.setPen(QPen(QColor(color), self.pen().width()))


class QGraphicsNode(QtGui.QGraphicsEllipseItem):
    """This class is the bare minimum to sustain a connected graph"""
    def __init__(self, rect=QRectF(-5, -5, 10, 10), view=None):
        super().__init__(rect)
        self.setCacheMode(self.DeviceCoordinateCache)
        self.setAcceptHoverEvents(True)
        self.setFlags(self.ItemIsMovable |
                      self.ItemIsSelectable |
                      self.ItemIgnoresTransformations |
                      self.ItemIgnoresParentOpacity |
                      self.ItemSendsGeometryChanges)
        self.setZValue(4)

        self.edges = []
        self._radius = rect.width() / 2
        self.__transform = view.transform
        # Add text labels
        label = self.label = QtGui.QGraphicsSimpleTextItem('', self)
        label.setVisible(False)
        label.setFlags(self.ItemIgnoresParentOpacity |
                       self.ItemIgnoresTransformations)
        label.setZValue(3)
        view.scene().addItem(label)

    def setPos(self, x, y):
        self.adjust()
        super().setPos(x, y)

    def adjust(self):
        # Adjust label position
        d = 1 / self.__transform().m11() * self._radius
        self.label.setPos(self.pos().x() + d, self.pos().y() + d)

    def addEdge(self, edge):
        self.edges.append(edge)

    def itemChange(self, change, value):
        if change == self.ItemPositionHasChanged:
            self.adjust()
            for edge in self.edges:
                edge.adjust()
        return super().itemChange(change, value)


class Node(QGraphicsNode):
    """
    This class provides an interface for all the bells & whistles of the
    Network Explorer.
    """

    BRUSH_DEFAULT = QBrush(QColor('#669'))

    class Pen:
        DEFAULT = QPen(Qt.black, 0)
        SELECTED = QPen(QColor('#ee0000'), 3)
        HIGHLIGHTED = QPen(QColor('#ff7700'), 3)

    _tooltip = lambda _: ''

    def __init__(self, id, view):
        super().__init__(view=view)
        self.id = id
        self.setBrush(Node.BRUSH_DEFAULT)
        self.setPen(Node.Pen.DEFAULT)

        self._is_highlighted = False

    def setSize(self, size):
        self._radius = radius = size/2
        self.setRect(-radius, -radius, size, size)

    def setText(self, text):
        if text: self.label.setText(text)
        self.label.setVisible(bool(text))

    def setColor(self, color=None):
        self.setBrush(QBrush(QColor(color)) if color else Node.BRUSH_DEFAULT)

    def isHighlighted(self):
        return self._is_highlighted
    def setHighlighted(self, highlight):
        self._is_highlighted = highlight
        if not self.isSelected():
            self.itemChange(self.ItemSelectedChange, False)

    def itemChange(self, change, value):
        if change == self.ItemSelectedChange:
            self.setPen(Node.Pen.SELECTED if value else
                        Node.Pen.HIGHLIGHTED if self._is_highlighted else
                        Node.Pen.DEFAULT)
        return super().itemChange(change, value)

    def paint(self, painter, option, widget):
        option.state &= ~QStyle.State_Selected  # We use a custom selection pen
        super().paint(painter, option, widget)

    def setTooltip(self, callback):
        self._tooltip = callback
    def hoverEnterEvent(self, event):
        self.setToolTip(self._tooltip())
    def hoverLeaveEvent(self, event):
        self.setToolTip('');

    #~ def mousePressEvent(self, event):
        #~ self.update()
        #~ super().mousePressEvent(event)
#~
    #~ def mouseReleaseEvent(self, event):
        #~ self.update()
        #~ super().mouseReleaseEvent(event)


class GraphView(QtGui.QGraphicsView):

    positionsChanged = QtCore.pyqtSignal(np.ndarray)
    # Emitted when nodes' selected or highlighted state changes
    selectionChanged = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.nodes = []
        self.edges = []
        self._selection = []
        self._clicked_node = None

        scene = QtGui.QGraphicsScene(self)
        scene.setItemIndexMethod(scene.NoIndex)
        scene.setSceneRect(-400, -400, 800, 800)
        self.setScene(scene)
        self.setCacheMode(self.CacheBackground)
        self.setViewportUpdateMode(self.BoundingRectViewportUpdate)

        self.setRenderHint(QtGui.QPainter.Antialiasing)

        self.setTransformationAnchor(self.AnchorUnderMouse)
        self.setResizeAnchor(self.AnchorViewCenter)

        #~ self.setDragMode(self.ScrollHandDrag)
        self.setDragMode(self.RubberBandDrag)

        self.setMinimumSize(400, 400)
        #~ self.positionsChanged.connect(self._update_positions, type=Qt.BlockingQueuedConnection)
        self.positionsChanged.connect(self._update_positions)

    def mousePressEvent(self, event):
        if self._is_animating:
            self._is_animating = False
            self.setCursor(Qt.ArrowCursor)
        # Save the current selection and restore it on mouse{Move,Release}
        self._selection = []
        self._clicked_node = self.itemAt(event.pos())
        if event.modifiers() & (Qt.ControlModifier | Qt.ShiftModifier):
            self._selection = self.scene().selectedItems()
        super().mousePressEvent(event)
    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if not self._clicked_node:
            for node in self._selection: node.setSelected(True)
    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        for node in self._selection: node.setSelected(True)
        self.selectionChanged.emit()

    def setHighlighted(self, nodes):
        for node in nodes:
            node.setHighlighted(True)
        self.selectionChanged.emit()

    def getSelected(self):
        return self.scene().selectedItems()

    def getHighlighted(self):
        return [node for node in self.nodes
                if node.isHighlighted() and not node.isSelected()]

    def set_graph(self, graph):
        assert isinstance(graph, nx.Graph)
        # TODO
        self.selectionChanged.emit()

    def addNode(self, node):
        assert isinstance(node, Node)
        self.nodes.append(node)
        self.scene().addItem(node)
    def addEdge(self, edge):
        assert isinstance(edge, Edge)
        self.edges.append(edge)
        self.scene().addItem(edge)

    def wheelEvent(self, event):
        self.scaleView(2**(event.delta() / 240))
    def scaleView(self, factor):
        magnitude = self.matrix().scale(factor, factor).mapRect(QRectF(0, 0, 1, 1)).width()
        if 0.2 < magnitude < 30:
            self.scale(factor, factor)
        # Reposition nodes' labels ...
        for node in self.nodes: node.adjust()
        # Reposition edges which are node-dependend (and nodes just "moved")
        for edge in self.edges: edge.adjust()

    def relayout(self):
        self._is_animating = True
        self.setCursor(Qt.ForbiddenCursor)
        ...

    def update_positions(self, positions):
        self.positionsChanged.emit(positions)
        return self._is_animating
    def _update_positions(self, positions):
        for node, pos in zip(self.nodes, positions):
            node.setPos(pos[0]*400, pos[1]*400)
        qApp.processEvents()

# TODO: integrate with pyqtgraph

if __name__ == '__main__':

    import sys
    app = QtGui.QApplication(sys.argv)
    widget = GraphView()
    widget.show()
    import networkx as nx
    G = nx.scale_free_graph(int(sys.argv[1]) if len(sys.argv) > 1 else 100, seed=0)
    for v in sorted(G.nodes()):
        widget.addNode(Node(v, view=widget))
    for u, v in G.edges():
        widget.addEdge(Edge(widget.nodes[u], widget.nodes[v], view=widget))

    print('nodes', len(widget.nodes), 'edges', len(widget.edges))

    widget.relayout()
    #~ from threading import Thread
    #~ Thread(target=fruchterman_reingold_layout, args=(G,), kwargs=dict(iterations=50, callback=widget.update_positions)).start()
#~
    QtCore.QTimer.singleShot(0, lambda:
        fruchterman_reingold_layout(G,
                                    iterations=50,
                                    callback=widget.update_positions) and
        (lambda: widget.mousePressEvent(1))())
    QtCore.QTimer.singleShot(1000, lambda:
        [node.setHighlighted(True) for node in widget.nodes[:10]])

    sys.exit(app.exec_())
