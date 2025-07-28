import os
import sys

import qt_parameters as qtp
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *

#from superqt import QCollapsible

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
		style = QFile('style.qss')
		if style.open(QIODevice.OpenModeFlag.ReadOnly | QIODevice.OpenModeFlag.Text):
			stream = QTextStream(style)
			self.setStyleSheet(stream.readAll())


class CirchartMainWindow(QMainWindow):
	def __init__(self):
		super().__init__()

		self.setWindowTitle("{} v{}".format(APP_NAME, APP_VERSION))
		self.setWindowIcon(QIcon('icons/logo.svg'))

		self.plot_view = CirchartGraphicsViewWidget(self)
		self.data_table = CirchartDataTableWidget(self)
		self.data_tree = CirchartDataTreeWidget(self)
		self.data_tree.show_data.connect(self.data_table.change_table)
		self.data_tree.clicked.connect(self.show_data_table)
		self.plot_tree = CirchartPlotTreeWidget(self)


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
		self.resize(QSize(800, 600))
		self.show()

	def create_actions(self):
		self.open_project_act = QAction("&Open Project...", self,
			shortcut = QKeySequence.Open,
			triggered = self.do_open_project
		)

		self.save_project_act = QAction("&Save Project", self,
			triggered = self.do_save_project
		)

		self.saveas_project_act = QAction("&Save Project As...", self,
			triggered = self.do_saveas_project
		)

		self.close_project_act = QAction("&Close Project", self,
			triggered = self.do_close_project
		)

		self.import_genome_act = QAction("&Import Genome File...", self,
			triggered = self.do_import_genome_file
		)

		self.import_annot_act = QAction("&Import Genome Annotation...", self,
			triggered = self.do_import_genome_annot
		)

		self.import_kdata_act = QAction("&Import Karyotype Data...", self,
			triggered = self.do_import_karyotype_data
		)

		self.import_pdata_act = QAction("&Import Plot Data...", self,
			triggered = self.do_import_plot_data
		)

		self.zoom_in_act = QAction(QIcon("icons/zoomin.svg"), "&Zoom In", self,
			triggered = self.do_zoom_in
		)

		self.zoom_out_act = QAction(QIcon("icons/zoomout.svg"), "&Zoom Out", self,
			triggered = self.do_zoom_out
		)



		self.quit_act = QAction("&Exit", self,
			shortcut = QKeySequence.Quit,
			triggered = self.close
		)

		self.prepare_kdata_act = QAction("&Prepare Karyotype Data", self,
			triggered = self.do_prepare_karyotype_data
		)

		self.prepare_pdata_act = QAction("&Prepare Plot Data", self,
			triggered = self.do_prepare_track_data
		)

		self.check_circos_act = QAction("&Check Circos Dependencies", self,
			triggered = self.do_circos_dependency_check
		)

		self.new_circos_act = QAction("&Create Circos Plot", self,
			triggered = self.do_create_circos_plot
		)

		self.add_track_act = QAction("&Add Circos Track", self,
			triggered = self.do_add_circos_track
		)

		self.update_circos_act = QAction("&Update Circos Plot", self,
			triggered = self.do_update_circos_plot
		)

		self.about_act = QAction("&About", self,
			triggered = self.go_to_about,
		)

		self.doc_act = QAction("&Documentation", self,
			triggered = self.go_to_document
		)

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
		self.import_menu.addSeparator()
		self.import_menu.addAction(self.import_kdata_act)
		self.import_menu.addAction(self.import_pdata_act)

		self.file_menu.addSeparator()
		self.file_menu.addAction(self.quit_act)

		self.edit_menu = self.menuBar().addMenu("&Edit")
		self.edit_menu.addAction(self.zoom_in_act)
		self.edit_menu.addAction(self.zoom_out_act)

		self.view_menu = self.menuBar().addMenu("&View")
		self.view_menu.addAction(self.toolbar_act)
		self.view_menu.addAction(self.data_dock_act)
		self.view_menu.addAction(self.plot_dock_act)
		self.view_menu.addAction(self.param_dock_act)

		self.tool_menu = self.menuBar().addMenu("&Tools")
		self.prepare_menu = self.tool_menu.addMenu("&Prepare Data")
		self.prepare_menu.addAction(self.prepare_kdata_act)
		self.prepare_menu.addAction(self.prepare_pdata_act)

		self.plot_menu = self.menuBar().addMenu("&Plot")
		self.circos_menu = self.plot_menu.addMenu("&Circos Plot")
		self.circos_menu.addAction(self.new_circos_act)
		self.circos_menu.addAction(self.add_track_act)
		self.circos_menu.addSeparator()
		self.circos_menu.addAction(self.update_circos_act)

		self.snail_menu = self.plot_menu.addMenu("&Snail Plot")

		self.tool_menu.addSeparator()
		self.tool_menu.addAction(self.check_circos_act)

		self.help_menu = self.menuBar().addMenu("&Help")
		self.help_menu.addAction(self.about_act)
		self.help_menu.addAction(self.doc_act)
		self.help_menu.addAction(self.issue_act)
		self.help_menu.addAction(self.update_act)


	def create_toolbar(self):
		self.tool_bar = self.addToolBar('Show Tool Bar')
		self.tool_bar.setMovable(False)
		self.tool_bar.setFloatable(False)
		self.tool_bar.setIconSize(QSize(20, 20))
		self.tool_bar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
		
		self.toolbar_act = self.tool_bar.toggleViewAction()
		self.tool_bar.addAction(self.zoom_in_act)
		self.tool_bar.addAction(self.zoom_out_act)


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
		#self.snail_panel = qtp.ParameterEditor()

		self.param_stack.addWidget(self.circos_panel)
		#self.param_stack.addWidget(self.snail_panel)



	def do_open_project(self):
		pass

	def do_close_project(self):
		pass

	def do_save_project(self):
		pass

	def do_saveas_project(self):
		pass

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
			filter=(
				"Fasta file (*.fa *.fas *.fna *.fasta "
				"*.fa.gz *.fas.gz *.fna.gz *.fasta.gz);;"
				"All files (*.*)"
			)
		)

		if not gfile:
			return

		worker = CirchartImportGenomeWorker({'fasta': gfile})
		worker.signals.success.connect(self.data_tree.update_tree)
		self.submit_new_worker(worker)

	def submit_new_worker(self, worker):
		if self.wait_spinner.running:
			return QMessageBox.warning(self, "Warning", "A task is already running")

		worker.signals.error.connect(self.show_error_message)
		worker.signals.started.connect(self.wait_spinner.start)
		worker.signals.finished.connect(self.wait_spinner.stop)
		worker.signals.toggle.connect(self.wait_action.setVisible)
		QThreadPool.globalInstance().start(worker)

	def do_import_genome_annot(self):
		pass

	def do_import_karyotype_data(self):
		pass

	def do_import_plot_data(self):
		pass

	def do_zoom_in(self):
		print('zoom in')

	def do_zoom_out(self):
		pass

	def do_prepare_karyotype_data(self):
		CirchartKaryotypePrepareDialog.make_karyotype(self)

	def do_prepare_track_data(self):
		pass

	def do_circos_dependency_check(self):
		dlg = CirchartCircosDependencyDialog(self)
		dlg.exec()

	def draw_circos_plot(self, params):
		worker = CirchartCircosPlotWorker(params)
		worker.signals.success.connect(self.plot_tree.update_tree)
		worker.signals.result.connect(self.show_svg_plot)
		self.submit_new_worker(worker)

	def do_create_circos_plot(self):
		params = CirchartCreateCircosPlotDialog.create_plot(self)

		if params:
			params['plot_id'] = SqlControl.add_plot(params['plot_name'], 'circos')
			params = self.circos_panel.new_circos_plot(params)
			self.draw_circos_plot(params)


	def do_add_circos_track(self):
		pass

	def do_update_circos_plot(self):
		params = self.circos_panel.values()
		self.draw_circos_plot(params)


	def go_to_about(self):
		QMessageBox.about(self, "About", APP_DESCRIPTION)

	def go_to_issues(self):
		QDesktopServices.openUrl(QUrl(APP_ISSUE_URL))

	def go_to_document(self):
		QDesktopServices.openUrl(QUrl(APP_DOCUMENT_URL))

	def go_to_update(self):
		QDesktopServices.openUrl(QUrl(APP_UPDATE_URL))

	@Slot(str)
	def show_error_message(self, error):
		QMessageBox.critical(self, "Error", error)

	def show_data_table(self):
		if self.stack_widget.currentIndex() != 1:
			self.stack_widget.setCurrentIndex(1)

	def show_svg_plot(self, plot_id):
		if self.stack_widget.currentIndex() != 0:
			self.stack_widget.setCurrentIndex(0)

		self.plot_view.show_plot(plot_id)












