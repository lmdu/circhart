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
	'CirchartImportLinkDataProcess',
	'CirchartImportVariationsProcess',
	'CirchartImportRegionsProcess',
	'CirchartBandPrepareProcess',
	'CirchartGCContentPrepareProcess',
	'CirchartDensityPrepareProcess',
	'CirchartCircosPlotProcess',
	'CirchartSnailPlotProcess',
	'CirchartImportCollinearityProcess',
	'CirchartLinkPrepareProcess',
	'CirchartTextPrepareProcess',
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

		rows = []
		features = set()
		attributes = set()

		for record in GXFParser(self.params.path, aformat):
			features.add(record.feature)

			for a in record.attrs.keys():
				if a not in attributes:
					attributes.add(a)

			rows.append(record.raw)
			if len(rows) >= 1000:
				break

		self.send('result', {
			'data': rows,
			'meta': {
				'format': aformat,
				'features': list(features),
				'attributes': list(attributes)
			}
		})

class CirchartImportVariationsProcess(CirchartBaseProcess):
	def do(self):
		if self.params.path.endswith('.gz'):
			fp = gzip.open(self.params.path)
		else:
			fp = open(self.params.path)

		rows = []

		with fp:
			for line in fp:
				if line.startswith('#'):
					continue

				line = line.strip()
				if not line:
					continue

				cols = line.split('\t')
				cols[1] = int(cols[1])
				row = cols[0:9]
				row.append('\t'.join(cols[9:]))
				rows.append(row)

				if len(rows) >= 1000:
					break

		self.send('result', rows)

class CirchartImportRegionsProcess(CirchartBaseProcess):
	def do(self):
		if self.params.path.endswith('.gz'):
			fp = gzip.open(self.params.path)
		else:
			fp = open(self.params.path)

		rows = []

		with fp:
			for line in fp:
				if line.startswith('#'):
					continue

				line = line.strip()
				if not line:
					continue

				cols = line.split('\t')
				cols[1] = int(cols[1])
				cols[2] = int(cols[2])
				row = cols[0:3]
				row.append('\t'.join(cols[3:]))
				rows.append(row)

				if len(rows) >= 1000:
					break

		self.send('result', rows)

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
		def file_reader(self, fh):
			if self.params.format == 'csv':
				reader = csv.reader(fh)
			else:
				for line in fh:
					line = line.strip()

					if not line:
						continue

					if line.startswith('#'):
						continue

					cols = line.strip().split()

					yield cols

		def prerun(self):
			brewer_file = str(CIRCOS_PATH / 'etc' / 'colors.brewer.conf')

			with open(brewer_file) as fh:
				for line in fh:
					if line.startswith('#'):
						continue

					if not line.strip():
						continue

					cols = line.strip().split('=')

					if cols[1].count(',') != 2:
						continue

					cname = cols[0].strip()
					crgb = cols[1].strip()

					if cname not in self.params.colors:
						self.params.colors[cname] = crgb

			color_files = [
				str(CIRCOS_PATH / 'etc' / 'colors.conf'),
				str(CIRCOS_PATH / 'etc' / 'colors.ucsc.conf'),
			]
			for color_file in color_files:
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
						crgb = cols[1].strip()

						if ',' in crgb:
							if cname not in self.params.colors:
								self.params.colors[cname] = crgb

								if cname.lower() not in self.params.colors:
									self.params.colors[cname.lower()] = crgb

						else:
							if cname not in self.params.colors:
								if crgb in self.params.colors:
									self.params.colors[cname] = self.params.colors[crgb]

									if cname.lower() not in self.params.colors:
										self.params.colors[cname.lower()] = self.params.colors[crgb]

		def do(self):
			rows = []
			ignore = 0

			alphas = {'a1': 0.83, 'a2': 0.67, 'a3': 0.5, 'a4': 0.33, 'a5': 0.17}

			with open(self.params.path) as fh:
				reader = self.file_reader(fh)

				for row in reader:
					if len(row) < self.params.column:
						ignore += 1
						continue

					res = row[:self.params.column]

					if self.params.type in ['karyotype', 'banddata']:
						if res[-1] in self.params.colors:
							res[-1] = self.params.colors.get(res[-1])

						elif '_a' in res[-1]:
							a = res[-1].strip().split('_')[-1]

							if a in alphas:
								alpha = alphas[a]

								c = res[-1].rstrip('_{}'.format(a))

								if c in self.params.colors:
									res[-1] = "{},{}".format(self.params.colors[c], alpha)

					elif self.params.type in ['plotdata', 'locidata', 'textdata']:
						if len(row) > self.params.column:
							res.append(row[self.params.column])
						else:
							res.append('')

					rows.append(res)

					if len(rows) == 200:
						self.send('result', rows)
						rows = []

			if rows:
				self.send('result', rows)

			if ignore > 0:
				self.send('warning', "Ignored {} lines due to missing columns".format(ignore))

class CirchartImportLinkDataProcess(CirchartImportDataProcess):
	def do(self):
		rows = []
		mappings = {}
		ignore = 0

		with open(self.params.path) as fh:
			reader = self.file_reader(fh)

			for row in reader:
				if len(row) < self.params.column:
					ignore += 1
					continue

				elif 4 <= len(row) < 6:
					if row[0] not in mappings:
						mappings[row[0]] = row[1:4]
						mappings[row[0]].append('')
						mappings[row[0]].append('')
						mappings[row[0]].append('')

						if len(row) > 4:
							mappings[row[0]].append(row[4])
						else:
							mappings[row[0]].append('')

					else:
						mappings[row[0]][3] = row[1]
						mappings[row[0]][4] = row[2]
						mappings[row[0]][5] = row[3]

						if len(row) > 4 and not mappings[row[0]][6]:
							mappings[row[0]][6] = row[4]

						rows.append(mappings[row[0]])

						if len(rows) == 200:
							self.send('result', rows)
							rows = []

				else:
					res = row[:7]

					if len(res) < 7:
						res.append('')

					rows.append(res)
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
			rows.append(('band', parent[0], band[3], band[3], band[1], band[2], color))

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
				rows.append((chrid, i+1, j, gc, ''))

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
	def parse_gxf(self, cols):
		if cols[2] != self.params.feature:
			return

		start = int(cols[3])
		end = int(cols[4])
		return start, end

	def parse_vcf(self):
		pos = int(cols[1])
		return pos, pos

	def parse_bed(self):
		start = int(cols[1])
		end = int(cols[2])
		return start, end

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

		if self.params.datatype == 'gxf':
			parse_func = self.parse_gxf

		elif self.params.datatype == 'vcf':
			parse_func = self.parse_vcf

		else:
			parse_func = self.parse_bed

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

				locus = parse_func(cols)
				if locus is None:
					continue

				ilist = interval_mapping[chrom].overlap(chrom, locus[0], locus[1])

				for _, _, index in ilist:
					counts_mapping[chrom][index] += 1

		for chrom, locus in location_mapping.items():
			counts = counts_mapping[chrom]
			rows = []

			for idx, loci in enumerate(locus):
				loci.append(counts[idx])
				loci.append('')
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
				row.append('')
				rows.append(row)

				if len(rows) == 200:
					self.send('result', rows)
					rows = []

		if rows:
			self.send('result', rows)

class CirchartTextPrepareProcess(CirchartBaseProcess):
	def do(self):
		rows = []

		if 'matches' in self.params:
			matches = {m.strip().lower() for m in self.params.matches.split('\n')}
		else:
			matches = {}

		attr = self.params.attribute

		for record in GXFParser(self.params.annotation):
			if record.chrom not in self.params.axes:
				continue

			if record.feature != self.params.feature:
				continue

			if attr not in record.attrs:
				continue

			a = record.attrs[attr]

			if matches and a.lower() not in matches:
				continue

			chrom = self.params.axes[record.chrom][0]
			rows.append((chrom, record.start, record.end, a, ''))

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

