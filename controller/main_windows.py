from PyQt5.QtWidgets import (
    QMainWindow, QDesktopWidget, QToolTip, QLabel, QShortcut,
    QWidget, QPushButton, QApplication, QScrollArea, QVBoxLayout, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap, QKeySequence, QPalette
import numpy as np
from controller.key_points import Keypoint, KeyPointTable, KeypointsCluster
from os.path import join, basename
import sip

def move2center(self):
    screen_size = QDesktopWidget().screenGeometry()
    client_size = self.geometry()
    self.move((screen_size.width() - client_size.width()) / 2,
              (screen_size.height() - client_size.height()) / 2)

def move2centertop(self):
    screen_size = QDesktopWidget().screenGeometry()
    client_size = self.geometry()
    self.move((screen_size.width() - client_size.width()) / 2, 0)


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("关键点标注工具")
        self.setWindowIcon(QIcon("pic/title.png"))
        self.resize(1280, 720)
        move2center(self)
        QShortcut(QKeySequence(self.tr("b")), self, self.before)
        QShortcut(QKeySequence(self.tr("n")), self, self.next)

        self.sub_window = QWidget(self)
        self.sub_window.resize(1000, 640)
        self.sub_window.setWindowFlags(Qt.FramelessWindowHint)
        self.sub_window.setAutoFillBackground(True)
        palette = QPalette()  # 创建调色板类实例
        palette.setColor(QPalette.Window, Qt.black)
        self.sub_window.setPalette(palette)
        self.sub_window.move(0, 0)

        self.save_btn = QPushButton("保存", self)
        self.save_btn.resize(100, 50)
        self.save_btn.move(1100, 20)
        self.save_btn.clicked.connect(self._clicked_save_btn)

    def read_dir_images(self, dirname="./"):
        from glob import glob
        files = glob(join(dirname, "*"))
        self.images = []
        for file in files:
            if "png" in file or "jpg" in file or "jpeg" in file:
                self.images.append(file)
        self.idx = 0

    def mouseDoubleClickEvent(self, event):
        self.grabKeyboard()

    def read_labels(self, filename):
        self.image2pts = {}
        with open(filename) as f:
            lines = f.readlines()
            idx = 0
            while idx < len(lines):
                image_path = lines[idx].strip()
                pts = []
                idx += 1
                num_face = lines[idx].strip()
                idx += 1
                for _ in range(int(num_face)):
                    pt = np.array([float(pt) for pt in lines[idx].strip().split(" ")]).reshape(-1, 2)
                    pts.append(pt)
                    idx += 1
                self.image2pts[image_path] = pts

    def run(self):
        if len(self.images) == 0:
            print("空")
            return
        if hasattr(self, "image_label") and self.image_label is not None:
            sip.delete(self.image_label)
            sip.delete(self.scroll)
            sip.delete(self.vbox)
        self.image_label = QLabel(self.sub_window)

        file = self.images[self.idx]
        image = QPixmap(file)
        self.image_label.setPixmap(image)
        self.image_label.show()
        self.image_label.resize(image.size())
        self.image_label.move(0, 0)
        self.image_label.setFrameShape(QFrame.NoFrame)
        # 加滚动条
        self.scroll = QScrollArea()
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setWidget(self.image_label)
        self.vbox = QVBoxLayout()
        self.vbox.setContentsMargins(0, 0, 0, 0)
        self.vbox.addWidget(self.scroll)
        self.sub_window.setLayout(self.vbox)

        self.status = self.statusBar()
        self.status.showMessage("{}, {}x{}".format(file, image.width(), image.height()))

        image_name = basename(file)
        pts_list = self.image2pts[image_name]

        self.kp_cluster = KeypointsCluster(pts_list, self.image_label)

        self.kp_tabel = KeyPointTable(self.kp_cluster, self)
        self.kp_tabel.move(1020, 80)

    def next(self):
        self._save_keypoints(self.idx, True)
        self.idx += 1
        self.idx = min(len(self.images) - 1, self.idx)
        self.run()

    def _save_keypoints(self, idx, del_pts=False):
        anno = join("{}/{}.pts".format(self.save_dir, basename(self.images[idx]).rsplit(".")[0]))
        with open(anno, "w") as f:
            f.write("{}\n".format(self.images[idx]))
            results = self.kp_cluster.get_points_str()
            f.write("%d\n" % len(results))
            for result in results:
                f.write("%s\n" % result)

        if del_pts:
            del self.pts

    def _clicked_save_btn(self):
        self._save_keypoints(self.idx, False)

    def before(self):
        self.idx -= 1
        self.idx = max(0, self.idx)
        self.run()

    def set_out_dir(self, dir):
        from os import makedirs, path
        self.save_dir = dir
        if not path.exists(dir):
            makedirs(dir)

    def set_important_point(self, idx):
        print(idx)
        for i, pt in enumerate(self.pts[0]):
            if i == idx:
                print("找到了%d" % i)
                self.pts[0][i].mouseDoubleClickEvent(None)
            else:
                self.pts[0][i].set_important_point(False)