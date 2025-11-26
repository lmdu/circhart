import os
import traceback
import multiprocessing

from PySide6.QtGui import *
from PySide6.QtCore import *

from config import *
from utils import *
from confile import *
from process import *
from backend import *

__all__ = [
	'CirchartImportGenomeWorker',
	'CirchartImportAnnotationWorker',
	'CirchartImportBuscoWorker',
	'CirchartGCContentPrepareWorker',
	'CirchartDensityPrepareWorker',
	'CirchartCircosPlotWorker',
	'CirchartProjectSaveWorker',
	'CirchartCircosColorWorker',
	'CirchartSnailPlotWorker',
]

class CirchartWorkerSignals(QObject):
	error = Signal(str)
	result = Signal(object)
	toggle = Signal(bool)
	message = Signal(str)
	started = Signal()
	stopped = Signal()
	success = Signal()
	progress = Signal(int)
	finished = Signal()

class CirchartBaseWorker(QRunnable):
	def __init__(self, params={}):
		super().__init__()
		self.params = params
		self.signals = CirchartWorkerSignals()

	def preprocess(self):
		pass

	def process(self):
		pass

	def run(self):
		try:
			self.signals.toggle.emit(True)
			self.signals.started.emit()
			self.preprocess()
			self.process()
			self.signals.stopped.emit()
			self.signals.success.emit()

		except:
			errmsg = traceback.format_exc()
			self.signals.error.emit(errmsg)

			if APP_DEBUG:
				print(errmsg)

		finally:
			self.signals.finished.emit()
			self.signals.toggle.emit(False)

	def on_error_occurred(self, error):
		self.signals.error.emit(str(error))

	def make_tempdir(self):
		self.tempdir = QTemporaryDir()
		self.tempdir.setAutoRemove(False)

		if not self.tempdir.isValid():
			raise Exception("Could not create temporary directory")

		if APP_DEBUG:
			print(self.tempdir.path())

		return self.tempdir.path()

class CirchartProcessWorker(CirchartBaseWorker):
	processor = None

	def __init__(self, params):
		super().__init__(params)
		self.queue = multiprocessing.Queue()

	def save_result(self, res):
		pass

	def response(self, res):
		match res['action']:
			case 'error':
				self.signals.error.emit(res['message'])

			case 'message':
				self.signals.message.emit(res['message'])

			case 'result':
				self.save_result(res['message'])

			case 'finished':
				self.signals.finished.emit()
				self.queue.close()

	def process(self):
		self.runner = self.processor(self.queue, self.params)
		self.runner.start()

		while True:
			try:
				res = self.queue.get()
				self.response(res)

			except ValueError:
				break

class CirchartImportGenomeWorker(CirchartProcessWorker):
	processor = CirchartImportFastaProcess

	def preprocess(self):
		qf = QFileInfo(self.params['fasta'])
		name = qf.completeBaseName()
		self.table_index = SqlControl.add_data(name, 'genome', self.params['fasta'])
		SqlControl.create_genome_table(self.table_index)

	def save_result(self, res):
		SqlControl.add_genome_data(self.table_index, res)

class CirchartImportAnnotationWorker(CirchartProcessWorker):
	processor = CirchartImportAnnotationProcess

	def preprocess(self):
		qf = QFileInfo(self.params['annotation'])
		name = qf.completeBaseName()
		self.table_index = SqlControl.add_data(name, 'annotation', self.params['annotation'])
		SqlControl.create_annotation_table(self.table_index)

	def save_result(self, res):
		SqlControl.add_annotation_data(self.table_index, res)

class CirchartImportBuscoWorker(CirchartProcessWorker):
	processor = CirchartImportBuscoProcess

	def preprocess(self):
		qf = QFileInfo(self.params['buscofile'])
		name = qf.completeBaseName()

		with open(self.params['buscofile']) as fh:
			for line in fh:
				if line[0] == '#' and 'version' in line:
					version = line.split(':')[-1].strip()

				elif line[0] == '#' and 'lineage' in line:
					lineage = line.split(':')[1].split('(')[0].strip()
					buscos = line.split(':')[-1].strip().strip(')')

				else:
					break

		metadata = dict_to_str({'version': version, 'lineage': lineage, 'buscos': buscos})
		self.table_index = SqlControl.add_data(name, 'busco', metadata)
		SqlControl.create_annotation_table(self.table_index)

	def save_result(self, res):
		SqlControl.add_annotation_data(self.table_index, res)

class CirchartGCContentPrepareWorker(CirchartProcessWorker):
	processor = CirchartGCContentPrepareProcess

	def preprocess(self):
		data = SqlControl.get_data_by_id(self.params['karyotype'])
		objs = SqlControl.get_data_objects('karyotype', self.params['karyotype'])

		self.params['axes'] = {
			obj.label: (obj.uid, obj.end)
			for obj in objs if obj.type == 'chr'
		}
		self.table_index = SqlControl.add_data("{}_gc_content".format(data.name), 'plotdata')
		SqlControl.create_plot_data_table(self.table_index)

	def save_result(self, res):
		SqlControl.add_plot_data(self.table_index, res)

class CirchartDensityPrepareWorker(CirchartProcessWorker):
	processor = CirchartDensityPrepareProcess

	def preprocess(self):
		data = SqlControl.get_data_by_id(self.params['karyotype'])
		objs = SqlControl.get_data_objects('karyotype', self.params['karyotype'])

		self.params['axes'] = {
			obj.label: (obj.uid, obj.end)
			for obj in objs if obj.type == 'chr'
		}
		data_name = "{}_{}_density".format(data.name, self.params['feature'])
		self.table_index = SqlControl.add_data(data_name, 'plotdata')
		SqlControl.create_plot_data_table(self.table_index)

		pos = SqlControl.get_annotation_content(self.params['annotation'], self.params['feature'])
		self.params['loci'] = {}

		for p in pos:
			if p[0] not in self.params['loci']:
				self.params['loci'][p[0]] = []

			self.params['loci'][p[0]].append((p[1], p[2]))

	def save_result(self, res):
		SqlControl.add_plot_data(self.table_index, res)

class CirchartCircosPlotWorker(CirchartBaseWorker):
	processor = CirchartCircosPlotProcess

	def preprocess(self):
		workdir = self.make_tempdir()

		for index in self.params['general']['global']['karyotype']:
			outfile = "karyotype{}.txt".format(index)
			data = SqlControl.get_data_content('karyotype', index)
			save_circos_data(workdir, outfile, data)

		for k in self.params:
			if k.startswith('track'):
				index = self.params[k]['main']['data']
				outfile = "data{}.txt".format(index)

				if os.path.isfile(outfile):
					continue

				data = SqlControl.get_data_content('plotdata', index)
				save_circos_data(workdir, outfile, data)

		confile = os.path.join(workdir, 'plot.conf')
		configer = CirchartCircosConfile(self.params)
		configer.save_to_file(confile)

	def process_error(self):
		error_data = self.runner.readAllStandardError()
		error_str = error_data.data().decode()

		if error_str:
			self.signals.error.emit(error_str)

			if APP_DEBUG:
				print(error_str)

	def process(self):
		parent = QObject()
		self.runner = self.processor(parent, self.tempdir.path())
		loop = QEventLoop()
		self.runner.finished.connect(loop.quit)
		self.runner.finished.connect(self.save_result)
		self.runner.errorOccurred.connect(loop.quit)
		self.runner.readyReadStandardError.connect(self.process_error)
		self.runner.start()
		loop.exec()

	def save_result(self):
		svg_file = os.path.join(self.tempdir.path(), 'circos.svg')

		if os.path.isfile(svg_file):
			with open(svg_file) as fh:
				content = fh.read()

			params = dict_to_str(self.params)
			plotid = self.params['general']['global']['plotid']
			SqlControl.update_plot(params, content, plotid)

			self.signals.result.emit(plotid)

class CirchartSnailPlotWorker(CirchartProcessWorker):
	processor = CirchartSnailPlotProcess

	def preprocess(self):
		workdir = self.make_tempdir()
		index = self.params['genome']

		data = SqlControl.get_data_content('genome', index)
		ids = []
		gcs = []
		lens = []
		ns = []
		size = 0
		count = 0

		for row in data:
			ids.append(row[0])
			lens.append(row[1])
			gcs.append(row[2])
			ns.append(row[3])

			size += row[1]
			count += 1

		metadata = {
			'id': "blobdir",
			'assembly': {
				'file': 'genome.fa',
				'scaffold-count': count,
				'span': size
			},
			'fields': [
				{
					'id': 'identifiers',
					'type': 'identifiers'
				},
				{
					'id': 'gc',
					'preload': True,
					'scale': 'scaleLinear',
					'name': 'GC',
					'datatype': 'float',
					'range': [min(gcs), max(gcs)],
					'type': 'variable'
				},
				{
					'id': 'length',
					'preload': True,
					'scale': 'scaleLog',
					'name': 'Length',
					'clamp': False,
					'datatype': 'integer',
					'range': [min(lens), max(lens)],
					'type': 'variable'
				},
				{
					'id': 'ncount',
					'scale': 'scaleLinear',
					'name': 'N count',
					'datatype': 'integer',
					'range': [min(ns), max(ns)],
					'type': 'variable'
				}
			],
			'links': {},
			'name': 'blobdir',
			'plot': {
				'x': 'gc',
				'z': 'length'
			},
			'record_type': 'record',
			'records': count,
			'taxon': {},
			'version': 1,
			'revision': 0
		}

		datasets = {
			'identifiers.json': {'values': ids, 'keys': []},
			'gc.json': {'values': gcs, 'keys': []},
			'length.json': {'values': lens, 'keys': []},
			'ncount.json': {'values': ns, 'keys': []},
			'meta.json': metadata,
		}

		for jfile, data in datasets.items():
			save_snail_data(workdir, jfile, data)

		self.params['workdir'] = workdir

	def save_result(self, res):
		svg_file = os.path.join(self.tempdir.path(), 'snail.svg')

		if os.path.isfile(svg_file):
			with open(svg_file) as fh:
				content = fh.read()

			params = dict_to_str(self.params)
			plotid = self.params['plotid']
			SqlControl.update_plot(params, content, plotid)

			self.signals.result.emit(plotid)
		
class CirchartProjectSaveWorker(CirchartBaseWorker):
	def process(self):
		self.signals.message.emit("Saving to {}".format(self.params['sfile']))
		progress = 0
		SqlBase.commit()

		with SqlBase.save_to_file(self.params['sfile']) as backup:
			while not backup.done:
				backup.step(10)
				p = int((backup.pagecount - backup.remaining) / backup.pagecount * 100)

				if p > progress:
					self.signals.progress.emit(p)
					progress = p

		self.signals.message.emit("Successfully saved project to {}".format(self.params['sfile']))

class CirchartCircosColorWorker(CirchartBaseWorker):
	def process(self):
		brewer_file = str(CIRCOS_PATH / 'etc' / 'colors.brewer.conf')

		brewer_colors = {}
		with open(brewer_file) as fh:
			for line in fh:
				if line.startswith('#'):
					continue

				if not line.strip():
					continue

				cols = line.strip().split('=')

				if cols[1].count(',') != 2:
					continue

				cname = '-'.join(cols[0].strip().split('-')[0:-1])
				r, g, b = cols[1].strip().split(',')

				if cname not in brewer_colors:
					brewer_colors[cname] = [cname]

				brewer_colors[cname].append(QColor(int(r), int(g), int(b)))

		color_file = str(CIRCOS_PATH / 'etc' / 'colors.conf')

		color_list = []
		with open(color_file) as fh:
			for line in fh:
				if line.startswith('#'):
					continue

				if not line.strip():
					continue

				if '=' not in line:
					continue

				cols = line.strip().split('=')
				cname = cols[0].strip()

				if ',' in cols[1]:
					r, g, b = cols[1].strip().split(',')
					color_list.append([cname, QColor(int(r), int(g), int(b))])

				elif '-' in cols[1]:
					temp = cols[1].strip().split('-')
					temp_name = '-'.join(temp[0:-1])
					temp_color = brewer_colors[temp_name][int(temp[-1])]
					color_list.append([cname, temp_color])

		color_list.extend(brewer_colors.values())
		self.signals.result.emit(color_list)
