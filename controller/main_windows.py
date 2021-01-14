from PyQt5.QtWidgets import (
    QMainWindow, QDesktopWidget, QShortcut,
    QWidget, QPushButton, QFrame, QApplication
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QKeySequence, QPalette, QFont
import numpy as np
from controller.key_points import KeyPointTable, KeypointsCluster
from controller.picture import ImageController
from controller.data_labels import Labels
from os.path import join, basename, exists
from controller.slider import MySlide
from controller.message_box import MyMessageBox, MySimpleMessageBox
from tools.megvii import read_anno
import cv2
from controller.login import LoginWindow
from tools.transmission import DataManager
import sip
from glob import glob

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
        move2center(self)
        QShortcut(QKeySequence(self.tr("b")), self, self.before)
        QShortcut(QKeySequence(self.tr("n")), self, self.next)

        self.login_win = LoginWindow(self)

    def setup_ui(self):
        desktop = QApplication.desktop()

        # 获取显示器分辨率大小
        screenRect = desktop.screenGeometry()
        self.height = screenRect.height()
        self.width = screenRect.width()
        self.resize(self.width, self.height-60)
        self.move(0, 0)

        self.manager = DataManager()

        expand_width = self.width - 638
        self.sub_window = QWidget(self)
        self.sub_window.resize(expand_width, self.height-80)
        self.sub_window.setWindowFlags(Qt.FramelessWindowHint)
        self.sub_window.setAutoFillBackground(True)
        palette = QPalette()  # 创建调色板类实例
        palette.setColor(QPalette.Window, Qt.black)
        self.sub_window.setPalette(palette)
        self.sub_window.move(0, 0)

        self.save_btn = QPushButton("保存", self)
        font = QFont()
        font.setFamily("Arial")  # 括号里可以设置成自己想要的其它字体
        font.setPointSize(10)  # 括号里的数字可以设置成自己想要的字体大小
        self.save_btn.setFont(font)
        self.save_btn.resize(50, 30)
        expand_width += self.save_btn.width()
        self.save_btn.move(expand_width, 0)
        self.save_btn.clicked.connect(self._clicked_save_btn)

        self.show_number = QPushButton("显示编号", self)
        self.show_number.setFont(font)
        self.show_number.resize(70, 30)
        expand_width += self.show_number.width()
        self.show_number.move(expand_width, 0)
        self.show_number.clicked.connect(self._clicked_show_btn)

        self.adjust_bright_slide = MySlide(self)
        self.adjust_bright_slide.resize(100, 30)
        expand_width += self.adjust_bright_slide.width()
        self.adjust_bright_slide.move(expand_width, 0)
        self.adjust_bright_slide.bound_brightness(self._adjust_brightness)

        self.rotate_button = QPushButton(self)
        self.rotate_button.setStyleSheet("QPushButton{border-image: url(pic/rotate.png)}"
                                  "QPushButton:hover{border-image: url(pic/rotate.png)}" 
                                  "QPushButton:pressed{border-image: url(pic/rotate.png)}")

        self.rotate_button.resize(20, 20)
        expand_width += self.rotate_button.width()
        self.rotate_button.move(expand_width, 5)
        self.rotate_button.clicked.connect(self._clicked_rotate_btn)

        self.view_button = QPushButton("查看全貌", self)
        self.view_button.setFont(font)
        self.view_button.resize(65, 30)
        expand_width += self.view_button.width()
        self.view_button.move(expand_width, 0)
        self.view_button.clicked.connect(self._clicked_view_btn)

        self.before_button = QPushButton("上一个", self)
        self.before_button.setFont(font)
        self.before_button.resize(55, 30)
        expand_width += self.before_button.width()
        self.before_button.move(expand_width, 0)
        self.before_button.clicked.connect(self.check_before)
        self.before_button.show()

        self.next_button = QPushButton("下一个", self)
        self.next_button.setFont(font)
        self.next_button.resize(55, 30)
        expand_width += self.next_button.width()
        self.next_button.move(expand_width, 0)
        self.next_button.clicked.connect(self.check_next)
        self.next_button.show()

        self.upload_button = QPushButton("上传", self)
        self.upload_button.setFont(font)
        self.upload_button.resize(55, 30)
        expand_width += self.upload_button.width()
        self.upload_button.move(expand_width, 0)
        self.upload_button.clicked.connect(self.check_upload)
        self.upload_button.show()

        self.next_message = MyMessageBox("还没保存，确定下一个？", self.next)
        self.before_message = MyMessageBox("还没保存，确定上一个？", self.before)
        self.upload_message = MyMessageBox("还没保存任何数据或存在未查看数据，确定上传？", self.upload)
        self.upload_status_message = MySimpleMessageBox("还没保存任何数据，确定上传？")

        self.can_check = True
        self.face_idx = 0

    def _get_manager(self):
        self.manager = DataManager()

    def mouseDoubleClickEvent(self, event):
        self.grabKeyboard()

    def run(self):
        if not self.can_check:
            self._clicked_view_btn()
        if self.face_idx == 0:
            self.file, anno, self.face_num, self.total_face_num = self.manager.download_data()
            anno = read_anno(anno)
            self.landmark_list = []
            self.attr_list = []
            for single_face in anno:
                landmark = single_face["landmark"]
                self.landmark_list.append(np.array(landmark, dtype=float).reshape(-1, 2))
                self.attr_list.append(single_face["attributes"])

            # 读取固定数据打开此注释
            # landmark, vc = self._load_had_anno(self.file)
            # self.landmark_list.append(landmark)
            # self.attr_list.append({})

            if hasattr(self, "image_label") and self.image_label is not None:
                self._delete_controller(self.image_label)
                self._delete_controller(self.face_label)
                self._delete_controller(self.kp_cluster)
                self._delete_controller(self.kp_cluster)
                self.sub_window.repaint()
        self.image_label = ImageController(self.file, self.sub_window)
        self.image_label.show()
        self.image_label.move(0, 0)
        self.image_label.setFrameShape(QFrame.NoFrame)
        self.show_number.setText("显示编号")
        self.status = self.statusBar()
        self.status.showMessage("{}, {}x{}, ratio={}, {}/{}张".format(
            self.file, self.image_label.img.width(), self.image_label.img.height(), self.image_label.ratio,
            self.face_num, self.total_face_num
        ))

        w, h = self.image_label.image_size()
        self.kp_cluster = KeypointsCluster(self.landmark_list[self.face_idx], self.image_label, w, h)

        # 单设置是否可见，需要上面注释的代码
        # self.kp_cluster.set_vc(vc)
        self.image_label.bind_keypoints_move(self.kp_cluster.scale_loc)
        self.image_label.bind_show(self.update_message_status)

        self.kp_tabel = KeyPointTable(self.kp_cluster, self)
        self.kp_tabel.move(640, 25)

        self.face_label = Labels(self)
        self.face_label.move(880, 45)
        for name, value in self.attr_list[self.face_idx].items():
            self.face_label.set_label(name, value)

    def check_next(self):
        anno = join("{}/{}_{:02d}.pts".format(self.save_dir, basename(self.file).rsplit(".")[0], self.face_idx))
        if not exists(anno):
            # print("没保存过")
            # self.next_message.setWindowModality(Qt.ApplicationModal)
            self.next_message.show()
        else:
            self.next()

    def next(self):
        if self.face_idx < len(self.attr_list) - 1:
            self.face_idx += 1
            self.run()

    def _save_keypoints(self,):
        anno = join("{}/{}_{:02d}.pts".format(self.save_dir, basename(self.file).rsplit(".")[0], self.face_idx))
        with open(anno, "w") as f:
            f.write("{}\n".format(self.file))
            results = self.kp_cluster.get_points_str()
            f.write("%d\n" % len(results))
            for result in results:
                f.write("%s\n" % result)
            results = self.face_label.get_labels()
            for name, value in results.items():
                f.write("{}, {}\n".format(name, " ".join(value)))

    def check_upload(self):
        anno = join("{}/{}_*.pts".format(self.save_dir, basename(self.file).rsplit(".")[0]))
        anno_files = glob(anno)
        if len(anno_files) == 0 or self.face_idx < len(self.landmark_list) - 1:
            self.upload_message.show()
        else:
            self.upload()

    def upload(self):
        status = self.manager.upload_data()
        self.upload_status_message.show_info("上传成功" if status else "上传失败")
        if status:
            self.face_idx = 0
            self.run()

    def _clicked_save_btn(self):
        self._save_keypoints()

    def _clicked_show_btn(self):
        if "显示编号" == self.show_number.text():
            self.show_number.setText("隐藏编号")
            self.kp_cluster.show_number(True)
        else:
            self.show_number.setText("显示编号")
            self.kp_cluster.show_number(False)

    def _clicked_view_btn(self):
        if self.can_check:
            self.view_button.setText("关闭窗口")
            self.view_button.repaint()
            self.can_check = False
        else:
            cv2.destroyWindow("check")
            self.view_button.setText("查看全貌")
            self.view_button.repaint()
            self.can_check = True
            return
        image = cv2.imread(self.file)
        pts = self.kp_cluster.get_points_str()[0].split(" ")
        pts = np.array(pts).reshape(-1, 4).astype(float).astype(int)
        x1 = image.shape[1]
        y1 = image.shape[0]
        x2 = 0
        y2 = 0
        for pt in pts:
            x, y, v, c = pt
            if v == 0:
                cv2.circle(image, (round(x), round(y)), 1, (255, 0, 0), 1)
            else:
                cv2.circle(image, (round(x), round(y)), 1, (0, 255, 0), 1)
            x1 = min(x1, x)
            x2 = max(x2, x)
            y1 = min(y1, y)
            y2 = max(y2, y)
        w = x2 - x1
        h = y2 - y1
        expand_w = int(w * 0.1)
        expand_h = int(h * 0.1)
        x1 = max(x1 - expand_w, 0)
        y1 = max(y1 - expand_h, 0)
        x2 = min(x2 + expand_w, image.shape[1])
        y2 = min(y2 + expand_h, image.shape[0])
        image = image[y1:y2, x1: x2, :]
        cv2.namedWindow("check", cv2.WINDOW_NORMAL)
        cv2.imshow("check", image)
        cv2.waitKey()

    def _clicked_rotate_btn(self):
        self.image_label.rotate_image()
        self.kp_cluster.rotate90()

    def _adjust_brightness(self, v):
        self.image_label.adjust_brightness(v)

    def _clicked_withdraw_btn(self):
        self.kp_tabel.reset_point()

    def check_before(self):
        anno = join(
            "{}/{}_{:02d}.pts".format(self.save_dir, basename(self.file).rsplit(".")[0], self.face_idx))
        if not exists(anno):
            # self.before_message.setWindowModality(Qt.ApplicationModal)
            self.before_message.show()
        else:
            self.before()

    def before(self):
        self.face_idx -= 1
        if self.face_idx >= 0:
            self.run()
        else:
            self.face_idx = 0

    def set_out_dir(self, dir):
        from os import makedirs, path
        self.save_dir = dir
        if not path.exists(dir):
            makedirs(dir)

    def update_message_status(self):
        self.status.showMessage("{}, {}x{}, ratio={:.1f}, {}/{}张".format(
            self.file, self.image_label.img.width(), self.image_label.img.height(), self.image_label.ratio,
            self.face_num, self.total_face_num
        ))

    def _delete_controller(self, controller):
        if isinstance(controller, QWidget):
            sip.delete(controller)
            controller = None
        else:
            for sub_con in dir(controller):
                if isinstance(sub_con, QWidget):
                    sip.delete(sub_con)
                    sub_con = None
            del controller

    def _load_had_anno(self, file):
        filename = basename(file).split(".")[0]
        anno_list = glob("annotation/{}*.pts".format(filename))

        with open(anno_list[0]) as f:
            lines = f.readlines()
        pts = np.array(lines[2].split(" ")).reshape(-1, 4)
        return pts[:, :2].astype(np.float32), pts[:, 2:].astype(int)

