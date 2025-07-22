from superqt import *
from qt_parameters import *

from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *

__all__ = [
	'CirchartCircosParameter',
]

class HiddenParameter(ParameterWidget):
	def __init__(self, name):
		super().__init__(name)
		self.set_label(None)
		self.hide()

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

	def create_name_widget(self, name):
		label = QLabel(name, self)
		self.add_widget(label)

	def create_karyotype_param(self, value):
		param = HiddenParameter('karyotype')
		param.set_value(value)
		self.add_parameter(param)

	def create_ideogram_form(self):
		form = ParameterForm('ideogram')
		box = self.add_form(form)
		box.set_title("Ideogram")
		box.set_box_style(CollapsibleBox.Style.SIMPLE)
		box.set_collapsed(True)

		param = SwitchParameter('show')
		param.set_value('yes')
		form.add_parameter(param)

		param = FloatParameter('spacing')
		param.set_default(0.005)
		form.add_parameter(param)

	def new_circos_plot(self, param):
		self.clear()
		self.create_name_widget(param['plot_name'])
		self.create_karyotype_param(param['karyotype'])
		self.create_ideogram_form()

		

class CirchartSnailParameter(ParameterEditor):
	def __init__(self, parent=None):
		super().__init__(parent)






