__all__ = ['CirchartCircosConfile']

class Confile:
	_blocks = []

	def option(self, key, value, unit=''):
		self._blocks.append("{} = {}{}".format(key, value, unit))

	def include(self, attr):
		self._blocks.append("<<include {}>>".format(attr))
		self._blocks.append('')

	def save_to_file(self, cfile):
		with open(cfile, 'w') as fw:
			for tag in self._blocks:
				print(tag, file=fw)

class Tag:
	def __init__(self, name):
		self.name = name

	def __enter__(self):
		Confile._blocks.append("<{}>".format(self.name))
		Confile._blocks.append('')

	def __exit__(self, *args):
		Confile._blocks.append("</{}>".format(self.name))
		Confile._blocks.append('')

class CirchartCircosConfile(Confile):
	def __init__(self, params):
		self.params = params
		self.parse()

	def parse_ideogram(self, ps):
		with Tag('ideogram'):
			for k, v in ps.items():
				match k:
					case 'spacing':
						with Tag('spacing'):
							self.option('default', v, 'r')

					case 'radius':
						self.option(k, v, 'r')

					case 'thickness':
						self.option(k, v, 'p')

					case _:
						self.option(k, v)

	def parse_track(self, tracks, name='plot'):
		with Tag('{}s'.format(name)):
			for track in tracks:
				with Tag(name):
					for k, v in track.items():
						match k:
							case 'data':
								self.option('file', 'data{}.txt'.format(v))

							case 'type':
								if v == 'highlight':
									pass

								else:
									self.option(k, v)

							case 'r0' | 'r1':
								if track['type'] == 'highlight' and track['ideogram'] == 'yes':
									pass

								else:
									self.option(k, v, 'r')

							case 'color':
								if isinstance(v, list):
									cs = []

									for c in v:
										if c not in custom_colors:
											custom_colors.append(c)

										cid = custom_colors.index(c)
										cs.append('cc{}'.format(cid))

									self.option(k, ','.join(cs))

								else:
									if v not in custom_colors:
										custom_colors.append(v)

									cid = custom_colors.index(v)
									self.option(k, 'cc{}'.format(cid))

							case _:
								self.option(k, v)

	def parse(self):
		Confile._blocks = []

		#karyotype
		kfiles = ['karyotype{}.txt'.format(i) \
			for i in self.params['karyotype']]
		self.option('karyotype', ','.join(kfiles))

		#ideogram
		ps = self.params['ideogram']
		self.parse_ideogram(ps)
		

		#tracks
		custom_colors = []
		plot_tracks = []
		highlight_tracks = []

		for p in self.params:
			if p.startswith('track'):
				ps = self.params[p]

				if ps['type'] == 'highlight':
					highlight_tracks.append(ps)
				else:
					plot_tracks.append(ps)

		if plot_tracks:
			self.parse_track(plot_tracks)

		if highlight_tracks:
			self.parse_track(highlight_tracks, 'highlight')


		with Tag('image'):
			self.include('etc/image.conf')

		self.include('etc/colors_fonts_patterns.conf')
		self.include('etc/housekeeping.conf')

		if custom_colors:
			with Tag('colors'):
				for i, c in enumerate(custom_colors):
					self.option('cc{}'.format(i), c)
