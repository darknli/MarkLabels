from PyQt5.QtWidgets import QLabel, QShortcut
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPalette, QKeySequence

class Keypoint(QLabel):
    def __init__(self, parent):
        super().__init__(parent)
        self.iniDragCor = [0, 0]
        self.resize(5, 5)
        self.setAutoFillBackground(True)
        palette = QPalette()  # 创建调色板类实例
        palette.setColor(QPalette.Window, Qt.black)
        self.setPalette(palette)
        self.setAlignment(Qt.AlignCenter)

    def mousePressEvent(self, e):
        self.iniDragCor[0] = e.x()
        self.iniDragCor[1] = e.y()
        self.grabKeyboard()

    def mouseMoveEvent(self, e):
        x = e.x() - self.iniDragCor[0]
        y = e.y() - self.iniDragCor[1]

        cor = QPoint(x, y)
        self.move(self.mapToParent(cor))  # 需要maptoparent一下才可以的,否则只是相对位置。
        print('move to', self.mapToParent(cor))

    def keyPressEvent(self, event):
        # 如果按下xxx则xxx
        if event.key() == Qt.Key_Left:
            x, y = self.geometry().x(), self.geometry().y()
            self.move(x - 1, y)
        elif (event.key() == Qt.Key_Right):
            x, y = self.geometry().x(), self.geometry().y()
            self.move(x + 1, y)
        elif (event.key() == Qt.Key_Up):
            x, y = self.geometry().x(), self.geometry().y()
            self.move(x, y - 1)
        elif (event.key() == Qt.Key_Down):
            x, y = self.geometry().x(), self.geometry().y()
            self.move(x, y + 1)

    def mouseDoubleClickEvent(self, event):
        print("double click")
        self.grabKeyboard()