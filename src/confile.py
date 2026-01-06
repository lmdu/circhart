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
	def __init__(self, name, attrs=None):
		self.name = name
		self.attrs = attrs

	def __enter__(self):
		if self.attrs:
			Confile._blocks.append("<{} {}>".format(self.name, self.attrs))
		else:
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

	def get_color(self, rgb):
		if rgb not in self.custom_colors:
			self.custom_colors.append(rgb)

		cid = self.custom_colors.index(rgb)
		return "cc{}".format(cid)

	def parse_ideogram(self, params):
		main_params = params['main']
		label_params = params['label']
		space_params = params['spaces']

		with Tag('ideogram'):
			for k, v in main_params.items():
				match k:
					case 'spacing':
						with Tag('spacing'):
							self.option('default', v, 'r')

							for ss in space_params.values():
								s = ss['space']

								with Tag('pairwise', s['pairwise']):
									self.option('spacing', s['spacing'], 'r')

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

					case 'label_format':
						if v == 'name':
							v = 'chr'
						self.option(k, "eval(var({}))".format(v))
					
					case _:
						self.option(k, v)

	def parse_ticks(self, params):
		main_params = params['main']
		tick_params = params['ticks']

		#get global ticks parameter
		for k in ['show_ticks', 'show_tick_labels', 'chromosomes_units']:
			self.option(k, main_params[k])

		with Tag('ticks'):
			for k in ['radius', 'label_multiplier', 'orientation']:
				self.option(k, main_params[k])

			for k, v in tick_params.items():
				with Tag('tick'):
					for x, y in v['styles'].items():
						match x:
							case 'thickness' | 'size' | 'label_size' | 'label_offset':
								self.option(x, y, 'p')

							case 'spacing':
								self.option(x, y, 'u')

							case 'color':
								self.option(x, self.get_color(y))

							case 'format':
								if y > 0:
									f = "%.{}f".format(y)
								else:
									f = "%d"

								self.option(x, f)

							case _:
								self.option(x, y)


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

								elif v == 'link':
									pass

								else:
									self.option(k, v)

							case 'r0r1':
								if main_params['type'] == 'highlight' and main_params['ideogram'] == 'yes':
									pass

								else:
									self.option('r0', v[0], 'r')
									self.option('r1', v[1], 'r')

							case 'radius' | 'bezier_radius':
								if main_params['type'] == 'link':
									self.option(k, v, 'r')

								else:
									self.option(k, v)

							case 'color':
								if isinstance(v, list):
									cs = []

									for c in v:
										cs.append(self.get_color(c))

									self.option(k, ','.join(cs))

								else:
									self.option(k, self.get_color(v))

							case _:
								self.option(k, v)

					if rule_params:
						with Tag('rules'):
							for k, v in rule_params.items():
								with Tag('rule'):
									for c in v['main'].get('condition', []):
										if c.startswith('var(chr'):
											cl = c.split(' eq ')
											cl[1] = '"{}"'.format(cl[1])
											c = ' eq '.join(cl)

										self.option('condition', c)

									for a, s in v['main'].get('style', []):
										if a == 'color':
											self.option(a, self.get_color(s))
										else:
											self.option(a, s)

					if axes_params:
						with Tag('axes'):
							for k, v in axes_params.items():
								with Tag('axis'):
									for x, y in v['main'].items():
										if x in ['spacing', 'position']:
											self.option(x, y, 'r')
										else:
											self.option(x, y)

					if bg_params:
						with Tag('backgrounds'):
							for k, v in bg_params.items():
								with Tag('background'):
									for x, y in v['main'].items():
										if x in ['y0', 'y1']:
											self.option(x, y, 'r')
										else:
											self.option(x, y)


	def parse(self):
		Confile._blocks = []
		self.custom_colors = []

		#karyotype
		kfiles = ['karyotype{}.txt'.format(i) \
			for i in self.params['general']['global']['karyotype']]
		self.option('karyotype', ','.join(kfiles))

		#ideogram
		ps = self.params['ideogram']
		self.parse_ideogram(ps)

		#ticks
		ps = self.params['ticks']
		self.parse_ticks(ps)

		#tracks
		plot_tracks = []
		link_tracks = []
		highlight_tracks = []

		for p in self.params:
			if p.startswith('track'):
				ps = self.params[p]

				if ps['main']['type'] == 'link':
					link_tracks.append(ps)

				elif ps['main']['type'] == 'highlight':
					highlight_tracks.append(ps)

				else:
					plot_tracks.append(ps)

		if plot_tracks:
			self.parse_track(plot_tracks)

		if link_tracks:
			self.parse_track(link_tracks, 'link')

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
