from pathlib import Path

from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *

from config import *
from widgets import *
from backend import *

__all__ = [
	'CirchartImportForGenomeDialog',
	'CirchartCircosDependencyDialog',
	'CirchartKaryotypePrepareDialog',
	'CirchartBandPrepareDialog',
	'CirchartGCContentPrepareDialog',
	'CirchartGCSkewPrepareDialog',
	'CirchartDensityPrepareDialog',
	'CirchartCreateCircosPlotDialog',
	'CirchartCreateSnailPlotDialog',
	'CirchartCircosColorSelectDialog',
	'CirchartLinkPrepareDialog',
]

class CirchartBaseDialog(QDialog):
	_title = ""

	def __init__(self, parent=None):
		super().__init__(parent)
		self.setWindowTitle(self._title)

		self.main_layout = QVBoxLayout()
		self.setLayout(self.main_layout)

		self._create_widgets()
		self._init_layouts()
		self._init_widgets()
		self._create_buttons()

	def sizeHint(self):
		return QSize(400, 30)

	def _create_widgets(self):
		pass

	def _create_buttons(self):
		self.btn_box = QDialogButtonBox(
			QDialogButtonBox.StandardButton.Cancel |
			QDialogButtonBox.StandardButton.Ok
		)
		self.btn_box.accepted.connect(self._on_accepted)
		self.btn_box.rejected.connect(self.reject)
		self.main_layout.addWidget(self.btn_box)

	def _init_widgets(self):
		pass

	def _init_layouts(self):
		pass

	def _on_accepted(self):
		self.accept()

class CirchartImportForGenomeDialog(CirchartBaseDialog):
	_title = "Select Genome"

	def _create_widgets(self):
		self.info = QLabel("Import for Genome:", self)
		self.select = QComboBox(self)

	def _init_widgets(self):
		gs = SqlControl.get_datas_by_type('genome')

		for g in gs:
			self.select.addItem(g.name, g.id)

	def _init_layouts(self):
		self.main_layout.addWidget(self.info)
		self.main_layout.addWidget(self.select)

	@classmethod
	def get_genome(cls, parent):
		dlg = cls(parent)

		if dlg.exec() == QDialog.Accepted:
			return dlg.select.currentData()

class CirchartCircosDependencyDialog(CirchartBaseDialog):
	_title = "Circos Perl Dependencies"

	def sizeHint(self):
		return QSize(400, 350)
	
	def _create_widgets(self):
		self.spinner = CirchartSpinnerWidget(self)
		self.updator = QPushButton("Refresh", self)
		self.tree = CirchartEmptyTreeWidget(self)
		self.tree.setHeaderLabels(['Module', 'Version', 'Status'])
		self.tree.setIconSize(QSize(12, 12))
		self.tree.setRootIsDecorated(False)
		self.tree.header().setStretchLastSection(False)
		self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
		self.tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
		self.tree.header().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

	def _create_buttons(self):
		self.btn_box = QDialogButtonBox(
			QDialogButtonBox.StandardButton.Ok
		)
		self.btn_box.accepted.connect(self.accept)
		self.main_layout.addWidget(self.btn_box)

	def _init_layouts(self):
		top_layout = QHBoxLayout()
		top_layout.addWidget(self.spinner)
		top_layout.addWidget(CirchartSpacerWidget(self))
		top_layout.addWidget(self.updator)
		self.main_layout.addLayout(top_layout)
		self.main_layout.addWidget(self.tree)

	def _init_widgets(self):
		self.process = QProcess(self)
		self.process.setProgram(str(CIRCOS_COMMAND))
		self.process.setArguments(["-modules"])
		self.updator.clicked.connect(self.process.start)
		self.process.started.connect(self.spinner.start)
		self.process.errorOccurred.connect(self.on_error_occurred)
		self.process.errorOccurred.connect(self.spinner.stop)
		self.process.finished.connect(self.on_update_finished)
		self.process.finished.connect(self.spinner.stop)
		self.process.start()

	@Slot()
	def on_error_occurred(self):
		error = self.process.errorString()
		QMessageBox.critical(self, "Error", error)

	@Slot(int, QProcess.ExitStatus)
	def on_update_finished(self, code, status):
		if status == QProcess.ExitStatus.NormalExit:
			output = self.process.readAllStandardOutput()
			result = output.data().decode()
			
			items = []
			for line in result.strip().split('\n'):
				cols = line.strip().split()

				if cols and cols[0] == 'ok':
					item = QTreeWidgetItem([cols[2], cols[1], cols[0]])
					item.setIcon(0, QIcon('icons/ok.svg'))
					items.append(item)

				elif cols and cols[0] == 'missing':
					item = QTreeWidgetItem([cols[1], '', cols[0]])
					item.setIcon(0, QIcon('icons/no.svg'))
					items.append(item)

			self.tree.clear()
			self.tree.addTopLevelItems(items)

class CirchartKaryotypePrepareDialog(CirchartBaseDialog):
	_title = "Prepare Karyotype Data"

	def sizeHint(self):
		return QSize(500, 400)

	def _create_widgets(self):
		self.select = QComboBox(self)
		self.select.currentIndexChanged.connect(self.change_genome)
		self.table = CirchartCheckTableWidget(self)
		self.table.setSortingEnabled(True)
		self.input = QLineEdit(self)
		
	def _init_layouts(self):
		self.main_layout.addWidget(QLabel("Select a genome:", self))
		self.main_layout.addWidget(self.select)
		self.main_layout.addWidget(QLabel("Select chromosomes:", self))
		self.main_layout.addWidget(self.table)
		self.main_layout.addWidget(QLabel("Specify a short and uniq chromosome id prefix:", self))
		self.main_layout.addWidget(self.input)

	def _init_widgets(self):
		self.genome_ids = []
		genome_names = []

		for g in SqlControl.get_datas_by_type('genome'):
			self.genome_ids.append(g.id)
			genome_names.append(g.name)

		if genome_names:
			self.select.addItems(genome_names)

	def change_genome(self, index):
		self.table.change_table('genome', self.genome_ids[index])

	@classmethod
	def make_karyotype(cls, parent):
		dlg = cls(parent)

		if dlg.exec() == QDialog.Accepted:
			if not dlg.table.is_selected():
				return QMessageBox.critical(parent, "Error",
					"Please select some chromosomes")

			prefix = dlg.input.text().strip()
			if not prefix:
				return QMessageBox.critical(parent, "Error",
					"Please specify a short and uniq chromosome id prefix")

			#get chr colors from circos
			color_file = CIRCOS_PATH / 'etc' / 'colors.ucsc.conf'

			circos_colors = {}
			with open(str(color_file)) as fh:
				for line in fh:
					if line.startswith('chr'):
						cols = line.strip().split('=')
						if ',' in cols[1]:
							circos_colors[cols[0].strip()] = cols[1].strip()

			items = []
			num = 0
			for rows in dlg.table.get_selected():
				for row in rows:
					num += 1
					chrid = '{}{}'.format(prefix, num)
					label = row[1]
					lenght = row[2]

					if label.lower() in circos_colors:
						color = circos_colors[label.lower()]

					else:
						temp_label = "chr{}".format(label).lower()

						if temp_label in circos_colors:
							color = circos_colors[temp_label]

						else:
							temp_label = "chr{}".format(num)
							color = circos_colors.get(temp_label, circos_colors['chrUn'])

					items.append(('chr', '-', chrid, label, 0, lenght, color))

			kname = "{}_{}".format(dlg.select.currentText(), prefix)
			index = SqlControl.add_data(kname, 'karyotype', '')
			SqlControl.create_index_table('karyotype', index)
			SqlControl.add_index_data('karyotype', index, items)
			parent.data_tree.update_tree()

class CirchartBandPrepareDialog(CirchartBaseDialog):
	_title = "Prepare Band Data"

	def _create_widgets(self):
		self.select_karyotype = QComboBox(self)
		self.select_bands = QComboBox(self)
		self.name_input = QLineEdit(self)
		self.name_input.setPlaceholderText("Band data name")

	def _init_layouts(self):
		self.main_layout.addWidget(self.name_input)
		self.main_layout.addWidget(QLabel("Select a karyotype:", self))
		self.main_layout.addWidget(self.select_karyotype)
		self.main_layout.addWidget(QLabel("Select genome bands", self))
		self.main_layout.addWidget(self.select_bands)

	def _init_widgets(self):
		ks = SqlControl.get_datas_by_type('karyotype')

		for k in ks:
			self.select_karyotype.addItem(k.name, k.id)

		bs = SqlControl.get_datas_by_type('bands')

		for b in bs:
			self.select_bands.addItem(b.name, b.id)

	def _on_accepted(self):
		kt = self.select_karyotype.currentData()

		if not kt:
			return QMessageBox.critical(self, 'Error', "No karyotype data selected")

		bd = self.select_bands.currentData()

		if not bd:
			return QMessageBox.critical(self, 'Error', "No band data selected")

		dn = self.name_input.text().strip()

		if not dn:
			return QMessageBox.critical(self, 'Error', "No band data name input")

		self.accept()

	@classmethod
	def prepare(cls, parent=None):
		dlg = cls(parent)

		if dlg.exec() == QDialog.Accepted:
			return {
				'dataname': dlg.name_input.text().strip(),
				'karyotype': dlg.select_karyotype.currentData(),
				'bands': dlg.select_bands.currentData()
			}

class CirchartGCContentPrepareDialog(CirchartBaseDialog):
	_title = "Prepare GC Content Data"

	def sizeHint(self):
		return QSize(400, 0)
	
	def _create_widgets(self):
		self.dataname_input = QLineEdit(self)
		self.dataname_input.setPlaceholderText("Specify a name for generated data")
		self.select_genome = QComboBox(self)
		self.select_karyotype = QComboBox(self)
		self.window_size = CirchartGenomeWindowSize(self)

	def _init_layouts(self):
		self.main_layout.addWidget(self.dataname_input)
		self.main_layout.addWidget(QLabel("Select a genome:", self))
		self.main_layout.addWidget(self.select_genome)
		self.main_layout.addWidget(QLabel("Select a karyotype:", self))
		self.main_layout.addWidget(self.select_karyotype)
		self.main_layout.addWidget(self.window_size)

	def _init_widgets(self):
		genomes = SqlControl.get_datas_by_type('genome')

		for g in genomes:
			self.select_genome.addItem(g.name, g.id)

		karyotypes = SqlControl.get_datas_by_type('karyotype')

		for k in karyotypes:
			self.select_karyotype.addItem(k.name, k.id)

	@classmethod
	def prepare(cls, parent=None):
		dlg = cls(parent)

		if dlg.exec() == QDialog.Accepted:
			genome = dlg.select_genome.currentData()
			karyotype = dlg.select_karyotype.currentData()
			window_size = dlg.window_size.get_values()
			data_name = dlg.dataname_input.text()

			if genome and karyotype:
				params = {
					'dataname': data_name,
					'genome': genome,
					'karyotype': karyotype,
				}

				params.update(window_size)
				return params

class CirchartGCSkewPrepareDialog(CirchartGCContentPrepareDialog):
	_title = "Prepare GC Skew Data"

class CirchartDensityPrepareDialog(CirchartBaseDialog):
	_title = "Prepare Density Data"

	def sizeHint(self):
		return QSize(400, 0)

	def _create_widgets(self):
		self.dataname_input = QLineEdit(self)
		self.dataname_input.setPlaceholderText("Specify a name for generated data")
		self.select_annotation = QComboBox(self)
		self.select_karyotype = QComboBox(self)
		self.select_feature = QComboBox(self)
		self.window_size = CirchartGenomeWindowSize(self)
		self.select_annotation.currentIndexChanged.connect(self.on_annotation_changed)

	def _init_widgets(self):
		annots = SqlControl.get_datas_by_type('annotation')

		for a in annots:
			self.select_annotation.addItem(a.name, a.id)

		karyotypes = SqlControl.get_datas_by_type('karyotype')

		for k in karyotypes:
			self.select_karyotype.addItem(k.name, k.id)

	def _init_layouts(self):
		self.main_layout.addWidget(self.dataname_input)
		self.main_layout.addWidget(QLabel("Select a karyotype:", self))
		self.main_layout.addWidget(self.select_karyotype)
		self.main_layout.addWidget(QLabel("Select an annotation:", self))
		self.main_layout.addWidget(self.select_annotation)
		self.main_layout.addWidget(QLabel("Select a feature:", self))
		self.main_layout.addWidget(self.select_feature)
		self.main_layout.addWidget(self.window_size)

	def on_annotation_changed(self, index):
		annot_id = self.select_annotation.currentData()
		features = SqlControl.get_annotation_features(annot_id)
		self.select_feature.addItems(features)

	@classmethod
	def prepare(cls, parent=None):
		dlg = cls(parent)

		if dlg.exec() == QDialog.Accepted:
			annotation_id = dlg.select_annotation.currentData()
			karyotype_id = dlg.select_karyotype.currentData()
			window_size = dlg.window_size.get_values()
			feature = dlg.select_feature.currentText()
			dataname = dlg.dataname_input.text()

			if annotation_id and karyotype_id:
				params = {
					'annotation': annotation_id,
					'karyotype': karyotype_id,
					'feature': feature,
					'dataname': dataname
				}

				params.update(window_size)
				return params

class CirchartCreateCircosPlotDialog(QDialog):
	def __init__(self, parent=None):
		super().__init__(parent)

		self.setWindowTitle("Create New Circos Plot")
		self.resize(QSize(400, 300))

		self.tree = CirchartEmptyTreeWidget(self)
		self.tree.setHeaderLabels(['ID', 'Name'])
		self.tree.setRootIsDecorated(False)
		self.input = QLineEdit(self)
		self.tree.hideColumn(0)
		#self.tree.resizeColumnToContents(0)

		self.btn_box = QDialogButtonBox(
			QDialogButtonBox.StandardButton.Cancel |
			QDialogButtonBox.StandardButton.Ok
		)
		self.btn_box.accepted.connect(self._on_accepted)
		self.btn_box.rejected.connect(self.reject)

		layout = QVBoxLayout()
		layout.addWidget(QLabel("Select karyotype data:", self))
		layout.addWidget(self.tree)
		layout.addWidget(QLabel("Circos plot name:", self))
		layout.addWidget(self.input)
		layout.addWidget(self.btn_box)
		self.setLayout(layout)

		self.fill_karyotype_data()

	def _on_accepted(self):
		ks = self.get_selected_karyotype()

		if not ks:
			return QMessageBox.critical(self, 'Error', "No karyotype data selected")

		pn = self.input.text().strip()

		if not pn:
			return QMessageBox.critical(self, 'Error', "No circos plot name input")

		self.accept()

	def fill_karyotype_data(self):
		for k in SqlControl.get_datas_by_type('karyotype'):
			item = QTreeWidgetItem([str(k.id), k.name])
			self.tree.addTopLevelItem(item)
			item.setCheckState(1, Qt.Unchecked)

	def get_selected_karyotype(self):
		it = QTreeWidgetItemIterator(self.tree)

		karyotypes = []
		while it.value():
			item = it.value()

			if item.checkState(1) == Qt.Checked:
				karyotypes.append(int(item.text(0)))

			it += 1

		return karyotypes

	@classmethod
	def create_plot(cls, parent):
		dlg = cls(parent)

		if dlg.exec() == QDialog.Accepted:
			return {
				'plot_type': 'circos',
				'plot_name': dlg.input.text(),
				'karyotype': dlg.get_selected_karyotype()
			}

class CirchartCreateSnailPlotDialog(CirchartBaseDialog):
	_title = "Create New Snail Plot"

	def _create_widgets(self):
		self.select_genome = QComboBox(self)
		self.plot_name = QLineEdit(self)

	def _init_widgets(self):
		gs = SqlControl.get_datas_by_type('genome')

		for g in gs:
			self.select_genome.addItem(g.name, g.id)

	def _init_layouts(self):
		self.main_layout.addWidget(QLabel("Select a genome:", self))
		self.main_layout.addWidget(self.select_genome)
		self.main_layout.addWidget(QLabel("Snail plot name:", self))
		self.main_layout.addWidget(self.plot_name)

	def _on_accepted(self):
		gi = self.select_genome.currentData()
		pn = self.plot_name.text().strip()

		if not gi:
			return QMessageBox.critical(self, 'Error', "No genome data selected")

		if not pn:
			return QMessageBox.critical(self, 'Error', "No snail plot name input")

		self.accept()

	@classmethod
	def create_plot(cls, parent):
		dlg = cls(parent)

		if dlg.exec() == QDialog.Accepted:
			genome = dlg.select_genome.currentData()
			name = dlg.plot_name.text().strip()

			if genome and name:
				return {
					'plot_type': 'snail',
					'plot_name': name,
					'genome': genome
				}

class CirchartCircosColorSelectDialog(QDialog):
	def __init__(self, initials=[], parent=None, multiple=False):
		super().__init__(parent)
		if multiple:
			self.setWindowTitle("Select colors")
		else:
			self.color_opacity = 1
			self.setWindowTitle("Select color")

		self.resize(QSize(500, 300))
		self.multiple = multiple

		self.color_table = CirchartCircosColorTable(self, self.multiple)
		self.color_table.color_changed.connect(self.on_select_color)
		self.more_color = QPushButton("More colors", self)
		self.more_color.clicked.connect(self.on_more_color)

		self.btn_box = QDialogButtonBox(self)
		self.btn_box.addButton(self.more_color, QDialogButtonBox.ResetRole)
		self.btn_box.setStandardButtons(
			QDialogButtonBox.StandardButton.Cancel |
			QDialogButtonBox.StandardButton.Ok
		)
		self.btn_box.accepted.connect(self.accept)
		self.btn_box.rejected.connect(self.reject)

		main_layout = QVBoxLayout()
		self.color_layout = QHBoxLayout()
		main_layout.addWidget(self.color_table)
		main_layout.addLayout(self.color_layout)
		main_layout.addWidget(self.btn_box)
		self.setLayout(main_layout)

		if multiple:
			self.color_layout.addWidget(QLabel("Selected colors:", self))
		else:
			self.color_layout.addWidget(QLabel("Selected color:", self))

		self.selected_colors = initials
		self.show_colors()

	def show_colors(self):
		if not self.selected_colors:
			return

		for i in range(1, self.color_layout.count()):
			item = self.color_layout.itemAt(i)

			if item.widget():
				item.widget().deleteLater()

		for c in self.selected_colors:
			cw = QLabel(self)
			cw.setFixedSize(16, 16)
			cw.setStyleSheet("background-color:rgb({});border:1px solid black;".format(c))
			self.color_layout.addWidget(cw)

		if not self.multiple:
			opacity_widget = QDoubleSpinBox(self)
			opacity_widget.setRange(0, 1)
			opacity_widget.setDecimals(2)
			opacity_widget.setSingleStep(0.01)
			opacity_widget.setValue(self.color_opacity)
			opacity_widget.valueChanged.connect(self.on_opacity_changed)

			self.color_layout.addSpacing(20)
			self.color_layout.addWidget(QLabel("Opacity:", self))
			self.color_layout.addWidget(opacity_widget)

		self.color_layout.addWidget(CirchartSpacerWidget(self))

	def on_opacity_changed(self, opacity):
		self.color_opacity = opacity

	def on_select_color(self, colors):
		self.selected_colors = []

		for color in colors:
			r = color.red()
			g = color.green()
			b = color.blue()
			c = "{},{},{}".format(r, g, b)
			self.selected_colors.append(c)

		if self.multiple:
			self.show_colors()
		else:
			self.change_color(c)

	def change_color(self, c):
		item = self.color_layout.itemAt(1)
		item.widget().setStyleSheet("background-color:rgb({});border:1px solid black;".format(c))

	def on_more_color(self):
		color = QColorDialog.getColor(parent=self)

		if color.isValid():
			r = color.red()
			g = color.green()
			b = color.blue()
			c = "{},{},{}".format(r, g, b)

			if self.multiple:
				self.selected_colors.append(c)
				self.show_colors()
			else:
				self.selected_colors = [c]
				self.change_color(c)

	@classmethod
	def get_color(cls, initials=[], parent=None, multiple=False):
		dlg = cls(initials, parent, multiple)

		if dlg.exec() == QDialog.Accepted:
			if multiple:
				return dlg.selected_colors
			else:
				if dlg.selected_colors:
					if dlg.color_opacity < 1:
						return "{},{}".format(dlg.selected_colors[0], dlg.color_opacity)

					else:
						return dlg.selected_colors[0]


class CirchartLinkPrepareDialog(CirchartBaseDialog):
	_title = "Prepare Link Data"

	def _create_widgets(self):
		self.mapping_widgets = []

		self.dataname_label = QLabel("Specify name for generated link data", self)
		self.dataname_input = QLineEdit(self)
		
		self.collinear_label = QLabel("Select collinearity data", self)
		self.collinear_select = QComboBox(self)

		self.species_label = QLabel("Number of species in collinearity", self)
		self.species_spin = QSpinBox(self)
		self.species_spin.setRange(1, 10)
		self.species_spin.valueChanged.connect(self._on_species_changed)

	def _init_layouts(self):
		self.base_layout = QGridLayout()
		self.subs_layout = QVBoxLayout()
		self.subs_layout.setContentsMargins(0, 0, 0, 0)

		self.base_layout.addWidget(self.dataname_label, 0, 0)
		self.base_layout.addWidget(self.dataname_input, 0, 1)
		self.base_layout.addWidget(self.collinear_label, 1, 0)
		self.base_layout.addWidget(self.collinear_select, 1, 1)
		self.base_layout.addWidget(self.species_label, 2, 0)
		self.base_layout.addWidget(self.species_spin, 2, 1)

		self.main_layout.addLayout(self.base_layout)
		self.main_layout.addLayout(self.subs_layout)

	def _init_widgets(self):
		cs = SqlControl.get_datas_by_type('collinearity')

		for c in cs:
			self.collinear_select.addItem(c.name, c.id)

		self.add_mapping("Species1")

	def add_mapping(self, title):
		mapwdg = CirchartCollinearityIdmappingWidget(title, self)
		self.subs_layout.addWidget(mapwdg)
		self.mapping_widgets.append(mapwdg)

	def remove_mapping(self):
		mapwdg = self.mapping_widgets.pop()
		self.subs_layout.removeWidget(mapwdg)
		mapwdg.deleteLater()

		self.adjustSize()

	def _on_species_changed(self, num):
		widget_num = len(self.mapping_widgets)

		if num > widget_num:
			j = widget_num
			for i in range(num - widget_num):
				j += 1
				self.add_mapping("Species{}".format(j))
		else:
			for i in range(widget_num - num):
				self.remove_mapping()

	def get_params(self):
		data = {'sp{}'.format(idx): wdg.get_values() for idx, wdg in enumerate(self.mapping_widgets)}
		data['collinearity'] = self.collinear_select.currentData()
		data['dataname'] = self.dataname_input.text()
		return data

	@classmethod
	def prepare(cls, parent):
		dlg = cls(parent)

		if dlg.exec() == QDialog.Accepted:
			params = dlg.get_params()
			return params
