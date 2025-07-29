import os
import gzip
import time
import traceback
import multiprocessing

import pyfastx

from PySide6.QtCore import *

from config import *
from utils import *
from params import *

__all__ = [
	'CirchartImportFastaProcess',
	'CirchartImportAnnotationProcess',
	'CirchartCircosPlotProcess',
]

class CirchartBaseProcess(multiprocessing.Process):
	def __init__(self, queue, params):
		super().__init__()
		self.queue = queue
		self.params = AttrDict(params)

	def send(self, action, message=None):
		self.queue.put({
			'action': action,
			'message': message
		})

	def before(self):
		pass

	def do(self):
		pass

	def run(self):
		try:
			self.send('started')
			self.before()
			self.do()

		except:
			error = traceback.format_exc()
			self.send('error', error)

			if APP_DEBUG:
				print(error)

		else:
			self.send('success')

		finally:
			self.send('finished')

class CirchartImportFastaProcess(CirchartBaseProcess):
	def do(self):
		fa = pyfastx.Fasta(self.params.fasta)

		rows = []
		for seq in fa:
			rows.append((seq.name, len(seq)))

			if len(rows) == 200:
				self.send('result', rows)

		if rows:
			self.send('result', rows)

class CirchartImportAnnotationProcess(CirchartBaseProcess):
	def do(self):
		if self.params.annotation.endswith('.gz'):
			fp = gzip.open(self.params.annotation, 'rt')
		else:
			fp = open(self.params.annotation)

		rows = []

		with fp:
			for line in fp:
				if line.startswith('#'):
					continue

				cols = line.strip().split('\t')

				if cols:
					rows.append((cols[0], cols[2], int(cols[3]), int(cols[4])))

				if len(rows) == 200:
					self.send('result', rows)

		if rows:
			self.send('result', rows)

class CirchartCircosPlotProcess(QProcess):
	def __init__(self, parent, workdir):
		super().__init__(parent)
		self.setProgram(CIRCOS_COMMAND)
		self.setArguments(['-conf', 'plot.conf'])
		self.setWorkingDirectory(workdir)

		

