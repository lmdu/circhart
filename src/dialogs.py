from pathlib import Path

from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *

from config import *
from widgets import *

__all__ = [
	'CirchartSelectDataTagDialog',
	'CirchartCircosDependencyDialog',
]

class CirchartSelectDataTagDialog(QDialog):
	def __init__(self, parent=None, file=None):
		super().__init__(parent)

		self.tag_select = QComboBox(self)
		self.tag_select.addItems([
			'Genome Fasta File',
			'Karyotype Data',
			'Plot Data'
		])

		self.btn_box = QDialogButtonBox(
			QDialogButtonBox.StandardButton.Cancel |
			QDialogButtonBox.StandardButton.Ok
		)
		self.btn_box.accepted.connect(self.accept)
		self.btn_box.rejected.connect(self.reject)

		layout = QVBoxLayout()
		layout.addWidget(QLabel("Import <b>{}</b> as:".format(file), self))
		layout.addWidget(self.tag_select)
		layout.addWidget(self.btn_box)
		self.setLayout(layout)

	def sizeHint(self):
		return QSize(300, 0)

	def get_tag(self):
		tags = ['genome', 'karyotype', 'plotdata']
		return tags[self.tag_select.currentIndex()]

	@classmethod
	def select(cls, parent, file):
		file = Path(file).name
		dlg = cls(parent, file)

		if dlg.exec() == QDialog.Accepted:
			return dlg.get_tag()

class CirchartCircosDependencyDialog(QDialog):
	def __init__(self, parent=None):
		super().__init__(parent)

		self.setWindowTitle("Circos Perl Dependencies")
		self.resize(QSize(400, 300))

		self.spinner = CirchartSpinnerWidget(self)
		self.updator = QPushButton("Refresh", self)
		self.updator.clicked.connect(self.spinner.start)
		self.tree = QTreeWidget(self)
		self.tree.setHeaderLabels(['Module', 'Version', 'Status'])
		self.tree.setIconSize(QSize(12, 12))
		self.tree.setRootIsDecorated(False)
		self.tree.header().setStretchLastSection(False)
		self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
		self.tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
		self.tree.header().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

		self.create_layout()
		self.create_process()

	def create_layout(self):
		self.layout = QVBoxLayout()
		self.setLayout(self.layout)
		top_layout = QHBoxLayout()
		top_layout.addWidget(self.spinner)
		top_layout.addWidget(CirchartSpacerWidget(self))
		top_layout.addWidget(self.updator)
		self.layout.addLayout(top_layout)
		self.layout.addWidget(self.tree)

	def create_process(self):
		self.process = QProcess(self)
		self.process.setProgram(CIRCOS_COMMAND)
		self.process.setArguments(["-modules"])
		self.updator.clicked.connect(self.process.start)
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



