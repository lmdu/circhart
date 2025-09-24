import math

from PySide6.QtSvg import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtSvgWidgets import *

from config import *
from models import *
from workers import *
from backend import *

__all__ = [
	'CirchartSpacerWidget',
	'CirchartSpinnerWidget',
	'CirchartDataTreeWidget',
	'CirchartPlotTreeWidget',
	'CirchartEmptyTreeWidget',
	'CirchartDataTableWidget',
	'CirchartCheckTableWidget',
	'CirchartGraphicsViewWidget',
	'CirchartGenomeWindowSize',
	'CirchartCircosColorTable',
]

class CirchartEmptyTreeWidget(QTreeWidget):
	pass

class CirchartSpacerWidget(QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

#from https://github.com/z3ntu/QtWaitingSpinner
class CirchartSpinnerWidget(QWidget):
	def __init__(self, parent):
		super().__init__(parent)

		# WAS IN initialize()
		self._color = QColor(Qt.black)
		self._roundness = 70.0
		self._minimumTrailOpacity = 3.14159265358979323846
		self._trailFadePercentage = 70.0
		self._revolutionsPerSecond = 1.57079632679489661923
		self._numberOfLines = 10
		self._lineLength = 6
		self._lineWidth = 3
		self._innerRadius = 4
		self._currentCounter = 0
		self._isSpinning = False

		self._timer = QTimer(self)
		self._timer.timeout.connect(self.rotate)
		self.updateSize()
		self.updateTimer()
		self.setVisible(False)
		# END initialize()

		self.setAttribute(Qt.WA_TranslucentBackground)

	def paintEvent(self, QPaintEvent):
		painter = QPainter(self)
		painter.fillRect(self.rect(), Qt.transparent)
		painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

		if self._currentCounter >= self._numberOfLines:
			self._currentCounter = 0

		painter.setPen(Qt.NoPen)
		for i in range(0, self._numberOfLines):
			painter.save()
			painter.translate(self._innerRadius + self._lineLength, self._innerRadius + self._lineLength)
			rotateAngle = float(360 * i) / float(self._numberOfLines)
			painter.rotate(rotateAngle)
			painter.translate(self._innerRadius, 0)
			distance = self.lineCountDistanceFromPrimary(i, self._currentCounter, self._numberOfLines)
			color = self.currentLineColor(distance, self._numberOfLines, self._trailFadePercentage,
										  self._minimumTrailOpacity, self._color)
			painter.setBrush(color)
			rect = QRect(0, int(-self._lineWidth / 2), int(self._lineLength), int(self._lineWidth))
			painter.drawRoundedRect(rect, self._roundness, self._roundness, Qt.SizeMode.RelativeSize)
			painter.restore()

	@property
	def running(self):
		return self._isSpinning

	def toggle(self, state):
		if state:
			self.start()
		else:
			self.stop()

	def start(self):
		self._isSpinning = True
		self.setVisible(True)

		if not self._timer.isActive():
			self._timer.start()
			self._currentCounter = 0

	def stop(self):
		self._isSpinning = False
		self.setVisible(False)

		if self._timer.isActive():
			self._timer.stop()
			self._currentCounter = 0

	def rotate(self):
		self._currentCounter += 1
		if self._currentCounter >= self._numberOfLines:
			self._currentCounter = 0
		self.update()

	def updateSize(self):
		size = int((self._innerRadius + self._lineLength) * 2)
		self.setFixedSize(size, size)

	def updateTimer(self):
		self._timer.setInterval(int(1000 / (self._numberOfLines * self._revolutionsPerSecond)))

	def lineCountDistanceFromPrimary(self, current, primary, totalNrOfLines):
		distance = primary - current
		if distance < 0:
			distance += totalNrOfLines
		return distance

	def currentLineColor(self, countDistance, totalNrOfLines, trailFadePerc, minOpacity, colorinput):
		color = QColor(colorinput)
		if countDistance == 0:
			return color
		minAlphaF = minOpacity / 100.0
		distanceThreshold = int(math.ceil((totalNrOfLines - 1) * trailFadePerc / 100.0))
		if countDistance > distanceThreshold:
			color.setAlphaF(minAlphaF)
		else:
			alphaDiff = color.alphaF() - minAlphaF
			gradient = alphaDiff / float(distanceThreshold + 1)
			resultAlpha = color.alphaF() - gradient * countDistance
			# If alpha is out of bounds, clip it.
			resultAlpha = min(1.0, max(0.0, resultAlpha))
			color.setAlphaF(resultAlpha)
		return color

class CirchartIOTreeWidget(QTreeView):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setRootIsDecorated(False)
		self.clicked.connect(self.on_row_clicked)

		self.create_model()
		self.set_header_width()

	def sizeHint(self):
		return QSize(200, 300)

	def create_model(self):
		pass

	def set_header_width(self):
		self.header().setStretchLastSection(False)
		self.header().setSectionResizeMode(0, QHeaderView.Stretch)
		self.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)

	def update_tree(self):
		self._model.update_model()

	def emit_signal(self, table, rowid):
		pass

	def on_row_clicked(self, index):
		rowid = self._model.get_id(index)
		table = self._model.get_value(index.row(), 1)
		self.emit_signal(table, rowid)

class CirchartDataTreeWidget(CirchartIOTreeWidget):
	show_data = Signal(str, int)

	def create_model(self):
		self._model = CirchartDataTreeModel(self)
		self.setModel(self._model)

	def emit_signal(self, table, rowid):
		self.show_data.emit(table, rowid)

class CirchartPlotTreeWidget(CirchartIOTreeWidget):
	show_plot = Signal(str, int)

	def create_model(self):
		self._model = CirchartPlotTreeModel(self)
		self.setModel(self._model)

	def emit_signal(self, ptype, rowid):
		self.show_plot.emit(ptype, rowid)

class CirchartDataTableWidget(QTableView):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.verticalHeader().hide()
		self._model = None

	def create_model(self, table):
		match table:
			case 'karyotype':
				if type(self._model) != CirchartKaryotypeTableModel:
					self._model = CirchartKaryotypeTableModel(self)
			
			case _:
				if type(self._model) != CirchartDataTableModel:
					self._model = CirchartDataTableModel(self)

	def change_table(self, table, index=None):
		self.create_model(table)

		if index is not None:
			table = "{}_{}".format(table, index)

		self._model.change_table(table)
		self._model.update_model()
		self.setModel(self._model)

class CirchartCheckTableWidget(CirchartDataTableWidget):
	def create_model(self, table):
		self._model = CirchartDataTableModel(self, True, True)
		self.setModel(self._model)

	def get_selected(self):
		return self._model.get_selected_rows()

	def is_selected(self):
		return True if self._model.selected else False

class CirchartGraphicsViewWidget(QGraphicsView):
	def __init__(self, parent):
		super().__init__(parent)

		self.setScene(QGraphicsScene(self))
		self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
		self.setDragMode(QGraphicsView.ScrollHandDrag)
		self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

		self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

		self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)

		#self.create_plot()

	def wheelEvent(self, event):
		if event.angleDelta().y() > 0:
			self.scale(1.15, 1.15)

		else:
			self.scale(1.0/1.15, 1.0/1.15)

		event.accept()

	def fit_view(self):
		view_rect = self.viewport().rect()
		svg_rect = self.svg_item.boundingRect()

		x_ratio = view_rect.width() / svg_rect.width()
		y_ratio = view_rect.height() / svg_rect.height()
		m_ratio = min(x_ratio, y_ratio) * 0.95

		self.resetTransform()
		self.scale(m_ratio, m_ratio)
		self.centerOn(self.svg_item)

	def load_svg(self, svg_str):
		if not svg_str:
			return

		self.scene().clear()
		self.resetTransform()
		svg_data = QByteArray(svg_str.encode())
		self.svg_item = QGraphicsSvgItem()
		self.svg_item.renderer().load(svg_data)
		self.svg_item.setElementId("")
		self.svg_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
		self.scene().addItem(self.svg_item)
		#self.fit_view()
		self.fitInView(self.svg_item, Qt.KeepAspectRatio)

	def show_plot(self, plottype, plotid):
		svg_str = SqlControl.get_svg(plotid)
		self.load_svg(svg_str)

	def create_plot(self):
		with open('test/circos.svg') as fh:
			svg_str = fh.read()

		self.load_svg(svg_str)

class CirchartGenomeWindowSize(QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)

		self.spin = QSpinBox(self)
		self.spin.setValue(10)
		self.spin.setMinimum(1)
		self.spin.setMaximum(1000000)
		self.spin.setAlignment(Qt.AlignCenter)

		self.unit = QComboBox(self)
		self.unit.addItems(['BP', 'KB', 'MB'])
		self.unit.setCurrentIndex(2)

		layout = QHBoxLayout()
		layout.setContentsMargins(0, 0, 0, 0)
		layout.addWidget(self.spin)
		layout.addWidget(self.unit)
		self.setLayout(layout)

	def get_value(self):
		scales = [1, 1000, 1000000]
		return self.spin.value() * scales[self.unit.currentIndex()]

class CirchartCircosColorTable(QTableView):
	color_changed = Signal(list)

	def __init__(self, parent=None, multiple=False):
		super().__init__(parent)
		self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
		self.horizontalHeader().hide()
		self.verticalHeader().hide()

		if not multiple:
			self.setSelectionMode(QAbstractItemView.SingleSelection)

		self.selected_index = []
		self.create_model()
		self.parse_colors()

	def create_model(self):
		self._model = CirchartCircosColorModel(self)
		self.setModel(self._model)

	def parse_colors(self):
		worker = CirchartCircosColorWorker()
		worker.signals.result.connect(self._model.set_data)
		QThreadPool.globalInstance().start(worker)

	def selectionChanged(self, selected, deselected):
		for index in selected.indexes():
			if index not in self.selected_index:
				
				self.selected_index.append(index)

		for index in deselected.indexes():
			if index in self.selected_index:
				self.selected_index.remove(index)

		colors = []
		for index in self.selected_index:
			c = self._model.get_color(index)
			colors.append(c)

		self.color_changed.emit(colors)

		super().selectionChanged(selected, deselected)
			

