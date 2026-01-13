import os
import gzip
import time
import traceback
import multiprocessing

import pygros
import pyfastx
from blobtk import plot as snail_plot

from PySide6.QtCore import *

from config import *
from utils import *

__all__ = [
	'CirchartImportFastaProcess',
	'CirchartImportAnnotationProcess',
	'CirchartImportBandsProcess',
	'CirchartImportDataProcess',
	'CirchartBandPrepareProcess',
	'CirchartGCContentPrepareProcess',
	'CirchartDensityPrepareProcess',
	'CirchartCircosPlotProcess',
	'CirchartSnailPlotProcess',
	'CirchartImportCollinearityProcess',
	'CirchartLinkPrepareProcess',
	'CirchartGCSkewPrepareProcess',
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
		fa = pyfastx.Fasta(self.params.path, full_index=True)

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
				rows = []

		if rows:
			self.send('result', rows)

class CirchartImportAnnotationProcess(CirchartBaseProcess):
	def do(self):
		aformat = get_gxf_format(self.params.path)
		assert aformat is not None, "the annotation format is not gtf or gff"

		if aformat == 'gtf':
			split_attrs = lambda x: x.split('"')
		else:
			split_attrs = lambda x: x.split('=')

		rows = []
		features = set()
		attributes = set()

		if self.params.path.endswith('.gz'):
			fp = gzip.open(self.params.path, 'rt')
		else:
			fp = open(self.params.path)

		with fp:
			for line in fp:
				if line.startswith('#'):
					continue

				line = line.strip()
				if not line:
					continue

				cols = line.split('\t')
				features.add(cols[2])

				for attr in cols[8].split(';'):
					a = split_attrs(attr)[0].strip()
					attributes.add(a)

				if len(rows) < 1000:
					cols[3] = int(cols[3])
					cols[4] = int(cols[4])
					rows.append(cols)
				else:
					break

		self.send('result', {
			'data': rows,
			'meta': {
				'format': aformat,
				'features': list(features),
				'attributes': list(attributes)
			}
		})

class CirchartImportBandsProcess(CirchartBaseProcess):
	def do(self):
		rows = []
		ignore = 0

		with open(self.params.path) as fh:
			for line in fh:
				line = line.strip()

				if not line:
					continue

				if line.startswith('#'):
					continue

				cols = line.strip().split()

				if len(cols) < 5:
					ignore += 1
					continue

				rows.append(cols[:5])

				if len(rows) == 200:
					self.send('result', rows)
					rows = []

		if rows:
			self.send('result', rows)

		if ignore > 0:
			self.send('warning', "Ignored {} lines due to missing columns".format(ignore))

class CirchartImportDataProcess(CirchartBaseProcess):
		def tsv_reader(self, fh):
			for line in fh:
				line = line.strip()

				if not line:
					continue

				if line.startswith('#'):
					continue

				cols = line.strip().split()

				yield cols

		def do(self):
			rows = []
			ignore = 0

			with open(self.params.path) as fh:
				if self.params.format == 'csv':
					reader = csv.reader(fh)
				
				else:
					reader = self.tsv_reader(fh)

				for row in reader:
					if len(row) < self.params.column:
						ignore += 1
						continue

					rows.append(row[:self.params.column])

					if len(rows) == 200:
						self.send('result', rows)
						rows = []

			if rows:
				self.send('result', rows)

			if ignore > 0:
				self.send('warning', "Ignored {} lines due to missing columns".format(ignore))

class CirchartImportCollinearityProcess(CirchartBaseProcess):
	def do(self):
		rows = []
		with open(self.params.path) as fh:
			for line in fh:
				if line[0] == '#':
					continue

				cols = line.strip().split()

				if len(rows) < 1000:
					rows.append((cols[2], cols[3]))
				else:
					break

		self.send('result', rows)

class CirchartBandPrepareProcess(CirchartBaseProcess):
	def do(self):
		#get band colors from circos
		color_file = CIRCOS_PATH / 'etc' / 'colors.ucsc.conf'
		comment_no = 0

		band_colors = {}
		with open(str(color_file)) as fh:
			for line in fh:
				if line[0] == '#':
					comment_no += 1

					if comment_no > 1:
						break
					else:
						continue

				if not line.strip():
					continue

				cols = line.strip().split('=')
				band_colors[cols[0].strip()] = cols[1].strip()

		rows = []
		for band in self.params.bands:
			parent = self.params.axes.get(band[0], None)
			
			if parent is None:
				continue

			color = band_colors.get(band[4])
			rows.append(('band', parent, band[3], band[3], band[1], band[2], color))

			if len(rows) == 200:
				self.send('result', rows)
				rows = []

		if rows:
			self.send('result', rows)

class CirchartGCContentPrepareProcess(CirchartBaseProcess):
	def _calc_gc(self, seq, i, j):
		a = seq.count('A', i, j)
		t = seq.count('T', i, j)
		g = seq.count('G', i, j)
		c = seq.count('C', i, j)

		if g or c:
			gc = (g + c) / (a + t + g + c)
		else:
			gc = 0

		return gc

	def do(self):
		fa = pyfastx.Fasta(self.params.genome, uppercase=True)
		wsize = self.params.window
		step = self.params.step

		for chrom in self.params.axes:
			chrid, size = self.params.axes[chrom]
			seq = fa[chrom].seq
			rows = []

			for i in range(0, size, step):
				j = i + wsize

				if j > size:
					j = size

				gc = self._calc_gc(seq, i, j)
				rows.append((chrid, i+1, j, gc))

				if j == size:
					break

			self.send('result', rows)

class CirchartGCSkewPrepareProcess(CirchartGCContentPrepareProcess):
	def _calc_gc(self, seq, i, j):
		g = seq.count('G', i, j)
		c = seq.count('C', i, j)

		if g or c:
			gc = (g - c) / (g + c)

		else:
			gc = 0

		return gc

class CirchartDensityPrepareProcess(CirchartBaseProcess):
	def do(self):
		wsize = self.params.window
		step = self.params.step

		interval_mapping = {}
		location_mapping = {}
		counts_mapping = {}
		
		for chrom in self.params.axes:
			ranges = pygros.Ranges()
			locus = []
			counts = []

			chrid, size = self.params.axes[chrom]

			for i in range(0, size, step):
				j = i + wsize
				i += 1

				if j > size:
					j = size

				index = len(locus)
				locus.append([chrid, i, j])
				counts.append(0)
				ranges.add(chrom, i, j, index)

				if j == size:
					break

			ranges.index()
			interval_mapping[chrom] = ranges
			location_mapping[chrom] = locus
			counts_mapping[chrom] = counts

		if self.params.annotation.endswith('.gz'):
			fp = gzip.open(self.params.annotation, 'rt')
		else:
			fp = open(self.params.annotation)

		with fp:
			for line in fp:
				if line[0] == '#':
					continue

				line = line.strip()

				if not line:
					continue

				cols = line.split('\t')

				chrom = cols[0]
				if chrom not in self.params.axes:
					continue

				feat = cols[2]
				if feat != self.params.feature:
					continue

				start = int(cols[3])
				end = int(cols[4])

				ilist = interval_mapping[chrom].overlap(chrom, start, end)

				for _, _, index in ilist:
					counts_mapping[chrom][index] += 1

		for chrom, locus in location_mapping.items():
			counts = counts_mapping[chrom]
			rows = []

			for idx, loci in enumerate(locus):
				loci.append(counts[idx])
				rows.append(loci)

			self.send('result', rows)

class CirchartLinkPrepareProcess(CirchartBaseProcess):
	def do(self):
		gene_mappings = {}

		for k in self.params:
			if not k.startswith('sp'):
				continue

			sp = self.params[k]

			if sp['annoformat'] == 'gtf':
				split_attrs = lambda x: x.split('"')
			else:
				split_attrs = lambda x: x.split('=')

			if sp['annotation'].endswith('.gz'):
				fp = gzip.open(sp['annotation'], 'rt')
			else:
				fp = open(sp['annotation'])

			with fp:
				for line in fp:
					if line[0] == '#':
						continue

					line = line.strip()

					if not line:
						continue

					cols = line.strip().split('\t')

					if cols[2] != sp['feature']:
						continue

					if cols[0] not in sp['karyotype']:
						continue

					chrid = sp['karyotype'][cols[0]]
					start = cols[3]
					end = cols[4]

					for attr in cols[8].split(';'):
						if attr.strip().startswith(sp['attribute']):
							val = split_attrs(attr)[1].strip().strip('"')
							gene_mappings[val] = (chrid, start, end)

		rows = []
		with open(self.params.collinearity) as fh:
			for line in fh:
				if line[0] == '#':
					continue

				cols = line.strip().split()
				row = []
				row.extend(gene_mappings[cols[2]])
				row.extend(gene_mappings[cols[3]])
				rows.append(row)

				if len(rows) == 200:
					self.send('result', rows)
					rows = []

		if rows:
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
		ps = self.params.plot['main']

		#if ps['max_span'] > 0:
		#	ps['max_span'] = int(ps['max_span'])
		
		#else:
		#	ps.pop('max_span')

		#if ps['max_scaffold'] > 0:
		#	ps['max_scaffold'] = int(ps['max_scaffold'])

		#else:
		#	ps.pop('max_scaffold')

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

