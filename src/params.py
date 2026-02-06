from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *

from utils import *
from config import *
from backend import *
from widgets import *
from dialogs import *

__all__ = [
	'CirchartCircosParameterManager',
	'CirchartSnailParameterManager',
	'CirchartDataFilterDialog',
]

#from https://gis.stackexchange.com/questions/350148/qcombobox-multiple-selection-pyqt5
class CirchartCheckableComboBox(QComboBox):
	def __init__(self, parent=None):
		super().__init__(parent)

		self.setEditable(True)
		self.lineEdit().setReadOnly(True)

		self.model().dataChanged.connect(self.update_text)

		self.lineEdit().installEventFilter(self)
		self.close_popup = False

		self.view().viewport().installEventFilter(self)
		self.setMinimumWidth(120)

	def resizeEvent(self, event):
		self.update_text()
		super().resizeEvent(event)

	def eventFilter(self, watched, event):
		if watched == self.lineEdit():
			if event.type() == QEvent.MouseButtonRelease:
				if self.close_popup:
					self.hidePopup()
				
				else:
					self.showPopup()
				
				return True
			
			return False

		if watched == self.view().viewport():
			if event.type() == QEvent.MouseButtonRelease:
				index = self.view().indexAt(event.pos())
				item = self.model().item(index.row())

				if item.checkState() == Qt.Checked:
					item.setCheckState(Qt.Unchecked)
				
				else:
					item.setCheckState(Qt.Checked)
				
				return True
		
		return False

	def showPopup(self):
		super().showPopup()
		self.close_popup = True

	def hidePopup(self):
		super().hidePopup()
		self.startTimer(100)
		self.update_text()

	def timerEvent(self, event):
		self.killTimer(event.timerId())
		self.close_popup = False

	def update_text(self):
		texts = []
		for i in range(self.model().rowCount()):
			item = self.model().item(i)

			if item.checkState() == Qt.Checked:
				texts.append(item.text())

		text = ",".join(texts)
		self.lineEdit().setText(text)

	def get_datas(self):
		res = []
		for i in range(self.model().rowCount()):
			item = self.model().item(i)
			res.append(item.data())

		return res

	def addItem(self, text, data=None):
		item = QStandardItem()
		item.setText(text)
		
		if data is None:
			item.setData(text)
		
		else:
			item.setData(data)
		
		item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
		item.setData(Qt.Unchecked, Qt.CheckStateRole)
		self.model().appendRow(item)

	def addItems(self, texts, datalist=None):
		for i, text in enumerate(texts):
			try:
				data = datalist[i]
			
			except (TypeError, IndexError):
				data = None
			
			self.addItem(text, data)

	def currentData(self):
		res = []
		for i in range(self.model().rowCount()):
			item = self.model().item(i)

			if item.checkState() == Qt.Checked:
				res.append(item.data())
		
		return res

	def setCurrentData(self, datas):
		for i in range(self.model().rowCount()):
			item = self.model().item(i)

			if item.data() in datas:
				item.setData(Qt.Checked, Qt.CheckStateRole)

		self.update_text()

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
		self._default = value
		self.setText(str(value))

	def get_value(self):
		return self._default

	def _init_widget(self):
		self.setWordWrap(True)

class CirchartTitleParameter(CirchartReadonlyParameter):
	def get_param(self):
		return {}

class CirchartAnnulusParameter(CirchartParameterMixin, QWidget):
	def _init_widget(self):
		self.radius0 = QDoubleSpinBox(self)
		self.radius0.setRange(0, 10)
		self.radius0.setDecimals(3)
		self.radius0.setSingleStep(0.01)
		self.radius1 = QDoubleSpinBox(self)
		self.radius1.setRange(0, 10)
		self.radius1.setDecimals(3)
		self.radius1.setSingleStep(0.01)

	def _set_layout(self):
		layout = QHBoxLayout()
		layout.setContentsMargins(0, 0, 0, 0)
		layout.addWidget(self.radius0)
		layout.addWidget(QLabel("to", self))
		layout.addWidget(self.radius1)
		self.setLayout(layout)

	def set_value(self, value):
		self.radius0.setValue(value[0])
		self.radius1.setValue(value[1])

	def get_value(self):
		return (self.radius0.value(), self.radius1.value())

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

			self.dynamic = None

		else:
			for row in SqlControl.get_datas_by_type(data):
				self.addItem(row.name, row.id)

			self.dynamic = data

	def showPopup(self):
		if self.dynamic:
			for row in SqlControl.get_datas_by_type(self.dynamic):
				if self.findData(row.id) < 0:
					self.addItem(row.name, row.id)

		super().showPopup()

class CirchartChoicesParameter(CirchartParameterMixin, CirchartCheckableComboBox):
	def get_value(self):
		return self.currentData()

	def set_value(self, value):
		self.setCurrentData(value)

	def set_data(self, data):
		if isinstance(data, list):
			for item in data:
				self.addItem(item, item)

			self.dynamic = None

		else:
			for row in SqlControl.get_datas_by_type(data):
				self.addItem(row.name, row.id)

			self.dynamic = data

	def showPopup(self):
		datas = self.get_datas()

		if self.dynamic:
			for row in SqlControl.get_datas_by_type(self.dynamic):
				if row.id not in datas:
					self.addItem(row.name, row.id)

		super().showPopup()


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
	def _init_widget(self):
		self._colors = []
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
		btn.setIcon(QIcon(':/icons/color.svg'))
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

class CirchartRadiusParameter(CirchartParameterMixin, QWidget):
	def _init_widget(self):
		self.location = QComboBox(self)
		self.location.addItems(['outer ideogram', 'inside ideogram', 'inner ideogram'])
		self.location.currentIndexChanged.connect(self._on_location_changed)
		self.offset = QSpinBox(self)
		self.offset.setPrefix('+')
		self.offset.setRange(0, 1000)

		self.radius_locations = [
			"dims(ideogram,radius_outer)",
			"(dims(ideogram,radius_outer)+dims(ideogram,radius_inner))/2",
			"dims(ideogram,radius_inner)"
		]

		self.set_layout()

	def set_layout(self):
		main_layout = QVBoxLayout()
		main_layout.addWidget(self.location)
		main_layout.setSpacing(5)
		main_layout.setContentsMargins(0, 0, 0, 0)
		sub_layout = QHBoxLayout()
		sub_layout.setSpacing(5)
		sub_layout.setContentsMargins(0, 0, 0, 0)
		sub_layout.addWidget(QLabel("Offset", self))
		sub_layout.addWidget(self.offset)
		sub_layout.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Preferred, QSizePolicy.Minimum))

		main_layout.addLayout(sub_layout)

		self.setLayout(main_layout)

	def _on_location_changed(self, index):
		if index == 0:
			self.offset.setPrefix('+')
			self.offset.setEnabled(True)
		
		elif index == 1:
			#self.offset.setPrefix('')
			self.offset.setEnabled(False)
		
		elif index == 2:
			self.offset.setPrefix('-')
			self.offset.setEnabled(True)

	def get_value(self):
		index = self.location.currentIndex()
		location = self.radius_locations[index]

		if self.offset.isEnabled():
			offset = self.offset.value()

			if offset:
				sign = self.offset.prefix()
				return "{} {} {}p".format(location, sign, offset)
		
		return location

	def set_value(self, value):
		vals = value.split()

		index = self.radius_locations.index(vals[0])
		self.location.setCurrentIndex(index)

		if len(vals) > 1:
			sign = vals[1]
			offset = int(vals[2].strip('p'))
			self.offset.setPrefix(sign)
			self.offset.setValue(offset)

class CirchartChromsParameter(CirchartParameterMixin, QWidget):
	def _init_widget(self):
		self.chr1_widget = QComboBox(self)
		self.chr2_widget = QComboBox(self)

	def _set_layout(self):
		main_layout = QHBoxLayout()
		main_layout.setContentsMargins(0, 0, 0, 0)
		main_layout.addWidget(self.chr1_widget)
		main_layout.addWidget(QLabel('and', self))
		main_layout.addWidget(self.chr2_widget)
		self.setLayout(main_layout)

	def set_data(self, chroms):
		self.chr1_widget.addItems(chroms)
		self.chr2_widget.addItems(chroms)

	def get_value(self):
		chr1 = self.chr1_widget.currentText()
		chr2 = self.chr2_widget.currentText()

		if chr1 == chr2:
			return chr1
		else:
			return "{} {}".format(chr1, chr2)

	def set_value(self, value):
		vals = value.split()

		if len(vals) > 1:
			self.chr1_widget.setCurrentText(vals[0])
			self.chr2_widget.setCurrentText(vals[1])
		else:
			self.chr1_widget.setCurrentText(vals[0])
			self.chr2_widget.setCurrentText(vals[0])

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

	def get_value(self):
		pass

	def set_value(self, value):
		pass

class CirchartRuleEmptyWidget(CirchartRuleWidget):
	pass

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
			self.unit_widget.setCurrentIndex(2)

	def _set_layout(self):
		super()._set_layout()

		self.main_layout.addWidget(self.sign_widget)
		self.main_layout.addWidget(self.val_widget, 1)

		if self._unit:
			self.main_layout.addWidget(self.unit_widget)

	def get_value(self):
		sign = self.sign_widget.currentText()

		if sign == '=':
			sign = 'eq'

		val = self.val_widget.text().strip()

		if self._unit:
			unit = self.unit_widget.currentText().replace('bp', '')
			ret = "{} {}{}".format(sign, val, unit)
		else:
			ret = "{} {}".format(sign, val)

		return ret

	def set_value(self, value):
		sign, val = value.split()

		if sign == 'eq':
			sign = '='

		if val.endswith(('bp', 'kb', 'mb', 'gb')):
			unit = val[-2:]
			val = val[0:-2]
		elif self._unit:
			unit = 'bp'

		self.sign_widget.setCurrentText(sign)
		self.val_widget.setText(val)

		if self._unit:
			self.unit_widget.setCurrentText(unit)

class CirchartRuleTextWidget(CirchartRuleValueWidget):
	_number = False

class CirchartRuleSizeWidget(CirchartRuleValueWidget):
	_number = True
	_unit = True

class CirchartRuleChromWidget(CirchartRuleWidget):
	_count = 1
	_equal = False

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

	def get_value(self):
		if self._count == 1:
			val = self.chr1_widget.currentText()

			if self._equal:
				return "eq {}".format(val)
			else:
				return val
		else:
			return "{}, {}".fomrat(
				self.chr1_widget.currentText(),
				self.chr2_widget.currentText()
			)

	def set_value(self, value):
		if self._count == 1:
			if self._equal:
				value = value.split()[1]

			self.chr1_widget.setCurrentText(value)

		else:
			chr1, chr2 = value.split(', ')
			self.chr1_widget.setCurrentText(chr1)
			self.chr2_widget.setCurrentText(chr2)

class CirchartRuleChromeWidget(CirchartRuleChromWidget):
	_equal = True

class CirchartRuleChromsWidget(CirchartRuleChromWidget):
	_count = 2

class CirchartRulePositionWidget(CirchartRuleWidget):
	def _init_widget(self):
		self.chr_widget = QComboBox(self)
		self.start_widget = QLineEdit(self)
		self.end_widget = QLineEdit(self)
		self.unit_widget = QComboBox(self)
		self.unit_widget.addItems(['bp', 'kb', 'mb', 'gb'])
		self.unit_widget.setCurrentIndex(2)

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

	def get_value(self):
		chrom = self.chr_widget.currentText()
		start = self.start_widget.text().strip()
		end = self.end_widget.text().strip()
		unit = self.unit_widget.currentText().replace('bp', '')

		return "{}, {}{}, {}{}".format(chrom, start, unit, end, unit)

	def set_value(self, value):
		chrom, start, end = value.split(', ')

		if start.endswith(['kb', 'mb', 'gb']):
			unit = start[-2:]
			start = start[0:-2]
			end = end[0:-2]
		else:
			unit = 'bp'

		self.chr_widget.setCurrentText(chrom)
		self.start_widget.setText(start)
		self.end_widget.setText(end)
		self.unit_widget.setCurrentText(unit)

class CirchartRuleFieldWidget(CirchartRuleWidget):
	def _init_widget(self):
		self.field_widget = QComboBox(self)
		self.field_widget.currentIndexChanged.connect(self._on_field_changed)
		self.rule_widget = QWidget(self)

		self.chroms = []

	def _set_layout(self):
		super()._set_layout()

		self.main_layout.addWidget(self.field_widget)
		self.main_layout.addWidget(self.rule_widget, 1)

	def set_data(self, fields, chroms):
		self.chroms = chroms

		for f in fields:
			self.field_widget.addItem(f.name, f)

	def _on_field_changed(self, index):
		f = self.field_widget.itemData(index)

		match f.type:
			case 'number':
				w = CirchartRuleValueWidget(self)

			case 'text':
				w = CirchartRuleTextWidget(self)

			case 'size':
				w = CirchartRuleSizeWidget(self)

			case 'chrom':
				w = CirchartRuleChromWidget(self)
				w.set_data(self.chroms)

			case 'chrome':
				w = CirchartRuleChromeWidget(self)
				w.set_data(self.chroms)

			case 'chroms':
				w = CirchartRuleChromsWidget(self)
				w.set_data(self.chroms)

			case 'position':
				w = CirchartRulePositionWidget(self)
				w.set_data(self.chroms)

			case _:
				w = CirchartRuleEmptyWidget(self)

		self.main_layout.replaceWidget(self.rule_widget, w)
		self.rule_widget.deleteLater()
		self.rule_widget = w

	def get_value(self):
		field = self.field_widget.currentText()
		rule = self.rule_widget.get_value()

		funcs = {'on', 'from', 'to', 'between', 'fromto', 'tofrom', 'within'}
		noval = {'interchr', 'intrachr', 'rev1', 'rev2', 'inv'}

		if field in funcs:
			return "{}({})".format(field, rule)

		elif field in noval:
			return "var({})".format(field)

		else:
			return "var({}) {}".format(field, rule)

	def set_value(self, value):
		funcs = ('on', 'from', 'to', 'between', 'fromto', 'tofrom', 'within')

		if value.startswith(funcs):
			field, rule = value.split('(')
			rule = rule.strip(')')
		else:
			field, rule = value.split(')')
			field = field.split('(')[1]
			rule = rule.strip()

		self.field_widget.setCurrentText(field)
		self.rule_widget.set_value(rule)

class CirchartRuleStyleWidget(CirchartRuleWidget):
	def _init_widget(self):
		self.style_widget = QComboBox(self)
		self.style_widget.currentIndexChanged.connect(self._on_style_changed)
		self.value_widget = QWidget(self)

	def _set_layout(self):
		super()._set_layout()

		self.main_layout.addWidget(self.style_widget)
		self.main_layout.addWidget(self.value_widget)

		spacer = QSpacerItem(10, 10, QSizePolicy.Expanding, QSizePolicy.Minimum)
		self.main_layout.addSpacerItem(spacer)

	def set_data(self, attrs):
		for a in attrs:
			self.style_widget.addItem(a.name, a)

	def _on_style_changed(self, index):
		p = self.style_widget.itemData(index)

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

	def get_value(self):
		style = self.style_widget.currentText()
		val = self.value_widget.get_value()

		return (style, val)

	def set_value(self, value):
		style, val = value
		self.style_widget.setCurrentText(style)
		self.value_widget.set_value(val)

class CirchartAddDelButton(QPushButton):
	def __init__(self, parent=None, btype='add'):
		super().__init__(parent)
		self.setIconSize(QSize(16, 16))
		self.setFixedSize(QSize(20, 20))

		if btype == 'add':
			self.setIcon(QIcon(':/icons/add.svg'))
		else:
			self.setIcon(QIcon(':/icons/delete.svg'))

class CirchartConditionParameter(CirchartParameterMixin, QWidget):
	def _init_widget(self):
		self.tests = []
		self.chroms = []

		self.add_btn = CirchartAddDelButton(self)
		self.add_btn.clicked.connect(self.add_condition)

		self.del_btn = CirchartAddDelButton(self, 'del')
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

	def set_chroms(self, chroms):
		self.chroms = chroms

	def add_condition(self):
		field_widget = CirchartRuleFieldWidget(self)
		field_widget.set_data(self.tests, self.chroms)
		self.main_layout.addWidget(field_widget)

		return field_widget

	def remove_condition(self):
		count = self.main_layout.count()

		if count > 1:
			item = self.main_layout.itemAt(count-1)
			widget = item.widget()
			self.main_layout.removeItem(item)

			if widget:
				widget.deleteLater()

	def clear_conditions(self):
		count = self.main_layout.count()

		for i in range(count):
			item = self.main_layout.itemAt(i)
			widget = item.widget()

			if widget:
				widget.deleteLater()

	def get_value(self):
		values = []

		count = self.main_layout.count()

		for i in range(count):
			item = self.main_layout.itemAt(i)
			widget = item.widget()

			if widget:
				values.append(widget.get_value())

		return values

	def set_value(self, values):
		self.clear_conditions()

		for value in values:
			widget = self.add_condition()
			widget.set_value(value)

	def get_param(self):
		return {self.key: self.get_value()}


class CirchartStyleParameter(CirchartParameterMixin, QWidget):
	style_changed = Signal()

	def _init_widget(self):
		self.attrs = []

		self.add_btn = CirchartAddDelButton(self)
		self.add_btn.clicked.connect(self.add_style)

		self.del_btn = CirchartAddDelButton(self, 'del')
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
		self.style_changed.emit()
		return style_widget

	def remove_style(self):
		count = self.main_layout.count()

		if count > 1:
			item = self.main_layout.itemAt(count-1)
			widget = item.widget()
			self.main_layout.removeItem(item)

			if widget:
				widget.deleteLater()

			self.style_changed.emit()

	def clear_styles(self):
		count = self.main_layout.count()

		for i in range(count):
			item = self.main_layout.itemAt(i)
			widget = item.widget()

			if widget:
				widget.deleteLater()

		self.style_changed.emit()

	def get_value(self):
		count = self.main_layout.count()

		values = []

		for i in range(count):
			item = self.main_layout.itemAt(i)
			widget = item.widget()

			if widget:
				values.append(widget.get_value())

		return values

	def set_value(self, values):
		self.clear_styles()

		for value in values:
			widget = self.add_style()
			widget.set_value(value)

	def get_param(self):
		return {self.key: self.get_value()}


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

		self.expand_icon = QIcon(':/icons/down.svg')
		self.collapse_icon = QIcon(':/icons/right.svg')

		self.title_btn = QPushButton(self)
		self.title_btn.setCheckable(True)
		self.title_btn.setIcon(self.collapse_icon)
		self.title_btn.clicked.connect(self._on_collapsed)
	
		if closable:
			self.close_btn = QPushButton(self)
			self.close_btn.setIcon(QIcon(':/icons/close.svg'))
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
	#deleted = Signal()

	def __init__(self, key, parent=None, **kwargs):
		super().__init__(parent)
		self.key = key
		self.kwargs = kwargs
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
		#self.deleted.emit()
		self.animation.setEndValue(0)
		self.animation.start()

		#if self.key in self.parent().params:
		#	self.params

		try:
			self.parent().remove_param(self.key)
		except:
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
		self.kcount = 0

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

	def set_kcount(self, kcount):
		self.kcount = kcount

	def set_spacing(self, space):
		self.param_layout.setVerticalSpacing(space)

	def add_param(self, param, label=None, group=False, parent=None):
		if label is None:
			label = param.key.replace('_', ' ').title()

		if not isinstance(param, CirchartHiddenParameter):
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

			#some subparameters were deleted with parent
			try:
				self.param_layout.removeRow(param)
			except:
				pass
			#do not need to delete widget manually after removerow
			#param.deleteLater()

	def remove_params(self, keys):
		for key in keys:
			self.remove_param(key)

	def clear_params(self):
		ks = [p.key for k, p in self.params.items()]
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

				case 'choices':
					if self.kcount > 1:
						w = CirchartChoicesParameter(p.name, self)
					else:
						w = CirchartChoiceParameter(p.name, self)

				case 'group':
					w = CirchartGroupParameter(p.name, self)

				case 'condition':
					w = CirchartConditionParameter(p.name, self)

				case 'style':
					w = CirchartStyleParameter(p.name, self)

				case 'title':
					w = CirchartTitleParameter(p.name, self)

				case 'radius':
					w = CirchartRadiusParameter(p.name, self)

				case 'annulus':
					w = CirchartAnnulusParameter(p.name, self)

				case 'chroms':
					w = CirchartChromsParameter(p.name, self)

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
						if p.mutex.startswith('~'):
							mname = p.mutex.strip('~')
							parent = self.params[mname]
							w.setEnabled(parent.isChecked())
							parent.toggled.connect(w.setEnabled)
						else:
							parent = self.params[p.mutex]
							w.setDisabled(parent.isChecked())
							parent.toggled.connect(w.setDisabled)

			if p.name in values:
				w.set_value(values[p.name])

			elif p.type == 'group':
				self.add_param(w, group=True)

			elif p.type == 'title':
				self.add_param(w, group=True)

			elif 'hide' in p:
				continue

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

			elif isinstance(p, CirchartParameterAccordion):
				values.update(p.get_params())

		return {self.key: values}

	def set_params(self, params):
		ps = params.get(self.key, {})

		for k, v in ps.items():
			if k in self.params:
				if isinstance(v, dict):
					self.params[k].set_params(ps)

				else:
					self.params[k].set_value(v)

class CirchartChildAccordion(CirchartParameterAccordion):
	def _init_panels(self):
		pass

class CirchartGeneralTrack(CirchartParameterAccordion):
	_closable = False

	def _init_panels(self):
		panel = self.create_panel('global')
		params = CIRCOS_PARAMS['general']
		panel.create_params(params)

class CirchartIdeogramTrack(CirchartParameterAccordion):
	_closable = False

	def _init_panels(self):
		self._create_main_panel()
		self._create_label_panel()
		self._create_space_panel()
		self.space_count = 0

	def _create_main_panel(self):
		main_params = CIRCOS_PARAMS['ideogram']
		ideogram_panel = self.create_panel('main', ':/icons/dna.svg', "Ideogram Parameters")
		ideogram_panel.create_params(main_params)

	def _create_label_panel(self):
		label_params = CIRCOS_PARAMS['labels']
		label_panel = self.create_panel('label', ':/icons/label.svg', "Show ideogram labels")
		label_panel.create_params(label_params)

	def _create_space_panel(self):
		self.space_panel = self.create_panel('spaces', ':/icons/space.svg', "Spacing between specific chromosomes")

		menu = QMenu(self.space_panel)
		space_act = QAction("Add Spacing", self.space_panel)
		space_act.triggered.connect(self.add_spacing)
		menu.addAction(space_act)

		open_menu = lambda x: (menu.move(QCursor().pos()), (menu.show()))
		self.space_panel.setContextMenuPolicy(Qt.CustomContextMenu)
		self.space_panel.customContextMenuRequested.connect(open_menu)

	def create_spacing(self, key):
		space_params = CIRCOS_PARAMS['spaces']
		space = CirchartChildAccordion(key, self.space_panel)
		panel = space.create_panel('space')
		panel.create_params(space_params)
		param = panel.get_widget('pairwise')
		param.set_data(self.chroms)
		self.space_panel.add_param(space, group=True)

	def add_spacing(self):
		self.space_count += 1
		key = 'spacing{}'.format(self.space_count)
		self.create_spacing(key)

	def set_params(self, params):
		if 'ideogram' in params:
			spaces = params['ideogram']['spaces']

			self.space_panel.clear_params()
			self.space_count = 0

			for s in spaces:
				sid = int(s.lstrip('spacing'))

				if sid > self.space_count:
					self.space_count = sid

				self.create_spacing(s)

		super().set_params(params)

class CirchartTickTrack(CirchartParameterAccordion):
	_closable = False

	def _init_panels(self):
		self._create_main_panel()
		self._create_ticks_panel()
		self.tick_count = 0

	def _create_main_panel(self):
		self.tick_params = CIRCOS_PARAMS['ticks']
		tick_level0 = [p for p in self.tick_params if p['level'] == 0]
		self.main_panel = self.create_panel('main', ':/icons/mark.svg', "Tick display parameters")
		self.main_panel.create_params(tick_level0)

	def _create_ticks_panel(self):
		self.ticks_panel = self.create_panel('ticks', ':/icons/tick.svg', "Ticks")

		menu = QMenu(self.ticks_panel)
		tick_act = QAction("Add Tick", self.ticks_panel)
		tick_act.triggered.connect(self.add_tick)
		menu.addAction(tick_act)

		open_menu = lambda x: (menu.move(QCursor().pos()), (menu.show()))
		self.ticks_panel.setContextMenuPolicy(Qt.CustomContextMenu)
		self.ticks_panel.customContextMenuRequested.connect(open_menu)

	def create_tick(self, key):
		tick_level1 = [p for p in self.tick_params if p['level'] == 1]
		tick_panel = CirchartChildAccordion(key, self.ticks_panel)
		style_panel = tick_panel.create_panel('styles')
		style_panel.create_params(tick_level1)
		self.ticks_panel.add_param(tick_panel, group=True)

	def add_tick(self):
		self.tick_count += 1
		key = 'tick{}'.format(self.tick_count)
		self.create_tick(key)

	def set_params(self, params):
		if 'ticks' in params:
			ticks = params['ticks']['ticks']

			self.ticks_panel.clear_params()
			self.tick_count = 0

			for k in ticks:
				tid = int(k.lstrip('tick'))

				if tid > self.tick_count:
					self.tick_count = tid

				self.create_tick(k)

		super().set_params(params)


class CirchartPlotTrack(CirchartParameterAccordion):
	def _init_panels(self):
		self.rule_count = 0
		self.axes_count = 0
		self.bg_count = 0

		self._create_plot_panel()
		self._create_rule_panel()
		self._create_axes_panel()
		self._create_background_panel()

	def _create_plot_panel(self):
		self.plot_panel = self.create_panel('main', ':/icons/chart.svg', "Track plot parameters")
		self.plot_panel.set_kcount(self.kwargs['kcount'])
		self.plot_params = CIRCOS_PARAMS['tracks']
		ptypes = [k for k in self.plot_params]

		self.type_param = CirchartChoiceParameter('type', self)
		self.plot_panel.add_param(self.type_param)
		self.type_param.currentTextChanged.connect(self._on_type_changed)
		self.type_param.set_data(ptypes)

	def _create_rule_panel(self):
		self.rule_panel = self.create_panel('rules', ':/icons/rule.svg', "Track display rules")
		self.rule_params = CIRCOS_PARAMS['rules']
		self.type_param.currentIndexChanged.connect(self.rule_panel.clear_params)

		menu = QMenu(self.rule_panel)
		rule_act = QAction("Add Rule", self.rule_panel)
		rule_act.triggered.connect(self.add_rule)
		menu.addAction(rule_act)

		open_menu = lambda x: (menu.move(QCursor().pos()), (menu.show()))
		self.rule_panel.setContextMenuPolicy(Qt.CustomContextMenu)
		self.rule_panel.customContextMenuRequested.connect(open_menu)

	def create_rule(self, key, ptype):
		plot_params = self.plot_params[ptype]
		rule_params = self.rule_params[ptype]
		tests = [AttrDict(p) for p in rule_params[0]['tests']]
		attrs = [AttrDict(name='show', type='bool', default='yes')]

		for p in plot_params:
			p = AttrDict(p)

			if p.name in rule_params[1]['attrs']:
				attrs.append(p)

		rule = CirchartChildAccordion(key, self.rule_panel)
		panel = rule.create_panel('main')
		panel.set_spacing(20)
		panel.create_params(rule_params)
		param = panel.get_widget('style')
		param.set_attrs(attrs)
		param = panel.get_widget('condition')
		param.set_tests(tests)
		param.set_chroms(self.kwargs['chroms'])

		self.rule_panel.add_param(rule, group=True)

	def add_rule(self):
		self.rule_count += 1
		key = 'rule{}'.format(self.rule_count)
		ptype = self.type_param.get_value()
		self.create_rule(key, ptype)

	def _create_axes_panel(self):
		self.axes_panel = self.create_panel('axes', ':/icons/axis.svg', "Track Axes")

		menu = QMenu(self.axes_panel)
		axes_space_act = QAction("Add Spacing Axis", self.axes_panel)
		axes_space_act.triggered.connect(lambda : self.add_axis('spacing'))

		axes_pos_act = QAction("Add Fixed Position Axis", self.axes_panel)
		axes_pos_act.triggered.connect(lambda: self.add_axis('position'))

		menu.addAction(axes_space_act)
		menu.addAction(axes_pos_act)

		open_menu = lambda x: (menu.move(QCursor().pos()), (menu.show()))
		self.axes_panel.setContextMenuPolicy(Qt.CustomContextMenu)
		self.axes_panel.customContextMenuRequested.connect(open_menu)

	def create_axis(self, key, by='spacing'):
		axis_params = CIRCOS_PARAMS['axes']

		if by == 'spacing':
			axis_params = [p for p in axis_params if p['name'] != 'position']
		else:
			axis_params = [p for p in axis_params if p['name'] != 'spacing']

		axis_panel = CirchartChildAccordion(key, self.axes_panel)
		style_panel = axis_panel.create_panel('main')
		style_panel.create_params(axis_params)
		self.axes_panel.add_param(axis_panel, group=True)

	def add_axis(self, by):
		self.axes_count += 1
		key = "axis{}".format(self.axes_count)
		self.create_axis(key, by)

	def _create_background_panel(self):
		self.bgs_panel = self.create_panel('backgrounds', ':/icons/bg.svg', "Track Backgrounds")

		menu = QMenu(self.bgs_panel)
		bg_act = QAction("Add Background", self.bgs_panel)
		bg_act.triggered.connect(self.add_background)
		menu.addAction(bg_act)

		open_menu = lambda x: (menu.move(QCursor().pos()), (menu.show()))
		self.bgs_panel.setContextMenuPolicy(Qt.CustomContextMenu)
		self.bgs_panel.customContextMenuRequested.connect(open_menu)

	def create_background(self, key):
		bg_params = CIRCOS_PARAMS['backgrounds']
		bg_panel = CirchartChildAccordion(key, self.bgs_panel)
		style_panel = bg_panel.create_panel('main')
		style_panel.create_params(bg_params)
		self.bgs_panel.add_param(bg_panel, group=True)

	def add_background(self):
		self.bg_count += 1
		key = 'background{}'.format(self.bg_count)
		self.create_background(key)

	def _on_type_changed(self, ptype):
		#self.set_title("Track:{}".format(ptype))
		panel = self.get_panel(0)
		params = self.plot_params[ptype]

		ks = []
		for k, p in panel.params.items():
			if k != 'type':
				ks.append(k)

		panel.remove_params(ks)
		panel.create_params(params)

	def set_params(self, params):
		self.rule_panel.clear_params()
		self.axes_panel.clear_params()
		self.bgs_panel.clear_params()

		self.rule_count = 0
		self.axes_count = 0
		self.bg_count = 0

		ps = params[self.key]
		ptype = ps['main']['type']

		#when type changed, will delete rules
		self.type_param.set_value(ptype)

		for k, v in ps.items():
			if k == 'rules':
				for x, y in v.items():
					rid = int(x.lstrip('rule'))

					if rid > self.rule_count:
						self.rule_count = rid

					self.create_rule(x, ptype)

			elif k == 'axes':
				for x, y in v.items():
					aid = int(x.lstrip('axis'))

					if aid > self.axes_count:
						self.axes_count = aid

					if 'spacing' in y['main']:
						self.create_axis(x, 'spacing')
					else:
						self.create_axis(x, 'position')

			elif k == 'backgrounds':
				for x, y in v.items():
					bid = int(x.lstrip('background'))

					if bid > self.bg_count:
						self.bg_count = bid

					self.create_background(x)

		super().set_params(params)


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
		self.plot_type = None

	def sizeHint(self):
		return QSize(250, 0)

	def add_widget(self, param):
		self.main_layout.addWidget(param)

	def get_widgets(self):
		count = self.main_layout.count()

		for i in range(count):
			item = self.main_layout.itemAt(i)
			widget = item.widget()

			if widget:
				yield widget

	def clear_widgets(self):
		count = self.main_layout.count()

		for i in range(count):
			item = self.main_layout.itemAt(i)

			if item:
				widget = item.widget()

				if widget:
					widget.deleteLater()

	def clear_params(self, plot_id):
		if self.plot_id == plot_id:
			self.clear_widgets()
			self.plot_id = 0

	def get_params(self):
		values = {}
		count = self.main_layout.count()

		for i in range(count):
			item = self.main_layout.itemAt(i)
			widget = item.widget()

			if isinstance(widget, CirchartParameterMixin):
				values.update(widget.get_param())

			elif isinstance(widget, CirchartParameterPanel):
				values.update(widget.get_params())

			elif isinstance(widget, CirchartParameterAccordion):
				values.update(widget.get_params())

		return values

	def reset_params(self, params):
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

		self.reset_params(params)
		#return params['general']['global']['plotname']

class CirchartCircosParameterManager(CirchartParameterManager):
	def new_circos_plot(self, params):
		self.clear_widgets()

		self.plot_id = params['general']['global']['plot_id']
		self.plot_type = params['general']['global']['plot_type']
		self.karyotype_count = len(params['general']['global']['karyotype'])

		karyotypes = []
		for row in SqlControl.get_datas_by_type('karyotype'):
			karyotypes.append(row.name)

		params['general']['global']['karyotypes'] = ', '.join(karyotypes)

		self.chroms = []
		for k in params['general']['global']['karyotype']:
			rows = SqlControl.get_data_objects('karyotype', k)

			for row in rows:
				self.chroms.append(row.name)

		form = CirchartGeneralTrack('general', self)
		form.set_params(params)
		self.add_widget(form)

		form = CirchartIdeogramTrack('ideogram', self, chroms=self.chroms)
		#form.set_chroms(self.chroms)
		form.set_params(params)
		self.add_widget(form)

		form = CirchartTickTrack('ticks', self)
		form.set_params(params)
		self.add_widget(form)

		params = self.get_params()
		return params

	def create_plot_track(self, key):
		track = CirchartPlotTrack(key, self, chroms=self.chroms,
			kcount=self.karyotype_count)
		#track.set_chroms(self.chroms)
		self.add_widget(track)
		return track

	def add_plot_track(self, key=None):
		if self.plot_type != 'circos' or self.plot_id == 0:
			return

		if key is None:
			self.track_count += 1
			key = 'track{}'.format(self.track_count)

		track = self.create_plot_track(key)
		return track

	def reset_params(self, params):
		self.new_circos_plot(params)
		self.track_count = 0

		for k, v in params.items():
			if k.startswith('track'):
				tid = int(k.replace('track', ''))

				if tid > self.track_count:
					self.track_count = tid

				track = self.add_plot_track(k)
				params[k]['kcount'] = self.karyotype_count
				track.set_params(params)

class CirchartSnailGeneralForm(CirchartParameterAccordion):
	_closable = False
	_visible = True

	def _init_panels(self):
		panel = self.create_panel('global')
		params = CIRCOS_PARAMS['snail']['general']
		panel.create_params(params)

class CirchartSnailPlotForm(CirchartParameterAccordion):
	_closable = False
	_visible = True

	def _init_panels(self):
		panel = self.create_panel('main')
		params = CIRCOS_PARAMS['snail']['plot']
		panel.create_params(params)

class CirchartSnailBuscoForm(CirchartParameterAccordion):
	_closable = False
	_visible = True

	def _init_panels(self):
		panel = self.create_panel('main')
		params = CIRCOS_PARAMS['snail']['busco']
		panel.create_params(params)

class CirchartSnailParameterManager(CirchartParameterManager):
	def new_snail_plot(self, params):
		self.clear_widgets()
		self.plot_id = params['general']['global']['plot_id']
		self.plot_type = params['general']['global']['plot_type']

		form = CirchartSnailGeneralForm('general', self)
		form.set_params(params)
		self.add_widget(form)

		form = CirchartSnailPlotForm('plot', self)
		form.set_params(params)
		self.add_widget(form)

		form = CirchartSnailBuscoForm('busco', self)
		form.set_params(params)
		self.add_widget(form)

		return self.get_params()

	def reset_params(self, params):
		self.new_snail_plot(params)

class CirchartDataFilterDialog(QDialog):
	def __init__(self, parent=None, table=None):
		super().__init__(parent)

		self.table = table
		self.setWindowTitle("Assign Plot Options")

		self.main_layout = QVBoxLayout()
		self.setLayout(self.main_layout)

		self._create_widgets()
		self._init_widgets()
		self._init_layouts()

	def sizeHint(self):
		return QSize(500, 300)

	def _create_widgets(self):
		self.tree = CirchartDataFilterTree(self, self.table)

		self.add_btn = QPushButton(self)
		self.add_btn.setIcon(QIcon(':/icons/add.svg'))
		self.add_btn.setToolTip("Add filter")
		self.add_btn.setFixedSize(24, 24)
		self.add_btn.clicked.connect(self.tree.add_filter)
		self.del_btn = QPushButton(self)
		self.del_btn.setFixedSize(24, 24)
		self.del_btn.setToolTip("Delete filter")
		self.del_btn.setIcon(QIcon(':/icons/delete.svg'))
		self.del_btn.clicked.connect(self.tree.delete_filter)
		self.clr_btn = QPushButton(self)
		self.clr_btn.setFixedSize(24, 24)
		self.clr_btn.setToolTip("Clear filters")
		self.clr_btn.setIcon(QIcon(':/icons/trash.svg'))
		self.clr_btn.clicked.connect(self.tree.clear_filters)

		self.styles = CirchartStyleParameter('options', self)
		self.styles.style_changed.connect(self.adjustSize)

		self.select = QComboBox(self)
		self.select.currentTextChanged.connect(self._on_plot_changed)

		self.btn_box = QDialogButtonBox(
			QDialogButtonBox.StandardButton.Cancel |
			QDialogButtonBox.StandardButton.Ok
		)
		self.btn_box.accepted.connect(self._on_accepted)
		self.btn_box.rejected.connect(self.reject)

	def _init_widgets(self):
		if self.table.startswith('linkdata'):
			plots = ['link']

		elif self.table.startswith('textdata'):
			plots = ['text']

		elif self.table.startswith('locidata'):
			plots = ['tile', 'connector', 'highlight']

		else:
			plots = ['line', 'scatter', 'histogram', 'heatmap']

		self.select.addItems(plots)

	def _init_layouts(self):
		btn_layout = QHBoxLayout()
		btn_layout.addWidget(QLabel("Data filters:", self), 1)
		btn_layout.addWidget(self.add_btn)
		btn_layout.addWidget(self.del_btn)
		btn_layout.addWidget(self.clr_btn)

		sel_layout = QHBoxLayout()
		sel_layout.addWidget(QLabel("Assign", self))
		sel_layout.addWidget(self.select)
		sel_layout.addWidget(QLabel("plot options to filtered data", self), 1)

		self.main_layout.addLayout(btn_layout)
		self.main_layout.addWidget(self.tree)
		self.main_layout.addLayout(sel_layout)
		self.main_layout.addWidget(self.styles)
		self.main_layout.addWidget(self.btn_box)

	def _on_plot_changed(self, ptype):
		self.styles.clear_styles()

		plot_params = CIRCOS_PARAMS['tracks'][ptype]
		rule_params = CIRCOS_PARAMS['rules'][ptype]
		attrs = [AttrDict(name='show', type='bool', default='yes')]

		for p in plot_params:
			p = AttrDict(p)

			if p.name in rule_params[1]['attrs']:
				attrs.append(p)

		self.styles.set_attrs(attrs)

	def _on_accepted(self):
		options = self.get_options()

		if not options:
			return QMessageBox.critical(self, 'Error', 'No style options added')

		self.accept()

	def get_options(self):
		values = self.styles.get_param()

		options = []
		for k, v in values['options']:
			if str(v).count(',') > 1:
				options.append("{}=({})".format(k, v))
			else:
				options.append("{}={}".format(k, v))

		return ','.join(options)

	def get_filters(self):
		return self.tree.get_filters()

	@classmethod
	def add_options(cls, parent=None, table=None):
		dlg = cls(parent, table)

		if dlg.exec() == QDialog.Accepted:
			options = dlg.get_options()
			filters = dlg.get_filters()
			counts = SqlControl.update_data_options(dlg.table, filters, options)
			QMessageBox.information(self, 'Information', "Added options to {} rows".format(counts))


