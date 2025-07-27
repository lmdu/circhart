import re

import yattag
from superqt import *
from qt_parameters import *

from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *

__all__ = [
	'CirchartCircosParameter',
	'CirchartCircosConfiger',
	'CirchartCircosParameterManager'
]

class CirchartParameterMixin:
	_default = 0

	def __init__(self, key, parent=None):
		super().__init__(parent)
		self.key = key

		self._init_widget()

	def _init_widget(self):
		pass

	def set_min(self, value):
		self.setMinimum(value)

	def set_max(self, value):
		self.setMaximum(value)

	def set_step(self, value):
		self.setSingleStep(value)

	def set_decimals(self, value):
		self.setDecimals(value)

	def get_value(self):
		return self.value()

	def set_value(self, value):
		self.setValue(value)

	def set_default(self, default):
		self._default = default
		self.set_value(default)

	def reset_default(self):
		self.set_value(self._default)

	def get_param(self):
		return {self.key: self.get_value()}

class CirchartHiddenParameter(CirchartParameterMixin, QWidget):
	_value = None

	def set_value(self, value):
		self._value = value

	def get_value(self):
		return self._value

class CirchartIntegerParameter(CirchartParameterMixin, QSpinBox):
	pass

class CirchartFloatParameter(CirchartParameterMixin, QDoubleSpinBox):
	pass

class CirchartStringParameter(CirchartParameterMixin, QLineEdit):
	def get_value(self):
		return self.text()

	def set_value(self, value):
		self.setText(value)

class CirchartColorParameter(CirchartParameterMixin, QPushButton):
	def _init_widget(self):
		self.setFocusPolicy(Qt.NoFocus)
		self.clicked.connect(self._on_pick_color)
		self.setMaximumWidth(self.sizeHint().height())

	def _on_pick_color(self):
		color = QColorDialog.getColor(self.get_color())

		if color.isValid():
			self.set_color(color)

	def get_color(self):
		return self.palette().color()

	def set_color(self, color):
		self.setPalette(QPalette(color))

	def set_value(self, value):
		r, g, b = value.split(',')
		color = QColor(int(r), int(g), int(b))
		self.set_color(color)

	def get_value(self, value):
		color = self.get_color()
		rgb = [str(color.red()), str(color.green()), str(color.blue())]
		return ','.join(rgb)

class CirchartParameterAccordion(QWidget):
	def __init__(self, key, parent=None):
		super().__init__(parent)
		self.key = key

		self.box = QWidget(self)
		self.box.setVisible(True)

		self.header = QToolButton(self)
		self.header.toggled.connect(self.on_checked)
		self.header.toggled.connect(self.box.setVisible)
		self.expand_icon = QIcon('icons/down.svg')
		self.collapse_icon = QIcon('icons/right.svg')
		self.header.setIcon(self.collapse_icon)
		self.header.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

		self.set_layout()

		self.set_title(self.key.replace('_', ' ').title())

	def set_title(self, text):
		self.header.setText(text)

	def set_layout(self):
		main_layout = QVBoxLayout()
		main_layout.setContentsMargins(0, 0, 0, 0)
		main_layout.addWidget(self.header)
		main_layout.addWidget(self.box)

		self.form_layout = QFormLayout()
		self.box.setLayout(self.form_layout)

		self.setLayout(main_layout)

	def on_checked(self, checked):
		if checked:
			self.header.setIcon(self.expand_icon)
		else:
			self.header.setIcon(self.collapse_icon)

	def add_parameter(self, param, label=None):
		if label is None:
			label = param.key.replace('_', ' ').title()

		self.form_layout.addRow(label, param)

class CirchartParameterManager(QScrollArea):
	def __init__(self, parent=None):
		super().__init__(parent)

		self.setFrameStyle(QFrame.NoFrame)
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.setWidgetResizable(True)

		self.main_widget = QWidget(self)
		self.main_layout = QVBoxLayout()
		self.main_layout.setContentsMargins(0, 0, 2, 0)
		self.main_widget.setLayout(self.main_layout)
		self.setWidget(self.main_widget)

	def sizeHint(self):
		return QSize(200, 0)

	def add_widget(self, param):
		self.main_layout.addWidget(param)

class CirchartCircosParameterManager(CirchartParameterManager):
	def create_name_widget(self, name):
		label = QLabel(name, self)
		self.add_widget(label)

	def create_plotid_param(self, value):
		param = CirchartHiddenParameter('plotid', self)
		param.set_value(value)
		self.add_widget(param)

	def create_karyotype_param(self, value):
		param = CirchartHiddenParameter('karyotype', self)
		param.set_value(value)
		self.add_widget(param)

	def create_ideogram_form(self):
		form = CirchartParameterAccordion('ideogram', self)

		param = CirchartFloatParameter('spacing')
		param.set_decimals(5)
		param.set_default(0.005)
		form.add_parameter(param)

		param = CirchartFloatParameter('radius')
		param.set_decimals(5)
		param.set_default(0.95)
		form.add_parameter(param)

		param = CirchartIntegerParameter('thickness')
		param.set_min(0)
		param.set_max(200)
		param.set_default(30)
		form.add_parameter(param)

		#param = SwitchParameter('fill')
		#param.set_default('yes')
		#form.add_parameter(param)

		param = CirchartIntegerParameter('stroke_thickness')
		param.set_min(0)
		param.set_max(20)
		param.set_default(1)
		form.add_parameter(param)

		param = CirchartColorParameter('stroke_color')
		param.set_default("0,0,0")
		form.add_parameter(param)

		self.add_widget(form)


	def new_circos_plot(self, param):
		self.create_name_widget(param['plot_name'])
		self.create_plotid_param(param['plot_id'])
		self.create_karyotype_param(param['karyotype'])
		self.create_ideogram_form()







class HiddenParameter(ParameterWidget):
	def __init__(self, name):
		super().__init__(name)
		self.set_label(None)
		self.hide()

class SingleColorParameter(ParameterWidget):
	def _init_ui(self):
		self.button = QPushButton()


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

	def create_plotid_param(self, value):
		param = HiddenParameter('plotid')
		param.set_value(value)
		self.add_parameter(param)

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

		param = FloatParameter('radius')
		param.set_default(0.95)
		form.add_parameter(param)

		param = IntParameter('thickness')
		param.set_default(30)
		form.add_parameter(param)

		param = SwitchParameter('fill')
		param.set_default('yes')
		form.add_parameter(param)

		param = IntParameter('stroke_thickness')
		param.set_default(1)
		form.add_parameter(param)

		param = ColorParameter('stroke_color')
		param.set_color_min(0)
		param.set_color_max(255)
		param.set_decimals(0)
		param.set_default(QColor(0, 0,0 ))
		form.add_parameter(param)


	def new_circos_plot(self, param):
		self.clear()
		self.create_name_widget(param['plot_name'])
		self.create_plotid_param(param['plot_id'])
		self.create_karyotype_param(param['karyotype'])
		self.create_ideogram_form()
		return self.values()

class CirchartCircosConfiger(yattag.SimpleDoc):
	def __init__(self, params):
		super().__init__(stag_end='>')

		self.params = params
		self.parse()

	def option(self, name, value, unit=''):
		line = "{} = {}{}".format(name, value, unit)
		self.asis(line)
		self.nl()

	def include(self, confile):
		self.stag('include', confile)
		#self.nl()

	def parse(self):
		tag = self.tag
		option = self.option
		include = self.include

		#karyotype
		kfiles = ['karyotype{}.txt'.format(i) \
			for i in self.params['karyotype']]
		option('karyotype', ','.join(kfiles))

		#ideogram
		ps = self.params['ideogram']
		with tag('ideogram'):
			for k, v in ps.items():
				if k == 'spacing':
					with tag('spacing'):
						option('default', v, 'r')

				elif k == 'radius':
					option(k, v, 'r')

				elif k == 'thickness':
					option(k, v, 'p')

				else:
					option(k, v)

		with tag('image'):
			include('image')

		include('colors_fonts_patterns')
		include('housekeeping')

	def save_to_file(self, file):
		content = yattag.indent(self.getvalue(),
			indentation = ' ',
			newline = '\n',
			indent_text = True
		)

		content = re.sub(r'\<include (.*)\>', r'<<include etc/\1.conf>>', content)

		with open(file, 'w') as fw:
			fw.write(content)

class CirchartSnailParameter(ParameterEditor):
	def __init__(self, parent=None):
		super().__init__(parent)





