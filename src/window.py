import os
import sys

from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *

from config import *
from dialogs import *
from widgets import *
from backend import *
from workers import *
from params import *

__all__ = [
	'CirchartApplication',
	'CirchartMainWindow',
]

class CirchartApplication(QApplication):
	osx_open_with = Signal(str)

	def __init__(self, argv):
		super().__init__(argv)

		self.load_style()
		self.setStyle(QStyleFactory.create('windowsvista'))

	def event(self, event):
		if sys.platform == 'darwin':
			if isinstance(event, QFileOpenEvent):
				self.osx_open_with.emit(event.file())

		return super().event(event)

	def load_style(self):
		file = QFile(':/style.qss')

		if file.open(QIODevice.ReadOnly | QIODevice.Text):
			stream = QTextStream(file)

		self.setStyleSheet(stream.readAll())


class CirchartMainWindow(QMainWindow):
	def __init__(self):
		super().__init__()

		self.project_file = None

		self.set_window_title()
		self.setWindowIcon(QIcon(':/icons/logo.svg'))

		self.plot_view = CirchartGraphicsViewWidget(self)
		self.data_table = CirchartDataTableWidget(self)
		self.data_tree = CirchartDataTreeWidget(self)
		self.data_tree.data_removed.connect(self.data_table.clear_table)
		self.data_tree.show_data.connect(self.data_table.change_table)
		self.data_tree.clicked.connect(self.show_data_table)
		self.plot_tree = CirchartPlotTreeWidget(self)
		self.plot_tree.show_plot.connect(self.show_plot_params)
		self.plot_tree.show_plot.connect(self.show_plot_image)
		self.plot_tree.clicked.connect(self.show_plot_view)

		self.stack_widget = QStackedWidget(self)
		self.stack_widget.addWidget(self.plot_view)
		self.stack_widget.addWidget(self.data_table)

		self.create_sidebar()
		self.create_actions()
		self.create_toolbar()
		self.create_menus()
		self.create_statusbar()
		self.create_plot_panels()

		self.setCentralWidget(self.stack_widget)
		
		self.read_settings()
		self.show()

	def closeEvent(self, event):
		self.write_settings()
		event.accept()

	def read_settings(self):
		settings = QSettings()
		settings.beginGroup('Window')
		self.resize(settings.value('size', QSize(900, 600)))
		self.move(settings.value('pos', QPoint(200, 200)))
		settings.endGroup()

	def write_settings(self):
		settings = QSettings()

		if not self.isMaximized():
			settings.beginGroup('Window')
			settings.setValue('size', self.size())
			settings.setValue('pos', self.pos())
			settings.endGroup()

	def set_window_title(self, pfile=None):
		if pfile is None:
			self.setWindowTitle("{} v{}".format(APP_NAME, APP_VERSION))

		else:
			self.setWindowTitle("{} v{} - {}".format(APP_NAME, APP_VERSION, pfile))

	def create_actions(self):
		self.open_project_act = QAction("&Open Project...", self,
			shortcut = QKeySequence.Open,
			triggered = self.do_open_project
		)

		self.save_project_act = QAction("&Save Project", self,
			shortcut = QKeySequence.Save,
			triggered = self.do_save_project
		)

		self.saveas_project_act = QAction("&Save Project As...", self,
			shortcut = QKeySequence.SaveAs,
			triggered = self.do_saveas_project
		)

		self.close_project_act = QAction("&Close Project", self,
			triggered = self.do_close_project
		)

		self.import_genome_act = QAction("&Import Genome File...", self,
			triggered = self.do_import_genome_file
		)

		self.import_annot_act = QAction("&Import Genome Annotation...", self,
			triggered = self.do_import_genome_annotation
		)

		self.import_gbands_act = QAction("&Import Genome Bands...", self,
			triggered = self.do_import_genome_bands
		)

		self.import_variant_act = QAction("&Import Genome Variations...", self,
			triggered = self.do_import_genome_variations
		)

		self.import_region_act = QAction("&Import Genome Regions...", self,
			triggered = self.do_import_genome_regions
		)

		self.import_collinearity_act = QAction("&Import Collinearity File...", self,
			triggered = self.do_import_mcscanx_collinearity
		)

		self.import_kdata_act = QAction("&Import Karyotype Data...", self,
			triggered = self.do_import_karyotype_data
		)

		self.import_band_act = QAction("&Import Band Data...", self,
			triggered = self.do_import_band_data
		)

		self.import_pdata_act = QAction("&Import Plot Data...", self,
			triggered = self.do_import_plot_data
		)

		self.import_link_act = QAction("&Import Link Data...", self,
			triggered = self.do_import_link_data
		)

		self.import_loci_act = QAction("&Import Loci Data...", self,
			triggered = self.do_import_loci_data
		)

		self.import_text_act = QAction("&Import Text Data...", self,
			triggered = self.do_import_text_data
		)

		self.export_image_act = QAction(QIcon(":/icons/save.svg"), "&Export Image...", self,
			triggered = self.do_export_image
		)
		self.export_image_act.setIconVisibleInMenu(False)

		self.zoom_in_act = QAction(QIcon(":/icons/zoomin.svg"), "&Zoom In", self,
			shortcut = QKeySequence.ZoomIn,
			triggered = self.do_zoom_in
		)

		self.zoom_out_act = QAction(QIcon(":/icons/zoomout.svg"), "&Zoom Out", self,
			shortcut = QKeySequence.ZoomOut,
			triggered = self.do_zoom_out
		)

		self.quit_act = QAction("&Exit", self,
			shortcut = QKeySequence.Quit,
			triggered = self.close
		)

		self.kcolor_default_act = QAction("Set to Default", self,
			triggered = self.do_set_karyotype_default_color
		)

		self.kcolor_random_act = QAction("Set to Random", self,
			triggered = self.do_set_karyotype_random_color
		)

		self.kcolor_pure_act = QAction("Set to Single", self,
			triggered = self.do_set_karyotype_pure_color
		)

		self.prepare_kdata_act = QAction("&Prepare Karyotype Data", self,
			triggered = self.do_prepare_karyotype_data
		)

		self.prepare_band_act = QAction("&Prepare Band Data", self,
			triggered = self.do_prepare_band_data
		)

		self.prepare_gc_act = QAction("&Prepare GC Content Data", self,
			triggered = self.do_prepare_gccontent_data
		)

		self.prepare_skew_act = QAction("&Prepare GC Skew Data", self,
			triggered = self.do_prepare_gcskew_data
		)

		self.prepare_pdata_act = QAction("&Prepare Density Data", self,
			triggered = self.do_prepare_density_data
		)

		self.prepare_ldata_act = QAction("&Prepare Link Data", self,
			triggered = self.do_prepare_link_data
		)

		self.prepare_tdata_act = QAction("&Prepare Text Data", self,
			triggered = self.do_prepare_text_data
		)

		self.check_circos_act = QAction("&Check Circos Dependencies", self,
			triggered = self.do_circos_dependency_check
		)

		self.new_circos_act = QAction(QIcon(':/icons/new.svg'), "&Create Circos Plot", self,
			triggered = self.do_create_circos_plot
		)
		self.new_circos_act.setIconVisibleInMenu(False)

		self.add_track_act = QAction(QIcon(':/icons/track.svg'), "&Add Circos Track", self,
			triggered = self.do_add_circos_track
		)
		self.add_track_act.setIconVisibleInMenu(False)

		self.update_circos_act = QAction(QIcon(':/icons/refresh.svg'), "&Update Circos Plot", self,
			triggered = self.do_update_circos_plot
		)
		self.update_circos_act.setIconVisibleInMenu(False)

		self.new_snail_act = QAction(QIcon(':/icons/spiral.svg'), "&Create Snail Plot", self,
			triggered = self.do_create_snail_plot
		)
		self.new_snail_act.setIconVisibleInMenu(False)

		self.update_snail_act = QAction("&Update Snail Plot", self,
			triggered = self.do_update_snail_plot
		)

		self.update_plot_act = QAction(QIcon(':/icons/refresh.svg'), "&Update Plot", self,
			triggered = self.do_update_plot
		)

		self.about_act = QAction("&About", self,
			triggered = self.go_to_about,
		)

		self.doc_act = QAction("&Documentation", self,
			triggered = self.go_to_document
		)

		self.cite_act = QAction(QIcon(':/icons/citation.svg'), "&Citation", self,
			triggered = self.go_to_citation
		)
		self.cite_act.setIconVisibleInMenu(False)

		self.issue_act = QAction("&Report Issues", self,
			triggered = self.go_to_issues
		)

		self.update_act = QAction("&Check Updates", self,
			triggered = self.go_to_update
		)



	def create_menus(self):
		self.file_menu = self.menuBar().addMenu("&File")
		self.file_menu.addAction(self.open_project_act)
		self.file_menu.addAction(self.save_project_act)
		self.file_menu.addAction(self.saveas_project_act)
		self.file_menu.addSeparator()
		self.file_menu.addAction(self.close_project_act)
		self.file_menu.addSeparator()
		self.import_menu = self.file_menu.addMenu("&Import Data")
		self.import_menu.addAction(self.import_genome_act)
		self.import_menu.addAction(self.import_annot_act)
		self.import_menu.addAction(self.import_gbands_act)
		self.import_menu.addAction(self.import_variant_act)
		self.import_menu.addAction(self.import_region_act)
		self.import_menu.addAction(self.import_collinearity_act)
		self.import_menu.addSeparator()
		self.import_menu.addAction(self.import_kdata_act)
		self.import_menu.addAction(self.import_band_act)
		self.import_menu.addAction(self.import_pdata_act)
		self.import_menu.addAction(self.import_link_act)
		self.import_menu.addAction(self.import_loci_act)
		self.import_menu.addAction(self.import_text_act)
		self.import_menu.addSeparator()
		self.file_menu.addAction(self.export_image_act)

		self.file_menu.addSeparator()
		self.file_menu.addAction(self.quit_act)

		self.edit_menu = self.menuBar().addMenu("&Edit")
		self.edit_menu.addAction(self.zoom_in_act)
		self.edit_menu.addAction(self.zoom_out_act)

		self.kcolor_menu = self.edit_menu.addMenu("&Karyotype Color")
		self.kcolor_menu.addAction(self.kcolor_default_act)
		self.kcolor_menu.addAction(self.kcolor_random_act)
		self.kcolor_menu.addAction(self.kcolor_pure_act)


		self.view_menu = self.menuBar().addMenu("&View")
		self.view_menu.addAction(self.toolbar_act)
		self.view_menu.addAction(self.data_dock_act)
		self.view_menu.addAction(self.plot_dock_act)
		self.view_menu.addAction(self.param_dock_act)

		self.tool_menu = self.menuBar().addMenu("&Tools")
		self.prepare_menu = self.tool_menu.addMenu("&Prepare Data")
		self.prepare_menu.addAction(self.prepare_kdata_act)
		self.prepare_menu.addAction(self.prepare_band_act)
		self.prepare_menu.addAction(self.prepare_gc_act)
		self.prepare_menu.addAction(self.prepare_skew_act)
		self.prepare_menu.addAction(self.prepare_pdata_act)
		self.prepare_menu.addAction(self.prepare_ldata_act)
		self.prepare_menu.addAction(self.prepare_tdata_act)

		self.plot_menu = self.menuBar().addMenu("&Plot")
		self.circos_menu = self.plot_menu.addMenu("&Circos Plot")
		self.circos_menu.addAction(self.new_circos_act)
		self.circos_menu.addSeparator()
		self.circos_menu.addAction(self.add_track_act)
		self.circos_menu.addSeparator()
		self.circos_menu.addAction(self.update_circos_act)

		self.snail_menu = self.plot_menu.addMenu("&Snail Plot")
		self.snail_menu.addAction(self.new_snail_act)
		self.snail_menu.addSeparator()
		self.snail_menu.addAction(self.update_snail_act)

		self.tool_menu.addSeparator()
		self.tool_menu.addAction(self.check_circos_act)

		self.help_menu = self.menuBar().addMenu("&Help")
		self.help_menu.addAction(self.about_act)
		self.help_menu.addAction(self.cite_act)
		self.help_menu.addAction(self.doc_act)
		self.help_menu.addAction(self.issue_act)
		self.help_menu.addAction(self.update_act)


	def create_toolbar(self):
		self.tool_bar = self.addToolBar('Show Tool Bar')
		self.tool_bar.setMovable(False)
		self.tool_bar.setFloatable(False)
		self.tool_bar.setIconSize(QSize(24, 24))
		self.tool_bar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
		
		self.toolbar_act = self.tool_bar.toggleViewAction()
		
		#self.tool_bar.addSeparator()

		self.tool_bar.addAction(self.new_circos_act)
		self.tool_bar.addAction(self.add_track_act)
		self.tool_bar.addSeparator()

		self.tool_bar.addAction(self.new_snail_act)
		self.tool_bar.addSeparator()
		
		self.tool_bar.addAction(self.zoom_in_act)
		self.tool_bar.addAction(self.zoom_out_act)
		self.tool_bar.addAction(self.export_image_act)
		self.tool_bar.addSeparator()

		self.tool_bar.addAction(self.cite_act)
		self.tool_bar.addSeparator()

		self.tool_bar.addAction(self.update_plot_act)

		self.tool_bar.addWidget(CirchartSpacerWidget(self))
		self.wait_spinner = CirchartSpinnerWidget(self)
		self.wait_action = self.tool_bar.addWidget(self.wait_spinner)

	def create_statusbar(self):
		self.status_bar = self.statusBar()

	def create_sidebar(self):
		self.data_dock = QDockWidget("Data", self)
		self.data_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
		self.addDockWidget(Qt.LeftDockWidgetArea, self.data_dock)
		self.data_dock_act = self.data_dock.toggleViewAction()
		self.data_dock_act.setText("Show Data Panel")
		self.data_dock.setWidget(self.data_tree)

		self.plot_dock = QDockWidget("Plot", self)
		self.plot_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
		self.addDockWidget(Qt.LeftDockWidgetArea, self.plot_dock)
		self.plot_dock_act = self.plot_dock.toggleViewAction()
		self.plot_dock_act.setText("Show Plot Panel")
		self.plot_dock.setWidget(self.plot_tree)


		self.param_dock = QDockWidget("Paramter", self)
		self.param_dock.layout().setContentsMargins(0, 0, 0, 0)
		self.param_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
		self.addDockWidget(Qt.RightDockWidgetArea, self.param_dock)
		self.param_dock_act = self.param_dock.toggleViewAction()
		self.param_dock_act.setText("Show Paramter Panel")

		self.param_stack = QStackedWidget(self)
		self.param_dock.setWidget(self.param_stack)


		#self.collapse = QCollapsible("Advanced settings")
		#self.collapse.addWidget(QLabel("test for me"))
		#for i in range(10):
		#	self.collapse.addWidget(QPushButton("button {}".format(i)))

		#self.sidebar.setWidget(self.collapse)

	def create_plot_panels(self):
		self.circos_panel = CirchartCircosParameterManager(self)
		self.plot_tree.plot_removed.connect(self.circos_panel.clear_params)
		self.snail_panel = CirchartSnailParameterManager(self)
		self.plot_tree.plot_removed.connect(self.snail_panel.clear_params)

		self.param_stack.addWidget(self.circos_panel)
		self.param_stack.addWidget(self.snail_panel)


	def do_open_project(self, pfile=None):
		if not pfile:
			if self.project_file:
				ret = QMessageBox.question(self, "Confirmation",
					"A project file is already opened. Would you like to open a new project file?"
				)

				if ret == QMessageBox.No:
					return

			if SqlBase.has_data():
				ret = QMessageBox.question(self, "Confirmation",
					"Would you like to save previous results before opening new project file?"
				)

				if ret == QMessageBox.Yes:
					self.do_saveas_project()

			pfile, _ = QFileDialog.getOpenFileName(self, filter="Circhart Project File (*.circ)")

		if not pfile:
			return

		self.project_file = pfile
		SqlBase.reconnect(pfile)
		self.data_tree.update_tree()
		self.plot_tree.update_tree()
		self.set_window_title(pfile)

	def do_close_project(self):
		pass

	def do_save_project(self):
		if self.project_file is None:
			sfile, _ = QFileDialog.getSaveFileName(self, filter="Circhart Project File (*.circ)")

			if not sfile:
				return

			self.project_file = sfile
			self.set_window_title(sfile)
			worker = CirchartProjectSaveWorker({'sfile': sfile})
			worker.signals.success.connect(lambda: SqlBase.reconnect(sfile))
			self.submit_new_worker(worker)

		else:
			SqlBase.save()

	def do_saveas_project(self):
		sfile, _ = QFileDialog.getSaveFileName(self, filter="Circhart Project File (*.circ)")

		if not sfile:
			return

		worker = CirchartProjectSaveWorker({'sfile': sfile})
		self.submit_new_worker(worker)

	def do_import_data(self):
		file, _ = QFileDialog.getOpenFileName(self, "Select Data File")
		tag = CirchartSelectDataTagDialog.select(self, file)
		name = os.path.basename(file)

		if self.data_tree.has_data(name):
			return QMessageBox.critical(self, "Import Failed",
				"A data named {} already exists".format(name))

		if tag:
			self.data_tree.add_data(name, tag, 'path', file)

	def do_import_genome_file(self):
		gfile, _ = QFileDialog.getOpenFileName(self, "Select Genome File",
			filter = (
				"Fasta file (*.fa *.fas *.fna *.fasta "
				"*.fa.gz *.fas.gz *.fna.gz *.fasta.gz);;"
				"All files (*.*)"
			)
		)

		if not gfile:
			return

		worker = CirchartImportGenomeWorker({'path': gfile})
		worker.signals.success.connect(self.data_tree.update_tree)
		self.submit_new_worker(worker)

	def submit_new_worker(self, worker):
		if self.wait_spinner.running:
			return QMessageBox.warning(self, "Warning", "A task is already running")

		worker.signals.error.connect(self.show_error_message)
		worker.signals.warning.connect(self.show_warning_message)
		worker.signals.started.connect(self.wait_spinner.start)
		worker.signals.finished.connect(self.wait_spinner.stop)
		worker.signals.toggle.connect(self.wait_action.setVisible)
		QThreadPool.globalInstance().start(worker)

	def do_import_genome_annotation(self):
		afile, _ = QFileDialog.getOpenFileName(self, "Select Genome Annotation File",
			filter = (
				"GXF file (*.gff *.gtf *.gff3 *.gff.gz *.gtf.gz *.gff3.gz);;"
				"All files (*.*)"
			)
		)

		if not afile:
			return

		worker = CirchartImportAnnotationWorker({'path': afile})
		worker.signals.success.connect(self.data_tree.update_tree)
		self.submit_new_worker(worker)

	def do_import_genome_bands(self):
		bfile, _ = QFileDialog.getOpenFileName(self, "Select Genome Bands File",
			filter = (
				"Band file (*.tsv *.txt);;"
				"All files (*.*)"
			)
		)

		if not bfile:
			return

		worker = CirchartImportBandsWorker({'path': bfile})
		worker.signals.success.connect(self.data_tree.update_tree)
		self.submit_new_worker(worker)

	def do_import_genome_variations(self):
		vfile, _ = QFileDialog.getOpenFileName(self, "Select Genome Variations File",
			filter = (
				"Variation file (*.vcf *.vcf.gz);;"
				"All files (*.*)"
			)
		)

		if not vfile:
			return

		worker = CirchartImportVariationsWorker({'path': vfile})
		worker.signals.success.connect(self.data_tree.update_tree)
		self.submit_new_worker(worker)

	def do_import_genome_regions(self):
		rfile, _ = QFileDialog.getOpenFileName(self, "Select Genome Regions File",
			filter = (
				"Region file (*.bed *.bed.gz *.txt *.tsv);;"
				"All files (*.*)"
			)
		)

		if not rfile:
			return

		worker = CirchartImportRegionsWorker({'path': rfile})
		worker.signals.success.connect(self.data_tree.update_tree)
		self.submit_new_worker(worker)

	def do_import_mcscanx_collinearity(self):
		cfile, _ = QFileDialog.getOpenFileName(self, "Select MCSCANX Collinearity File",
			filter = (
				"Collinearity file (*.collinearity);;"
				"All files (*.*)"
			)
		)

		if not cfile:
			return

		worker = CirchartImportCollinearityWorker({'path': cfile})
		worker.signals.success.connect(self.data_tree.update_tree)
		self.submit_new_worker(worker)

	def do_import_bed_file(self):
		pass

	def import_plot_data(self, dtype, column):
		dfile, _ = QFileDialog.getOpenFileName(self, "Select Data File",
			filter = (
				"Data file (*.tsv *.csv *.txt);;"
				"All files (*.*)"
			)
		)

		if not dfile:
			return

		dformat = dfile.split('.')[-1].lower()

		params = {
			'path': dfile,
			'format': dformat,
			'type': dtype,
			'column': column
		}

		worker = CirchartImportDataWorker(params)
		worker.signals.success.connect(self.data_tree.update_tree)
		self.submit_new_worker(worker)

	def do_import_karyotype_data(self):
		self.import_plot_data('karyotype', 7)

	def do_import_band_data(self):
		self.import_plot_data('banddata', 7)

	def do_import_plot_data(self):
		self.import_plot_data('plotdata', 4)

	def do_import_link_data(self):
		self.import_plot_data('linkdata', 6)

	def do_import_loci_data(self):
		self.import_plot_data('locidata', 3)

	def do_import_text_data(self):
		self.import_plot_data('textdata', 4)

	def do_export_image(self):
		ifile, ext = QFileDialog.getSaveFileName(self,
			filter = (
				"PNG file (*.png);;"
				"SVG file (*.svg);;"
				"PDF file (*.pdf);;"
				"JPG file (*.jpg);;"
				"TIFF file (*.tif)"
			)
		)

		if not ifile:
			return

		iformat = ext.split()[0].lower()
		self.plot_view.save_plot(ifile, iformat)

	def do_zoom_in(self):
		self.plot_view.scale(1.15, 1.15)

	def do_zoom_out(self):
		self.plot_view.scale(1.0/1.15, 1.0/1.15)

	def do_set_karyotype_default_color(self):
		if self.stack_widget.currentIndex() != 1:
			return

		self.data_table.update_karyotype_color('default')

	def do_set_karyotype_random_color(self):
		if self.stack_widget.currentIndex() != 1:
			return

		self.data_table.update_karyotype_color('random')

	def do_set_karyotype_pure_color(self):
		if self.stack_widget.currentIndex() != 1:
			return

		color = QColorDialog.getColor(parent=self)

		if not color.isValid():
			return

		self.data_table.update_karyotype_color('single', color)

	def do_prepare_karyotype_data(self):
		CirchartKaryotypePrepareDialog.prepare(self)

	def do_prepare_band_data(self):
		params = CirchartBandPrepareDialog.prepare(self)

		if params:
			worker = CirchartBandPrepareWorker(params)
			worker.signals.success.connect(self.data_tree.update_tree)
			self.submit_new_worker(worker)

	def do_prepare_gccontent_data(self):
		params = CirchartGCContentPrepareDialog.prepare(self)

		if params:
			worker = CirchartGCContentPrepareWorker(params)
			worker.signals.success.connect(self.data_tree.update_tree)
			self.submit_new_worker(worker)

	def do_prepare_gcskew_data(self):
		params = CirchartGCSkewPrepareDialog.prepare(self)

		if params:
			worker = CirchartGCSkewPrepareWorker(params)
			worker.signals.success.connect(self.data_tree.update_tree)
			self.submit_new_worker(worker)

	def do_prepare_density_data(self):
		params = CirchartDensityPrepareDialog.prepare(self)

		if params:
			worker = CirchartDensityPrepareWorker(params)
			worker.signals.success.connect(self.data_tree.update_tree)
			self.submit_new_worker(worker)

	def do_prepare_link_data(self):
		params = CirchartLinkPrepareDialog.prepare(self)

		if params:
			worker = CirchartLinkPrepareWorker(params)
			worker.signals.success.connect(self.data_tree.update_tree)
			self.submit_new_worker(worker)

	def do_prepare_text_data(self):
		params = CirchartTextPrepareDialog.prepare(self)

		if params:
			worker = CirchartTextPrepareWorker(params)
			worker.signals.success.connect(self.data_tree.update_tree)
			self.submit_new_worker(worker)

	def do_circos_dependency_check(self):
		dlg = CirchartCircosDependencyDialog(self)
		dlg.exec()

	def draw_circos_plot(self, params):
		worker = CirchartCircosPlotWorker(params)
		worker.signals.success.connect(self.plot_tree.update_tree)
		worker.signals.result.connect(self.show_svg_plot)
		self.submit_new_worker(worker)

	def draw_snail_plot(self, params):
		worker = CirchartSnailPlotWorker(params)
		worker.signals.success.connect(self.plot_tree.update_tree)
		worker.signals.result.connect(self.show_svg_plot)
		self.submit_new_worker(worker)

	def do_create_circos_plot(self):
		params = CirchartCreateCircosPlotDialog.create_plot(self)

		if params:
			params['plot_id'] = SqlControl.add_plot(params['plot_name'], 'circos')
			plot_id = params['plot_id']
			params = {'general': {'global': params}}
			params = self.circos_panel.new_circos_plot(params)
			self.draw_circos_plot(params)
			self.show_plot_params('circos', plot_id)

	def do_add_circos_track(self):
		self.circos_panel.add_plot_track()

	def do_update_circos_plot(self):
		params = self.circos_panel.get_params()
		self.draw_circos_plot(params)

	def do_create_snail_plot(self):
		params = CirchartCreateSnailPlotDialog.create_plot(self)

		if params:
			plot_name = params['plot_name']
			params['plot_id'] = SqlControl.add_plot(plot_name, 'snail')
			plot_id = params['plot_id']
			params = {'general': {'global': params}}
			params = self.snail_panel.new_snail_plot(params)
			self.draw_snail_plot(params)
			self.show_plot_params('snail', plot_id)

	def do_update_snail_plot(self):
		params = self.snail_panel.get_params()
		self.draw_snail_plot(params)

	def do_update_plot(self):
		widget = self.param_stack.currentWidget()

		if widget.plot_id == 0:
			return

		if self.param_stack.currentIndex() == 0:
			self.do_update_circos_plot()

		else:
			self.do_update_snail_plot()

	def go_to_about(self):
		QMessageBox.about(self, "About", APP_DESCRIPTION)

	def go_to_citation(self):
		QMessageBox.information(self, "Citation", APP_CITATION)

	def go_to_issues(self):
		QDesktopServices.openUrl(QUrl(APP_ISSUE_URL))

	def go_to_document(self):
		QDesktopServices.openUrl(QUrl(APP_DOCUMENT_URL))

	def go_to_update(self):
		QDesktopServices.openUrl(QUrl(APP_UPDATE_URL))

	@Slot(str)
	def show_error_message(self, error):
		QMessageBox.critical(self, "Error", error)

	@Slot(str)
	def show_warning_message(self, warns):
		QMessageBox.warning(self, "Warning", warns)

	def show_data_table(self):
		if self.stack_widget.currentIndex() != 1:
			self.stack_widget.setCurrentIndex(1)

	def show_plot_view(self):
		if self.stack_widget.currentIndex() != 0:
			self.stack_widget.setCurrentIndex(0)

	def show_svg_plot(self, plot_id):
		self.show_plot_view()
		self.plot_view.show_plot(plot_id)

	def show_plot_image(self, ptype, pid):
		worker = CirchartSvgRenderWorker({'plotid': pid})
		worker.signals.result.connect(self.plot_view.change_render)
		self.submit_new_worker(worker)

		#self.plot_view.show_plot(pid)

	def show_plot_params(self, ptype, pid):
		if ptype == 'snail':
			if self.param_stack.currentIndex() != 1:
				self.param_stack.setCurrentIndex(1)

			self.snail_panel.change_plot(pid)

		elif ptype == 'circos':
			if self.param_stack.currentIndex() != 0:
				self.param_stack.setCurrentIndex(0)
			
			self.circos_panel.change_plot(pid)

