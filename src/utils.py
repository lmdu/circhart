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
	'get_gxf_format'
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

