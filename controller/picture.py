from PyQt5.QtWidgets import QLabel, QTableWidget, QPushButton, \
    QTableWidgetItem, QApplication, QHeaderView, QAbstractItemView
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPalette, QKeySequence, QPixmap, QPainter
from functools import partial

MAX_SCALE = 10
MIN_SCALE = 1


class ImageController(QLabel):
    def __init__(self, image_path, parent):
        super().__init__(parent)
        self.resize(parent.width(), parent.height())
        self.img = QPixmap(image_path)
        self.scaled_img = self.img.copy()
        self.point = QPoint(0, 0)
        self.left_point = QPoint(0, 0)
        self.right_point = QPoint(self.img.width(), self.img.height())
        self.global_shift = QPoint(0, 0)
        self.ratio = 1.0
        self.kp_move = None

    def bind_show(self, update_show_status):
        self.update_show_status = update_show_status

    def paintEvent(self, e):
        painter = QPainter()
        painter.begin(self)
        self.draw_img(painter)
        painter.end()

    def draw_img(self, painter):
        painter.drawPixmap(self.point, self.scaled_img)

    def resizeEvent(self, e):
        self.point = QPoint(0, 0)
        self.update()

    def mouseMoveEvent(self, e):  # 重写移动事件
        if self.left_click:
            move_distance = e.pos() - self._startPos
            move_distance += self.global_shift * self.ratio
            delta_x, delta_y = move_distance.x(), move_distance.y()
            delta_x = min(max(delta_x, self.width() - self.img.width()*self.ratio), 0)
            delta_y = min(max(delta_y, self.height() - self.img.height()*self.ratio), 0)
            move_distance.setX(delta_x)
            move_distance.setY(delta_y)
            self.global_shift = move_distance / self.ratio
            self.point = QPoint(0, 0) + move_distance
            self.right_point = self.right_point + move_distance
            self._startPos = e.pos()
            if self.kp_move is not None:
                self.kp_move(self.ratio, self.global_shift)
            self.repaint()

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.left_click = True
            self._startPos = e.pos()

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.left_click = False

    def wheelEvent(self, e):
        cpoint = QPoint(e.x(), e.y())
        last_ratio = self.ratio
        if e.angleDelta().y() > 0:
            self.ratio = min(self.ratio + 0.1, MAX_SCALE)
        elif e.angleDelta().y() < 0:
            self.ratio = max(self.ratio - 0.1, MIN_SCALE)
        self.scaled_img = self.img.scaled(int(self.img.width() * self.ratio), int(self.img.height() * self.ratio))
        self.point = cpoint - (cpoint - self.point) * self.ratio / last_ratio
        self.global_shift = self.point / self.ratio
        delta_x = min(max(self.point.x(), self.width() - self.img.width() * self.ratio), 0)
        delta_y = min(max(self.point.y(), self.height() - self.img.height() * self.ratio), 0)
        self.point = QPoint(delta_x, delta_y)
        self.global_shift = self.point / self.ratio
        self.right_point = QPoint(self.scaled_img.height(), self.scaled_img.width()) + self.point
        if self.kp_move is not None:
            self.kp_move(self.ratio, self.global_shift)
        self.update_show_status()
        self.repaint()

    def bind_keypoints_move(self, rescale_shift):
        self.kp_move = rescale_shift