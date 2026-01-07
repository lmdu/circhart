# importing libraries
from PySide6.QtWidgets import * 
from PySide6 import QtCore, QtGui
from PySide6.QtGui import * 
from PySide6.QtCore import * 
import sys

# new check-able combo box
class CheckableComboBox(QComboBox):
	
	# constructor
	def __init__(self, parent = None):
		super(CheckableComboBox, self).__init__(parent)

		self.setEditable(True)
		self.lineEdit().setReadOnly(True)

		self.view().pressed.connect(self.handleItemPressed)
		#self.setModel(QStandardItemModel(self))

	def hidePopup(self):
		super().hidePopup()
		self.update_text()

	def update_text(self):
		texts = []
		for i in range(self.model().rowCount()):
			item = self.model().item(i)

			if item.checkState() == Qt.Checked:
				texts.append(item.text())

		text = ",".join(texts)
		self.lineEdit().setText(text)

	# when any item get pressed
	def handleItemPressed(self, index):
		
		# getting the item
		item = self.model().itemFromIndex(index)
		
		# checking if item is checked
		if item.checkState() == Qt.Checked:
			
			# making it unchecked
			item.setCheckState(Qt.Unchecked)
			
		# if not checked
		else:
			# making the item checked
			item.setCheckState(Qt.Checked)

class Window(QMainWindow):

	def __init__(self):
		super().__init__()

		# setting title
		self.setWindowTitle("Python ")

		# setting geometry
		self.setGeometry(100, 100, 600, 400)

		# calling method
		self.UiComponents()

		# showing all the widgets
		self.show()

	# method for widgets
	def UiComponents(self):
		
		# creating a check-able combo box object
		self.combo_box = CheckableComboBox(self)

		# setting geometry of combo box
		self.combo_box.setGeometry(200, 150, 150, 30)

		# geek list
		geek_list = ["Sayian", "Super Sayian",
					 "Super Sayian 2", "Super Sayian B"]

		# adding list of items to combo box
		self.combo_box.addItems(geek_list)


# create pyqt5 app
App = QApplication(sys.argv)

# create the instance of our Window
window = Window()

window.show()

# start the app
sys.exit(App.exec())