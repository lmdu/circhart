import os
import sys
import multiprocessing

from PySide6.QtSvg import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *

import resources

from config import *
from window import *


def render_to_svg(widget):
	g = QSvgGenerator()
	g.setFileName('circhart_screen.svg')
	g.setSize(widget.size())
	g.setViewBox(widget.rect())
	g.setTitle('circhart')
	g.setDescription('bypy')

	#p = QPainter()
	#p.begin(g)
	#widget.render(p,
	#	targetOffset=None,
	#	sourceRegion=None,
	#	renderFlags=QWidget.RenderFlag.DrawChildren
	#)
	#p.end()
	widget.render(g)


if __name__ == "__main__":
	multiprocessing.freeze_support()

	if os.name == 'nt':
		import ctypes
		ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)

	QCoreApplication.setOrganizationName(APP_ORG_NAME)
	QCoreApplication.setOrganizationDomain(APP_ORG_DOMAIN)
	QCoreApplication.setApplicationName(APP_NAME)
	QCoreApplication.setApplicationVersion(APP_VERSION)
	QSettings.setDefaultFormat(QSettings.IniFormat)

	app = CirchartApplication(sys.argv)
	win = CirchartMainWindow()
	app.osx_open_with.connect(win.do_open_project)

	args = app.arguments()
	if len(args) > 1:
		if os.path.isfile(args[1]):
			win.do_open_project(args[1])

	render_to_svg(win)

	sys.exit(app.exec())
