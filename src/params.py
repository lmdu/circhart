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

class CirchartAccordionHeader(QFrame):
	def __init__(self, parent=None):
		super().__init__(parent)

		self.expand_icon = QIcon('icons/down.svg')
		self.collapse_icon = QIcon('icons/right.svg')
		
		self.title_btn = QPushButton(self)
		self.title_btn.setCheckable(True)
		self.title_btn.setIcon(self.collapse_icon)
		self.title_btn.clicked.connect(self._on_clicked)

		self.close_btn = QPushButton(self)
		self.close_btn.setIcon(QIcon('icons/close.svg'))
		self.close_btn.setIconSize(QSize(12, 12))

		self.toggled = self.title_btn.toggled
		self.closed = self.close_btn.clicked

		self.set_layout()

	def set_layout(self):
		layout = QHBoxLayout()
		layout.setSpacing(0)
		layout.setContentsMargins(0, 0, 0, 0)
		layout.addWidget(self.title_btn, 1)
		layout.addWidget(self.close_btn)
		layout.setAlignment(self.close_btn, Qt.AlignRight)
		self.setLayout(layout)

	def set_text(self, text):
		self.title_btn.setText(text)

	def _on_clicked(self, checked):
		if checked:
			self.title_btn.setIcon(self.expand_icon)
		else:
			self.title_btn.setIcon(self.collapse_icon)

		self.toggled.emit(checked)


class CirchartEmptyWidget(QFrame):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setVisible(False)

class CirchartAccordionContent(CirchartEmptyWidget):
	pass

class CirchartParameterAccordion(QWidget):
	def __init__(self, key, parent=None):
		super().__init__(parent)
		self.key = key

		self.box = CirchartAccordionContent(self)
		self.header = CirchartAccordionHeader(self)

		self.set_animate()
		self.set_layout()
		self.set_title(self.key.replace('_', ' ').title())

		self.header.toggled.connect(self.box.setVisible)
		self.header.toggled.connect(self._on_collapsed)
		self.header.closed.connect(self._on_closed)

		self.params = {}

		self._init_widgets()

	def _init_widgets(self):
		pass

	def set_key(self, key):
		self.key = key

	def set_title(self, text):
		self.header.set_text(text)

	def set_animate(self):
		#self.animation = QPropertyAnimation(self.box, b"minimumHeight", self)
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

	def set_layout(self):
		main_layout = QVBoxLayout()
		main_layout.setSpacing(0)
		main_layout.setContentsMargins(0, 0, 0, 0)
		main_layout.addWidget(self.header)
		main_layout.addWidget(self.box)

		self.form_layout = QFormLayout()
		self.form_layout.setVerticalSpacing(5)
		self.form_layout.setRowWrapPolicy(QFormLayout.DontWrapRows)
		#self.form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
		self.form_layout.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)
		self.form_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
		self.form_layout.setLabelAlignment(Qt.AlignLeft)

		self.box.setLayout(self.form_layout)

		self.setLayout(main_layout)

	def add_parameter(self, param, label=None, group=None):
		if label is None:
			label = param.key.replace('_', ' ').title()

		if group is True:
			self.form_layout.addRow(param)

		elif group:
			parent = self.params[group]
			param.setParent(parent)
			parent.add_subparam(param, label)

		else:
			self.form_layout.addRow(label, param)

		self.params[param.key] = param

	def create_parameters(self, params, values={}):
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

			if p.type == 'group':
				self.add_parameter(w, group=True)

			elif 'group' in p:
				self.add_parameter(w, group=p.group)

			elif 'label' in p:
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

class CirchartDisplayRule(CirchartParameterAccordion):
	def _init_widgets(self):
		pass

class CirchartPlotTrack(CirchartParameterAccordion):
	def _init_widgets(self):
		self.configs = CIRCOS_PARAMS['tracks']
		types = [k for k in self.configs]
		
		self.plot_type = CirchartChoiceParameter('type', self)
		self.add_parameter(self.plot_type)
		self.plot_type.currentTextChanged.connect(self._on_type_changed)
		self.plot_type.set_data(types)


	def _on_type_changed(self, ptype):
		#self.set_title("Track:{}".format(ptype))

		params = self.configs[ptype]

		values = {}
		for k, p in self.params.items():
			if k in ['data', 'r0', 'r1']:
				values[k] = p.get_value()

			if k != 'type':
				try:
					if self.form_layout.indexOf(p) != -1:
						self.form_layout.removeRow(p)
				except:
					pass

		self.params = {'type': self.params['type']}
		self.create_parameters(params, values)

	def contextMenuEvent(self, event):
		menu = QMenu(self)
		rule_act = QAction("Add Rules", self)
		rule_act.triggered.connect(self.add_rules)
		bg_act = QAction("Add Backgrounds", self)
		axes_act = QAction("Add Axes", self)
		grid_act = QAction("Add Grids", self)

		menu.addAction(rule_act)
		menu.addAction(bg_act)
		menu.addAction(axes_act)
		menu.addAction(grid_act)
		menu.exec(self.mapToGlobal(event.pos()))

	def add_rules(self):
		rule_box = CirchartDisplayRule("Rules", self)
		self.form_layout.addRow(rule_box)



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




