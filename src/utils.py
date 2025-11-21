import os
import csv
import json

__all__ = [
	'AttrDict',
	'save_circos_data',
	'dict_to_str',
	'str_to_dict',
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

	with open(outfile, 'w', newline='') as fw:
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

