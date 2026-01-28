import math

from PySide6.QtSvg import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtSvgWidgets import *
from PySide6.QtPrintSupport import *

from utils import *
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
	'CirchartCollinearityIdmappingWidget',
	'CirchartCustomColorTable',
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

		self._init_widget()

	def _init_widget(self):
		pass

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

class CirchartBrowseWidget(QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)

		self._init_widget()
		self._init_layout()

	def _init_widget(self):
		self.input = QLineEdit(self)
		self.input.setReadOnly(True)
		self.browse = QPushButton(self)
		self.browse.setFlat(True)
		self.browse.setIcon(QIcon(':/icons/folder.svg'))
		self.browse.clicked.connect(self.select_path)

	def _init_layout(self):
		self.main_layout = QHBoxLayout()
		self.main_layout.setSpacing(0)
		self.main_layout.setContentsMargins(0, 0, 0, 0)
		self.main_layout.addWidget(self.input, 1)
		self.main_layout.addWidget(self.browse)

		self.setLayout(self.main_layout)

	def select_path(self):
		path, _ = QFileDialog.getOpenFileName(self)

		if path:
			self.set_path(path)

	def set_path(self, path):
		self.input.setText(path)

	def get_path(self):
		return self.input.text()

class CirchartFileBrowseDialog(QDialog):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setWindowTitle("Change File Path")

		self._init_widget()
		self._init_layout()

	def sizeHint(self):
		return QSize(450, 10)

	def _init_widget(self):
		self.file_browse = CirchartBrowseWidget(self)

		self.btn_box = QDialogButtonBox(
			QDialogButtonBox.StandardButton.Cancel |
			QDialogButtonBox.StandardButton.Ok
		)
		self.btn_box.accepted.connect(self.accept)
		self.btn_box.rejected.connect(self.reject)

	def _init_layout(self):
		self.main_layout = QVBoxLayout()
		self.main_layout.addWidget(QLabel("File Path:", self))
		self.main_layout.addWidget(self.file_browse)
		self.main_layout.addWidget(self.btn_box)
		self.setLayout(self.main_layout)

	@classmethod
	def get_path(cls, parent=None, path=''):
		dlg = cls(parent)
		dlg.file_browse.set_path(path)

		if dlg.exec() == QDialog.Accepted:
			return dlg.file_browse.get_path()

class CirchartDataTreeWidget(CirchartIOTreeWidget):
	show_data = Signal(str, int)
	data_removed = Signal(str)

	def _init_widget(self):
		self.setContextMenuPolicy(Qt.CustomContextMenu)
		self.customContextMenuRequested.connect(self._show_context_menu)

	def create_model(self):
		self._model = CirchartDataTreeModel(self)
		self.setModel(self._model)

	def emit_signal(self, table, rowid):
		self.show_data.emit(table, rowid)

	def _show_context_menu(self, pos):
		path_action = QAction("Change Path")
		path_action.triggered.connect(self.change_path)
		rename_action = QAction("Rename")
		rename_action.triggered.connect(self.rename_data)
		delete_action = QAction("Delete")
		delete_action.triggered.connect(self.delete_data)

		menu = QMenu(self)
		menu.addAction(rename_action)
		menu.addAction(delete_action)
		menu.addSeparator()
		menu.addAction(path_action)

		menu.exec(self.mapToGlobal(pos))

	def rename_data(self):
		index = self.currentIndex()

		if not index.isValid():
			return

		new_name, ok = QInputDialog.getText(self, "Rename data", "Input new name:")
		new_name = new_name.strip()

		if ok and new_name:
			self._model.rename_data(index, new_name)

	def change_path(self):
		index = self.currentIndex()

		if not index.isValid():
			return

		did = self._model.get_id(index)
		meta_data = SqlControl.get_data_meta(did)

		if meta_data and 'path' in meta_data:
			new_path = CirchartFileBrowseDialog.get_path(self, meta_data['path'])

			if new_path is not None:
				if new_path != meta_data['path']:
					meta_data['path'] = new_path
					SqlControl.update_data_meta(did, meta_data)

	def delete_data(self):
		index = self.currentIndex()

		if not index.isValid():
			return

		ret = QMessageBox.question(self, "Comfirmation",
			"Are you sure you want to delete this data?")

		if ret == QMessageBox.No:
			return

		data_id = self._model.get_id(index)
		data_type = index.siblingAtColumn(1).data()
		self._model.remove_row(index)
		table = "{}_{}".format(data_type, data_id)
		SqlBase.drop_table(table)
		self.data_removed.emit(table)

class CirchartPlotTreeWidget(CirchartIOTreeWidget):
	show_plot = Signal(str, int)
	plot_removed = Signal(int)

	def _init_widget(self):
		self.setContextMenuPolicy(Qt.CustomContextMenu)
		self.customContextMenuRequested.connect(self._show_context_menu)

	def create_model(self):
		self._model = CirchartPlotTreeModel(self)
		self.setModel(self._model)

	def emit_signal(self, ptype, rowid):
		self.show_plot.emit(ptype, rowid)

	def _show_context_menu(self, pos):
		delete_action = QAction("Delete")
		delete_action.triggered.connect(self.delete_plot)

		menu = QMenu(self)
		menu.addAction(delete_action)
		menu.exec(self.mapToGlobal(pos))

	def delete_plot(self):
		index = self.currentIndex()

		if not index.isValid():
			return

		ret = QMessageBox.question(self, "Comfirmation",
			"Are you sure you want to delete this plot?")

		if ret == QMessageBox.No:
			return

		plot_id = self._model.get_id(index)
		self._model.remove_row(index)
		self.plot_removed.emit(plot_id)

class CirchartDataTableWidget(QTableView):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.verticalHeader().hide()
		#self.horizontalHeader().setStretchLastSection(True)
		self.setSortingEnabled(True)
		self._model = None

	def create_model(self, table):
		match table:
			case 'karyotype' | 'banddata':
				if type(self._model) != CirchartKaryotypeTableModel:
					self._model = CirchartKaryotypeTableModel(self)

				delegate = CirchartKaryotypeDelegate(self)
				self.setItemDelegate(delegate)
			
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

	def clear_table(self, table):
		if self._model is None:
			return

		if table == self._model.get_table():
			self._model = None
			self.setModel(None)

	def update_karyotype_color(self, method, color=None):
		if type(self._model) != CirchartKaryotypeTableModel:
			return

		table = self._model.get_table()

		if table.startswith('banddata'):
			return

		match method:
			case 'single':
				self._model.update_single_color(color)

			case 'random':
				self._model.update_random_color()

			case 'default':
				self._model.update_default_color()

class CirchartCheckTableWidget(CirchartDataTableWidget):
	def create_model(self, table):
		self._model = CirchartDataTableModel(self, True, True)
		self.setModel(self._model)

	def get_selected(self):
		return self._model.get_selected_rows()

	def is_selected(self):
		if not self._model:
			return False

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

		self.plot_id = 0
		self.create_svg_item()

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
		m_ratio = min(x_ratio, y_ratio) * 0.8

		self.resetTransform()
		self.scale(m_ratio, m_ratio)
		self.centerOn(self.svg_item)

	def create_svg_item(self):
		self.svg_render = QSvgRenderer()
		self.svg_item = QGraphicsSvgItem()
		self.svg_item.setSharedRenderer(self.svg_render)
		self.svg_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
		self.scene().addItem(self.svg_item)
		self.fitInView(self.svg_item, Qt.KeepAspectRatio)

	def load_svg(self, svg_str):
		if not svg_str:
			return

		svg_width = self.svg_item.boundingRect().width()

		svg_data = QByteArray(svg_str.encode())
		#self.svg_item.renderer().load(svg_data)
		self.svg_render.load(svg_data)
		self.svg_item.setElementId("")

		if svg_width <= 0:
			self.fitInView(self.svg_item, Qt.KeepAspectRatio)

	def show_plot(self, plotid):
		svg_str = SqlControl.get_svg(plotid)
		self.plot_id = plotid
		self.load_svg(svg_str)

	def change_render(self, render):
		self.plot_id, self.svg_render = render
		self.svg_item.setSharedRenderer(self.svg_render)
		self.svg_item.setElementId('')
		self.fitInView(self.svg_item, Qt.KeepAspectRatio)


	def save_plot(self, ifile, iformat):
		scene = self.scene()
		scene_rect = scene.sceneRect()

		if scene_rect.isEmpty():
			scene_rect = scene.itemsBoundingRect()

		if iformat == 'svg':
			#generator = QSvgGenerator()
			#generator.setFileName(ifile)
			#generator.setSize(scene_rect.size().toSize())
			#generator.setViewBox(scene_rect)

			#painter = QPainter()
			#painter.begin(generator)
			#painter.setRenderHint(QPainter.Antialiasing)
			#scene.render(painter)
			#painter.end()

			if self.plot_id > 0:
				with open(ifile, 'w') as fw:
					svg_str = SqlControl.get_svg(self.plot_id)
					fw.write(svg_str)

		elif iformat == 'pdf':
			printer = QPrinter(QPrinter.PrinterResolution)
			printer.setOutputFormat(QPrinter.PdfFormat)
			printer.setOutputFileName(ifile)
			printer.setResolution(300)

			size = scene_rect.size()

			page_size = QPageSize(size, QPageSize.Point)
			printer.setPageSize(page_size)
			printer.setPageMargins(QMarginsF(0, 0, 0, 0))
			printer.setFullPage(True)
			painter = QPainter(printer)
			painter.setRenderHint(QPainter.Antialiasing)
			painter.setRenderHint(QPainter.SmoothPixmapTransform)

			scene.render(painter)
			painter.end()

		else:
			size = scene_rect.size().toSize()

			if size.width() < 3000:
				size *= 3

			image = QImage(size, QImage.Format_RGB32)
			image.fill(Qt.white)

			painter = QPainter(image)
			painter.setRenderHint(QPainter.Antialiasing)
			painter.setRenderHint(QPainter.SmoothPixmapTransform)
			scene.render(painter)
			painter.end()

			dpm = 300 * 39.37
			image.setDotsPerMeterX(dpm)
			image.setDotsPerMeterY(dpm)
			#image.save(ifile, quality=100)

			writer = QImageWriter(ifile)

			if iformat == 'png':
				writer.setQuality(85)
			else:
				writer.setQuality(100)

			if iformat in ['tif', 'tiff']:
				writer.setCompression(1)

			writer.write(image)

class CirchartGenomeWindowSize(QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)

		self.win_spin = QSpinBox(self)
		self.win_spin.setValue(5)
		self.win_spin.setMinimum(1)
		self.win_spin.setMaximum(1000000)
		self.win_spin.setAlignment(Qt.AlignCenter)

		self.step_spin = QSpinBox(self)
		self.step_spin.setValue(3)
		self.step_spin.setMinimum(1)
		self.step_spin.setMaximum(1000000)
		self.step_spin.setAlignment(Qt.AlignCenter)
		self.step_spin.setVisible(False)

		self.win_unit = QComboBox(self)
		self.win_unit.addItems(['BP', 'KB', 'MB'])
		self.win_unit.setCurrentIndex(2)

		self.step_unit = QComboBox(self)
		self.step_unit.addItems(['BP', 'KB', 'MB'])
		self.step_unit.setCurrentIndex(2)
		self.step_unit.setVisible(False)

		self.win_label = QLabel("Window size", self)
		self.step_label = QLabel("Step size", self)
		self.step_label.setVisible(False)

		self.fixed_radio = QRadioButton("Use tumbling window", self)
		self.fixed_radio.setChecked(True)
		self.slide_radio = QRadioButton("Use sliding window", self)
		self.slide_radio.toggled.connect(self._on_slide_checked)

		layout = QGridLayout()
		layout.setColumnStretch(0, 1)
		layout.setColumnStretch(2, 1)
		layout.setContentsMargins(0, 0, 0, 0)
		layout.addWidget(self.fixed_radio, 0, 0, 1, 2)
		layout.addWidget(self.slide_radio, 0, 2, 1, 2)
		layout.addWidget(self.win_label, 1, 0)
		layout.addWidget(self.step_label, 1, 2)
		layout.addWidget(self.win_spin, 2, 0)
		layout.addWidget(self.win_unit, 2, 1)
		layout.addWidget(self.step_spin, 2, 2)
		layout.addWidget(self.step_unit, 2, 3)
		self.setLayout(layout)

	def _on_slide_checked(self, checked):
		self.step_label.setVisible(checked)
		self.step_spin.setVisible(checked)
		self.step_unit.setVisible(checked)

	def get_values(self):
		scales = [1, 1000, 1000000]

		window_size = self.win_spin.value() * scales[self.win_unit.currentIndex()]

		if self.slide_radio.isChecked():
			step_size = self.step_spin.value() * scales[self.step_unit.currentIndex()]
		else:
			step_size = window_size

		return {
			'window': window_size,
			'step': step_size
		}

class CirchartCustomColorTable(QTableView):
	def __init__(self, parent=None):
		super().__init__(parent)

		#self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
		#self.horizontalHeader().hide()
		self.horizontalHeader().setStretchLastSection(True)
		self.verticalHeader().hide()
		self.create_model()

	def create_model(self):
		self._model = CirchartCustomColorModel(self)
		self.setModel(self._model)
		self._model.update_model()


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
		#worker = CirchartCircosColorWorker()
		#worker.signals.result.connect(self._model.set_data)
		#QThreadPool.globalInstance().start(worker)
		app = QApplication.instance()
		colors = app.property('precolors')
		self._model.set_data(colors)

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
			

class CirchartCollinearityIdmappingWidget(QWidget):
	def __init__(self, title=None, parent=None, label=True):
		super().__init__(parent)
		self.title = title
		self.label = label
		self.features = {}
		self.attributes = {}

		self._create_widgets()
		self._init_layouts()
		self._init_widgets()

	def _create_widgets(self):
		self.title_label = QLabel("<b>{}</b>".format(self.title), self)

		if self.label:
			self.kary_label = QLabel("Karyotype", self)
			self.anno_label = QLabel("Annotation", self)
			self.feat_label = QLabel("Feature", self)
			self.attr_label = QLabel("Attirbute", self)

		self.kary_select = QComboBox(self)
		self.anno_select = QComboBox(self)
		self.anno_select.currentIndexChanged.connect(self._on_annotation_changed)
		self.feat_select = QComboBox(self)
		self.attr_select = QComboBox(self)

	def _init_layouts(self):
		layout = QGridLayout()
		layout.setContentsMargins(0, 0, 0, 0)
		self.setLayout(layout)

		if self.label:
			layout.addWidget(self.title_label, 1, 0)

			layout.addWidget(self.kary_label, 0, 1)
			layout.addWidget(self.kary_select, 1, 1)

			layout.addWidget(self.anno_label, 0, 2)
			layout.addWidget(self.anno_select, 1, 2)

			layout.addWidget(self.feat_label, 0, 3)
			layout.addWidget(self.feat_select, 1, 3)

			layout.addWidget(self.attr_label, 0, 4)
			layout.addWidget(self.attr_select, 1, 4)

		else:
			layout.addWidget(self.title_label, 0, 0)
			layout.addWidget(self.kary_select, 0, 1)
			layout.addWidget(self.anno_select, 0, 2)
			layout.addWidget(self.feat_select, 0, 3)
			layout.addWidget(self.attr_select, 0, 4)

	def _init_widgets(self):
		ks = SqlControl.get_datas_by_type('karyotype')
		for k in ks:
			self.kary_select.addItem(k.name, k.id)

		ans = SqlControl.get_datas_by_type('annotation')
		for a in ans:
			meta = str_to_dict(a.meta)
			self.features[a.id] = meta['features']
			self.attributes[a.id] = meta['attributes']

			self.anno_select.addItem(a.name, a.id)

	def _on_annotation_changed(self, index):
		index = self.anno_select.itemData(index)

		self.attr_select.clear()
		self.feat_select.clear()

		feats = self.features[index]
		self.feat_select.addItems(feats)

		attrs = self.attributes[index]
		self.attr_select.addItems(attrs)

	def get_values(self):
		return {
			'karyotype': self.kary_select.currentData(),
			'annotation': self.anno_select.currentData(),
			'feature': self.feat_select.currentText(),
			'attribute': self.attr_select.currentText()
		}
