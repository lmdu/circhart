import traceback

from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *

from config import *

__all__ = [
	'CirchartCircosDependencyWorker',
]

class CirchartBaseWorker(QObject):
	error = Signal(str)
	result = Signal(object)
	started = Signal()
	stopped = Signal()
	success = Signal()
	finished = Signal()

	def __init__(self):
		super().__init__()

	def process(self):
		pass

	def run(self):
		try:
			self.started.emit()
			self.process()
			self.stopped.emit()
			self.success.emit()

		except:
			errmsg = traceback.format_exc()
			self.error.emit(errmsg)

			if CIRCHART_DEBUG:
				print(errmsg)

		finally:
			self.finished.emit()

	def on_error_occurred(self, error):
		self.error.emit(str(error))

class CirchartCircosDependencyWorker(CirchartBaseWorker):
	def process(self):
		proc = QProcess()
		proc.errorOccurred.connect(self.on_error_occurred)
		proc.start()
		proc.waitForFinished()
		res = proc.readAllStandardOutput()
		lines = res.data().decode().split('\n')
