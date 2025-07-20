
__all__ = [
	'AttrDict',
]

class AttrDict(dict):
	def __getattr__(self, attr):
		try:
			return self[attr]
		except:
			raise AttributeError

	def __setattr__(self, attr, val):
		self[attr] = val