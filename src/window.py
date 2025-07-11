import sys

from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *

#from superqt import QCollapsible

from config import *
from dialogs import *
from widgets import *

__all__ = [
	'CirchartApplication',
	'CirchartMainWindow',
]

class CirchartApplication(QApplication):
	osx_open_with = Signal(str)

	def __init__(self, argv):
		super().__init__(argv)
		self.load_style()
		#self.setStyle(QStyleFactory.create('windowsvista'))

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

		self.setWindowTitle("Circhart v{}".format(CIRCHART_VERSION))

		self.create_actions()
		self.create_menus()
		self.create_toolbar()
		self.create_statusbar()
		self.create_sidebar()

		self.plot_view = QGraphicsView(self)
		self.setCentralWidget(self.plot_view)
		self.resize(QSize(800, 600))
		self.show()

	def create_actions(self):
		self.open_act = QAction("&Open Project...", self,
			shortcut = QKeySequence.Open,
			triggered = self.do_open_project
		)

		self.quit_act = QAction("&Exit", self,
			shortcut = QKeySequence.Quit,
			triggered = self.close
		)

		self.circos_act = QAction("&Check Circos Dependencies", self,
			triggered = self.do_circos_dependency_check
		)

	def create_menus(self):
		self.file_menu = self.menuBar().addMenu("&File")
		self.file_menu.addAction(self.open_act)
		self.file_menu.addSeparator()
		self.file_menu.addAction(self.quit_act)

		self.edit_menu = self.menuBar().addMenu("&Edit")

		self.tool_menu = self.menuBar().addMenu("&Tools")
		self.tool_menu.addAction(self.circos_act)


		self.help_menu = self.menuBar().addMenu("&Help")


	def create_toolbar(self):
		self.tool_bar = self.addToolBar('main')
		self.tool_bar.addAction(self.open_act)

	def create_statusbar(self):
		self.status_bar = self.statusBar()

	def create_sidebar(self):
		self.sidebar = QDockWidget("", self)
		self.sidebar.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
		self.addDockWidget(Qt.RightDockWidgetArea, self.sidebar)

		#self.collapse = QCollapsible("Advanced settings")
		#self.collapse.addWidget(QLabel("test for me"))
		#for i in range(10):
		#	self.collapse.addWidget(QPushButton("button {}".format(i)))

		#self.sidebar.setWidget(self.collapse)



	def do_open_project(self):
		pass

	def do_circos_dependency_check(self):
		dlg = CirchartCircosDependencyDialog(self)
		dlg.exec()