from PyQt5.QtWidgets import QCheckBox, QPushButton, \
    QComboBox, QWidget
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPalette, QFont
from functools import partial

AGE = ["婴儿(0-4)", "儿童(5-18)", "青年(19-30)", "中老年(31-150)", "未知"]
RACE = ["黄", "白", "黑", "未知"]
GENDER = ["男", "女", "未知"]

class Selector(QWidget):
    def __init__(self, values, parent):
        super(Selector, self).__init__(parent)
        self.check_boxes = []
        span = 0
        for i, v in enumerate(values):
            width_b = len(v) * 6 + 30
            # width_b = 100
            cb = QCheckBox(v, self)
            cb.move(span, 0)
            cb.resize(width_b, 20)
            span += width_b
            if v == "未知":
                self.unknow_box_idx = i
            cb.stateChanged.connect(partial(self.set_unknow, i))
            self.check_boxes.append(cb)
        self.values = values
        self.shield_signal = False

    def get_selected_value(self):
        results = []
        for b, v in zip(self.check_boxes, self.values):
            if b.isChecked():
                results.append(v)

    def set_unknow(self, idx):
        if hasattr(self, "unknow_box_idx") and self.check_boxes[idx].isChecked():
            if idx == self.unknow_box_idx:
                for i, v in enumerate(self.check_boxes):
                    if i != self.unknow_box_idx:
                        v.setChecked(False)
            else:
                self.check_boxes[self.unknow_box_idx].setChecked(False)


class Labels:
    def __init__(self, parent):
        self.panel = QWidget(parent)
        self.panel.resize(500, 200)
        self.age = Selector(AGE, self.panel)
        self.age.move(0, 0)
        self.age.resize(400, 20)
        self.race = Selector(RACE, self.panel)
        self.race.move(0, 20)
        self.race.resize(400, 20)
        self.gender = Selector(GENDER, self.panel)
        self.gender.move(0, 40)
        self.gender.resize(400, 20)
        self.panel.show()

        font = QFont()
        font.setFamily("Arial")  # 括号里可以设置成自己想要的其它字体
        font.setPointSize(10)
        self.set_font(font)

    def move(self, *value):
        self.panel.move(*value)

    def resize(self, *value):
        self.panel.resize(*value)

    def set_font(self, font):
        self.age.setFont(font)
        self.race.setFont(font)
        self.gender.setFont(font)

    def get_labels(self):
        results = {}
        results["age"] = self.age.get_selected_value()
        results["race"] = self.race.get_selected_value()
        results["gender"] = self.race.get_selected_value()

from PyQt5.QtWidgets import QWidget, QCheckBox, QApplication, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
import sys


class Example(QWidget):

    def __init__(self):
        super().__init__()
        self.resize(600, 400)
        label = Labels(self)
        label.move(0, 0)




if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec_())