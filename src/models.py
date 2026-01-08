import distinctipy

from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *

from config import *
from backend import *

__all__ = [
	'CirchartDataTreeModel',
	'CirchartPlotTreeModel',
	'CirchartDataTableModel',
	'CirchartKaryotypeDelegate',
	'CirchartKaryotypeTableModel',
	'CirchartCircosColorModel',
]

class CirchartBaseTableModel(QAbstractTableModel):
	row_count = Signal(int)
	col_count = Signal(int)
	sel_count = Signal(int)
	_headers = []
	_fields = []
	_table = None

	def __init__(self, parent=None, checkable=False, sortable=False):
		super().__init__(parent)
		self.checkable = checkable
		self.sortable = sortable

		self.displays = []
		self.selected = []

		self.total_count = 0
		self.read_count = 0
		self.read_size = 200

		self.cache_data = {}

		self.order_by = None
		self.order_asc = True
		self.filters = {}

	def rowCount(self, parent=QModelIndex()):
		if parent.isValid():
			return 0

		return len(self.displays)

	def columnCount(self, parent=QModelIndex()):
		if parent.isValid():
			return 0

		return len(self._headers)

	def data(self, index, role=Qt.DisplayRole):
		if not index.isValid():
			return None

		row = index.row()
		col = index.column()

		if role == Qt.DisplayRole:
			return self.get_value(row, col)

		elif role == Qt.CheckStateRole:
			if col == 0 and self.checkable:
				if self.displays[row] in self.selected:
					return Qt.Checked

				else:
					return Qt.Unchecked

	def setData(self, index, value, role):
		if not index.isValid():
			return False

		row = index.row()
		col = index.column()

		if role == Qt.CheckStateRole and col == 0:
			rowid = self.displays[row]

			if Qt.CheckState(value) == Qt.Checked:
				if rowid not in self.selected:
					self.selected.append(rowid)

			else:
				if rowid in self.selected:
					self.selected.remove(rowid)

			self.dataChanged.emit(index, index)
			self.sel_count.emit(len(self.selected))

			return True

		return False

	def flags(self, index):
		flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable

		if index.column() == 0:
			flags |= Qt.ItemIsUserCheckable

		return flags

	def sort(self, column, order):
		if self._table is None:
			return

		if self._fields:
			self.order_by = self._fields[column]

		else:
			fields = SqlBase.get_fields(self._table)
			self.order_by = fields[column]

		if order == Qt.SortOrder.DescendingOrder:
			self.order_asc = False
		
		elif order == Qt.AscendingOrder:
			self.order_asc = True

		else:
			self.order_by = None

		self.update_model()

	def headerData(self, section, orientation, role=Qt.DisplayRole):
		if orientation == Qt.Horizontal and role == Qt.DisplayRole:
			return self._headers[section]

	def canFetchMore(self, parent):
		if parent.isValid():
			return False

		if self.read_count < self.total_count:
			return True

		return False

	def fetchMore(self, parent):
		if parent.isValid():
			return

		ids = SqlBase.get_column(self.read_sql)
		fetch_count = len(ids)
		fetch_end = self.read_count+fetch_count-1
		self.beginInsertRows(QModelIndex(), self.read_count, fetch_end)
		self.displays.extend(ids)
		self.read_count += fetch_count
		self.endInsertRows()

	def set_headers(self, headers):
		self._headers = headers

	def set_fields(self, fields):
		self._fields = fields

	def set_table(self, table):
		self._table = table

	def set_filter(self, **filters):
		pass

	@property
	def count_sql(self):
		return SqlQuery(self._table)\
			.select('COUNT(1)')\
			.first()

	@property
	def delete_sql(self):
		return SqlQuery(self._table)\
			.delete()\
			.where('id=?')

	@property
	def read_sql(self):
		remain_count = self.total_count - self.read_count
		fetch_count = min(self.read_size, remain_count)
		sql = SqlQuery(self._table)\
			.select('id')\
			.limit(fetch_count)\
			.offset(self.read_count)

		if self.order_by:
			sql = sql.orderby(self.order_by, asc=self.order_asc)

		return sql

	@property
	def get_sql(self):
		return SqlQuery(self._table)\
			.select(*self._fields)\
			.where('id=?')\
			.first()

	def update_cache(self, row):
		row_id = self.displays[row]
		self.cache_data ={row: SqlBase.get_row(self.get_sql, row_id)}

	def update_count(self):
		self.row_count.emit(self.total_count)
		self.col_count.emit(len(self._headers))

	def get_value(self, row, col):
		if row not in self.cache_data:
			self.update_cache(row)

		return self.cache_data[row][col]

	def get_id(self, index):
		return self.displays[index.row()]

	def get_table(self):
		return self._table

	def remove_row(self, index, parent=QModelIndex()):
		row = index.row()
		self.beginRemoveRows(parent, row, row)
		SqlBase.delete_row(self.delete_sql, self.displays[row])
		self.displays.pop(row)
		self.total_count -= 1
		self.read_count -= 1
		self.endRemoveRows()
		self.update_count()

	def update_model(self):
		self.beginResetModel()
		self.read_count = 0
		self.selected = []
		self.total_count = SqlBase.get_one(self.count_sql)
		self.displays = SqlBase.get_column(self.read_sql)
		self.read_count = len(self.displays)
		self.cache_data = {}
		self.endResetModel()
		self.update_count()

	def reset_model(self):
		self.beginResetModel()
		self.cache_data = {}
		self.read_count = 0
		self.displays = []
		self.selected = []
		self.total_count = 0
		self.endResetModel()
		self.update_count()

	def clear_model(self):
		sql = SqlQuery(self._table).delete()
		SqlBase.query(sql)
		self.reset()

	def update_row_by_dataid(self, data_id):
		if data_id in self.displays:
			row_id = self.displays.index(data_id)
			self.update_cache(row_id)

	def get_selected_rows(self):
		if not self.selected:
			return

		select_count = len(self.selected)
		extract_once = 100

		if select_count == self.total_count:
			sql = SqlQuery(self._table).select()

			rows = []

			for row in SqlBase.query(sql):
				rows.append(row)

				if len(rows) == extract_once:
					yield rows

			if rows:
				yield rows

		else:
			for i in range(0, select_count, extract_once):
				ids = self.selected[i:i+extract_once]

				sql = SqlQuery(self._table)\
					.select()\
					.where('id IN ({})'.format(','.join(['?']*len(ids))))

				yield SqlBase.get_rows(sql, *ids)

class CirchartDataTableModel(CirchartBaseTableModel):
	def change_table(self, table):
		self.set_table(table)
		fields = [field.capitalize() for field in SqlBase.get_fields(table)]
		self.set_headers(fields)

class CirchartKaryotypeDelegate(QStyledItemDelegate):
	def __init__(self, parent=None):
		super().__init__(parent)

	def createEditor(self, parent, option, index):
		col = index.column()

		if col == 3:
			return QLineEdit(parent)

		elif col == 7:
			return QColorDialog(parent)

	def setEditorData(self, editor, index):
		col = index.column()
		

		if col == 7:
			value = index.model().data(index, Qt.BackgroundRole)
			editor.setCurrentColor(value)

		elif col == 3:
			value = index.model().data(index, Qt.DisplayRole)
			editor.setText(value)

	def setModelData(self, editor, model, index):
		col = index.column()

		if col == 7:
			value = editor.currentColor()

			if value.isValid():
				model.setData(index, value, Qt.EditRole)

		elif col == 3:
			value = editor.text()
			model.setData(index, value, Qt.EditRole)

	def updateEditorGeometry(self, editor, option, index):
		if index.column() == 3:
			editor.setGeometry(option.rect)


class CirchartKaryotypeTableModel(CirchartDataTableModel):
	def data(self, index, role=Qt.DisplayRole):
		if not index.isValid():
			return None

		row = index.row()
		col = index.column()

		if role == Qt.DisplayRole:
			if col == 7:
				return None

			return self.get_value(row, col)

		elif role == Qt.CheckStateRole:
			if col == 0 and self.checkable:
				if self.displays[row] in self.selected:
					return Qt.Checked

				else:
					return Qt.Unchecked

		elif role == Qt.BackgroundRole:
			if col == 7:
				r, g, b = self.get_value(row, col).split(',')
				return QColor(int(r), int(g), int(b))

	def flags(self, index):
		flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable

		if index.column() in [3, 7]:
			flags |= Qt.ItemIsEditable

		return flags

	def setData(self, index, value, role):
		if role == Qt.EditRole:
			col = index.column()

			if col == 3:
				self.update_name(index, value)

			elif col == 7:
				self.update_color(index, value)
				
			self.dataChanged.emit(index, index)
			return True

		return False

	def update_name(self, index, name):
		kid = self.get_id(index)
		sql = SqlQuery(self._table)\
			.update('name')\
			.where('id=?')

		SqlBase.update_row(sql, name, kid)

	def update_color(self, index, color):
		kid = self.get_id(index)
		r, g, b, _ = color.toTuple()
		color = "{},{},{}".format(r, g, b)
		sql = SqlQuery(self._table)\
			.update('color')\
			.where('id=?')

		SqlBase.update_row(sql, color, kid)

	def update_single_color(self, color):
		r, g, b, _ = color.toTuple()
		color = "{},{},{}".format(r, g, b)
		sql = SqlQuery(self._table)\
			.update('color')
		SqlBase.update_row(sql, color)

		sindex = self.createIndex(0, 7)
		eindex = self.createIndex(self.total_count-1, 7)
		self.dataChanged.emit(sindex, eindex)

	def update_random_color(self):
		colors = distinctipy.get_colors(self.total_count)

		sql = SqlQuery(self._table)\
			.update('color')\
			.where('rowid=?')

		for i, c in enumerate(colors, 1):
			c = ','.join(map(str, distinctipy.get_rgb256(c)))
			SqlBase.update_row(sql, c, i)

		sindex = self.createIndex(0, 7)
		eindex = self.createIndex(self.total_count-1, 7)
		self.dataChanged.emit(sindex, eindex)

	def update_default_color(self):
		#get chr colors from circos
		color_file = CIRCOS_PATH / 'etc' / 'colors.ucsc.conf'

		circos_colors = {}
		with open(str(color_file)) as fh:
			for line in fh:
				if line.startswith('chr'):
					cols = line.strip().split('=')
					if ',' in cols[1]:
						circos_colors[cols[0].strip().lower()] = cols[1].strip()

		sql = SqlQuery(self._table)\
			.update('color')\
			.where('rowid=?')

		for i in range(self.total_count):
			name = self.createIndex(i, 3).data(Qt.DisplayRole)
			label = self.createIndex(i, 4).data(Qt.DisplayRole)

			if label.lower() in circos_colors:
				color = circos_colors[label.lower()]

			elif name.lower() in circos_colors:
				color = circos_colors[name.lower()]

			else:
				temp = 'chr{}'.format(i+1)

				if temp in circos_colors:
					color = circos_colors[temp]
				else:
					color = circos_colors['chrun']

			SqlBase.update_row(sql, color, i+1)

		sindex = self.createIndex(0, 7)
		eindex = self.createIndex(self.total_count-1, 7)
		self.dataChanged.emit(sindex, eindex)

class CirchartDataTreeModel(CirchartBaseTableModel):
	_table = 'data'
	_fields = ['name', 'type']
	_headers = ['Name', 'Type']

class CirchartPlotTreeModel(CirchartBaseTableModel):
	_table = 'plot'
	_fields = ['name', 'type']
	_headers = ['Name', 'Type']

	
class CirchartCircosColorModel(QAbstractTableModel):
	def __init__(self, parent=None):
		super().__init__(parent)
		self._colors = []
		self._rows = 0
		self._cols = 0

	def rowCount(self, parent=QModelIndex()):
		if parent.isValid():
			return 0

		return self._rows

	def columnCount(self, parent=QModelIndex()):
		if parent.isValid():
			return 0

		return self._cols

	def flags(self, index):
		row = index.row()
		col = index.column()

		if col == 0:
			return Qt.ItemIsEnabled

		if col > 0 and col < len(self._colors[row]):
			return Qt.ItemIsEnabled | Qt.ItemIsSelectable

		return Qt.NoItemFlags

	def data(self, index, role=Qt.DisplayRole):
		if not index.isValid():
			return

		row = index.row()
		col = index.column()

		if role == Qt.DisplayRole:
			if col == 0:
				return self._colors[row][col]

		elif role == Qt.BackgroundRole:
			if col > 0 and col < len(self._colors[row]):
				return self._colors[row][col]

	def set_data(self, colors):
		self.beginResetModel()
		self._colors = colors
		self._rows = len(colors)
		self._cols = 16
		self.endResetModel()

	def get_color(self, index):
		row = index.row()
		col = index.column()
		return self._colors[row][col]

		





