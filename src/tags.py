__all__ = ['CirchartCircosTags']

class Tags:
	_tags = []

	def reset(self):
		self._tags = []

	def option(self, key, value, unit=''):
		self._tags.append("{} = {}{}".format(key, value, unit))

	def include(self, attr):
		self._tags.append("<<include {}>>".format(attr))
		self._tags.append('')

	def save_to_file(self, cfile):
		with open(cfile, 'w') as fw:
			for tag in self._tags:
				print(tag, file=fw)

class Tag(Tags):
	def __init__(self, name, *args, **kwargs):
		self.name = name
		self.attrs = list(args)

		for k, v in kwargs.items():
			self.attrs.append("{}={}".format(k, v))

	def __enter__(self):
		if self.attrs:
			line = "<{} {}>".format(self.name, ' '.join(self.attrs))
		else:
			line = "<{}>".format(self.name)

		self._tags.append(line)
		self._tags.append('')

	def __exit__(self, *args):
		self._tags.append("</{}>".format(self.name))
		self._tags.append('')

class CirchartCircosTags(Tags):
	def __init__(self, params):
		self.params = params
		self.reset()
		self.parse()

	def parse(self):
		option = self.option
		include = self.include
		tag = Tag

		#karyotype
		kfiles = ['karyotype{}.txt'.format(i) \
			for i in self.params['karyotype']]
		option('karyotype', ','.join(kfiles))

		#ideogram
		ps = self.params['ideogram']
		with tag('ideogram'):
			for k, v in ps.items():
				match k:
					case 'spacing':
						with tag('spacing'):
							option('default', v, 'r')

					case 'radius':
						option(k, v, 'r')

					case 'thickness':
						option(k, v, 'p')

					case _:
						option(k, v)

		#tracks
		custom_colors = []
		if any([p.startswith('track') for p in self.params]):
			with tag('plots'):
				for p in self.params:
					if p.startswith('track'):
						ps = self.params[p]

						with tag('plot'):
							for k, v in ps.items():
								match k:
									case 'data':
										option('file', 'data{}.txt'.format(v))

									case 'r0' | 'r1':
										option(k, v, 'r')

									case 'color':
										if isinstance(v, list):
											cs = []

											for c in v:
												if c not in custom_colors:
													custom_colors.append(c)

												cid = custom_colors.index(c)
												cs.append('cc{}'.format(cid))

											option(k, ','.join(cs))

										else:
											if v not in custom_colors:
												custom_colors.append(v)

											cid = custom_colors.index(v)
											option(k, 'cc{}'.format(cid))

									case _:
										option(k, v)

		with tag('image'):
			include('etc/image.conf')

		include('etc/colors_fonts_patterns.conf')
		include('etc/housekeeping.conf')

		if custom_colors:
			with tag('colors'):
				for i, c in enumerate(custom_colors):
					option('cc{}'.format(i), c)
