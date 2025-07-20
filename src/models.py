from PySide6.QtGui import *
from PySide6.QtCore import *

from backend import *

__all__ = [
	'CirchartDataTreeModel',
	'CirchartDataTableModel',
	'CirchartGenomeTableModel',
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

	@property
	def count_sql(self):
		return SqlQuery(self._table)\
			.select('COUNT(1)')\
			.first()

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

class CirchartGenomeTableModel(CirchartDataTableModel):
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


class CirchartDataTreeModel(CirchartBaseTableModel):
	_table = 'data'
	_fields = ['name', 'type']
	_headers = ['Name', 'Type']

	







