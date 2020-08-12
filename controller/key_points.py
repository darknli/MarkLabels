from PyQt5.QtWidgets import QLabel, QTableWidget, QPushButton, \
    QTableWidgetItem, QApplication, QHeaderView, QAbstractItemView
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPalette, QKeySequence
from functools import partial

class Keypoint(QLabel):
    def __init__(self, parent, upper_controller, idx_face, idx_points, visible=True):
        super().__init__(parent)
        self.iniDragCor = [0, 0]
        self.resize(5, 5)
        self.setAutoFillBackground(True)
        palette = QPalette()  # 创建调色板类实例
        palette.setColor(QPalette.Window, Qt.black)
        self.setPalette(palette)
        self.setAlignment(Qt.AlignCenter)
        self.visible = visible
        self.upper_controller = upper_controller
        self.idx_face = idx_face
        self.idx_points = idx_points
        self.parent = parent

    def set_important_point(self, is_highlight=False):
        palette = QPalette()  # 创建调色板类实例
        if is_highlight:
            palette.setColor(QPalette.Window, Qt.red)
        else:
            palette.setColor(QPalette.Window, Qt.black)
        self.setPalette(palette)
        self.setAlignment(Qt.AlignCenter)
        self.repaint()

    def mousePressEvent(self, e):
        self.iniDragCor[0] = e.x()
        self.iniDragCor[1] = e.y()
        self.mouseDoubleClickEvent(None)

    def mouseMoveEvent(self, e):
        x = e.x() - self.iniDragCor[0]
        y = e.y() - self.iniDragCor[1]

        cor = QPoint(x, y)
        self.move(self.mapToParent(cor))  # 需要maptoparent一下才可以的,否则只是相对位置。
        self.after_move_action(self.move_controller)

    def keyPressEvent(self, event):
        # 如果按下xxx则xxx
        if event.key() == Qt.Key_Left:
            x, y = self.geometry().x(), self.geometry().y()
            self.move(x - 1, y)
            self.after_move_action(self.move_controller)
        elif (event.key() == Qt.Key_Right):
            x, y = self.geometry().x(), self.geometry().y()
            self.move(x + 1, y)
            self.after_move_action(self.move_controller)
        elif (event.key() == Qt.Key_Up):
            x, y = self.geometry().x(), self.geometry().y()
            self.move(x, y - 1)
            self.after_move_action(self.move_controller)
        elif (event.key() == Qt.Key_Down):
            x, y = self.geometry().x(), self.geometry().y()
            self.move(x, y + 1)
            self.after_move_action(self.move_controller)
        elif (event.key() == Qt.Key_V):
            self.visible = not self.visible

    def mouseDoubleClickEvent(self, event):
        self.set_important_point(True)
        self.grabKeyboard()
        self.upper_controller.notify_other_points_normal(self.idx_face, self.idx_points)

    def set_visible(self):
        self.visible = not self.visible

    def bind_point_move_controller(self, move_controller):
        self.move_controller = move_controller

    # 当该点被移动了，则对别的控件采取某些行动
    def after_move_action(self, controller):
        controller.after_move_action(self.idx_face, self.idx_points)

class KeypointsCluster:
    def __init__(self, pts_list, prarent):
        self.pts = []
        for idx_face, pts in enumerate(pts_list):
            controller = []
            for idx_point, (x, y) in enumerate(pts):
                kp = Keypoint(prarent, self, idx_face, idx_point)
                kp.bind_point_move_controller(self)
                controller.append(kp)
                kp.move(x, y)
                kp.show()
            self.pts.append(controller)
        self.highlight_idx_face = None
        self.highlight_idx_point = None

    def set_high_light_point(self, idx_face, idx_points):
        self.highlight_idx_face = idx_face
        self.highlight_idx_point = idx_points
        for f_idx, pts in enumerate(self.pts):
            is_face = f_idx == idx_face
            for i, pt in enumerate(pts):
                if is_face and i == idx_points:
                    print("找到了%d" % i)
                    self.pts[0][i].mouseDoubleClickEvent(None)
                else:
                    self.pts[0][i].set_important_point(False)

    def notify_other_points_normal(self, idx_face, idx_points):
        self.highlight_idx_face = idx_face
        self.highlight_idx_point = idx_points
        for f_idx, pts in enumerate(self.pts):
            is_face = f_idx == idx_face
            for i, pt in enumerate(pts):
                if is_face and i != idx_points:
                    self.pts[0][i].set_important_point(False)

    def release_keyboard(self):
        if self.highlight_idx_point is not None:
            idx_face = self.highlight_idx_face
            idx_point = self.highlight_idx_point
            print(idx_face, idx_point)
            self.highlight_idx_face = None
            self.highlight_idx_point = None
            self.pts[idx_face][idx_point].set_important_point(False)
            self.pts[idx_face][idx_point].releaseKeyboard()

    def get_points_str(self):
        points_str_list = []
        for pts_controller in self.pts:
            points_str = " ".join(
                ["%.1f %.1f %d"%(pt.geometry().x(), pt.geometry().y(), pt.visible) for pt in pts_controller])
            points_str_list.append(points_str)
        return points_str_list

    def change_location(self, idx_face, idx_point, xory, v):
        # 是x值
        pt = self.pts[idx_face][idx_point]
        if xory:
            pt.move(v, pt.geometry().y())
        else:
            pt.move(pt.geometry().x(), v)

    # 捆绑控件，当有点移动时，该控件也会跟着起行动
    def bind_point_move_controller(self, move_controller):
        self.move_controller = move_controller

    def after_move_action(self, idx_face, idx_point):
        self.move_controller.after_move_action(idx_face, idx_point)

class KeyPointTable:
    def __init__(self, kp_cluster, parent):
        rows = len(kp_cluster.pts[0])
        self.kp_tabel = QTableWidget(rows, 4, parent)
        self.kp_tabel.setHorizontalHeaderLabels(["序号", "X", "Y", "可见"])
        self.kp_cluster = kp_cluster
        self.kp_cluster.bind_point_move_controller(self)
        for i, kp in enumerate(kp_cluster.pts[0]):
            btn = QPushButton(str(i))
            btn.clicked.connect(partial(self._highlight, kp))
            visible_btn = QPushButton("Yes" if kp.visible else "No")
            visible_btn.clicked.connect(partial(self._set_visible, kp, visible_btn))

            self.kp_tabel.setCellWidget(i, 0, btn)
            self.kp_tabel.setItem(i, 1, QTableWidgetItem(str(kp.geometry().x())))
            self.kp_tabel.setItem(i, 2, QTableWidgetItem(str(kp.geometry().y())))
            self.kp_tabel.setCellWidget(i, 3, visible_btn)
        self.kp_tabel.cellChanged.connect(self.cell_change)
        self.kp_tabel.cellClicked.connect(self.release_keyboard)
        self.kp_tabel.resize(210, 550)
        self.kp_tabel.show()
        self.kp_tabel.verticalHeader().hide()
        self.kp_tabel.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.kp_tabel.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.kp_tabel.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.kp_tabel.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)

    def release_keyboard(self, row, col):
        if col == 1 or col == 2:
            self.kp_cluster.release_keyboard()

    def cell_change(self, row, col):
        if col != 1 and col != 2:
            return
        value = self.kp_tabel.item(row, col).text()
        self.kp_cluster.change_location(0, row, col == 1, float(value))

    def move(self, x, y):
        self.kp_tabel.move(x, y)

    def _highlight(self, kp):
        kp.mouseDoubleClickEvent(None)
        # self.kp_tabel.grabKeyboard()
        # self._set_edit()
        # self.kp_tabel.setEditTriggers(QAbstractItemView.AllEditTriggers)

    def _set_visible(self, kp, btn):
        btn.setText("Yes" if btn.text() == "No" else "No")
        btn.repaint()
        kp.set_visible()
        # self._set_edit()
        # self.kp_tabel.setEditTriggers(QAbstractItemView.AllEditTriggers)

    def _set_edit(self):
        for row in range(self.kp_tabel.rowCount()):
            self.kp_tabel.item(row, 1).setFlags(Qt.ItemIsEnabled|Qt.ItemIsEditable)

    def after_move_action(self, idx_face, idx_point):
        pt_geometry = self.kp_cluster.pts[idx_face][idx_point].geometry()
        self.kp_tabel.item(idx_point, 1).setText("%d" % (pt_geometry.x()))
        self.kp_tabel.item(idx_point, 2).setText("%d" % (pt_geometry.y()))