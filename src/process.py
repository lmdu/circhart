import time
import traceback
import multiprocessing

import pyfastx

from config import *
from utils import *

__all__ = [
	'CirchartImportFastaProcess'
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

	def do(self):
		pass

	def run(self):
		try:
			self.send('started')
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
		seqs = [(None, seq.name, len(seq)) for seq in fa]
		self.send('result', seqs)








