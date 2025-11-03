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
		self.custom_colors = []

	def parse_ideogram(self, params):
		main_params = params['main']
		label_params = params['label']
		ticks_params = params['ticks']

		with Tag('ideogram'):
			for k, v in main_params.items():
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

			for k, v in label_params.items():
				match k:
					case 'label_size':
						self.option(k, v, 'p')
					
					case _:
						self.option(k, v)

			ticks_count = 0
			#get global ticks parameter
			for k, v in ticks_params.items():
				if not k.startswith('tick'):
					self.option(k, v)

				else:
					ticks_count += 1

			if ticks_count > 0:
				with Tag('ticks'):
					for k, v in ticks_params.items():
						if k.startswith('tick'):
							with Tag('tick'):
								match k:
									case 'thickness' | 'size' | 'label_size' | 'label_offset':
										self.option(k, v, 'p')

									case 'spacing':
										self.option(k, v, 'u')

									case _:
										self.option(k, v)


	def parse_track(self, tracks, name='plot'):
		with Tag('{}s'.format(name)):
			for track in tracks:
				main_params = track['main']
				rule_params = track['rules']
				axes_params = track['axes']
				bg_params = track['backgrounds']

				with Tag(name):
					for k, v in main_params.items():
						match k:
							case 'data':
								self.option('file', 'data{}.txt'.format(v))

							case 'type':
								if v == 'highlight':
									pass

								else:
									self.option(k, v)

							case 'r0' | 'r1':
								if main_params['type'] == 'highlight' and main_params['ideogram'] == 'yes':
									pass

								else:
									self.option(k, v, 'r')

							case 'color':
								if isinstance(v, list):
									cs = []

									for c in v:
										if c not in self.custom_colors:
											self.custom_colors.append(c)

										cid = self.custom_colors.index(c)
										cs.append('cc{}'.format(cid))

									self.option(k, ','.join(cs))

								else:
									if v not in self.custom_colors:
										self.custom_colors.append(v)

									cid = self.custom_colors.index(v)
									self.option(k, 'cc{}'.format(cid))

							case _:
								self.option(k, v)

					if rule_params:
						with Tag('rules'):
							for k, v in rule_params.items():
								with Tag('rule'):
									for c in v.get('conditions', []):
										self.option('condition', c)

									for a, s in v.get('styles', []):
										if a == 'color':
											if s not in self.custom_colors:
												self.custom_colors.append(s)

											cid = self.custom_colors.index(v)
											self.option(a, 'cc{}'.format(cid))
										else:
											self.option(a, s)

					if axes_params:
						with Tag('axes'):
							for k, v in axes_params.items():
								with Tag('axis'):
									for x, y in v.items():
										self.option(x, y)

					if bg_params:
						with Tag('backgrounds'):
							for k, v in bg_params.items():
								with Tag('background'):
									for x, y in v.items():
										self.option(x, y)


	def parse(self):
		Confile._blocks = []

		#karyotype
		kfiles = ['karyotype{}.txt'.format(i) \
			for i in self.params['general']['global']['karyotype']]
		self.option('karyotype', ','.join(kfiles))

		#ideogram
		ps = self.params['ideogram']
		self.parse_ideogram(ps)

		#tracks
		self.custom_colors = []
		plot_tracks = []
		highlight_tracks = []

		for p in self.params:
			if p.startswith('track'):
				ps = self.params[p]

				if ps['main']['type'] == 'highlight':
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

		if self.custom_colors:
			with Tag('colors'):
				for i, c in enumerate(self.custom_colors):
					self.option('cc{}'.format(i), c)
