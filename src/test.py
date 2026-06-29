from PySide6.QtCore import QMimeData, Qt
from PySide6.QtGui import QDrag
from PySide6.QtWidgets import QApplication, QHBoxLayout, QPushButton, QWidget


class DragButton(QPushButton):
    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            drag.setMimeData(mime)
            drag.exec(Qt.DropAction.MoveAction)


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)

        self.blayout = QHBoxLayout()
        for l in ["A", "B", "C", "D"]:
            btn = DragButton(l)
            self.blayout.addWidget(btn)

        self.setLayout(self.blayout)

    def dragEnterEvent(self, e):
        e.accept()

    def dropEvent(self, e):
        pos = e.position()
        widget = e.source()
        self.blayout.removeWidget(widget)

        for n in range(self.blayout.count()):
            # Get the widget at each index in turn.
            w = self.blayout.itemAt(n).widget()
            if pos.x() < w.x() + w.size().width() // 2:
                # We didn't drag past this widget.
                # insert to the left of it.
                break
        else:
            # We aren't on the left hand side of any widget,
            # so we're at the end. Increment 1 to insert after.
            n += 1

        self.blayout.insertWidget(n, widget)

        e.accept()


app = QApplication([])
w = Window()
w.show()

app.exec()
