from PyQt5.QtWidgets import QLabel, QTableWidget, QPushButton, \
    QTableWidgetItem, QApplication, QHeaderView, QAbstractItemView
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPalette, QKeySequence, QPixmap, QPainter
from functools import partial


class ImageController(QLabel):
    def __init__(self, image_path, parent):
        super().__init__(parent)
        self.resize(parent.width(), parent.height())
        self.img = QPixmap(image_path)
        self.scaled_img = self.img.copy()
        self.point = QPoint(0, 0)
        self.left_point = QPoint(0, 0)
        self.right_point = QPoint(self.img.width(), self.img.height())
        self.ratio = 1.0

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
            delta_x, delta_y = move_distance.x(), move_distance.y()
            print("x", (delta_x, -self.left_point.x()), self.width() - self.right_point.x())
            print("y", (delta_y, -self.left_point.y()), self.height() - self.right_point.y())
            delta_x = max(min(delta_x, -self.left_point.x()), self.width() - self.right_point.x())
            delta_y = max(min(delta_y, -self.left_point.y()), self.height() - self.right_point.y())
            move_distance.setX(delta_x)
            move_distance.setY(delta_y)
            move_distance = move_distance
            self.point = self.point + move_distance
            self.left_point = self.left_point + move_distance
            self.right_point = self.right_point + move_distance
            self._startPos = e.pos()
            self.repaint()
            print()

    def mousePressEvent(self, e):
        # print(e.pos())
        if e.button() == Qt.LeftButton:
            self.left_click = True
            self._startPos = e.pos()

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.left_click = False
        elif e.button() == Qt.RightButton:
            self.point = QPoint(0, 0)
            self.scaled_img = self.img.scaled(self.size())
            self.repaint()

    def wheelEvent(self, e):
        if e.angleDelta().y() > 0:
            self.ratio = min(self.ratio + 0.1, 2.5)
        elif e.angleDelta().y() < 0:
            self.ratio = max(self.ratio - 0.1, 1)
        print("ratio {}".format(self.ratio))
        # 放大
        if self.ratio == 1:
            self.scaled_img = self.img.copy()
        else:
            self.scaled_img = self.img.scaled(int(self.img.width()*self.ratio), int(self.img.height()*self.ratio))
        self.point = QPoint(0, 0)
        self.left_point = QPoint(0, 0)
        self.right_point = QPoint(self.scaled_img.width(), self.scaled_img.height())
        self.repaint()

    def bind_keypoints_cluster(self, cluster):
        self.cluster = cluster