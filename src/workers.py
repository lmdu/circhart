import os
import time
import traceback
import multiprocessing

from PySide6.QtGui import *
from PySide6.QtSvg import *
from PySide6.QtCore import *

from config import *
from utils import *
from confile import *
from process import *
from backend import *

__all__ = [
	'CirchartImportGenomeWorker',
	'CirchartImportAnnotationWorker',
	'CirchartImportCollinearityWorker',
	'CirchartImportBandsWorker',
	'CirchartImportDataWorker',
	'CirchartImportLinkDataWorker',
	'CirchartImportVariationsWorker',
	'CirchartImportRegionsWorker',
	'CirchartBandPrepareWorker',
	'CirchartGCContentPrepareWorker',
	'CirchartGCSkewPrepareWorker',
	'CirchartDensityPrepareWorker',
	'CirchartLinkPrepareWorker',
	'CirchartTextPrepareWorker',
	'CirchartCircosPlotWorker',
	'CirchartProjectSaveWorker',
	'CirchartCircosColorWorker',
	'CirchartSnailPlotWorker',
	'CirchartSvgRenderWorker',
]

class CirchartWorkerSignals(QObject):
	error = Signal(str)
	result = Signal(object)
	toggle = Signal(bool)
	warning = Signal(str)
	message = Signal(str)
	started = Signal()
	stopped = Signal()
	success = Signal()
	progress = Signal(int)
	finished = Signal()

class CirchartBaseWorker(QRunnable):
	def __init__(self, params={}):
		super().__init__()
		self.params = AttrDict(params)
		self.signals = CirchartWorkerSignals()

	def preprocess(self):
		pass

	def process(self):
		pass

	def cleanup(self):
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
			self.cleanup()

	def on_error_occurred(self, error):
		self.signals.error.emit(str(error))

	def make_tempdir(self):
		self.tempdir = QTemporaryDir()

		if APP_DEBUG:
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

			case 'warning':
				self.signals.warning.emit(res['message'])

			case 'message':
				self.signals.message.emit(res['message'])

			case 'result':
				self.save_result(res['message'])

			case 'finished':
			#	self.signals.finished.emit()
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

class CirchartImportBaseWorker(CirchartProcessWorker):
	data_type = None

	def preprocess(self):
		qf = QFileInfo(self.params['path'])
		name = qf.completeBaseName()
		meta = dict_to_str(self.params)
		self.data_index = SqlControl.add_data(name, self.data_type, meta)
		SqlControl.create_index_table(self.data_type, self.data_index)

	def save_result(self, res):
		SqlControl.add_index_data(self.data_type, self.data_index, res)

class CirchartImportGenomeWorker(CirchartImportBaseWorker):
	processor = CirchartImportFastaProcess
	data_type = 'genome'

class CirchartImportAnnotationWorker(CirchartImportBaseWorker):
	processor = CirchartImportAnnotationProcess
	data_type = 'annotation'

	def save_result(self, res):
		super().save_result(res['data'])
		SqlControl.update_data_meta(self.data_index, res['meta'])

class CirchartImportCollinearityWorker(CirchartImportBaseWorker):
	processor = CirchartImportCollinearityProcess
	data_type = 'collinearity'

class CirchartImportBandsWorker(CirchartImportBaseWorker):
	processor = CirchartImportBandsProcess
	data_type = 'bands'

class CirchartImportVariationsWorker(CirchartImportBaseWorker):
	processor = CirchartImportVariationsProcess
	data_type = 'variants'

class CirchartImportRegionsWorker(CirchartImportBaseWorker):
	processor = CirchartImportRegionsProcess
	data_type = 'regions'

class CirchartImportDataWorker(CirchartImportBaseWorker):
	processor = CirchartImportDataProcess

	def preprocess(self):
		self.params['colors'] = {c.name: c.color for c in SqlControl.get_custom_colors()}
		self.data_type = self.params['type']
		super().preprocess()

class CirchartImportLinkDataWorker(CirchartImportDataWorker):
	processor = CirchartImportLinkDataProcess

class CirchartPrepareWorker(CirchartProcessWorker):
	data_type = 'plotdata'

	def preprocess(self):
		objs = SqlControl.get_data_objects('karyotype', self.params.karyotype)

		self.params.axes = {
			obj.label: (obj.name, obj.end)
			for obj in objs if obj.type == 'chr'
		}

		self.data_index = SqlControl.add_data(self.params.dataname, self.data_type)
		SqlControl.create_index_table(self.data_type, self.data_index)

	def save_result(self, res):
		SqlControl.add_index_data(self.data_type, self.data_index, res)

class CirchartBandPrepareWorker(CirchartPrepareWorker):
	processor = CirchartBandPrepareProcess
	data_type = 'banddata'

	def preprocess(self):
		super().preprocess()

		objs = SqlControl.get_data_content('bands', self.params.bands)
		self.params.bands = list(objs)

class CirchartGCContentPrepareWorker(CirchartPrepareWorker):
	processor = CirchartGCContentPrepareProcess

	def preprocess(self):
		super().preprocess()

		gmeta = SqlControl.get_data_meta(self.params.genome)
		self.params['genome'] = gmeta['path']

class CirchartGCSkewPrepareWorker(CirchartGCContentPrepareWorker):
	processor = CirchartGCSkewPrepareProcess

class CirchartDensityPrepareWorker(CirchartPrepareWorker):
	processor = CirchartDensityPrepareProcess

	def preprocess(self):
		super().preprocess()

		ameta = SqlControl.get_data_meta(self.params.annotation)
		self.params['annotation'] = ameta['path']

class CirchartLinkPrepareWorker(CirchartProcessWorker):
	processor = CirchartLinkPrepareProcess
	data_type = 'linkdata'

	def preprocess(self):
		cmeta = SqlControl.get_data_meta(self.params['collinearity'])
		self.params['collinearity'] = cmeta['path']

		for k in self.params:
			if not k.startswith('sp'):
				continue

			rows = SqlControl.get_data_content('karyotype', self.params[k]['karyotype'])
			self.params[k]['karyotype'] = {row[3]: row[2] for row in rows}

			ameta = SqlControl.get_data_meta(self.params[k]['annotation'])
			self.params[k]['annotation'] = ameta['path']
			self.params[k]['annoformat'] = ameta['format']

		self.data_index = SqlControl.add_data(self.params.dataname, self.data_type)
		SqlControl.create_index_table(self.data_type, self.data_index)

class CirchartTextPrepareWorker(CirchartPrepareWorker):
	processor = CirchartTextPrepareProcess
	data_type = 'textdata'

	def preprocess(self):
		super().preprocess()

		ameta = SqlControl.get_data_meta(self.params['annotation'])
		self.params['annotation'] = ameta['path']

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
				ptype = self.params[k]['main']['type']
				index = self.params[k]['main']['data']

				if isinstance(index, int):
					outfile = "data{}.txt".format(index)
					kids = [index]
				else:
					outfile = "data{}.txt".format('-'.join(map(str, index)))
					kids = index

				if ptype == 'link':
					tag = 'linkdata'

				elif ptype == 'text':
					tag = 'textdata'

				elif ptype in ['tile', 'connector', 'highlight']:
					tag = 'locidata'

				else:
					tag = 'plotdata'

				for kid in kids:
					data = SqlControl.get_data_content(tag, kid)
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

			font_str = "Arial, Helvetica Neue, Helvetica, sans-serif"
			content = content.replace('CMUBright-Roman', font_str)

			params = dict_to_str(self.params)
			plotid = self.params['general']['global']['plot_id']
			SqlControl.update_plot(params, content, plotid)

			self.signals.result.emit(plotid)

class CirchartSnailPlotWorker(CirchartProcessWorker):
	processor = CirchartSnailPlotProcess

	def preprocess(self):
		workdir = self.make_tempdir()
		index = self.params['general']['global']['genome']
		dname = self.params['plot']['main']['dataset_name']

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
			'id': dname,
			'assembly': {
				'file': 'genome.fa',
				'scaffold-count': count,
				'span': size
			},
			'fields': [
				{
					'id': 'identifiers',
					'type': 'identifier'
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

		busco_lineage = self.params['busco']['main']['busco_lineage']
		busco_count = self.params['busco']['main']['busco_count']
		singlecopy = self.params['busco']['main']['singlecopy']
		duplicated = self.params['busco']['main']['duplicated']
		fragmented = self.params['busco']['main']['fragmented']

		datasets = {}

		if busco_count and singlecopy:
			busco_keys = ['Complete', 'Duplicated', 'Fragmented']
			busco_code = 0
			busco_res = []
			
			for i in range(singlecopy):
				busco_code += 1
				busco_res.append(["B{}".format(busco_code), 0])

			for i in range(duplicated):
				busco_code += 1
				busco_res.append(["B{}".format(busco_code), 1])
				busco_res.append(["B{}".format(busco_code), 1])

			for i in range(fragmented):
				busco_code += 1
				busco_res.append(["B{}".format(busco_code), 2])


			busco_list = [busco_res]
			empty_count = count - 1

			for i in range(empty_count):
				busco_list.append([])

			busco_dict = {
				'values': busco_list,
				'keys': busco_keys,
				'category_slot': 1,
				'headers': [
					"Busco id",
					"Status"
				]
			}

			busco_plot = {
				'datatype': 'mixed',
				'type': 'array',
				'id': 'busco',
				'name': 'Busco',
				'children': [{
					'version': '3.0.1',
					'set': busco_lineage,
					'count': busco_count,
					'file': 'busco.tsv',
					'id': 'buscos',
					'type': 'multiarray',
					'category_slot': 1,
					'headers': [
						"Busco id",
						"Status"
					]
				}]
			}

			metadata['fields'].append(busco_plot)
			datasets['buscos.json'] = busco_dict

		datasets.update({
			'identifiers.json': {'values': ids, 'keys': []},
			'gc.json': {'values': gcs, 'keys': []},
			'length.json': {'values': lens, 'keys': []},
			'ncount.json': {'values': ns, 'keys': []},
			'meta.json': metadata,
		})

		for jfile, data in datasets.items():
			save_snail_data(workdir, jfile, data)

		self.params['workdir'] = workdir

	def save_result(self, res):
		svg_file = os.path.join(self.tempdir.path(), 'snail.svg')
		font_str1 = "Roboto, Open sans, DejaVu Sans, Arial, sans-serif"
		font_str2 = "Arial, Helvetica Neue, Helvetica, sans-serif"

		if os.path.isfile(svg_file):
			with open(svg_file) as fh:
				content = fh.read()

			content = content.replace('viewBox="0 0 1000 1000"', 'width="1000" height="1000" version="1.1"')
			content = content.replace(font_str1, font_str2)

			params = dict_to_str(self.params)
			plotid = self.params['general']['global']['plot_id']
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

class CirchartSvgRenderWorker(CirchartBaseWorker):
	def process(self):
		QThread.msleep(10)
		plotid = self.params['plotid']

		svg_str = SqlControl.get_svg(plotid)
		svg_data = QByteArray(svg_str.encode())
		svg_render = QSvgRenderer()
		svg_render.load(svg_data)

		self.signals.result.emit((plotid, svg_render))


