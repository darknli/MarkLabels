from controller.main_windows import MainWindow
from PyQt5.QtWidgets import QApplication

if __name__ == '__main__':
    app = QApplication([])
    main_win = MainWindow()
    main_win.show()
    main_win.read_dir_images("data")
    main_win.read_labels("data/sublabels")
    main_win.set_out_dir("anno")
    main_win.run()
    app.exec_()