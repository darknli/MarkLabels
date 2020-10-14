from PyQt5.QtWidgets import QLabel, QTableWidget, QPushButton, QWidget, QVBoxLayout,\
    QHBoxLayout, QLineEdit, QMessageBox, QTableWidgetItem, QAbstractItemView
from PyQt5.QtCore import Qt
from math import ceil
from functools import partial

class TableWidget(QWidget):
    """
    带导航界面的table
    """
    def __init__(self, rows, cols, limit_num_page, parent):
        super(TableWidget, self).__init__(parent)
        self.rows, self.cols = rows, cols
        self.limit_num_page = limit_num_page

        self.backstage_value = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.now_idx_page = -1

    def setFont(self, font):
        [table.setFont(font) for table in self.table_list]
        self.homePage.setFont(font)
        self.prePage.setFont(font)
        self.curPage.setFont(font)
        self.nextPage.setFont(font)
        self.finalPage.setFont(font)
        self.totalPage.setFont(font)
        self.skipLable_0.setFont(font)
        self.skipPage.setFont(font)
        self.skipLabel_1.setFont(font)
        self.confirmSkip.setFont(font)

    def setHorizontalHeaderLabels(self, header):
        self.header = header

    def setItem(self, row, col, item):
        self.backstage_value[row][col] = item

    def setCellWidget(self, row, col, cell_widget):
        self.backstage_value[row][col] = cell_widget

    def cellChangedconnect(self, f):
        [table.cellChanged.connect(f) for table in self.table_list]

    def cellClickedconnect(self, f):
        [table.cellClicked.connect(f) for table in self.table_list]


    def columnCount(self):
        return self.table_list[int(self.curPage.text()) - 1].columnCount()

    def setPageController(self, page):
        """自定义页码控制器"""
        control_layout = QHBoxLayout()
        self.homePage = QPushButton("首页")
        self.prePage = QPushButton("<上一页")
        self.curPage = QLabel("1")
        self.nextPage = QPushButton("下一页>")
        self.finalPage = QPushButton("尾页")
        self.totalPage = QLabel("共" + str(page) + "页")
        self.skipLable_0 = QLabel("跳到")
        self.skipPage = QLineEdit()
        self.skipLabel_1 = QLabel("页")
        self.confirmSkip = QPushButton("确定")
        self.homePage.clicked.connect(partial(self.page_controller, "home"))
        self.prePage.clicked.connect(partial(self.page_controller, "pre", self.curPage.text()))
        self.nextPage.clicked.connect(partial(self.page_controller, "next", self.curPage.text()))
        self.finalPage.clicked.connect(partial(self.page_controller, "final", self.curPage.text()))
        self.confirmSkip.clicked.connect(partial(self.page_controller, "confirm", self.skipPage.text()))
        # control_layout.addStretch(1)
        control_layout.addWidget(self.homePage)
        control_layout.addWidget(self.prePage)
        control_layout.addWidget(self.curPage)
        control_layout.addWidget(self.nextPage)
        control_layout.addWidget(self.finalPage)
        control_layout.addWidget(self.totalPage)
        control_layout.addWidget(self.skipLable_0)
        control_layout.addWidget(self.skipPage)
        control_layout.addWidget(self.skipLabel_1)
        control_layout.addWidget(self.confirmSkip)
        # control_layout.addStretch(1)
        self.__layout.addLayout(control_layout)

    def showTotalPage(self):
        """返回当前总页数"""
        return int(self.totalPage.text()[1:-1])

    def page_controller(self, *signal):
        signal = list(signal)
        signal[1] = self.curPage.text()
        total_page = self.showTotalPage()
        if "home" == signal[0]:
            self.curPage.setText("1")
        elif "pre" == signal[0]:
            if 1 == int(signal[1]):
                QMessageBox.information(self, "提示", "已经是第一页了", QMessageBox.Yes)
                return
            self.curPage.setText(str(int(signal[1]) - 1))
        elif "next" == signal[0]:
            if total_page == int(signal[1]):
                QMessageBox.information(self, "提示", "已经是最后一页了", QMessageBox.Yes)
                return
            self.curPage.setText(str(int(signal[1]) + 1))
        elif "final" == signal[0]:
            self.curPage.setText(str(total_page))
        elif "confirm" == signal[0]:
            if total_page < int(signal[1]) or int(signal[1]) < 0:
                QMessageBox.information(self, "提示", "跳转页码超出范围", QMessageBox.Yes)
                return
            self.curPage.setText(signal[1])

        print(self.curPage.text())
        self.change_table_content()  # 改变表格内容
        self.repaint()

    def change_table_content(self):
        """根据当前页改变表格的内容"""
        cur_page = self.curPage.text()
        self.now_idx_page = int(cur_page) - 1
        self.reload_table(self.now_idx_page)

    def load_data(self):
        num_pages = ceil(self.rows / self.limit_num_page)
        self.__layout = QVBoxLayout()
        self.table_list = []
        for idx in range(num_pages):
            start_idx = idx * self.limit_num_page
            end_idx = min(len(self.backstage_value), start_idx + self.limit_num_page)
            col = self.cols
            row = min(self.rows, end_idx - start_idx)
            table = QTableWidget(row, col)
            table.setHorizontalHeaderLabels(self.header)
            for irow, idx in enumerate(range(start_idx, end_idx)):
                item_list = self.backstage_value[idx]
                for icol, item in enumerate(item_list):
                    if isinstance(item, QTableWidgetItem):
                        table.setItem(irow, icol, item)
                    else:
                        table.setCellWidget(irow, icol, item)
            table.verticalHeader().hide()
            for i in range(table.columnCount()):
                table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)

            self.__layout.addWidget(table)
            self.setLayout(self.__layout)
            self.table_list.append(table)

        self.setPageController(ceil(self.rows / self.limit_num_page))

    def reload_table(self, page_idx):
        for i, table in enumerate(self.table_list):
            if i == page_idx:
                table.show()
            else:
                table.hide()
        return

    def item(self, row, col):
        return self.table_list[self.now_idx_page].item(row, col)


class BulkIndexTabelWidget(QWidget):
    """
    带分页button的table
    """
    def __init__(self, rows, cols, limit_num_page, parent):
        super(BulkIndexTabelWidget, self).__init__(parent)
        self.rows, self.cols = rows, cols
        self.limit_num_page = limit_num_page
        self.num_pages = ceil(self.rows / self.limit_num_page)

        self.backstage_value = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.now_idx_page = 0

    def setFont(self, font):
        [table.setFont(font) for table in self.table_list]
        [btn.setFont(font) for btn in self.jump_pages]

    def setHorizontalHeaderLabels(self, header):
        self.header = header

    def setItem(self, row, col, item):
        self.backstage_value[row][col] = item

    def setCellWidget(self, row, col, cell_widget):
        self.backstage_value[row][col] = cell_widget

    def cellChangedconnect(self, f):
        [table.cellChanged.connect(f) for table in self.table_list]

    def cellClickedconnect(self, f):
        [table.cellClicked.connect(f) for table in self.table_list]


    def columnCount(self):
        return self.table_list[int(self.curPage.text()) - 1].columnCount()

    def setPageController(self):
        self.jump_pages = []
        for idx in range(self.num_pages):
            start_idx = idx * self.limit_num_page
            end_idx = min(start_idx + self.limit_num_page, self.rows)
            btn = QPushButton("{}~{}".format(start_idx, end_idx - 1), self)
            btn.clicked.connect(partial(self.page_controller, idx))
            btn.move(idx * 50, 0)
            btn.resize(60, 30)
            self.jump_pages.append(btn)
        self.page_controller(0)

    def page_controller(self, idx):
        self.now_idx_page = idx
        self.reload_table(idx)  # 改变表格内容
        self.repaint()

    def load_data(self):
        self.table_list = []
        for idx in range(self.num_pages):
            start_idx = idx * self.limit_num_page
            end_idx = min(len(self.backstage_value), start_idx + self.limit_num_page)
            col = self.cols
            row = min(self.rows, end_idx - start_idx)
            table = QTableWidget(row, col, self)
            if hasattr(self, "header"):
                table.setHorizontalHeaderLabels(self.header)
            for irow, idx in enumerate(range(start_idx, end_idx)):
                item_list = self.backstage_value[idx]
                for icol, item in enumerate(item_list):
                    if icol == 0:
                        item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                    if isinstance(item, QTableWidgetItem):
                        table.setItem(irow, icol, item)
                    else:
                        table.setCellWidget(irow, icol, item)
            table.verticalHeader().hide()
            table.setSelectionBehavior(QAbstractItemView.SelectRows)
            table.move(5, 30)
            table.resize(37 * self.cols, 600)
            for i in range(table.columnCount()):
                table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)
            self.table_list.append(table)

        self.setPageController()

    def reload_table(self, page_idx):
        for i, table in enumerate(self.table_list):
            if i == page_idx:
                table.show()
            else:
                table.hide()
        self.now_idx_page = page_idx

    def select(self, row):
        idx = row // self.limit_num_page
        real_row = row % self.limit_num_page
        self.reload_table(idx)
        self.table_list[self.now_idx_page].setCurrentCell(real_row, 0)

    def item(self, row, col):
        real_row = row % self.limit_num_page
        return self.table_list[self.now_idx_page].item(real_row, col)

from PyQt5.QtWidgets import QMainWindow, QApplication, QHeaderView
from PyQt5.QtGui import QPalette, QFont
import sys
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.resize(200, 800)
        self.t = BulkIndexTabelWidget(10, 2, 4, self)
        for i in range(10):
            for j in range(2):
                self.t.setItem(i, j, QTableWidgetItem("{},{}".format(i, j)))
        self.t.load_data()
        self.t.resize(600, 400)
        font = QFont()
        font.setFamily("Arial")  # 括号里可以设置成自己想要的其它字体
        font.setPointSize(10)
        self.t.setFont(font)
        # self.t.verticalHeader().hide()
        # for i in range(self.t.columnCount()):
        #     self.t.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)
        self.t.show()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())