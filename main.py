from controller.main_windows import MainWindow
from PyQt5.QtWidgets import QApplication
from tools.transmission import ANNOTATION_DIRECTORY

if __name__ == '__main__':
    app = QApplication([])
    main_win = MainWindow()
    main_win.set_out_dir(ANNOTATION_DIRECTORY)
    main_win.run()
    app.exec_()