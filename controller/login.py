from PyQt5.QtWidgets import QLineEdit, QPushButton, \
    QLabel, QWidget, QApplication, QMessageBox

CACHE_DIR = "./cache"

def login():
    """
    缺省，等待服务端正式连接
    :return:
    """
    pass

class LoginWindow(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.title_label = QLabel("登录", self)
        self.user_label = QLabel("用户名", self)
        self.password_label = QLabel("密码", self)
        self.user_txt = QLineEdit(self)
        self.password_txt = QLineEdit(self)
        self.login_btn = QPushButton("登录", self)

        self.resize(300, 200)
        self.move(600, 400)
        self.title_label.move(130, 10)
        self.user_label.move(30, 60)
        self.user_txt.move(100, 60)
        self.password_label.move(30, 90)
        self.password_txt.move(100, 90)
        self.login_btn.move(130, 140)

        self.login_btn.clicked.connect(self._login_btn_clicked)

    def _login_btn_clicked(self):
        print("登录了")
        user_name, user_password = self.user_txt.text(), self.password_txt.text()
        print("用户{}\n密码{}".format(user_name, user_password))
        if login() is None:
            QMessageBox.information(self, "登录消息", "登录失败，用户名或密码错误!")
        else:
            QMessageBox.information(self, "登录消息", "登陆成功!")
            self.save_user_info(user_name, user_password)

    def save_user_info(self, user_name, user_password):
        import os
        if not os.path.isdir(CACHE_DIR):
            os.makedirs(CACHE_DIR)

        with open(os.path.join(CACHE_DIR, "user_info.txt")) as f:
            f.write("{}\n{}".format(user_name, user_password))


if __name__ == '__main__':
    app = QApplication([])
    window = LoginWindow(None)
    window.show()
    app.exec_()