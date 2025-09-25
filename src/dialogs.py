from pathlib import Path

from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *

from config import *
from widgets import *
from backend import *

__all__ = [
	'CirchartCircosDependencyDialog',
	'CirchartKaryotypePrepareDialog',
	'CirchartGCContentPrepareDialog',
	'CirchartDensityPrepareDialog',
	'CirchartCreateCircosPlotDialog',
	'CirchartCircosColorSelectDialog',
]

class CirchartBaseDialog(QDialog):
	_title = ""

	def __init__(self, parent=None):
		super().__init__(parent)
		self.setWindowTitle(self._title)

		self.main_layout = QVBoxLayout()
		self.setLayout(self.main_layout)

		self.create_widgets()
		self.create_buttons()
		self.init_layouts()
		self.init_widgets()

	def sizeHint(self):
		return QSize(400, 300)

	def create_widgets(self):
		pass

	def create_buttons(self):
		self.btn_box = QDialogButtonBox(
			QDialogButtonBox.StandardButton.Cancel |
			QDialogButtonBox.StandardButton.Ok
		)
		self.btn_box.accepted.connect(self.accept)
		self.btn_box.rejected.connect(self.reject)

	def init_widgets(self):
		pass

	def init_layouts(self):
		pass
		

class CirchartCircosDependencyDialog(CirchartBaseDialog):
	_title = "Circos Perl Dependencies"
	
	def create_widgets(self):
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

	def create_buttons(self):
		self.btn_box = QDialogButtonBox(
			QDialogButtonBox.StandardButton.Ok
		)
		self.btn_box.accepted.connect(self.accept)

	def init_layouts(self):
		top_layout = QHBoxLayout()
		top_layout.addWidget(self.spinner)
		top_layout.addWidget(CirchartSpacerWidget(self))
		top_layout.addWidget(self.updator)
		self.main_layout.addLayout(top_layout)
		self.main_layout.addWidget(self.tree)
		self.main_layout.addWidget(self.btn_box)

	def init_widgets(self):
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

	def create_widgets(self):
		self.select = QComboBox(self)
		self.select.currentIndexChanged.connect(self.change_genome)
		self.table = CirchartCheckTableWidget(self)
		self.table.setSortingEnabled(True)
		self.input = QLineEdit(self)
		
	def init_layouts(self):
		self.main_layout.addWidget(QLabel("Select a genome:", self))
		self.main_layout.addWidget(self.select)
		self.main_layout.addWidget(QLabel("Select chromosomes:", self))
		self.main_layout.addWidget(self.table)
		self.main_layout.addWidget(QLabel("Specify a short and uniq chromosome id prefix:", self))
		self.main_layout.addWidget(self.input)
		self.main_layout.addWidget(self.btn_box)

	def init_widgets(self):
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
			SqlControl.create_karyotype_table(index)
			SqlControl.add_karyotype_data(index, items)

			parent.data_tree.update_tree()

class CirchartGCContentPrepareDialog(CirchartBaseDialog):
	_title = "Prepare GC Content Data"

	def sizeHint(self):
		return QSize(400, 0)
	
	def create_widgets(self):
		self.select_genome = QComboBox(self)
		self.select_karyotype = QComboBox(self)
		self.window_size = CirchartGenomeWindowSize(self)

	def init_layouts(self):
		self.main_layout.addWidget(QLabel("Select a genome:", self))
		self.main_layout.addWidget(self.select_genome)
		self.main_layout.addWidget(QLabel("Select a karyotype:", self))
		self.main_layout.addWidget(self.select_karyotype)
		self.main_layout.addWidget(QLabel("Window size:", self))
		self.main_layout.addWidget(self.window_size)
		self.main_layout.addWidget(self.btn_box)

	def init_widgets(self):
		genomes = SqlControl.get_datas_by_type('genome')

		for g in genomes:
			self.select_genome.addItem(g.name, g.path)

		karyotypes = SqlControl.get_datas_by_type('karyotype')

		for k in karyotypes:
			self.select_karyotype.addItem(k.name, k.id)

	@classmethod
	def calculate_gc_content(cls, parent=None):
		dlg = cls(parent)

		if dlg.exec() == QDialog.Accepted:
			genome_path = dlg.select_genome.currentData()
			karyotype_id = dlg.select_karyotype.currentData()
			window_size = dlg.window_size.get_value()

			if genome_path and karyotype_id:
				return {
					'genome': genome_path,
					'karyotype': karyotype_id,
					'window': window_size
				}

class CirchartDensityPrepareDialog(CirchartBaseDialog):
	_title = "Prepare Density Data"

	def sizeHint(self):
		return QSize(400, 0)

	def create_widgets(self):
		self.select_annotation = QComboBox(self)
		self.select_karyotype = QComboBox(self)
		self.select_feature = QComboBox(self)
		self.window_size = CirchartGenomeWindowSize(self)
		self.select_annotation.currentIndexChanged.connect(self.on_annotation_changed)

	def init_widgets(self):
		annots = SqlControl.get_datas_by_type('annotation')

		for a in annots:
			self.select_annotation.addItem(a.name, a.id)

		karyotypes = SqlControl.get_datas_by_type('karyotype')

		for k in karyotypes:
			self.select_karyotype.addItem(k.name, k.id)

	def init_layouts(self):
		self.main_layout.addWidget(QLabel("Select a karyotype:", self))
		self.main_layout.addWidget(self.select_karyotype)
		self.main_layout.addWidget(QLabel("Select an annotation:", self))
		self.main_layout.addWidget(self.select_annotation)
		self.main_layout.addWidget(QLabel("Select a feature:", self))
		self.main_layout.addWidget(self.select_feature)
		self.main_layout.addWidget(QLabel("Window size:", self))
		self.main_layout.addWidget(self.window_size)
		self.main_layout.addWidget(self.btn_box)

	def on_annotation_changed(self, index):
		annot_id = self.select_annotation.currentData()
		features = SqlControl.get_annotation_features(annot_id)
		self.select_feature.addItems(features)

	@classmethod
	def count_feature(cls, parent=None):
		dlg = cls(parent)

		if dlg.exec() == QDialog.Accepted:
			annotation_id = dlg.select_annotation.currentData()
			karyotype_id = dlg.select_karyotype.currentData()
			window_size = dlg.window_size.get_value()
			feature = dlg.select_feature.currentText()

			if annotation_id and karyotype_id:
				return {
					'annotation': annotation_id,
					'karyotype': karyotype_id,
					'feature': feature,
					'window': window_size
				}

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
		self.btn_box.accepted.connect(self.accept)
		self.btn_box.rejected.connect(self.reject)

		layout = QVBoxLayout()
		layout.addWidget(QLabel("Select karyotype data:", self))
		layout.addWidget(self.tree)
		layout.addWidget(QLabel("Specify circos plot name:", self))
		layout.addWidget(self.input)
		layout.addWidget(self.btn_box)
		self.setLayout(layout)

		self.fill_karyotype_data()

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
				'plotname': dlg.input.text(),
				'karyotype': dlg.get_selected_karyotype()
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
















