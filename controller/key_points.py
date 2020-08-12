from PyQt5.QtWidgets import QLabel, QTableWidget, QPushButton, QTableWidgetItem, QApplication, QHeaderView
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPalette, QKeySequence
from functools import partial

class Keypoint(QLabel):
    def __init__(self, parent, visible=True):
        super().__init__(parent)
        self.iniDragCor = [0, 0]
        self.resize(5, 5)
        self.setAutoFillBackground(True)
        palette = QPalette()  # 创建调色板类实例
        palette.setColor(QPalette.Window, Qt.black)
        self.setPalette(palette)
        self.setAlignment(Qt.AlignCenter)
        self.visible = visible

    def set_important_point(self):
        palette = QPalette()  # 创建调色板类实例
        palette.setColor(QPalette.Window, Qt.red)
        self.setPalette(palette)
        self.setAlignment(Qt.AlignCenter)
        QApplication.processEvents()
        print("设置完毕")

    def set_normal_point(self):
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
        elif (event.key() == Qt.Key_V):
            self.visible = not self.visible

    def mouseDoubleClickEvent(self, event):
        print("double click")
        self.set_important_point()
        self.grabKeyboard()

class KeyPointTable:
    def __init__(self, kp_list, parent):
        self.kp_list = kp_list
        rows = len(kp_list[0])
        self.kp_tabel = QTableWidget(rows, 4, parent)
        self.kp_tabel.setHorizontalHeaderLabels(["序号", "X", "Y", "可见"])
        for i, kp in enumerate(self.kp_list[0]):
            btn = KeyPointButton(i, str(i))
            btn.clicked.connect(partial(self._transmit_signal, parent, i))
            self.kp_tabel.setCellWidget(i, 0, btn)
            # self.kp_tabel.setItem(i, 0, QTableWidgetItem(str(i)))
            self.kp_tabel.setItem(i, 1, QTableWidgetItem(str(kp.geometry().x())))
            self.kp_tabel.setItem(i, 2, QTableWidgetItem(str(kp.geometry().y())))
            self.kp_tabel.setItem(i, 3, QTableWidgetItem("Yes" if kp.visible else "No"))
        self.kp_tabel.resize(180, 550)
        self.kp_tabel.show()
        self.kp_tabel.verticalHeader().hide()
        # self.kp_tabel.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.kp_tabel.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.kp_tabel.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.kp_tabel.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.kp_tabel.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)

    def move(self, x, y):
        self.kp_tabel.move(x, y)

    def _transmit_signal(self, parent, idx):
        print("press btn!")
        parent.set_important_point(idx)

class KeyPointButton(QPushButton):
    def __init__(self, idx, *__args):
        super().__init__(*__args)
        self.idx = idx
    #     self.clicked.connect(self._transmit_signal)
    #
    # def _transmit_signal(self):
    #     print(self.idx)
