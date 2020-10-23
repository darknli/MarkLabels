from PyQt5.QtWidgets import QLabel, QPushButton, \
    QTableWidgetItem
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPalette, QFont
from functools import partial
from controller.page_table import BulkIndexTabelWidget
from controller.utils import Rotator
from math import ceil
from controller.picture import FloatPoints

visiable_color = Qt.green
disvisiable_color = Qt.blue
seleted_color = Qt.red


class Keypoint(QLabel):
    def __init__(self, parent, loc, upper_controller, idx_points, w, h, visible=True, convinced=True):
        super().__init__(parent)
        self.backup_loc = loc
        self.precision_x = loc[0]
        self.precision_y = loc[1]
        self.iniDragCor = [0, 0]
        self.resize(5, 5)
        self.setAutoFillBackground(True)
        palette = QPalette()  # 创建调色板类实例
        if visible:
            palette.setColor(QPalette.Window, visiable_color)
        else:
            palette.setColor(QPalette.Window, disvisiable_color)
        self.setPalette(palette)
        self.setAlignment(Qt.AlignCenter)
        self.visible = visible
        self.convinced = convinced
        self.upper_controller = upper_controller
        self.idx_points = idx_points
        self.parent = parent
        self.move(int(self.precision_x + 0.5), int(self.precision_y + 0.5))
        self.scale = 1
        self.shift = FloatPoints(0, 0)
        self.label = QLabel(str(idx_points), parent)
        self.label.setStyleSheet('color:rgb(255, 120, 255)')
        self.label.move(self.geometry().x(), self.geometry().y())
        self.raise_()
        self.rotator = Rotator(w, h)

    def set_label(self, flag):
        if flag:
            self.label.show()
        else:
            self.label.hide()

    def set_important_point(self, is_highlight=False):
        """
        是否设置该点成高亮颜色
        :param is_highlight: 是否高亮
        """
        palette = QPalette()  # 创建调色板类实例
        if is_highlight:
            self.raise_()
            palette.setColor(QPalette.Window, seleted_color)
        elif self.visible:
            palette.setColor(QPalette.Window, visiable_color)
        else:
            palette.setColor(QPalette.Window, disvisiable_color)
        self.setPalette(palette)
        # self.setAlignment(Qt.AlignCenter)
        self.repaint()

    def mousePressEvent(self, e):
        self.iniDragCor[0] = e.x()
        self.iniDragCor[1] = e.y()
        self.mouseDoubleClickEvent(None)

    def mouseMoveEvent(self, e):
        x = e.x() - self.iniDragCor[0]
        y = e.y() - self.iniDragCor[1]

        cor = QPoint(x, y)
        self.my_move(self.mapToParent(cor))  # 需要maptoparent一下才可以的,否则只是相对位置。
        self.after_move_action(self.move_controller)

    def my_move(self, *loc):
        """
        先将坐标转换为基础坐标并保存到precisionxy，再做移动。
        :param loc: 坐标，可选为(x, y)和Qpoint
        """
        if len(loc) == 1:
            loc = (loc[0].x(), loc[0].y())
        x, y = loc

        fact_x = x / self.scale - self.shift.x
        fact_y = y / self.scale - self.shift.y
        self.precision_x, self.precision_y = self.rotator.recover_location(fact_x, fact_y)
        self.move(int(x + 0.5), int(y + 0.5))
        self.label.move(int(x + 0.5), int(y + 0.5))

    def keyPressEvent(self, event):
        # 如果按下xxx则xxx
        if event.key() == Qt.Key_Left:
            x, y = self.geometry().x(), self.geometry().y()
            self.my_move(x - 1, y)
            self.after_move_action(self.move_controller)
        elif event.key() == Qt.Key_Right:
            x, y = self.geometry().x(), self.geometry().y()
            self.my_move(x + 1, y)
            self.after_move_action(self.move_controller)
        elif event.key() == Qt.Key_Up:
            x, y = self.geometry().x(), self.geometry().y()
            self.my_move(x, y - 1)
            self.after_move_action(self.move_controller)
        elif event.key() == Qt.Key_Down:
            x, y = self.geometry().x(), self.geometry().y()
            self.my_move(x, y + 1)
            self.after_move_action(self.move_controller)
        elif event.key() == Qt.Key_V:
            self.visible = not self.visible
        elif event.key() == Qt.Key_Escape:
            self.relative_move(*self.backup_loc)
            self.after_move_action(self.move_controller)

    def mouseDoubleClickEvent(self, event):
        self.set_important_point(True)
        self.grabKeyboard()
        self.upper_controller.notify_other_points_normal(self.idx_points)
        self.move_controller.table_select_action(self.idx_points)

    def set_visible(self):
        self.visible = not self.visible
        palette = QPalette()  # 创建调色板类实例
        if self.visible:
            palette.setColor(QPalette.Window, visiable_color)
        else:
            palette.setColor(QPalette.Window, disvisiable_color)
        self.setPalette(palette)
        self.repaint()

    def set_convinced(self, convinced=True):
        self.convinced = convinced

    def bind_point_move_controller(self, move_controller):
        self.move_controller = move_controller

    # 当该点被移动了，则对别的控件采取某些行动
    def after_move_action(self, controller):
        controller.after_move_action(self.idx_points)

    def rescale_shift(self, scale, shift):
        self.scale = scale
        self.shift = shift
        fact_x, fact_y = self.rotator.cal_rotate_location(self.precision_x, self.precision_y)
        # fact_x = round(scale * (fact_x + shift.x()))
        # fact_y = round(scale * (fact_y + shift.y()))
        fact_x = round(scale * fact_x) + ceil(scale * shift.x)
        fact_y = round(scale * fact_y) + ceil(scale * shift.y)
        self.move(fact_x, fact_y)
        self.label.move(fact_x, fact_y)

    def relative_move(self, x, y):
        self.precision_x = x
        self.precision_y = y
        fact_x, fact_y = self.rotator.cal_rotate_location(self.precision_x, self.precision_y)
        # fact_x = round(self.scale * (fact_x + self.shift.x()))
        # fact_y = round(self.scale * (fact_y + self.shift.y()))
        fact_x = round(self.scale * fact_x) + ceil(self.scale * self.shift.x)
        fact_y = round(self.scale * fact_y) + ceil(self.scale * self.shift.y)
        self.move(fact_x, fact_y)
        self.label.move(fact_x, fact_y)

    def rotate90(self):
        """
        当图像有旋转的时候调用这个函数，设置使当前点跟图像同步+90°，并将上一次的平移量清零。
        """
        self.rotator.rotation()
        self.shift = FloatPoints(0, 0)
        fact_x, fact_y = self.rotator.cal_rotate_location(self.precision_x, self.precision_y)
        fact_x = round(self.scale * fact_x)
        fact_y = round(self.scale * fact_y)
        self.move(fact_x, fact_y)
        self.label.move(fact_x, fact_y)

class KeypointsCluster:
    def __init__(self, pts_list, prarent, w, h):
        self.pts = []
        for idx_point, (x, y) in enumerate(pts_list):
            kp = Keypoint(prarent, (x, y), self, idx_point, w, h)
            kp.bind_point_move_controller(self)
            self.pts.append(kp)
            kp.show()
        self.highlight_idx_point = None

    def set_high_light_point(self, idx_points):
        self.highlight_idx_point = idx_points
        for i, pt in enumerate(self.pts):
            if i == idx_points:
                self.pts[i].mouseDoubleClickEvent(None)
            else:
                self.pts[i].set_important_point(False)

    def notify_other_points_normal(self, idx_points):
        self.highlight_idx_point = idx_points
        for i, pt in enumerate(self.pts):
            if i != idx_points:
                self.pts[i].set_important_point(False)

    def release_keyboard(self):
        if self.highlight_idx_point is not None:
            self.pts[self.highlight_idx_point].set_important_point(False)
            self.pts[self.highlight_idx_point].releaseKeyboard()
            self.highlight_idx_point = None

    def get_points_str(self):
        points_str_list = []
        points_str = " ".join(
            ["%.6f %.6f %d %d" % (pt.precision_x, pt.precision_y, pt.visible, pt.convinced) for pt in self.pts])
        points_str_list.append(points_str)
        return points_str_list

    def change_location(self, idx_point, xory, v):
        # 是x值
        pt = self.pts[idx_point]
        if xory:
            if v != "%.2f" % pt.precision_x:
                pt.relative_move(float(v), pt.precision_y)
        else:
            if v != "%.2f" % pt.precision_y:
                pt.relative_move(pt.precision_x, float(v))

    def scale_loc(self, scale, shift):
        for pt in self.pts:
            pt.rescale_shift(scale, shift)

    # 捆绑控件，当有点移动时，该控件也会跟着起行动
    def bind_point_move_controller(self, move_controller):
        self.move_controller = move_controller

    def after_move_action(self, idx_point):
        self.move_controller.after_move_action(idx_point)

    def table_select_action(self, row):
        self.move_controller.select_table_line(row)

    def show_number(self, flag):
        for pt in self.pts:
            pt.set_label(flag)
            pt.repaint()

    def rotate90(self):
        for pt in self.pts:
            pt.rotate90()

class KeyPointTable:
    def __init__(self, kp_cluster, parent):
        font = QFont()
        font.setFamily("Arial")  # 括号里可以设置成自己想要的其它字体
        font.setPointSize(10)  # 括号里的数字可以设置成自己想要的字体大小
        rows = len(kp_cluster.pts)
        self.kp_tabel = BulkIndexTabelWidget(rows, 6, 19, parent)
        self.kp_tabel.setHorizontalHeaderLabels(["序号", "X", "Y", "可见", "确定", "改变"])
        self.kp_cluster = kp_cluster
        self.kp_cluster.bind_point_move_controller(self)
        self.backup_kp = []
        for i, kp in enumerate(kp_cluster.pts):
            self.backup_kp.append(("%.2f" % kp.precision_x, "%.2f" % kp.precision_y))

            sure_btn = QPushButton("Yes" if kp.visible else "No")
            sure_btn.clicked.connect(partial(self._set_convinced, kp, sure_btn))
            sure_btn.setStyleSheet("border:none")
            sure_btn.setFont(font)
            sure_btn.setFlat(True)

            visible_btn = QPushButton("Yes" if kp.visible else "No")
            visible_btn.clicked.connect(partial(self._set_visible, kp, visible_btn, sure_btn))
            # visible_btn.resize(3, 3)
            visible_btn.setStyleSheet("border:none")
            visible_btn.setFont(font)
            visible_btn.setFlat(True)

            self.kp_tabel.setItem(i, 0, QTableWidgetItem(str(i)))
            self.kp_tabel.setItem(i, 1, QTableWidgetItem("%.2f" % kp.precision_x))
            self.kp_tabel.setItem(i, 2, QTableWidgetItem("%.2f" % kp.precision_y))
            self.kp_tabel.setCellWidget(i, 3, visible_btn)
            self.kp_tabel.setCellWidget(i, 4, sure_btn)
            self.kp_tabel.setItem(i, 5, QTableWidgetItem("No"))
        self.kp_tabel.load_data()
        self.kp_tabel.setFont(font)
        self.kp_tabel.cellChangedconnect(self.cell_change)
        self.kp_tabel.cellClickedconnect(self.click_cell)
        self.kp_tabel.resize(400, 650)
        self.kp_tabel.show()

    def click_cell(self, row, col):
        real_row = int(self.kp_tabel.item(row, 0).text())
        self._highlight(self.kp_cluster.pts[real_row])
        if col == 1 or col == 2:
            self.kp_cluster.release_keyboard()
        elif col == 5:
            if self.kp_tabel.item(row, col).text() == "Yes":
                real_row = int(self.kp_tabel.item(row, 0).text())
                self.kp_tabel.item(row, 1).setText(self.backup_kp[real_row][0])
                self.kp_tabel.item(row, 2).setText(self.backup_kp[real_row][1])
                self.kp_tabel.item(row, 5).setText("No")

    def select_table_line(self, row):
        self.kp_tabel.select(row)

    def cell_change(self, row, col):
        if col != 1 and col != 2:
            return
        real_row = int(self.kp_tabel.item(row, 0).text())
        value = self.kp_tabel.item(row, col).text()
        if value != self.backup_kp[real_row][col == 2]:
            self.kp_tabel.item(row, 5).setText("Yes")
        self.kp_cluster.change_location(real_row, col == 1, value)

    def move(self, x, y):
        self.kp_tabel.move(x, y)

    def _highlight(self, kp):
        kp.mouseDoubleClickEvent(None)

    def _set_visible(self, kp, btn, sure_btn):
        btn.setText("Yes" if btn.text() == "No" else "No")
        btn.repaint()
        kp.set_visible()
        # 确定位置键也需要重新设置，逻辑是：如果不可见则默认不确定；如果可见默认确定
        sure_btn.setText("No" if btn.text() == "No" else "Yes")
        sure_btn.repaint()
        kp.set_convinced(True if sure_btn.text() == "Yes" else False)

    def _set_convinced(self, kp, btn):
        btn.setText("Yes" if btn.text() == "No" else "No")
        btn.repaint()
        kp.set_convinced(True if btn.text() == "Yes" else False)

    def after_move_action(self, idx_point):
        pt = self.kp_cluster.pts[idx_point]
        x = "%.2f" % pt.precision_x
        y = "%.2f" % pt.precision_y
        self.kp_tabel.item(idx_point, 1).setText(x)
        self.kp_tabel.item(idx_point, 2).setText(y)
        if x == self.backup_kp[idx_point][0] and y == self.backup_kp[idx_point][1]:
            self.kp_tabel.item(idx_point, 5).setText("No")
