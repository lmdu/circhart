import os
import csv

__all__ = [
	'AttrDict',
	'save_circos_data',
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


