import os
import gzip
import time
import traceback
import multiprocessing

import pyfastx
from blobtk import plot as snail_plot

from PySide6.QtCore import *

from config import *
from utils import *

__all__ = [
	'CirchartImportFastaProcess',
	'CirchartImportAnnotationProcess',
	'CirchartGCContentPrepareProcess',
	'CirchartDensityPrepareProcess',
	'CirchartCircosPlotProcess',
	'CirchartSnailPlotProcess',
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

	def prerun(self):
		pass

	def do(self):
		pass

	def run(self):
		try:
			self.send('started')
			self.prerun()
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
		fa = pyfastx.Fasta(self.params.fasta, full_index=True)

		rows = []
		for seq in fa:
			comp = seq.composition
			gc = 0
			ns = 0

			for k in comp:
				if k in ['G', 'C', 'g', 'c']:
					gc += comp[k]

				elif k not in ['A', 'T', 'G', 'C', 'a', 't', 'g', 'c']:
					ns += comp[k]

			gc = round(gc / len(seq), 4)
			rows.append((seq.name, len(seq), gc, ns))

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
					rows = []

		if rows:
			self.send('result', rows)

class CirchartGCContentPrepareProcess(CirchartBaseProcess):
	def do(self):
		fa = pyfastx.Fasta(self.params.genome, uppercase=True)
		wsize = self.params.window

		rows = []
		for chrom in self.params.axes:
			chrid, size = self.params.axes[chrom]
			seq = fa[chrom].seq

			for i in range(0, size, wsize):
				j = i + wsize

				if j > size:
					j = size

				a = seq.count('A', i, j)
				t = seq.count('T', i, j)
				g = seq.count('G', i, j)
				c = seq.count('C', i, j)

				if g + c:
					gc = (g + c) / (a + t + g + c)
				else:
					gc = 0

				rows.append((chrid, i+1, j, gc))

				if len(rows) == 200:
					self.send('result', rows)
					rows = []

		if rows:
			self.send('result', rows)

class CirchartDensityPrepareProcess(CirchartBaseProcess):
	def do(self):
		wsize = self.params.window

		for chrom, loci in self.params['loci'].items():
			if chrom not in self.params.axes:
				continue

			chrid, size = self.params.axes[chrom]
			loci = iter(loci)
			rows = []
			s = 0
			e = 0

			for i in range(0, size, wsize):
				j = i + wsize
				i += 1
				c = 0

				if j > size:
					j = size

				if s and e:
					if i <= s <= j or i <= e <= j:
						c += 1

					elif s <= i <= j <= e:
						c += 1

					else:
						rows.append((chrid, i, j, c))
						continue

				for s, e in loci:
					if i <= s <= j or i <= e <= j:
						c += 1

					elif s <= i <= j <= e:
						c += 1

					else:
						break

				rows.append((chrid, i, j, c))

			self.send('result', rows)

class CirchartCircosPlotProcess(QProcess):
	def __init__(self, parent, workdir):
		super().__init__(parent)
		self.setProgram(CIRCOS_COMMAND)
		self.setArguments(['-conf', 'plot.conf', '-nopng'])
		self.setWorkingDirectory(workdir)

class CirchartSnailPlotProcess(CirchartBaseProcess):
	def do(self):
		outfile = os.path.join(self.params.workdir, 'snail.svg')
		ps = self.params.snail

		if ps['max_span'] > 0:
			ps['max_span'] = int(ps['max_span'])
		
		else:
			ps.pop('max_span')

		if ps['max_scaffold'] > 0:
			ps['max_scaffold'] = int(ps['max_scaffold'])

		else:
			ps.pop('max_scaffold')

		if ps['show_numbers'] == 'yes':
			ps['show_numbers'] = True

		else:
			ps['show_numbers'] = False

		if ps['busco_numbers'] == 'yes':
			ps['busco_numbers'] = True

		else:
			ps['busco_numbers'] = False

		snail_plot.plot(
			blobdir = self.params.workdir,
			output = outfile,
			view = 'snail',
			**ps
		)

		self.send('result')

