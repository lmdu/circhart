import os
import csv
import json
import gzip

__all__ = [
	'AttrDict',
	'save_circos_data',
	'save_snail_data',
	'dict_to_str',
	'str_to_dict',
	'get_gxf_format',
	'GXFParser',
]

class AttrDict(dict):
	def __getattr__(self, attr):
		try:
			return self[attr]
		except:
			raise AttributeError

	def __setattr__(self, attr, val):
		self[attr] = val

def save_circos_data(workdir, filename, data):
	outfile = os.path.join(workdir, filename)

	with open(outfile, 'a', newline='', encoding='utf-8') as fw:
		writer = csv.writer(fw, delimiter=' ', quoting=csv.QUOTE_NONE)
		writer.writerows(data)

def save_snail_data(workdir, filename, data):
	outfile = os.path.join(workdir, filename)

	with open(outfile, 'w') as fw:
		fw.write(json.dumps(data, indent=2))

def dict_to_str(obj):
	return json.dumps(obj)

def str_to_dict(obj):
	return json.loads(obj)

def get_gxf_format(gxf):
	if gxf.endswith('.gz'):
		fp = gzip.open(gxf, 'rt')
	else:
		fp = open(gxf)

	gxformat = None

	with fp:
		for line in fp:
			line = line.strip()

			if line[0] == '#':
				continue

			elif line:
				cols = line.split('\t')
				attrs = cols[8].split(';')

				if '=' in attrs[0]:
					gxformat = 'gff'

				elif '"' in attrs[0]:
					gxformat = 'gtf'

				break

	return gxformat

class GXFRecord:
	def __init__(self, raw, attrs={}):
		self.raw = raw
		self.attrs = AttrDict(attrs)
		self.raw[3] = int(self.raw[3])
		self.raw[4] = int(self.raw[4])

		self.keys = ['chrom', 'source', 'feature', 'start', 'end',
			'score', 'strand', 'phase']
		
	def __getattr__(self, attr):
		index = self.keys.index(attr)
		return self.raw[index]

class GXFParser:
	def __init__(self, gxf_file, gxf_format=None):
		self.gxf_file = gxf_file

		if gxf_file.endswith('.gz'):
			self.fp = gzip.open(gxf_file, 'rt')
		else:
			self.fp = open(gxf_file)

		if gxf_format is None:
			gxf_format = self.get_format()

		if gxf_format == 'gtf':
			self.split_attr = self.split_gtf_attr
		else:
			self.split_attr = self.split_gff_attr

	def __iter__(self):
		self.fp.seek(0)
		
		for line in self.fp:
			if line.startswith('#'):
				continue

			line = line.strip().strip(';')
			if not line:
				continue

			cols = line.split('\t')
			record = GXFRecord(cols)

			for attr in cols[8].split(';'):
				k, v  = self.split_attr(attr)
				record.attrs[k] = v

			yield record

	def __exit__(self):
		self.fp.close()

	def get_format(self):
		self.fp.seek(0)
		gxformat = None

		for line in self.fp:
			line = line.strip()

			if line[0] == '#':
				continue

			elif line:
				cols = line.split('\t')
				attrs = cols[8].split(';')

				if '=' in attrs[0]:
					gxformat = 'gff'

				elif '"' in attrs[0]:
					gxformat = 'gtf'

				break

		return gxformat

	def split_gff_attr(self, attr):
		ks = attr.split('=')
		k = ks[0].strip().lower()
		v = ks[1].strip().strip('"')
		return k, v

	def split_gtf_attr(self, attr):
		if '"' in attr:
			ks = attr.split('"')
		else:
			ks = attr.split()

		k = ks[0].strip()
		v = ks[1].strip().strip('"')
		return k, v

