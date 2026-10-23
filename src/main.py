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

	fonts = QDirIterator(
		str(CIRCOS_PATH / 'fonts'),
		QDir.Files | QDir.NoDotAndDotDot,
		QDirIterator.Subdirectories
	)

	while fonts.hasNext():
		fonts.next()
		font = fonts.filePath()

		if font.endswith('.otf'):
			QFontDatabase.addApplicationFont(font)

	args = app.arguments()
	if len(args) > 1:
		if os.path.isfile(args[1]):
			win.do_open_project(args[1])

	sys.exit(app.exec())
