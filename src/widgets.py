import math

from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *

__all__ = [
	'CirchartSpacerWidget',
	'CirchartSpinnerWidget',
]

class CirchartSpacerWidget(QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

#from https://github.com/z3ntu/QtWaitingSpinner
class CirchartSpinnerWidget(QWidget):
	def __init__(self, parent):
		super().__init__(parent)

		# WAS IN initialize()
		self._color = QColor(Qt.black)
		self._roundness = 70.0
		self._minimumTrailOpacity = 3.14159265358979323846
		self._trailFadePercentage = 70.0
		self._revolutionsPerSecond = 1.57079632679489661923
		self._numberOfLines = 10
		self._lineLength = 6
		self._lineWidth = 3
		self._innerRadius = 4
		self._currentCounter = 0
		self._isSpinning = False

		self._timer = QTimer(self)
		self._timer.timeout.connect(self.rotate)
		self.updateSize()
		self.updateTimer()
		self.setVisible(False)
		# END initialize()

		self.setAttribute(Qt.WA_TranslucentBackground)

	def paintEvent(self, QPaintEvent):
		painter = QPainter(self)
		painter.fillRect(self.rect(), Qt.transparent)
		painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

		if self._currentCounter >= self._numberOfLines:
			self._currentCounter = 0

		painter.setPen(Qt.NoPen)
		for i in range(0, self._numberOfLines):
			painter.save()
			painter.translate(self._innerRadius + self._lineLength, self._innerRadius + self._lineLength)
			rotateAngle = float(360 * i) / float(self._numberOfLines)
			painter.rotate(rotateAngle)
			painter.translate(self._innerRadius, 0)
			distance = self.lineCountDistanceFromPrimary(i, self._currentCounter, self._numberOfLines)
			color = self.currentLineColor(distance, self._numberOfLines, self._trailFadePercentage,
										  self._minimumTrailOpacity, self._color)
			painter.setBrush(color)
			rect = QRect(0, int(-self._lineWidth / 2), int(self._lineLength), int(self._lineWidth))
			painter.drawRoundedRect(rect, self._roundness, self._roundness, Qt.SizeMode.RelativeSize)
			painter.restore()

	@property
	def running(self):
		return self._isSpinning

	def toggle(self, state):
		if state:
			self.start()
		else:
			self.stop()

	def start(self):
		self._isSpinning = True
		self.setVisible(True)

		if not self._timer.isActive():
			self._timer.start()
			self._currentCounter = 0

	def stop(self):
		self._isSpinning = False
		self.setVisible(False)

		if self._timer.isActive():
			self._timer.stop()
			self._currentCounter = 0

	def rotate(self):
		self._currentCounter += 1
		if self._currentCounter >= self._numberOfLines:
			self._currentCounter = 0
		self.update()

	def updateSize(self):
		size = int((self._innerRadius + self._lineLength) * 2)
		self.setFixedSize(size, size)

	def updateTimer(self):
		self._timer.setInterval(int(1000 / (self._numberOfLines * self._revolutionsPerSecond)))

	def lineCountDistanceFromPrimary(self, current, primary, totalNrOfLines):
		distance = primary - current
		if distance < 0:
			distance += totalNrOfLines
		return distance

	def currentLineColor(self, countDistance, totalNrOfLines, trailFadePerc, minOpacity, colorinput):
		color = QColor(colorinput)
		if countDistance == 0:
			return color
		minAlphaF = minOpacity / 100.0
		distanceThreshold = int(math.ceil((totalNrOfLines - 1) * trailFadePerc / 100.0))
		if countDistance > distanceThreshold:
			color.setAlphaF(minAlphaF)
		else:
			alphaDiff = color.alphaF() - minAlphaF
			gradient = alphaDiff / float(distanceThreshold + 1)
			resultAlpha = color.alphaF() - gradient * countDistance
			# If alpha is out of bounds, clip it.
			resultAlpha = min(1.0, max(0.0, resultAlpha))
			color.setAlphaF(resultAlpha)
		return color