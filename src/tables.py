from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *

#from utils import *
#from config import *
from models import *
#from workers import *
#from backend import *

__all__ = [
	'CirchartDataTreeWidget',
	'CirchartPlotTreeWidget',
	'CirchartDataTableWidget',
	'CirchartCheckTableWidget',
]

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
		meta_action = QAction("View meta")
		meta_action.triggered.connect(self.view_meta)
		rename_action = QAction("Rename")
		rename_action.triggered.connect(self.rename_data)
		delete_action = QAction("Delete")
		delete_action.triggered.connect(self.delete_data)

		menu = QMenu(self)
		menu.addAction(rename_action)
		menu.addAction(delete_action)
		menu.addSeparator()
		menu.addAction(meta_action)

		menu.exec(self.mapToGlobal(pos))

	def rename_data(self):
		new_name, ok = QInputDialog.getText(self, "Rename data", "Input new name:")
		new_name = new_name.strip()

		if ok and new_name:
			index = self.currentIndex()
			self._model.rename_data(index, new_name)

	def view_meta(self):
		pass

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
		self._model = None

	def create_model(self, table):
		match table:
			case 'karyotype':
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
		return True if self._model.selected else False
