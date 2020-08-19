from PyQt5.QtWidgets import QCheckBox, QPushButton, \
    QLabel, QWidget
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPalette, QFont
from functools import partial

AGE = ["婴儿(0-4)", "儿童(5-18)", "青年(19-30)", "中老年(31-150)", "未知"]
# AGE = ["0-4", "5-18", "19-30", "30-150", "未知"]
RACE = ["黄", "白", "黑", "未知"]
GENDER = ["男", "女", "未知"]
EXPRESSION = ["无", "开心", "愤怒", "悲伤", "未知"]

class Selector(QWidget):
    def __init__(self, name, values, parent):
        super(Selector, self).__init__(parent)
        self.check_boxes = []
        span = 40
        label = QLabel(name, self)
        label.setStyleSheet("border:1px solid black;")
        values.append("未标")
        for i, v in enumerate(values):
            height_b = 25

            num_lines = len(v) // 3 + 1
            if num_lines > 1:
                v = list(v)
                v = "\n".join(["".join(v[s:s+3]) for s in range(0, len(v), 3)])
                cb = QCheckBox(v, self)
            else:
                cb = QCheckBox(v, self)
            cb.move(0, span)
            cb.resize(50, height_b * num_lines)
            span += height_b * num_lines
            if v == "未知":
                self.unknow_box_idx = i
            cb.stateChanged.connect(partial(self.set_unknow, i))
            self.check_boxes.append(cb)
        self.check_boxes[-1].setChecked(True)
        self.values = values

    def get_selected_value(self):
        results = []
        for b, v in zip(self.check_boxes, self.values):
            if b.isChecked():
                results.append(v)
        return results

    def set_unknow(self, idx):
        for c in self.check_boxes:
            c.disconnect()
        if hasattr(self, "unknow_box_idx") and self.check_boxes[idx].isChecked():
            if idx == self.unknow_box_idx:
                for i, v in enumerate(self.check_boxes):
                    if i != self.unknow_box_idx:
                        v.setChecked(False)
            else:
                self.check_boxes[self.unknow_box_idx].setChecked(False)

        if idx == len(self.check_boxes) - 1:
            for c in self.check_boxes[:-1]:
                c.setChecked(False)
            self.check_boxes[idx].setChecked(True)
        elif not self.check_boxes[idx].isChecked():
            has_select = False
            for c in self.check_boxes[:-1]:
                if c.isChecked():
                    has_select = True
            if not has_select:
                self.check_boxes[-1].setChecked(True)
        else:
            self.check_boxes[-1].setChecked(False)
        for i, c in enumerate(self.check_boxes):
            c.stateChanged.connect(partial(self.set_unknow, i))



class Labels:
    def __init__(self, parent):
        self.panel = QWidget(parent)
        self.panel.resize(600, 600)

        self.race = Selector("肤色", RACE.copy(), self.panel)
        self.race.move(60, 0)
        self.race.resize(60, 600)

        self.gender = Selector("性别", GENDER.copy(), self.panel)
        self.gender.move(0, 0)
        self.gender.resize(60, 600)

        self.expression = Selector("表情", EXPRESSION.copy(), self.panel)
        self.expression.move(120, 0)
        self.expression.resize(60, 600)

        self.age = Selector("年龄", AGE.copy(), self.panel)
        self.age.move(180, 0)
        self.age.resize(60, 600)
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
        self.expression.setFont(font)

    def get_labels(self):
        results = {}
        results["age"] = self.age.get_selected_value()
        results["race"] = self.race.get_selected_value()
        results["gender"] = self.gender.get_selected_value()
        results["expression"] = self.expression.get_selected_value()
        return results

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