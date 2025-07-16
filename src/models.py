from PySide6.QtGui import *
from PySide6.QtCore import *

from backend import *

__all__ = [
	'CirchartDataTreeModel',
	'CirchartDataTableModel',
]

class CirchartBaseTableModel(QAbstractTableModel):
	row_count = Signal(int)
	col_count = Signal(int)
	_headers = []
	_fields = []
	_table = None

	def __init__(self, parent=None):
		super().__init__(parent)

		self.displays = []
		self.selected = []

		self.total_count = 0
		self.read_count = 0
		self.read_size = 200

		self.cache_data = {}

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
		return SqlQuery(self._table)\
			.select('id')\
			.limit(fetch_count)\
			.offset(self.read_count)

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

class CirchartDataTreeModel(CirchartBaseTableModel):
	_table = 'data'
	_fields = ['name', 'type']
	_headers = ['Name', 'Type']

	@classmethod
	def add_data(cls, name, type, path):
		sql = SqlQuery(cls._table)\
			.insert(4)

		return SqlBase.insert_row(sql, None, name, type, path)

	def get_data(self, name):
		sql = SqlQuery(self._table)\
			.select()\
			.where('name=?')\
			.first()

		return SqlBase.get_row(sql, name)

	def get_datas(self, tag):
		sql = SqlQuery(self._table)\
			.select()\
			.where('tag=?')\

		return SqlBase.get_rows(sql, tag)

	def get_data_table(self, index):
		rowid = self.get_id(index)
		rowtb = self.get_value(index.row(), 1)
		return "{}{}".format(rowtb, rowid)

class CirchartDataTableModel(CirchartBaseTableModel):
	@staticmethod
	def add_data(table, rows, columns):
		SqlBase.create_table(table, columns)

		sql = SqlQuery(table)\
			.insert(len(rows[0]))

		SqlBase.insert_rows(sql, rows)

	def change_table(self, table):
		self.set_table(table)
		fields = SqlBase.get_fields(table)
		self.set_headers(fields)

	







