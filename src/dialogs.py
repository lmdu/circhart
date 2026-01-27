from pathlib import Path

from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *

from utils import *
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
	'CirchartTextPrepareDialog',
	'CirchartCreateCircosPlotDialog',
	'CirchartCreateSnailPlotDialog',
	'CirchartCircosColorSelectDialog',
	'CirchartLinkPrepareDialog',
	'CirchartCustomColorDialog',
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

class CirchartCustomColorDialog(CirchartBaseDialog):
	_title = "Show Custom Colors"

	def sizeHint(self):
		return QSize(550, 400)

	def _create_widgets(self):
		self.table = CirchartCustomColorTable(self)
		self.input = QTextEdit(self)
		self.input.setPlaceholderText("Format: colorname = r,g,b one color per line")
		self.button = QPushButton("Add Colors", self)
		self.button.clicked.connect(self._on_add_colors)

	def _create_buttons(self):
		self.btn_box = QDialogButtonBox(
			QDialogButtonBox.StandardButton.Ok
		)
		self.btn_box.accepted.connect(self._on_accepted)
		self.main_layout.addWidget(self.btn_box)

	def _init_layouts(self):
		sub_layout = QHBoxLayout()
		self.main_layout.addLayout(sub_layout)

		left_layout = QVBoxLayout()
		left_layout.addWidget(QLabel("Custom color list:", self))
		left_layout.addWidget(self.table)

		right_layout = QVBoxLayout()
		right_layout.addWidget(QLabel("Input colors:", self))
		right_layout.addWidget(self.input)
		right_layout.addWidget(self.button)
		
		sub_layout.addLayout(left_layout)
		sub_layout.addLayout(right_layout)

	def _on_add_colors(self):
		lines = self.input.toPlainText().strip()
		count = 0

		colors = []
		for line in lines.split('\n'):
			count += 1

			cols = line.strip().split('=')

			name = cols[0].strip()
			color = cols[1].strip().replace(' ', '')

			if not all(v.isdigit() for v in color.split(',')):
				return QMessageBox.critical(self, 'Error', "Error in line {}".format(count))

			colors.append((name, color))

		if colors:
			SqlControl.add_custom_colors(colors)
			self.table._model.update_model()

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
		self.process.readyReadStandardError.connect(self.on_monitor_stderr)
		self.process.finished.connect(self.on_update_finished)
		self.process.finished.connect(self.spinner.stop)
		self.process.start()

	def on_error_occurred(self):
		error = self.process.errorString()
		QMessageBox.critical(self, "Error", error)

	def on_monitor_stderr(self):
		data = self.process.readAllStandardError()
		QMessageBox.critical(self, 'Error', data.data().decode())

	def on_update_finished(self, code, status):
		if status == QProcess.ExitStatus.NormalExit:
			output = self.process.readAllStandardOutput()
			result = output.data().decode()
			
			items = []

			self.tree.clear()
			for line in result.strip().split('\n'):
				cols = line.strip().split()

				if cols and cols[0] == 'ok':
					item = QTreeWidgetItem([cols[2], cols[1], cols[0]])
					item.setIcon(0, QIcon(':/icons/ok.svg'))
					self.tree.addTopLevelItem(item)

				elif cols and cols[0] == 'missing':
					item = QTreeWidgetItem([cols[1], '', cols[0]])
					item.setIcon(0, QIcon(':/icons/no.svg'))
					self.tree.addTopLevelItem(item)

class CirchartKaryotypePrepareDialog(CirchartBaseDialog):
	_title = "Prepare Karyotype Data"

	def sizeHint(self):
		return QSize(500, 400)

	def _create_widgets(self):
		self.name_input = QLineEdit(self)
		self.name_input.setPlaceholderText("input name for generated karyotype data")
		self.select = QComboBox(self)
		self.select.currentIndexChanged.connect(self.change_genome)
		self.table = CirchartCheckTableWidget(self)
		self.table.setSortingEnabled(True)
		self.prefix_input = QLineEdit(self)
		self.prefix_input.setPlaceholderText("e.g. use hs for human, mm for mouse, or chr")
		
	def _init_layouts(self):
		self.main_layout.addWidget(self.name_input)
		self.main_layout.addWidget(QLabel("Select a genome:", self))
		self.main_layout.addWidget(self.select)
		self.main_layout.addWidget(QLabel("Select chromosomes:", self))
		self.main_layout.addWidget(self.table)
		self.main_layout.addWidget(QLabel("Chromosome name prefix:", self))
		self.main_layout.addWidget(self.prefix_input)

	def _init_widgets(self):
		self.genome_ids = []
		genome_names = []

		for g in SqlControl.get_datas_by_type('genome'):
			self.genome_ids.append(g.id)
			genome_names.append(g.name)

		if genome_names:
			self.select.addItems(genome_names)

	def _on_accepted(self):
		kn = self.name_input.text().strip()
		if not kn:
			return QMessageBox.critical(self, 'Error', "No karyotype data name input")

		selected = self.table.is_selected()
		if not selected:
			return QMessageBox.critical(self, "Error", "No chromosome selected")

		px = self.prefix_input.text().strip()
		if not px:
			return QMessageBox.critical(self, "Error", "No chromosome name prefix input")

		self.accept()

	def change_genome(self, index):
		self.table.change_table('genome', self.genome_ids[index])

	@classmethod
	def prepare(cls, parent=None):
		dlg = cls(parent)

		if dlg.exec() == QDialog.Accepted:
			#get chr colors from circos
			color_file = CIRCOS_PATH / 'etc' / 'colors.ucsc.conf'

			circos_colors = {}
			with open(str(color_file)) as fh:
				for line in fh:
					if line.startswith('chr'):
						cols = line.strip().split('=')
						if ',' in cols[1]:
							circos_colors[cols[0].strip()] = cols[1].strip()

			prefix = dlg.prefix_input.text().strip()

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

			kname = dlg.name_input.text().strip()
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
		self.name_input.setPlaceholderText("input name for generated band data")

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
		dn = self.name_input.text().strip()
		if not dn:
			return QMessageBox.critical(self, 'Error', "No band data name input")

		kt = self.select_karyotype.currentData()
		if not kt:
			return QMessageBox.critical(self, 'Error', "No karyotype data selected")

		bd = self.select_bands.currentData()
		if not bd:
			return QMessageBox.critical(self, 'Error', "No band data selected")

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
		self.dataname_input.setPlaceholderText("input name for generated data")
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
		gs = SqlControl.get_datas_by_type('genome')
		for g in gs:
			self.select_genome.addItem(g.name, g.id)

		ks = SqlControl.get_datas_by_type('karyotype')
		for k in ks:
			self.select_karyotype.addItem(k.name, k.id)

	def _on_accepted(self):
		dn = self.dataname_input.text().strip()
		if not dn:
			return QMessageBox.critical(self, 'Error', 'No GC data name input')

		gi = self.select_genome.currentData()
		if not gi:
			return QMessageBox.critical(self, 'Error', 'No genome selected')

		ki = self.select_karyotype.currentData()
		if not ki:
			return QMessageBox.critical(self, 'Error', "No karyotype selected")

		self.accept()

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
		self.dataname_input.setPlaceholderText("input name for generated data")
		self.select_datatype = QComboBox(self)
		self.select_annotation = QComboBox(self)
		self.select_karyotype = QComboBox(self)
		self.feature_label = QLabel("Select a feature:", self)
		self.select_feature = QComboBox(self)
		self.window_size = CirchartGenomeWindowSize(self)

		self.select_datatype.currentIndexChanged.connect(self._on_datatype_changed)
		self.select_annotation.currentIndexChanged.connect(self._on_annotation_changed)

	def _init_widgets(self):
		formats = [
			('Genome annotation (gtf or gff)', 'gxf'),
			('Genome variations (vcf)', 'vcf'),
			('Genome regions (bed)', 'bed')
		]

		for desc, fmt in formats:
			self.select_datatype.addItem(desc, fmt)

		ks = SqlControl.get_datas_by_type('karyotype')
		for k in ks:
			self.select_karyotype.addItem(k.name, k.id)

	def _init_layouts(self):
		self.main_layout.addWidget(self.dataname_input)
		self.main_layout.addWidget(QLabel("Select a karyotype:", self))
		self.main_layout.addWidget(self.select_karyotype)
		self.main_layout.addWidget(QLabel("Select source data type:", self))
		self.main_layout.addWidget(self.select_datatype)
		self.main_layout.addWidget(QLabel("Select source data:", self))
		self.main_layout.addWidget(self.select_annotation)
		self.main_layout.addWidget(self.feature_label)
		self.main_layout.addWidget(self.select_feature)
		self.main_layout.addWidget(self.window_size)

	def _on_datatype_changed(self, index):
		if index == 0:
			self.feature_label.setVisible(True)
			self.select_feature.setVisible(True)
			self.adjustSize()
		else:
			self.feature_label.setVisible(False)
			self.select_feature.setVisible(False)
			self.adjustSize()

		data_types = ['annotation', 'variants', 'regions']

		ds = SqlControl.get_datas_by_type(data_types[index])
		self.select_annotation.clear()
		for d in ds:
			self.select_annotation.addItem(d.name, d.id)

	def _on_annotation_changed(self, index):
		if self.select_datatype.currentIndex() == 0:
			annot_id = self.select_annotation.currentData()
			features = SqlControl.get_annotation_features(annot_id)
			self.select_feature.clear()
			self.select_feature.addItems(features)

	def _on_accepted(self):
		dn = self.dataname_input.text().strip()
		if not dn:
			return QMessageBox.critical(self, 'Error', "No data name input")

		ki = self.select_karyotype.currentData()
		if not ki:
			return QMessageBox.critical(self, 'Error', "No karyotype selected")

		di = self.select_annotation.currentData()
		if not di:
			return QMessageBox.critical(self, 'Error', "No source data selected")

		if self.select_datatype.currentIndex() == 0:
			fi = self.select_feature.currentData()
			if not fi:
				return QMessageBox.critical(self, 'Error', "No feature selected")

		self.accept()

	@classmethod
	def prepare(cls, parent=None):
		dlg = cls(parent)

		if dlg.exec() == QDialog.Accepted:
			annotation_id = dlg.select_annotation.currentData()
			karyotype_id = dlg.select_karyotype.currentData()
			window_size = dlg.window_size.get_values()
			feature = dlg.select_feature.currentText()
			dataname = dlg.dataname_input.text().strip()
			datatype = dlg.select_datatype.currentData()

			params = {
				'annotation': annotation_id,
				'karyotype': karyotype_id,
				'feature': feature,
				'dataname': dataname,
				'datatype': datatype
			}

			params.update(window_size)
			return params

class CirchartTextPrepareDialog(CirchartBaseDialog):
	_title = "Prepare Text Data"

	def _create_widgets(self):
		self.dataname_input = QLineEdit(self)
		self.dataname_input.setPlaceholderText("input name for generated data")
		self.annot_select = QComboBox(self)
		self.select_karyotype = QComboBox(self)
		self.feat_select = QComboBox(self)
		self.attr_select = QComboBox(self)
		self.match_text = QTextEdit(self)
		self.match_text.setVisible(False)
		self.match_text.setPlaceholderText("One attribute value per line")
		self.match_check = QCheckBox("Only extract records whose attribute value in below list")
		self.match_check.toggled.connect(self._on_method_changed)

		self.annot_select.currentIndexChanged.connect(self._on_annotation_changed)

	def _init_widgets(self):
		self.features = {}
		self.attributes = {}

		ks = SqlControl.get_datas_by_type('karyotype')
		for k in ks:
			self.select_karyotype.addItem(k.name, k.id)

		ans = SqlControl.get_datas_by_type('annotation')
		for a in ans:
			meta = str_to_dict(a.meta)
			self.features[a.id] = meta['features']
			self.attributes[a.id] = meta['attributes']

			self.annot_select.addItem(a.name, a.id)

	def _init_layouts(self):
		self.main_layout.addWidget(self.dataname_input)
		self.main_layout.addWidget(QLabel("Select a karyotype:", self))
		self.main_layout.addWidget(self.select_karyotype)
		self.main_layout.addWidget(QLabel("Select an annotation:", self))
		self.main_layout.addWidget(self.annot_select)

		subs_layout = QGridLayout()
		subs_layout.setContentsMargins(0, 0, 0, 0)
		subs_layout.addWidget(QLabel("Select a feature:", self), 0, 0)
		subs_layout.addWidget(self.feat_select, 1, 0)
		subs_layout.addWidget(QLabel("Select an attribute:"), 0, 1)
		subs_layout.addWidget(self.attr_select, 1, 1)
		
		self.main_layout.addLayout(subs_layout)
		self.main_layout.addWidget(self.match_check)
		self.main_layout.addWidget(self.match_text)

	def _on_annotation_changed(self, index):
		aid = self.annot_select.currentData()
		
		self.feat_select.clear()
		self.feat_select.addItems(self.features[aid])

		self.attr_select.clear()
		self.attr_select.addItems(self.attributes[aid])

	def _on_method_changed(self, checked):
		self.match_text.setVisible(checked)
		self.adjustSize()

	def _on_accepted(self):
		dn = self.dataname_input.text().strip()
		if not dn:
			return QMessageBox.critical(self, 'Error', "No data name input")

		ki = self.select_karyotype.currentData()
		if not ki:
			return QMessageBox.critical(self, 'Error', "No karyotype selected")

		ai = self.annot_select.currentData()
		if not ai:
			return QMessageBox.critical(self, 'Error', "No annotation selected")

		ft = self.feat_select.currentText()
		if not ft:
			return QMessageBox.critical(self, 'Error', "No feature selected")
		
		at = self.attr_select.currentText()
		if not at:
			return QMessageBox.critical(self, 'Error', "No attribute selected")

		if self.match_check.isChecked():
			mt = self.match_text.toPlainText().strip()
			if not mt:
				return QMessageBox.critical(self, 'Error', "No attribute value list input")

		self.accept()

	@classmethod
	def prepare(cls, parent=None):
		dlg = cls(parent)

		if dlg.exec() == QDialog.Accepted:
			annotation_id = dlg.annot_select.currentData()
			karyotype_id = dlg.select_karyotype.currentData()
			feature = dlg.feat_select.currentText()
			dataname = dlg.dataname_input.text().strip()
			attribute = dlg.attr_select.currentText()
			matches = dlg.match_text.toPlainText()
			method = dlg.match_check.isChecked()

			params = {
				'annotation': annotation_id,
				'karyotype': karyotype_id,
				'feature': feature,
				'attribute': attribute,
				'dataname': dataname
			}

			if method:
				params['matches'] = matches

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

		self.dataname_input = QLineEdit(self)
		self.dataname_input.setPlaceholderText("input name for generated data")
		
		self.collinear_label = QLabel("Select collinearity data:", self)
		self.collinear_select = QComboBox(self)

		self.species_label = QLabel("Number of species in collinearity:", self)
		self.species_spin = QSpinBox(self)
		self.species_spin.setRange(1, 10)
		self.species_spin.valueChanged.connect(self._on_species_changed)

	def _init_layouts(self):
		self.base_layout = QVBoxLayout()
		self.subs_layout = QVBoxLayout()
		self.subs_layout.setContentsMargins(0, 0, 0, 0)

		self.base_layout.addWidget(self.dataname_input)
		self.base_layout.addWidget(self.collinear_label)
		self.base_layout.addWidget(self.collinear_select)
		self.base_layout.addWidget(self.species_label)
		self.base_layout.addWidget(self.species_spin)

		self.main_layout.addLayout(self.base_layout)
		self.main_layout.addLayout(self.subs_layout)

	def _init_widgets(self):
		cs = SqlControl.get_datas_by_type('collinearity')

		for c in cs:
			self.collinear_select.addItem(c.name, c.id)

		self.add_mapping("Species1", True)

	def add_mapping(self, title, label=False):
		mapwdg = CirchartCollinearityIdmappingWidget(title, self, label)
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
		data['dataname'] = self.dataname_input.text().strip()
		return data

	def _on_accepted(self):
		data = self.get_params()
		if not data['dataname']:
			return QMessageBox.critical(self, 'Error', "No data name input")

		if not data['collinearity']:
			return QMessageBox.critical(self, 'Error', "No collinearity data selected")

		for k, v in data.items():
			if not k.startswith('sp'):
				if not all(v.values()):
					return QMessageBox.critical(self, 'Error', "Species information is not completely filled out")

		self.accept()

	@classmethod
	def prepare(cls, parent):
		dlg = cls(parent)

		if dlg.exec() == QDialog.Accepted:
			params = dlg.get_params()
			return params
