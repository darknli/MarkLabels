from PyQt5.QtWidgets import (
    QApplication, QDesktopWidget, QVBoxLayout,
    QWidget, QPushButton, QHBoxLayout, QTextEdit
)
from PyQt5.QtGui import QPalette, QBrush, QColor
from PyQt5.QtCore import Qt

class MyMessageBox(QWidget):
    def __init__(self, info, yes_action=None, no_action=None):
        super().__init__()
        self.setWindowTitle("消息")
        self.txt = QTextEdit(info)
        self.txt.setReadOnly(True)
        pl = self.txt.palette()
        pl.setBrush(QPalette.Base, QBrush(QColor(255, 0, 0, 0)))
        self.txt.setPalette(pl)

        self.no_btn = QPushButton("不")
        self.yes_btn = QPushButton("是")
        self.no_btn.clicked.connect(self._click_no)
        self.no_action = no_action
        self.yes_btn.clicked.connect(self._click_yes)
        self.yes_action = yes_action

        self.hbox = QHBoxLayout()
        self.hbox.addStretch(1)
        self.hbox.addWidget(self.no_btn)
        self.hbox.addWidget(self.yes_btn)

        self.vbox = QVBoxLayout()
        self.vbox.addStretch(1)
        self.vbox.addWidget(self.txt)
        self.vbox.addLayout(self.hbox)
        self.setLayout(self.vbox)
        self.resize(120, 30)

    def _click_yes(self):
        self.hide()
        if self.yes_action is not None:
            self.yes_action()

    def _click_no(self):
        self.hide()
        if self.no_action is not None:
            self.no_action()

class mainW(QWidget):
    def __init__(self):
        super(mainW, self).__init__()
        b = QPushButton("点", self)
        b.show()
        b.clicked.connect(self.message)

    def message(self):
        m = MyMessageBox("确定点了？")
        m.resize(120, 50)
        m.setWindowModality(Qt.ApplicationModal)
        m.show()
        while True:
            continue

if __name__ == '__main__':
    app = QApplication([])
    ma = mainW()
    ma.show()
    app.exec_()