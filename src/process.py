import os
import time
import traceback
import multiprocessing

import pyfastx

from config import *
from utils import *
from params import *

__all__ = [
	'CirchartImportFastaProcess',
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
		seqs = [(seq.name, len(seq)) for seq in fa]
		self.send('result', seqs)

class CirchartCircosPlotProcess(CirchartBaseProcess):
	def before(self):
		self.workdir = self.params.pop('workdir')
		confile = os.path.join(self.workdir, 'plot.conf')
		configer = CirchartCircosConfiger(self.params)
		configer.save_to_file(confile)

	def do(self):
		pass

