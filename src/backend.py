import apsw
import threading

__all__ = [
	'SqlTable',
	'SqlQuery',
	'SqlBase',
	'KaryotypeTable',
	'GenomeTable',
	'SqlControl',
]

from utils import *

class SqlTable:
	types = {int: 'INTEGER', float: 'REAL', str: 'TEXT'}

	def __setattr__(cls, name, val):
		super().__setattr__(name, val)

	@classmethod
	def tables(cls):
		for sc in cls.__subclasses__():
			if sc._index:
				continue

			table = sc.__name__.replace('Table', '').lower()
			fields = ['id INTEGER PRIMARY KEY']
			fields.extend([
				"{} {}".format(attr, cls.types[getattr(sc, attr)])
				for attr in sc.__dict__
				if not attr.startswith('_')
			])

			yield table, fields

	@classmethod
	def table(cls, index=None):
		fields = ['id INTEGER PRIMARY KEY']

		table = cls.__name__.replace('Table', '').lower()

		if index is not None:
			table = "{}_{}".format(table, index)

		for attr in cls.__dict__:
			if not attr.startswith('_'):
				fields.append("{} {}".format(attr, cls.types[getattr(cls, attr)]))

		return table, fields

	@classmethod
	def fields(cls):
		return [attr for attr in cls.__dict__ if not attr.startswith('_')]

class DataTable(SqlTable):
	_index = False
	name = str
	type = str
	meta = str

class PlotTable(SqlTable):
	_index = False
	name = str
	type = str
	param = str
	svg = str

class GenomeTable(SqlTable):
	_index = True
	chrom = str
	length = int
	gc = float
	ns = int

class KaryotypeTable(SqlTable):
	_index = True
	type = str
	parent = str
	uid = str
	label = str
	start = int
	end = int
	color = str

class AnnotationTable(SqlTable):
	_index = True
	chrom = str
	feature = str
	start = int
	end = int

class BuscoTable(SqlTable):
	_index = True
	busco = str
	status = str

class PlotDataTable(SqlTable):
	_index = True
	chrid = str
	start = int
	end = int
	value = float


class SqlQuery:
	def __init__(self, table):
		self._table = table
		self._selects = []
		self._updates = []
		self._inserts = []
		self._creates = []
		self._and_wheres = []
		self._or_wheres = []
		self._order_bys = []
		self._order_asc = True
		self._limit = []
		self._offset = []
		self._action = None
		self._querys = []

	def __str__(self):
		return self.build()

	def __add(self, item):
		self._querys.extend([' ', item])

	def create(self, *args):
		self._creates.extend(args)
		self._action = 'CREATE'
		return self

	def select(self, *args):
		self._selects.extend(args)
		self._action = 'SELECT'
		return self

	def insert(self, *args):
		self._inserts.extend(args)
		self._action = 'INSERT'
		return self

	def update(self, *args):
		self._updates.extend(args)
		self._action = 'UPDATE'
		return self

	def delete(self):
		self._action = 'DELETE'
		return self

	def drop(self):
		self._action = 'DROP'
		return self

	def where(self, *args, logic='and'):
		if logic == 'and':
			self._and_wheres.extend(args)
		elif logic == 'or':
			self._or_wheres.extend(args)

		return self

	def orderby(self, *args, asc=True):
		self._order_bys.extend(args)
		self._order_asc = asc
		return self

	def limit(self, num):
		self._limit = num
		return self

	def offset(self, num):
		self._offset = num
		return self

	def first(self):
		self._limit = 1
		return self

	def build(self):
		self._querys = [self._action]

		match self._action:
			case 'CREATE':
				self.__add("TABLE IF NOT EXISTS {} ({})".format(self._table, ','.join(self._creates)))

			case 'SELECT':
				if self._selects:
					self.__add(','.join(self._selects))
				else:
					self.__add('*')

				self.__add("FROM {}".format(self._table))
			
			case 'INSERT':
				self.__add("INTO {}".format(self._table))

				if self._inserts and isinstance(self._inserts[0], int):
					self.__add("VALUES ({})".format(','.join(['?']*self._inserts[0])))
				else:
					self.__add("({}) VALUES ({})".format(
						','.join(self._inserts),
						','.join(['?']*len(self._inserts))
						)
					)

			case 'UPDATE':
				self.__add("{} SET".format(self._table))
				self.__add(','.join("{}=?".format(u) for u in self._updates))

			case 'DELETE':
				self.__add("FROM {}".format(self._table))

			case 'DROP':
				self.__add("TABLE IF EXISTS {}".format(self._table))


		if self._and_wheres or self._or_wheres:
			self.__add("WHERE")

			if self._and_wheres:
				self.__add(' AND '.join(self._and_wheres))

			if self._or_wheres:
				if self._and_wheres:
					self.__add('OR')

				self.__add(' OR '.join(self._or_wheres))

		if self._order_bys:
			if self._order_asc:
				self.__add("ORDER BY {}".format(','.join(self._order_bys)))
			else:
				self.__add("ORDER BY {} DESC".format(','.join(self._order_bys)))

		if self._limit:
			self.__add("LIMIT {}".format(self._limit))

		if self._offset:
			self.__add("OFFSET {}".format(self._offset))

		return ''.join(self._querys)

class DataBackend:
	conn = None
	lock = threading.RLock()

	def __init__(self):
		self.connect()

	def __del__(self):
		if self.conn is not None:
			self.conn.close()

	def connect(self, file=':memory:'):
		if self.conn is not None:
			self.conn.close()

		self.conn = apsw.Connection(file)
		self.create_tables()

	def reconnect(self, file):
		_conn = self.conn
		self.conn = apsw.Connection(file)
		_conn.close()

	@property
	def cursor(self):
		with self.lock:
			cur = self.conn.cursor()

		return cur

	def query(self, sql, args=None):
		if args:
			return self.cursor.execute(str(sql), args)
		else:
			return self.cursor.execute(str(sql))

	def create_tables(self):
		for table, fields in SqlTable.tables():
			sql = SqlQuery(table).create(*fields)
			self.query(sql)

	def create_table(self, table, fields):
		sql = SqlQuery(table).create(*fields)
		self.query(sql)

	def insert_row(self, sql, *args):
		cur = self.query(sql, args)
		return cur.connection.last_insert_rowid()

	def insert_rows(self, sql, rows):
		self.cursor.executemany(str(sql), rows)

	def update_row(self, sql, *args):
		self.query(sql, args)

	def get_one(self, sql, *args):
		for row in self.query(sql, args):
			return row[0]

	def get_row(self, sql, *args):
		for row in self.query(sql, args):
			return row

	def get_rows(self, sql, *args):
		for row in self.query(sql, args):
			yield row

	def get_column(self, sql, *args):
		return [row[0] for row in self.query(sql, args)]

	def get_dict(self, sql, *args):
		res = self.query(sql, args)

		for row in res:
			fields = [col[0] for col in res.description]
			return AttrDict(zip(fields, row))

	def get_dicts(self, sql, *args):
		res = self.query(sql, args)
		fields = None

		for row in res:
			if fields is None:
				fields = [col[0] for col in res.description]
			yield AttrDict(zip(fields, row))

	def has_table(self, table):
		sql = SqlQuery('sqlite_master')\
			.select('name')\
			.where('type=?', 'name=?')\
			.first()
		res = self.get_one(sql, 'table', table)
		return True if res else False

	def has_data(self):
		sql = SqlQuery('data')\
			.select('1')\
			.first()
		res = self.get_one(sql)
		return True if res else False

	def get_fields(self, table):
		sql = SqlQuery(table).select().first()
		res = self.query(sql)
		return [col[0] for col in res.description]

	@property
	def autocommit(self):
		return self.conn.getautocommit()

	def begin(self):
		self.query("BEGIN")

	def commit(self):
		if not self.autocommit:
			self.query("COMMIT")

	def save(self):
		if self.changed:
			self.commit()
			self.begin()

	@property
	def changed(self):
		return self.conn.changes() > 0

	def save_to_file(self, sfile):
		target = apsw.Connection(sfile)
		return target.backup('main', self.conn, 'main')

SqlBase = DataBackend()

class SqlControl:
	@staticmethod
	def add_data(name, type, meta=''):
		sql = SqlQuery('data')\
			.insert('name', 'type', 'meta')

		return SqlBase.insert_row(sql, name, type, meta)

	@staticmethod
	def create_genome_table(index):
		table, fields = GenomeTable.table(index)
		SqlBase.create_table(table, fields)

	@staticmethod
	def add_genome_data(index, data):
		table, _ = GenomeTable.table(index)
		sql = SqlQuery(table)\
			.insert(*GenomeTable.fields())
		SqlBase.insert_rows(sql, data)

	@staticmethod
	def create_karyotype_table(index):
		table, fields = KaryotypeTable.table(index)
		SqlBase.create_table(table, fields)

	@staticmethod
	def add_karyotype_data(index, data):
		table, _ = KaryotypeTable.table(index)
		sql = SqlQuery(table)\
			.insert(*KaryotypeTable.fields())
		SqlBase.insert_rows(sql, data)

	@staticmethod
	def create_annotation_table(index):
		table, fields = AnnotationTable.table(index)
		SqlBase.create_table(table, fields)

	@staticmethod
	def add_annotation_data(index, data):
		table, _ = AnnotationTable.table(index)
		sql = SqlQuery(table)\
			.insert(*AnnotationTable.fields())
		SqlBase.insert_rows(sql, data)

	@staticmethod
	def create_busco_table(index):
		table, fields = BuscoTable.table(index)
		SqlBase.create_table(table, fields)

	@staticmethod
	def add_busco_data(index, data):
		table, _ = BuscoTable.table(index)
		sql = SqlQuery(table)\
			.insert(*BuscoTable.fields())
		SqlBase.insert_rows(sql, data)

	@staticmethod
	def create_plot_data_table(index):
		table, fields = PlotDataTable.table(index)
		SqlBase.create_table(table, fields)

	@staticmethod
	def add_plot_data(index, data):
		table, _ = PlotDataTable.table(index)
		sql = SqlQuery(table)\
			.insert(*PlotDataTable.fields())
		SqlBase.insert_rows(sql, data)

	@staticmethod
	def get_data_by_id(did):
		sql = SqlQuery('data')\
			.select()\
			.where('id=?')

		return SqlBase.get_dict(sql, did)

	@staticmethod
	def get_datas_by_type(type):
		sql = SqlQuery('data')\
			.select()\
			.where('type=?')

		return SqlBase.get_dicts(sql, type)

	@staticmethod
	def get_data_content(type, index):
		table = '{}_{}'.format(type, index)
		fields = SqlBase.get_fields(table)
		fields = fields[1:]

		sql = SqlQuery(table)\
			.select(*fields)

		return SqlBase.get_rows(sql)

	@staticmethod
	def get_data_objects(type, index):
		table = '{}_{}'.format(type, index)
		sql = SqlQuery(table)\
			.select()

		return SqlBase.get_dicts(sql)

	@staticmethod
	def get_annotation_features(index):
		table = '{}_{}'.format('annotation', index)
		sql = SqlQuery(table)\
			.select("DISTINCT feature")

		return SqlBase.get_column(sql)

	@staticmethod
	def get_annotation_content(index, feature):
		table = '{}_{}'.format('annotation', index)
		sql = SqlQuery(table)\
			.select('chrom', 'start', 'end')\
			.where('feature=?')\
			.orderby('chrom', 'start')

		return SqlBase.get_rows(sql, feature)

	@staticmethod
	def add_plot(name, type):
		sql = SqlQuery('plot')\
			.insert('name', 'type')

		rowid = SqlBase.insert_row(sql, name, type)
		return rowid

	@staticmethod
	def update_plot(param, svg, pid):
		sql = SqlQuery('plot')\
			.update('param', 'svg')\
			.where('id=?')

		SqlBase.update_row(sql, param, svg, pid)

	@staticmethod
	def get_svg(pid):
		sql = SqlQuery('plot')\
			.select('svg')\
			.where('id=?')

		return SqlBase.get_one(sql, pid)

	@staticmethod
	def get_params(pid):
		sql = SqlQuery('plot')\
			.select('param')\
			.where('id=?')

		return SqlBase.get_one(sql, pid)














	