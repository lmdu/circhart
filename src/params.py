from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *

from utils import *
from config import *
from backend import *
from dialogs import *

__all__ = [
	'CirchartCircosParameterManager',
	'CirchartSnailParameterManager',
]

#from pyside6 examples
class FlowLayout(QLayout):
	def __init__(self, parent=None):
		super().__init__(parent)

		#if parent is not None:
		self.setContentsMargins(QMargins(0, 0, 0, 0))

		self._item_list = []

	def __del__(self):
		item = self.takeAt(0)
		while item:
			item = self.takeAt(0)

	def addItem(self, item):
		self._item_list.append(item)

	def count(self):
		return len(self._item_list)

	def itemAt(self, index):
		if 0 <= index < len(self._item_list):
			return self._item_list[index]

		return None

	def takeAt(self, index):
		if 0 <= index < len(self._item_list):
			return self._item_list.pop(index)

		return None

	def expandingDirections(self):
		return Qt.Orientation(0)

	def hasHeightForWidth(self):
		return True

	def heightForWidth(self, width):
		height = self._do_layout(QRect(0, 0, width, 0), True)
		return height

	def setGeometry(self, rect):
		super().setGeometry(rect)
		self._do_layout(rect, False)

	def sizeHint(self):
		return self.minimumSize()

	def minimumSize(self):
		size = QSize()

		for item in self._item_list:
			size = size.expandedTo(item.minimumSize())

		size += QSize(2 * self.contentsMargins().top(), 2 * self.contentsMargins().top())
		return size

	def _do_layout(self, rect, test_only):
		x = rect.x()
		y = rect.y()
		line_height = 0
		spacing = self.spacing()

		for item in self._item_list:
			style = item.widget().style()
			layout_spacing_x = style.layoutSpacing(
				QSizePolicy.ControlType.PushButton, QSizePolicy.ControlType.PushButton,
				Qt.Orientation.Horizontal
			)
			layout_spacing_y = style.layoutSpacing(
				QSizePolicy.ControlType.PushButton, QSizePolicy.ControlType.PushButton,
				Qt.Orientation.Vertical
			)
			space_x = spacing + layout_spacing_x
			space_y = spacing + layout_spacing_y
			next_x = x + item.sizeHint().width() + space_x
			if next_x - space_x > rect.right() and line_height > 0:
				x = rect.x()
				y = y + line_height + space_y
				next_x = x + item.sizeHint().width() + space_x
				line_height = 0

			if not test_only:
				item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

			x = next_x
			line_height = max(line_height, item.sizeHint().height())

		return y + line_height - rect.y()


class CirchartParameterMixin:
	_default = None

	def __init__(self, key, parent=None):
		super().__init__(parent)
		self.key = key

		self._init_widget()
		self._set_layout()

	def _init_widget(self):
		pass

	def _set_layout(self):
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

	def set_tooltip(self, tip):
		self.setToolTip(tip)

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

class CirchartTitleParameter(CirchartReadonlyParameter):
	def get_param(self):
		return {}

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
		index = self.findData(value)

		if index >= 0:
			self.setCurrentIndex(index)

	def set_data(self, data):
		if isinstance(data, list):
			for item in data:
				self.addItem(item, item)

		else:
			for row in SqlControl.get_datas_by_type(data):
				self.addItem(row.name, row.id)


class CirchartBoolParameter(CirchartParameterMixin, QCheckBox):
	def _init_widget(self):
		#self.setFixedSize(60, 30)
		self.stateChanged.connect(self._on_state_changed)
		self._handle_position = 0
		self._halo_radius = 0

		self.set_animations()

	def set_animations(self):
		self.handle_animation = QPropertyAnimation(self, b"handle_position", self)
		self.handle_animation.setEasingCurve(QEasingCurve.InOutCubic)
		self.handle_animation.setDuration(200)

		self.halo_animation = QPropertyAnimation(self, b"halo_radius", self)
		self.halo_animation.setDuration(350)
		self.halo_animation.setStartValue(4)
		self.halo_animation.setEndValue(8)

		self.animation_group = QSequentialAnimationGroup()
		self.animation_group.addAnimation(self.handle_animation)
		self.animation_group.addAnimation(self.halo_animation)

	def sizeHint(self):
		return QSize(50, 20)

	def hitButton(self, pos):
		return self.contentsRect().contains(pos)

	def _on_state_changed(self, checked):
		self.animation_group.stop()

		if checked:
			self.handle_animation.setEndValue(1)
		else:
			self.handle_animation.setEndValue(0)

		self.animation_group.start()

	def paintEvent(self, event):
		painter = QPainter(self)
		painter.setRenderHint(QPainter.Antialiasing)

		if self.isChecked():
			bar_color = QColor("#4caf50")
			halo_color = QColor("#ADDBAF")
		else:
			bar_color = QColor("#cccccc")
			halo_color = QColor("#f2f2f2")

		bar_rect = self.contentsRect()
		bar_radius = bar_rect.height() / 2
		handle_radius = bar_radius - 4

		painter.setPen(Qt.NoPen)
		painter.setBrush(bar_color)
		painter.drawRoundedRect(bar_rect, bar_radius, bar_radius)
		
		handle_xpos = bar_rect.x() + bar_radius + (bar_rect.width() - 2*bar_radius) * self._handle_position

		if self.halo_animation.state() == QPropertyAnimation.Running:
			painter.setBrush(halo_color)
			painter.drawEllipse(QPointF(handle_xpos, bar_rect.center().y()+1), self._halo_radius, self._halo_radius)
		
		font = self.font()
		font.setBold(True)
		font.setPointSize(8)
		painter.setPen(Qt.white)
		painter.setFont(font)

		if self.isChecked():
			text_rect = QRect(5, 0, bar_rect.width()-5, bar_rect.height())
			painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, "YES")
		else:
			text_rect = QRect(0, 0, bar_rect.width()-5, bar_rect.height())
			painter.drawText(text_rect, Qt.AlignRight | Qt.AlignVCenter, "NO")

		painter.setPen(Qt.NoPen)
		painter.setBrush(Qt.white)
		painter.drawEllipse(
			QPointF(handle_xpos, bar_rect.center().y()+1),
			handle_radius, handle_radius
		)

		painter.end()

	@Property(float)
	def handle_position(self):
		return self._handle_position

	@handle_position.setter
	def handle_position(self, pos):
		self._handle_position = pos
		self.update()

	@Property(float)
	def halo_radius(self):
		return self._halo_radius

	@halo_radius.setter
	def halo_radius(self, pos):
		self._halo_radius = pos
		self.update()

	def get_value(self):
		return 'yes' if self.isChecked() else 'no'

	def set_value(self, value):
		value = True if value == 'yes' else False
		self.setChecked(value)

class CirchartColorParameter(CirchartParameterMixin, QPushButton):
	_color = "255,255,255"

	def _init_widget(self):
		self.setFixedSize(QSize(18, 18))
		self.setFocusPolicy(Qt.NoFocus)
		self.clicked.connect(self._on_pick_color)
		self.setMaximumWidth(self.sizeHint().height())

	def _on_pick_color(self):
		color = CirchartCircosColorSelectDialog.get_color([self.get_color()])

		if color:
			self._color = color
			self.set_color()

	def get_color(self):
		#r, g, b = self._color.split(',')
		#color = QColor(int(r), int(g), int(b))
		#return color
		return self._color

	def set_color(self):
		if self._color.count(',') > 2:
			self.setStyleSheet("background-color:rgba({});".format(self._color))
		else:
			self.setStyleSheet("background-color:rgb({});".format(self._color))

	def set_value(self, value):
		self._color = value
		self.set_color()

	def get_value(self):
		return self._color

class CirchartColorsParameter(CirchartParameterMixin, QWidget):
	_colors = []

	def _init_widget(self):
		self.main_layout = QGridLayout()
		self.main_layout.setContentsMargins(0, 0, 0, 0)
		self.main_layout.setHorizontalSpacing(1)
		#self.main_layout.setVerticalSpacing(5)
		self.setLayout(self.main_layout)
		self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
		self.max_column =  int(self.width() / 16)
		self.show_colors()

	def sizeHint(self):
		return QSize(100, 0)

	def show_colors(self):
		while self.main_layout.count():
			item = self.main_layout.takeAt(0)

			if item.widget():
				item.widget().deleteLater()
 
		row = 0
		col = 0

		for c in self._colors:
			self.add_widget(row, col, c)

			col += 1

			if col >= self.max_column:
				col = 0
				row += 1

		self.add_button(row, col)

	def add_widget(self, row, col, color):
		cw = QPushButton(self)
		cw.setFixedSize(16, 16)
		cw.clicked.connect(self._on_color_clicked)
		cw.setStyleSheet("background-color:rgb({});border: 1px solid black;border-radius:none;".format(color))
		cw.setContextMenuPolicy(Qt.CustomContextMenu)
		cw.customContextMenuRequested.connect(self._on_right_menu)
		cw.setProperty('cindex', row*self.max_column+col)
		self.main_layout.addWidget(cw, row, col)

	def add_button(self, row, col):
		btn = QPushButton(self)
		btn.setFixedSize(16, 16)
		btn.setIcon(QIcon('icons/color.svg'))
		btn.setStyleSheet("border: 1px solid black;border-radius:none;")
		btn.clicked.connect(self._on_add_color)
		self.main_layout.addWidget(btn, row, col)

	def _on_add_color(self, color):
		colors = CirchartCircosColorSelectDialog.get_color(parent=self, multiple=True)

		if colors:
			for color in colors:
				self._colors.append(color)

			self.show_colors()

	def delete_color(self, cindex):
		self._colors.pop(cindex)
		self.show_colors()

	def delete_all_colors(self):
		self._colors = []
		self.show_colors()

	def _on_color_clicked(self):
		btn = self.sender()
		cidx = btn.property('cindex')
		old_color = self._colors[cidx]
		new_color = CirchartCircosColorSelectDialog.get_color([old_color])
		
		if new_color:
			self._colors[cidx] = new_color
			btn.setStyleSheet("background-color:rgb({});border: 1px solid black;border-radius:none;".format(new_color))

	def _on_right_menu(self, pos):
		cindex = self.sender().property('cindex')
		menu = QMenu(self)
		del_act = menu.addAction("Delete")
		del_act.triggered.connect(lambda: self.delete_color(cindex))
		all_act = menu.addAction("Delete All")
		all_act.triggered.connect(self.delete_all_colors)

		menu.exec(self.sender().mapToGlobal(pos))

	def set_value(self, value):
		self._colors = value
		self.show_colors()

	def get_value(self):
		return self._colors

class CirchartGroupParameter(CirchartParameterMixin, QWidget):
	def _init_widget(self):
		self.check_box = QCheckBox(self.key.replace('_', ' ').title(), self)
		self.content_box = QGroupBox(self)
		self.content_box.setVisible(False)
		self.check_box.toggled.connect(self.content_box.setVisible)
		self.set_layout()

	def set_tooltip(self, tip):
		self.check_box.setToolTip(tip)

	def set_layout(self):
		self.main_layout = QFormLayout()
		self.main_layout.setVerticalSpacing(5)
		self.main_layout.setRowWrapPolicy(QFormLayout.DontWrapRows)
		self.main_layout.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)
		self.main_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
		self.main_layout.setLabelAlignment(Qt.AlignLeft)

		#self.main_layout.setContentsMargins(5, 5, 5, 5)
		self.content_box.setLayout(self.main_layout)

		layout = QVBoxLayout()
		layout.setSpacing(3)
		layout.setContentsMargins(0, 0, 0, 0)
		layout.addWidget(self.check_box)
		layout.addWidget(self.content_box)
		self.setLayout(layout)

	def add_subparam(self, widget, label=None):
		if label:
			self.main_layout.addRow(label, widget)
		else:
			self.main_layout.addRow(widget)

	def get_value(self):
		return 'yes' if self.check_box.isChecked() else 'no'

	def set_value(self, value):
		value = True if value == 'yes' else False
		self.check_box.setChecked(value)

class CirchartRuleWidget(QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)

		self._init_widget()
		self._set_layout()

	def _init_widget(self):
		pass

	def _set_layout(self):
		self.main_layout = QHBoxLayout()
		self.main_layout.setSpacing(5)
		self.main_layout.setContentsMargins(0, 0, 0, 0)
		self.setLayout(self.main_layout)

class CirchartRuleValueWidget(CirchartRuleWidget):
	_number = True
	_unit = False

	def _init_widget(self):
		self.sign_widget = QComboBox(self)

		if self._number:
			self.sign_widget.addItems(['=', '>', '>=', '<', '<='])
		else:
			self.sign_widget.addItems(['='])

		self.val_widget = QLineEdit(self)

		if self._unit:
			self.unit_widget = QComboBox(self)
			self.unit_widget.addItems(['bp', 'kb', 'mb', 'gb'])

	def _set_layout(self):
		super()._set_layout()

		self.main_layout.addWidget(self.sign_widget)
		self.main_layout.addWidget(self.val_widget, 1)

		if self._unit:
			self.main_layout.addWidget(self.unit_widget)

class CirchartRuleTextWidget(CirchartRuleValueWidget):
	_number = False

class CirchartRuleSizeWidget(CirchartRuleValueWidget):
	_number = True
	_unit = True

class CirchartRuleChromWidget(CirchartRuleWidget):
	_count = 1

	def _init_widget(self):
		self.chr1_widget = QComboBox(self)

		if self._count > 1:
			self.chr2_widget = QComboBox(self)

	def _set_layout(self):
		super()._set_layout()

		self.main_layout.addWidget(self.chr1_widget, 1)

		if self._count > 1:
			self.main_layout.addWidget(QLabel('-', self))
			self.main_layout.addWidget(self.chr2_widget, 1)

	def set_data(self, chroms):
		self.chr1_widget.addItems(chroms)

		if self._count > 1:
			self.chr2_widget.addItems(chroms)

class CirchartRuleChromsWidget(CirchartRuleChromWidget):
	_count = 2

class CirchartRulePositionWidget(CirchartRuleWidget):
	def _init_widget(self):
		self.chr_widget = QComboBox(self)
		self.start_widget = QLineEdit(self)
		self.end_widget = QLineEdit(self)
		self.unit_widget = QComboBox(self)
		self.unit_widget.addItems(['bp', 'kb', 'mb', 'gb'])

	def _set_layout(self):
		super()._set_layout()

		self.main_layout.addWidget(self.chr_widget)
		self.main_layout.addWidget(QLabel(':', self))
		self.main_layout.addWidget(self.start_widget, 1)
		self.main_layout.addWidget(QLabel('-', self))
		self.main_layout.addWidget(self.end_widget, 1)
		self.main_layout.addWidget(self.unit_widget)

	def set_data(self, chroms):
		self.chr_widget.addItems(chroms)

class CirchartRuleFieldWidget(CirchartRuleWidget):
	def _init_widget(self):
		self.field_widget = QComboBox(self)
		self.field_widget.currentIndexChanged.connect(self._on_field_changed)
		self.rule_widget = QWidget(self)

	def _set_layout(self):
		super()._set_layout()

		self.main_layout.addWidget(self.field_widget)
		self.main_layout.addWidget(self.rule_widget, 1)

	def set_data(self, fields):
		names = []
		datas = []
		for f in fields:
			names.append(f['name'])
			datas.append(f['type'])

		self.field_widget.addItems(names)

		for i, d in enumerate(datas):
			self.field_widget.setItemData(i, d)

	def _on_field_changed(self, index):
		ftype = self.field_widget.itemData(index)

		match ftype:
			case 'number':
				w = CirchartRuleValueWidget(self)

			case 'text':
				w = CirchartRuleTextWidget(self)

			case 'size':
				w = CirchartRuleSizeWidget(self)

			case 'chrom':
				w = CirchartRuleChromWidget(self)

			case 'chroms':
				w = CirchartRuleChromsWidget(self)

			case 'position':
				w = CirchartRulePositionWidget(self)

			case _:
				w = QWidget(self)

		self.main_layout.replaceWidget(self.rule_widget, w)
		self.rule_widget.deleteLater()
		self.rule_widget = w

class CirchartRuleStyleWidget(CirchartRuleWidget):
	def _init_widget(self):
		self.style_widget = QComboBox(self)
		self.style_widget.currentTextChanged.connect(self._on_style_changed)
		self.value_widget = QWidget(self)

	def _set_layout(self):
		super()._set_layout()

		self.main_layout.addWidget(self.style_widget)
		self.main_layout.addWidget(self.value_widget)

	def set_data(self, attrs):
		self.attrs = attrs
		self.style_widget.addItems(list(attrs.keys()))

	def _on_style_changed(self, attr):
		p = self.attrs[attr]

		match p.type:
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

			case 'colors':
				w = CirchartColorsParameter(p.name, self)

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
					w.set_tooltip(p.tooltip)

		self.main_layout.replaceWidget(self.value_widget, w)
		self.value_widget.deleteLater()
		self.value_widget = w


class CirchartConditionParameter(CirchartParameterMixin, QWidget):
	def _init_widget(self):
		self.tests = []

		self.add_btn = QPushButton(self)
		self.add_btn.setIconSize(QSize(16, 16))
		self.add_btn.setFixedSize(QSize(20, 20))
		self.add_btn.setIcon(QIcon('icons/addrule.svg'))
		self.add_btn.clicked.connect(self.add_condition)

		self.del_btn = QPushButton(self)
		self.del_btn.setIconSize(QSize(16, 16))
		self.del_btn.setFixedSize(QSize(20, 20))
		self.del_btn.setIcon(QIcon('icons/delrule.svg'))
		self.del_btn.clicked.connect(self.remove_condition)

	def _set_layout(self):
		sub_layout = QHBoxLayout()
		sub_layout.setSpacing(5)
		sub_layout.setContentsMargins(0, 0, 0, 0)
		sub_layout.addWidget(QLabel("<b>Conditions:</b>", self))
		sub_layout.addStretch()
		sub_layout.addWidget(self.add_btn)
		sub_layout.addWidget(self.del_btn)

		self.main_layout = QVBoxLayout()
		self.main_layout.setSpacing(5)
		self.main_layout.setContentsMargins(0, 0, 0, 0)
		self.main_layout.addLayout(sub_layout)
		self.setLayout(self.main_layout)
		#self.add_condition()

	def set_tests(self, tests):
		self.tests = tests

	def add_condition(self):
		field_widget = CirchartRuleFieldWidget(self)
		field_widget.set_data(self.tests)
		self.main_layout.addWidget(field_widget)

	def remove_condition(self):
		count = self.main_layout.count()

		if count > 1:
			item = self.main_layout.itemAt(count-1)
			widget = item.widget()
			self.main_layout.removeItem(item)

			if widget:
				widget.deleteLater()

class CirchartStyleParameter(CirchartParameterMixin, QWidget):
	def _init_widget(self):
		self.attrs = {}

		self.add_btn = QPushButton(self)
		self.add_btn.setIconSize(QSize(16, 16))
		self.add_btn.setFixedSize(QSize(20, 20))
		self.add_btn.setIcon(QIcon('icons/addrule.svg'))
		self.add_btn.clicked.connect(self.add_style)

		self.del_btn = QPushButton(self)
		self.del_btn.setIconSize(QSize(16, 16))
		self.del_btn.setFixedSize(QSize(20, 20))
		self.del_btn.setIcon(QIcon('icons/delrule.svg'))
		self.del_btn.clicked.connect(self.remove_style)

	def _set_layout(self):
		sub_layout = QHBoxLayout()
		sub_layout.setSpacing(5)
		sub_layout.setContentsMargins(0, 0, 0, 0)
		sub_layout.addWidget(QLabel("<b>Styles:</b>", self))
		sub_layout.addStretch()
		sub_layout.addWidget(self.add_btn)
		sub_layout.addWidget(self.del_btn)

		self.main_layout = QVBoxLayout()
		self.main_layout.setSpacing(5)
		self.main_layout.setContentsMargins(0, 0, 0, 0)
		self.main_layout.addLayout(sub_layout)
		self.setLayout(self.main_layout)
		#self.add_style()

	def set_attrs(self, attrs):
		self.attrs = attrs

	def add_style(self):
		style_widget = CirchartRuleStyleWidget(self)
		style_widget.set_data(self.attrs)
		self.main_layout.addWidget(style_widget)

	def remove_style(self):
		count = self.main_layout.count()

		if count > 1:
			item = self.main_layout.itemAt(count-1)
			widget = item.widget()
			self.main_layout.removeItem(item)

			if widget:
				widget.deleteLater()

class CirchartEmptyWidget(QFrame):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setVisible(False)

class CirchartAccordionHeader(QFrame):
	closed = Signal()
	collapsed = Signal(bool)

	def __init__(self, parent=None, closable=True):
		super().__init__(parent)
		self.closable = closable

		self.expand_icon = QIcon('icons/down.svg')
		self.collapse_icon = QIcon('icons/right.svg')

		self.title_btn = QPushButton(self)
		self.title_btn.setCheckable(True)
		self.title_btn.setIcon(self.collapse_icon)
		self.title_btn.clicked.connect(self._on_collapsed)
	
		if closable:
			self.close_btn = QPushButton(self)
			self.close_btn.setIcon(QIcon('icons/close.svg'))
			self.close_btn.setIconSize(QSize(12, 12))
			self.close_btn.setFixedSize(32, 16)
			self.close_btn.clicked.connect(self._on_closed)

		self.set_layout()

	def set_layout(self):
		layout = QHBoxLayout()
		layout.setSpacing(0)
		layout.setContentsMargins(0, 0, 0, 0)
		layout.addWidget(self.title_btn, 1)

		if self.closable:
			layout.addWidget(self.close_btn)
			layout.setAlignment(self.close_btn, Qt.AlignRight)

		self.setLayout(layout)

	def set_text(self, text):
		self.title_btn.setText(text)

	def _on_closed(self):
		self.closed.emit()

	def _on_collapsed(self, checked):
		if checked:
			self.title_btn.setIcon(self.expand_icon)
		else:
			self.title_btn.setIcon(self.collapse_icon)

		self.collapsed.emit(checked)

class CirchartParameterAccordion(QWidget):
	_visible = True
	_closable = True

	def __init__(self, key, parent=None):
		super().__init__(parent)
		self.key = key
		self.setVisible(self._visible)

		self.box = QTabWidget(self)
		self.box.setVisible(False)
		self.box.setTabBarAutoHide(True)
		self.box.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
		self.header = CirchartAccordionHeader(self, self._closable)
		self.header.collapsed.connect(self.box.setVisible)
		self.header.collapsed.connect(self._on_collapsed)
		self.header.closed.connect(self._on_closed)

		self.set_title(self.key.replace('_', ' ').title())

		self._set_animation()
		self._set_layout()
		self._init_panels()

	def _init_panels(self):
		pass

	def _set_animation(self):
		self.animation = QPropertyAnimation(self.box, b"geometry")
		self.animation.setEasingCurve(QEasingCurve.OutCubic)
		self.animation.setDuration(300)
	
	def _on_collapsed(self, checked):
		self.animation.stop()

		x = self.box.x()
		y = self.box.y()
		w = self.box.width()

		if checked:
			#self.animation.setStartValue(0)
			#self.animation.setEndValue(self.box.sizeHint().height())
			srect = QRect(x, y, w, 0)
			self.animation.setStartValue(srect)
			erect = QRect(x, y, w, self.box.sizeHint().height())
			self.animation.setEndValue(erect)
		else:
			#self.animation.setStartValue(self.box.height())
			#self.animation.setEndValue(0)
			srect = QRect(x, y, w, self.box.height())
			self.animation.setStartValue(srect)
			erect = QRect(x, y, w, 0)
			self.animation.setEndValue(erect)

		self.animation.start()

	def _on_closed(self):
		self.animation.setEndValue(0)
		self.animation.start()
		self.deleteLater()

	def _set_layout(self):
		main_layout = QVBoxLayout()
		main_layout.setSpacing(0)
		main_layout.setContentsMargins(0, 0, 0, 0)
		main_layout.addWidget(self.header)
		main_layout.addWidget(self.box)
		self.setLayout(main_layout)

	def add_panel(self, panel, icon=None , tip=None):
		if icon:
			idx = self.box.addTab(panel, QIcon(icon), '')

		else:
			idx = self.box.addTab(panel, '')


		if tip:
			self.box.setTabToolTip(idx, tip)

	def set_key(self, key):
		self.key = key

	def set_title(self, text):
		self.header.set_text(text)

	def get_panel(self, index):
		return self.box.widget(index)

	def get_params(self):
		params = {}

		for i in range(self.box.count()):
			panel = self.get_panel(i)
			params.update(panel.get_params())

		return {self.key: params}

	def set_params(self, params):
		if self.key not in params:
			return

		ps = params[self.key]

		for i in range(self.box.count()):
			panel = self.get_panel(i)
			panel.set_params(ps)

	def create_panel(self, key, icon=None, tip=None):
		panel = CirchartParameterPanel(key, self)
		self.add_panel(panel, icon, tip)
		return panel

class CirchartParameterPanel(QWidget):
	def __init__(self, key, parent=None):
		super().__init__(parent)
		self.key = key
		self.params = {}

		self._set_layout()
		self._init_widgets()

	def _init_widgets(self):
		pass

	def _set_layout(self):
		self.param_layout = QFormLayout()
		self.param_layout.setContentsMargins(5, 10, 5, 10)
		self.param_layout.setVerticalSpacing(5)
		self.param_layout.setRowWrapPolicy(QFormLayout.DontWrapRows)
		#self.param_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
		self.param_layout.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)
		self.param_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
		self.param_layout.setLabelAlignment(Qt.AlignLeft)
		self.setLayout(self.param_layout)

	def set_key(self, key):
		self.key = key

	def add_param(self, param, label=None, group=False, parent=None):
		if label is None:
			label = param.key.replace('_', ' ').title()

		if group:
			self.param_layout.addRow(param)

		elif parent:
			parent = self.params[parent]
			param.setParent(parent)
			parent.add_subparam(param, label)

		else:
			self.param_layout.addRow(label, param)

		self.params[param.key] = param

	def remove_param(self, key):
		if key in self.params:
			param = self.params.pop(key)
			self.param_layout.removeRow(param)
			param.deleteLater()

	def remove_params(self, keys):
		for key in keys:
			self.remove_param(key)

	def clear_params(self):
		ks = [p.key for p in self.params]
		self.remove_params(ks)

	def create_params(self, params, values={}):
		for param in params:
			p = AttrDict(param)

			if 'disable' in p:
				continue

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

				case 'colors':
					w = CirchartColorsParameter(p.name, self)

				case 'choice':
					w = CirchartChoiceParameter(p.name, self)

				case 'group':
					w = CirchartGroupParameter(p.name, self)

				case 'condition':
					w = CirchartConditionParameter(p.name, self)

				case 'style':
					w = CirchartStyleParameter(p.name, self)

				case 'title':
					w = CirchartTitleParameter(p.name, self)

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
						w.set_tooltip(p.tooltip)

					case 'mutex':
						parent = self.params[p.mutex]
						w.setDisabled(parent.isChecked())
						parent.toggled.connect(w.setDisabled)

			if p.name in values:
				w.set_value(values[p.name])

			elif p.type == 'group':
				self.add_param(w, group=True)

			elif p.type == 'title':
				self.add_param(w, group=True)

			elif 'parent' in p:
				self.add_param(w, parent=p.parent)

			elif 'label' in p:
				if p.label:
					self.add_param(w, p.label)

				else:
					self.add_param(w, group=True)

			else:
				self.add_param(w)

	def get_widget(self, key):
		return self.params[key]

	def get_params(self):
		values = {}

		for k, p in self.params.items():
			if isinstance(p, CirchartParameterMixin):
				values.update(p.get_param())

		return {self.key: values}

	def set_params(self, params):
		ps = params.get(self.key, {})

		for k, v in ps.items():
			if k in self.params:
				self.params[k].set_value(v)

class CirchartGeneralTrack(CirchartParameterAccordion):
	_closable = False
	_visible = False

	def _init_panels(self):
		panel = self.create_panel('general')
		params = CIRCOS_PARAMS['general']
		panel.create_params(params)

class CirchartIdeogramTrack(CirchartParameterAccordion):
	_closable = False

	def _init_panels(self):
		panel = self.create_panel('ideogram')
		params = CIRCOS_PARAMS['ideogram']
		panel.create_params(params)

class CirchartDisplayRule(CirchartParameterAccordion):
	def _init_panels(self):
		pass

class CirchartPlotTrack(CirchartParameterAccordion):
	def _init_panels(self):
		self._create_plot_panel()
		self._create_rule_panel()
		self._create_axes_panel()
		self._create_grid_panel()
		self._create_background_panel()

	def _create_plot_panel(self):
		self.plot_panel = self.create_panel('plot', 'icons/chart.svg', "Plot")
		self.plot_params = CIRCOS_PARAMS['tracks']
		ptypes = [k for k in self.plot_params]

		self.type_param = CirchartChoiceParameter('type', self)
		self.plot_panel.add_param(self.type_param)
		self.type_param.currentTextChanged.connect(self._on_type_changed)
		self.type_param.set_data(ptypes)

	def _create_rule_panel(self):
		self.rule_panel = self.create_panel('rules', 'icons/rule.svg', "Rules")
		self.rule_params = CIRCOS_PARAMS['rules']
		self.type_param.currentIndexChanged.connect(self.rule_panel.clear_params)

		menu = QMenu(self.rule_panel)
		rule_act = QAction("Add Rule", self.rule_panel)
		rule_act.triggered.connect(self.add_rule)
		menu.addAction(rule_act)

		open_menu = lambda x: (menu.move(QCursor().pos()), (menu.show()))
		self.rule_panel.setContextMenuPolicy(Qt.CustomContextMenu)
		self.rule_panel.customContextMenuRequested.connect(open_menu)

	def add_rule(self):
		ptype = self.type_param.get_value()
		plot_params = self.plot_params[ptype]
		rule_params = self.rule_params[ptype]

		tests = rule_params[0]['tests']
		attrs = {'show': AttrDict(name='show', type='bool', default='yes')}

		for p in plot_params:
			p = AttrDict(p)

			if p.name in rule_params[1]['attrs']:
				attrs[p.name] = p

		rule = CirchartDisplayRule('rule0', self.rule_panel)
		panel = rule.create_panel('rules')
		panel.create_params(rule_params)
		param = panel.get_widget('style')
		param.set_attrs(attrs)
		param = panel.get_widget('condition')
		param.set_tests(tests)

		self.rule_panel.add_param(rule, group=True)

	def _create_axes_panel(self):
		panel = self.create_panel('axes', 'icons/axis.svg', "Axes")

	def _create_grid_panel(self):
		panel = self.create_panel('grids', 'icons/grid.svg', "Grid")

	def _create_background_panel(self):
		panel = self.create_panel('backgrounds', 'icons/bg.svg', "Backgrounds")

	def _on_type_changed(self, ptype):
		#self.set_title("Track:{}".format(ptype))
		panel = self.get_panel(0)
		params = self.plot_params[ptype]

		values = {}
		ks = []
		for k, p in panel.params.items():
			if k in ['data', 'r0', 'r1']:
				values[k] = p.get_value()

			if k != 'type':
				ks.append(k)

		panel.remove_params(ks)
		panel.create_params(params, values)



class CirchartParameterManager(QScrollArea):
	def __init__(self, parent=None):
		super().__init__(parent)

		self.setFrameStyle(QFrame.NoFrame)
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.setWidgetResizable(True)

		self.main_widget = CirchartEmptyWidget(self)
		self.main_layout = QVBoxLayout()
		self.main_layout.setSpacing(0)
		self.main_layout.setContentsMargins(0, 0, 0, 0)
		self.main_layout.setAlignment(Qt.AlignTop)
		self.main_widget.setLayout(self.main_layout)
		self.setWidget(self.main_widget)

		self.track_count = 0
		self.plot_id = 0

	def sizeHint(self):
		return QSize(250, 0)

	def add_widget(self, param):
		self.main_layout.addWidget(param)

	def clear_widgets(self):
		for i in range(self.main_layout.count()):
			item = self.main_layout.itemAt(i)

			if item:
				widget = item.widget()

				if widget:
					widget.deleteLater()

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

	def reset_parameters(self, params):
		pass

	def change_plot(self, pid):
		if pid == self.plot_id:
			return

		params = SqlControl.get_params(pid)

		if not params:
			return

		params = str_to_dict(params)

		if not params:
			return

		self.reset_parameters(params)

class CirchartCircosParameterManager(CirchartParameterManager):
	def new_circos_plot(self, params):
		self.plot_id = params['plotid']

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
		return form

	def reset_parameters(self, params):
		self.clear_widgets()
		self.new_circos_plot(params)

		track_id = 0
		for k, v in params.items():
			if k.startswith('track'):
				tid = int(k.replace('track', ''))

				if tid > track_id:
					track_id = tid

				form = self.add_plot_track()
				form.set_key(k)
				form.set_values(v)

		self.track_count = track_id




class CirchartSnailParameterManager(CirchartParameterManager):
	pass




