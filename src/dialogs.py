from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *

from widgets import *

__all__ = [
	'CirchartCircosDependencyDialog',
]

class CirchartCircosDependencyDialog(QDialog):
	def __init__(self, parent=None):
		super().__init__(parent)

		self.setWindowTitle("Circos Dependencies")

		self.progress = CirchartSpinnerWidget(self)
		self.progress.hide()
		spacer = CirchartSpacerWidget(self)
		self.update_btn = QPushButton("Refresh", self)
		self.package_manager = RNASuitePackageTreeView(self)
		self.update_btn.clicked.connect(self.on_update_status)
		self.status_info = RNASuitePackageInstallMessage(self)
		self.package_manager.error.connect(self.on_error_occurred)
		self.package_manager.message.connect(self.on_update_message)
		self.package_manager.started.connect(self.on_install_started)
		self.package_manager.stopped.connect(self.on_install_stopped)

		self.layout = QVBoxLayout()
		self.setLayout(self.layout)
		top_layout = QHBoxLayout()
		top_layout.addWidget(self.progress)
		top_layout.addWidget(spacer)
		top_layout.addWidget(self.update_btn)
		self.layout.addLayout(top_layout)
		self.layout.addWidget(self.package_manager)
		self.layout.addWidget(self.status_info)

	def closeEvent(self, event):
		if self.package_manager.task_running():
			info = (
				"Are you sure you want to close the package manager?\n"
				"Closing the manager will stop the current package installation"
			)
			btn = QMessageBox.question(self, "Warnning", info)

			if btn == QMessageBox.Yes:
				self.package_manager.stop_task()
				event.accept()
			else:
				event.ignore()
				return

		event.accept()

	@Slot()
	def on_error_occurred(self, error):
		QMessageBox.critical(self, "Error", error)

	@Slot()
	def on_update_message(self, text):
		self.status_info.insertPlainText(text)
		scroll_bar = self.status_info.verticalScrollBar()
		scroll_bar.setValue(scroll_bar.maximum())

	@Slot()
	def on_update_status(self):
		if self.package_manager.task_running():
			return QMessageBox.warning(self, "Warnning", "A package installation is running")

		self.package_manager.update_version()

	@Slot()
	def on_install_started(self):
		self.progress.show()
		self.progress.start()

	@Slot()
	def on_install_stopped(self):
		self.progress.hide()
		self.progress.stop()