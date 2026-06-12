import sys
from PySide6.QtGui import *
from PySide6.QtCore import * 
from PySide6.QtWidgets import * 

class Window(QMainWindow):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("Python")

		list_widget = QListWidget(self)
		list_widget.setDragEnabled(True)
		list_widget.setAcceptDrops(True)
		list_widget.viewport().setAcceptDrops(True)
		list_widget.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
		list_widget.setDefaultDropAction(Qt.DropAction.MoveAction)

		self.setCentralWidget(list_widget)

		list_widget.addItems(['A', 'B', 'C', 'D'])

		for i in range(list_widget.count()):
			item = list_widget.item(i)

			item.setFlags(item.flags() | Qt.ItemIsUserCheckable)

			item.setCheckState(Qt.Unchecked)

		self.show()


App = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(App.exec())
