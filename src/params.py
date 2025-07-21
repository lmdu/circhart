from superqt import *
from qt_parameters import *

from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *

__all__ = [
	'CirchartCircosParameter',
]

class SwitchParameter(ParameterWidget):
	def _init_ui(self):
		self.switch = QToggleSwitch()
		self.switch.toggled.connect(super().set_value)
		self._layout.addWidget(self.switch)
		self._layout.addStretch()
		self.setFocusProxy(self.switch)

	def value(self):
		return 'yes' if super().value() else 'no'

	def set_value(self, value):
		value = True if value == 'yes' else False
		super().set_value(value)
		self.switch.blockSignals(True)
		self.switch.setChecked(value)
		self.switch.blockSignals(False)

class CirchartCircosParameter(ParameterEditor):
	def __init__(self, parent=None):
		super().__init__(parent)

		self.create_ideogram_form()

	def create_ideogram_form(self):
		form = ParameterForm('ideogram')
		box = self.add_form(form)
		box.set_title("Ideogram")
		box.set_box_style(CollapsibleBox.Style.BUTTON)
		box.set_collapsed(True)

		param = SwitchParameter('show')
		form.add_parameter(param)

		param = FloatParameter('spacing')
		form.add_parameter(param)

		print(self.values())








