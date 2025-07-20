import traceback
import multiprocessing

from PySide6.QtGui import *
from PySide6.QtCore import *


from config import *
from utils import *
from models import *
from process import *
from backend import *

__all__ = [
	'CirchartImportGenomeWorker',
]

class CirchartWorkerSignals(QObject):
	error = Signal(str)
	result = Signal(object)
	toggle = Signal(bool)
	started = Signal()
	stopped = Signal()
	success = Signal()
	finished = Signal()

class CirchartBaseWorker(QRunnable):
	def __init__(self):
		super().__init__()
		self.signals = CirchartWorkerSignals()

	def process(self):
		pass

	def run(self):
		try:
			self.signals.toggle.emit(True)
			self.signals.started.emit()
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
		super().__init__()
		self.params = params
		self.queue = multiprocessing.Queue()

	def save_result(self, res):
		pass

	def response(self, res):
		match res['action']:
			case 'error':
				self.signals.error.emit(res['message'])

			case 'result':
				self.save_result(res['message'])

			case 'finished':
				self.signals.finished.emit()
				self.queue.close()

	def process(self):
		proc = self.processor(self.queue, self.params)
		proc.start()

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







