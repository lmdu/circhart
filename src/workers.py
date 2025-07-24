import os
import traceback
import multiprocessing

from PySide6.QtGui import *
from PySide6.QtCore import *


from config import *
from utils import *
from models import *
from params import *
from process import *
from backend import *

__all__ = [
	'CirchartImportGenomeWorker',
	'CirchartCircosPlotWorker',
]

class CirchartWorkerSignals(QObject):
	error = Signal(str)
	result = Signal(object)
	toggle = Signal(bool)
	message = Signal(str)
	started = Signal()
	stopped = Signal()
	success = Signal()
	finished = Signal()

class CirchartBaseWorker(QRunnable):
	def __init__(self, params):
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

	def save_result(self, res):
		qf = QFileInfo(self.params['fasta'])
		name = qf.completeBaseName()
		SqlControl.add_data(name, 'genome', self.params['fasta'], res)
		self.signals.success.emit()


class CirchartCircosPlotWorker(CirchartBaseWorker):
	processor = CirchartCircosPlotProcess

	def make_tempdir(self):
		self.tempdir = QTemporaryDir()
		self.tempdir.setAutoRemove(False)

		if not self.tempdir.isValid():
			raise Exception("Could not create temporary directory")

		return self.tempdir.path()

	def preprocess(self):
		workdir = self.make_tempdir()

		for index in self.params['karyotype']:
			outfile = "{}{}.txt".format('karyotype', index)
			data = SqlControl.get_data_content('karyotype', index)
			save_circos_data(workdir, outfile, data)

		confile = os.path.join(workdir, 'plot.conf')
		configer = CirchartCircosConfiger(self.params)
		configer.save_to_file(confile)

	def process(self):
		parent = QObject()
		self.runner = self.processor(parent, self.tempdir.path())
		loop = QEventLoop()
		self.runner.finished.connect(loop.quit)
		self.runner.finished.connect(self.save_result)
		self.runner.errorOccurred.connect(loop.quit)
		self.runner.errorOccurred.connect(self.signals.error.emit)
		self.runner.start()
		loop.exec()

	def save_result(self):
		svg_file = os.path.join(self.tempdir.path(), 'circos.svg')

		if os.path.isfile(svg_file):
			with open(svg_file) as fh:
				content = fh.read()

			params = dict_to_str(self.params)
			plotid = self.params['plotid']
			SqlControl.update_plot(params, content, plotid)

			self.signals.result.emit(plotid)
		







