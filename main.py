from controller.main_windows import MainWindow
from PyQt5.QtWidgets import QApplication

# 开始索引
start_idx = 132


if __name__ == '__main__':
    app = QApplication([])
    main_win = MainWindow()
    main_win.show()
    # main_win.read_dir_images("data", start_idx)
    # main_win.read_labels("data/sublabels")
    main_win.read_data("关键点标注数据default/表情", start_idx)
    main_win.set_out_dir("anno")
    main_win.run()
    app.exec_()