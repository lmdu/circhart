import re

import yattag
from superqt import *

from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *

from utils import *
from config import *
from backend import *

__all__ = [
	'CirchartCircosConfiger',
	'CirchartCircosParameterManager'
]

class CirchartParameterMixin:
	_default = None

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

	def set_range(self, values):
		self.setRange(*values)

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
		if self._default is not None:
			self.set_value(self._default)

	def get_param(self):
		return {self.key: self.get_value()}

class CirchartHiddenParameter(CirchartParameterMixin, QWidget):
	_value = None

	def set_value(self, value):
		self._value = value

	def get_value(self):
		return self._value

	def _init_widget(self):
		self.setVisible(False)

class CirchartReadonlyParameter(CirchartParameterMixin, QLabel):
	def set_value(self, value):
		self.setText(value)

	def get_value(self):
		return self.text()

class CirchartIntegerParameter(CirchartParameterMixin, QSpinBox):
	def _init_widget(self):
		self.adjustSize()
		self.setAlignment(Qt.AlignCenter)

class CirchartFloatParameter(CirchartParameterMixin, QDoubleSpinBox):
	def _init_widget(self):
		self.adjustSize()
		self.setAlignment(Qt.AlignCenter)

class CirchartStringParameter(CirchartParameterMixin, QLineEdit):
	def get_value(self):
		return self.text()

	def set_value(self, value):
		self.setText(value)

class CirchartChoiceParameter(CirchartParameterMixin, QComboBox):
	def get_value(self):
		return self.currentData()

	def set_value(self, value):
		self.setCurrentIndex(self.findText(value))

	def set_data(self, data):
		if isinstance(data, list):
			for item in data:
				self.addItem(item, item)

		else:
			for row in SqlControl.get_datas_by_type(data):
				self.addItem(row.name, row.id)


class CirchartBoolParameter(CirchartParameterMixin, QCheckBox):
	def _init_widget(self):
		self.setFixedSize(60, 30)
		self.stateChanged.connect(self.update)

	def paintEvent(self, event):
		painter = QPainter(self)
		painter.setRenderHint(QPainter.Antialiasing)

		bg_color = QColor("#4CAF50") if self.isChecked() else QColor("#CCCCCC")
		knob_color = QColor("#FFFFFF")
		border_color = QColor("#888888")
		
		rect = self.rect().adjusted(2, 2, -2, -2)
		painter.setPen(QPen(border_color, 1))
		painter.setBrush(bg_color)
		painter.drawRoundedRect(rect, 10, 10)

		knob_radius = 13
		if self.isChecked():
			knob_pos = QPoint(self.width() - knob_radius - 4, self.height() // 2)
		else:
			knob_pos = QPoint(knob_radius + 4, self.height() // 2)
		
		painter.setPen(Qt.NoPen)
		painter.setBrush(knob_color)
		painter.drawEllipse(knob_pos, knob_radius, knob_radius)

		text = "ON" if self.isChecked() else "OFF"
		text_color = QColor("#FFFFFF") if self.isChecked() else QColor("#666666")

		painter.setPen(text_color)
		painter.setFont(self.font())
		text_rect = QRect(0, 0, self.width() - 20, self.height())

		if self.isChecked():
			painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, text)
		else:
			painter.drawText(text_rect, Qt.AlignRight | Qt.AlignVCenter, text)

	def get_value(self):
		return 'yes' if self.isChecked() else 'no'

	def set_value(self, value):
		value = True if value == 'yes' else False
		self.setChecked(value)

class CirchartColorParameter(CirchartParameterMixin, QPushButton):
	_color = "255,255,255"

	def _init_widget(self):
		self.setFocusPolicy(Qt.NoFocus)
		self.clicked.connect(self._on_pick_color)
		self.setMaximumWidth(self.sizeHint().height())

	def _on_pick_color(self):
		color = QColorDialog.getColor(self.get_color())

		if color.isValid():
			r = color.red()
			g = color.green()
			b = color.blue()
			self._color = "{},{},{}".format(r, g, b)
			self.set_color()

	def get_color(self):
		r, g, b = self._color.split(',')
		color = QColor(int(r), int(g), int(b))
		return color

	def set_color(self):
		self.setStyleSheet("background-color:rgb({});".format(self._color))

	def set_value(self, value):
		self._color = value
		self.set_color()

	def get_value(self):
		return self._color

class CirchartAccordionHeader(QPushButton):
	def __init__(self, parent=None):
		super().__init__(parent)

		self.setCheckable(True)
		self.expand_icon = QIcon('icons/down.svg')
		self.collapse_icon = QIcon('icons/right.svg')
		self.setIcon(self.collapse_icon)
		self.toggled.connect(self._on_clicked)

	def _on_clicked(self, checked):
		if checked:
			self.setIcon(self.expand_icon)
		else:
			self.setIcon(self.collapse_icon)

class CirchartEmptyWidget(QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setVisible(False)

class CirchartParameterAccordion(QWidget):
	def __init__(self, key, parent=None):
		super().__init__(parent)
		self.key = key

		self.box = CirchartEmptyWidget(self)
		self.header = CirchartAccordionHeader(self)
		self.header.toggled.connect(self.box.setVisible)

		self.set_layout()
		self.set_title(self.key.replace('_', ' ').title())

		self.params = {}

		self._init_widgets()

	def _init_widgets(self):
		pass

	def set_title(self, text):
		self.header.setText(text)

	def set_layout(self):
		main_layout = QVBoxLayout()
		main_layout.setContentsMargins(0, 0, 0, 0)
		main_layout.addWidget(self.header)
		main_layout.addWidget(self.box)

		self.form_layout = QFormLayout()
		self.form_layout.setVerticalSpacing(3)
		self.form_layout.setRowWrapPolicy(QFormLayout.DontWrapRows)
		#self.form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
		self.form_layout.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)
		self.form_layout.setFormAlignment(Qt.AlignHCenter | Qt.AlignTop)
		self.form_layout.setLabelAlignment(Qt.AlignLeft)

		self.box.setLayout(self.form_layout)

		self.setLayout(main_layout)

	def add_parameter(self, param, label=None):
		if label is None:
			label = param.key.replace('_', ' ').title()

		self.form_layout.addRow(label, param)
		self.params[param.key] = param

	def remove_parameter(self, row):
		item = self.form_layout.itemAt(row)
		widget = item.widget()
		self.params.remove(widget.key)
		self.form_layout.removeRow(row)

	def create_parameters(self, params):
		for param in params:
			p = AttrDict(param)

			match p.type:
				case 'hidden':
					w = CirchartHiddenParameter(p.name, self)

				case 'readonly':
					w = CirchartReadonlyParameter(p.name, self)

				case 'int':
					w = CirchartIntegerParameter(p.name, self)

				case 'float':
					w = CirchartFloatParameter(p.name, self)

				case 'bool':
					w = CirchartBoolParameter(p.name, self)

				case 'str':
					w = CirchartStringParameter(p.name, self)

				case 'color':
					w = CirchartColorParameter(p.name, self)

				case 'choice':
					w = CirchartChoiceParameter(p.name, self)

			for k in p:
				match k:
					case 'range':
						w.set_range(p.range)

					case 'min':
						w.set_min(p.min)

					case 'max':
						w.set_max(p.max)

					case 'step':
						w.set_step(p.step)

					case 'decimal':
						w.set_decimals(p.decimal)

					case 'default':
						w.set_default(p.default)

					case 'source':
						w.set_data(p.source)

					case 'tooltip':
						w.setToolTip(p.tooltip)

			if 'label' in p:
				self.add_parameter(w, p.label)
			else:
				self.add_parameter(w)

	def get_values(self):
		values = {}

		for k, p in self.params.items():
			if isinstance(p, CirchartParameterMixin):
				values.update(p.get_param())

		return {self.key: values}

	def set_values(self, values):
		for k, v in values.items():
			if k in self.params:
				self.params[k].set_value(v)

class CirchartGeneralTrack(CirchartParameterAccordion):
	def _init_widgets(self):
		self.setVisible(False)
		params = CIRCOS_PARAMS['general']
		self.create_parameters(params)

class CirchartIdeogramTrack(CirchartParameterAccordion):
	def _init_widgets(self):
		params = CIRCOS_PARAMS['ideogram']
		self.create_parameters(params)

class CirchartPlotTrack(CirchartParameterAccordion):
	def _init_widgets(self):
		self.configs = CIRCOS_PARAMS['tracks']
		types = [k for k in self.configs]
		
		self.plot_type = CirchartChoiceParameter('type', self)
		self.add_parameter(self.plot_type)
		self.plot_type.currentTextChanged.connect(self._on_type_changed)
		self.plot_type.set_data(types)

	def _on_type_changed(self, ptype):
		params = self.configs[ptype]
		count = self.form_layout.rowCount()

		for i in range(1, count):
			self.remove_parameter(i)

		self.create_parameters(params)

class CirchartParameterManager(QScrollArea):
	def __init__(self, parent=None):
		super().__init__(parent)

		self.setFrameStyle(QFrame.NoFrame)
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.setWidgetResizable(True)

		self.main_widget = CirchartEmptyWidget(self)
		self.main_layout = QVBoxLayout()
		self.main_layout.setContentsMargins(0, 0, 2, 0)
		self.main_layout.setAlignment(Qt.AlignTop)
		self.main_widget.setLayout(self.main_layout)
		self.setWidget(self.main_widget)

		w = CirchartIntegerParameter('dd', self)
		self.main_layout.addWidget(w)

		self.track_count = 0

	def sizeHint(self):
		return QSize(250, 0)

	def add_widget(self, param):
		self.main_layout.addWidget(param)

	def get_values(self):
		values = {}

		for i in range(self.main_layout.count()):
			item = self.main_layout.itemAt(i)
			widget = item.widget()

			if isinstance(widget, CirchartParameterMixin):
				values.update(widget.get_param())

			elif isinstance(widget, CirchartGeneralTrack):
				for _, vals in widget.get_values().items():
					values.update(vals)

			elif isinstance(widget, CirchartParameterAccordion):
				values.update(widget.get_values())

		return values
	
class CirchartCircosParameterManager(CirchartParameterManager):
	def new_circos_plot(self, params):
		form = CirchartGeneralTrack('general')
		form.set_values(params)
		self.add_widget(form)

		form = CirchartIdeogramTrack('ideogram')
		form.set_values(params)
		self.add_widget(form)

		return self.get_values()

	def add_plot_track(self):
		self.track_count += 1
		form = CirchartPlotTrack('track{}'.format(self.track_count), self)
		self.add_widget(form)

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

class CirchartSnailParameter:
	def __init__(self, parent=None):
		super().__init__(parent)





