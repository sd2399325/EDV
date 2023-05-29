import os
import re
import sys
import dateparser

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QMenu, QFileDialog, QSplitter, QTreeView, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QFrame

from overviewdata import read_excel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # self.setWindowTitle("测试")
        # self.initMenuBar()
        # self.initMainWindows()
        # self.showMaximized()
        # dataOver = read_excel("D:\\projects\\python\\DPT\\2021年10月\\1018\\试验说明\\32.9.16-20211018-中通道.xlsx")
        # self.root_folder_path = ""
        # self.search_input.textChanged.connect(self.filterTreeView)
        self.loadProjects("D:\\projects\\python\\DPT")





    def initMenuBar(self):
        """
        初始化菜单栏
        """
        # 创建菜单栏
        menu_bar = self.menuBar()

        # 创建文件菜单
        file_menu = menu_bar.addMenu("文件")
        open_folder_action = QAction("打开文件夹", self)
        open_folder_action.triggered.connect(self.openFolder)
        file_menu.addAction(open_folder_action)
        file_menu.addAction("保存")
        file_menu.addAction("退出")

        # 创建编辑菜单
        edit_menu = menu_bar.addMenu("编辑")
        edit_menu.addAction("复制")
        edit_menu.addAction("剪切")
        edit_menu.addAction("粘贴")

        # 创建帮助菜单
        help_menu = menu_bar.addMenu("帮助")
        help_menu.addAction("查看帮助")
        help_menu.addAction("关于")

    def initMainWindows(self):
        """
        初始化主窗口
        """
        splitter = QSplitter(self)

        # 创建左侧的TreeView控件
        self.tree_frame = QFrame()
        self.tree_frame.setFrameShape(QFrame.StyledPanel)  # 设置边框样式
        tree_layout = QVBoxLayout(self.tree_frame)
        self.search_input = QLineEdit()
        self.tree_view = QTreeView()
        tree_layout.addWidget(self.search_input)
        tree_layout.addWidget(self.tree_view)
        splitter.addWidget(self.tree_frame)

        # 创建右侧的TabWidget控件
        tab_widget = QTabWidget()
        tab_widget.addTab(QWidget(), "概述")
        tab_widget.addTab(QWidget(), "截屏")
        tab_widget.addTab(QWidget(), "录波")
        tab_widget.addTab(QWidget(), "报文")
        splitter.addWidget(tab_widget)

        # 设置QSplitter的布局方式为水平布局
        splitter.setOrientation(Qt.Horizontal)

        # 设置TreeView的宽度为TabWidget宽度的1/5
        splitter.setSizes([round(self.width() / 5), round(self.width() * 4 / 5)])

        self.setCentralWidget(splitter)

    def openFolder(self):
        """
        打开文件夹, 用于加载目录结构
        """
        folder_dialog = QFileDialog()
        folder_dialog.setFileMode(QFileDialog.DirectoryOnly)
        folder_dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        folder_path = folder_dialog.getExistingDirectory(self, "选择文件夹", ".")
        if folder_path:
            print("选择的文件夹路径:", folder_path)
            self.root_folder_path = folder_path  # 保存文件夹路径
            self.loadTreeView(folder_path)

    def loadTreeView(self, folder_path):
        """
        加载目录结构到QTreeView
        """
        model = QStandardItemModel()


        root_item = QStandardItem(os.path.basename(folder_path))
        root_item.setData(folder_path, Qt.UserRole)  # 设置根节点的路径属性
        root_item.setEditable(False)  # 设置根节点不可编辑
        model.appendRow(root_item)

        self.loadSubDirectories(root_item, folder_path)

        self.tree_view.setModel(model)
        self.tree_view.header().setVisible(False)
        self.tree_view.expandAll()

    def loadTreeView1(self, folder_path):
        pass

    def loadSubDirectories1(self, parent_item, projects_info):
        """
        递归加载子目录
        """
        if not projects_info:
            return None
        else:
           for first_key in projects_info.keys():
               item = QStandardItem(first_key)
               item.setData(first_key, Qt.UserRole)
               parent_item.appendRow(item)
               self.



    def loadSubDirectories(self, parent_item, folder_path, depth=2):
        """
        递归加载子目录
        """
        if depth <= 0:
            return

        for item_name in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item_name)

            if os.path.isdir(item_path):
                item = QStandardItem(item_name)
                item.setData(item_path, Qt.UserRole)  # 设置节点的路径属性
                parent_item.appendRow(item)
                self.loadSubDirectories(item, item_path, depth - 1)

    def filterTreeView(self, keyword):
        """
        模糊匹配目录树
        """
        if keyword:
            root_item = self.tree_view.model().item(0)
            if root_item:
                for i in range(root_item.rowCount()):
                    item = root_item.child(i)
                    self.filterItem(item, keyword)
        else:
            self.loadTreeView(self.root_folder_path)  # 加载最初的目录树

    def filterItem(self, item, keyword):
        """
        递归过滤目录树节点
        """
        if self.matchItem(item, keyword):
            index = item.index()
            self.tree_view.setRowHidden(index.row(), index.parent(), False)  # 设置节点可见
            self.tree_view.expand(index.parent())
            return True

        for i in range(item.rowCount()):
            child_item = item.child(i)
            if self.filterItem(child_item, keyword):
                index = child_item.index()
                self.tree_view.setRowHidden(index.row(), index.parent(), False)  # 设置节点可见
                self.tree_view.expand(index.parent())
                return True

        index = item.index()
        self.tree_view.setRowHidden(index.row(), index.parent(), True)  # 设置节点隐藏
        return False

    def matchItem(self, item, keyword):
        """
        判断节点是否与关键词匹配
        """
        item_text = item.text()
        if re.search(keyword, item_text, re.IGNORECASE):
            return True

        return False


    def loadProjects(self, folder_path):
        result = {}
        pattern = r'\d+\.\d+\.\d+'

        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            return result

        for root, dirs, files in os.walk(folder_path):
            for dir_name in dirs:
                if re.match(pattern, dir_name):
                    # 10.1.1 => 10 and 1.1
                    parts = dir_name.split(".", 1)
                    first_dir = parts[0]
                    secrond_dir = parts[1]
                    secrond_result = {}

                    if first_dir in result:
                        path1 = result[dir_name][first_dir]
                        path2 = os.path.join(root, dir_name)

                        new_path = self.compareDirs(path1, path2)
                        result[dir_name][first_dir] = new_path if new_path is not None else path1
                    else:
                        dir_path = os.path.join(root, dir_name)
                        secrond_result[secrond_dir] = dir_path
                        result[first_dir] = secrond_result

        return result

    def compareDirs(self, path1, path2):
        dir1_parent = os.path.dirname(os.path.dirname(os.path.dirname(path1)))
        dir2_parent = os.path.dirname(os.path.dirname(os.path.dirname(path2)))
        dir1_year_month = os.path.basename(dir1_parent)
        dir2_year_month = os.path.basename(dir2_parent)

        year_month1 = self.parse_year_month(dir1_year_month)
        year_month2 = self.parse_year_month(dir2_year_month)

        dir1_number = os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(path1))))
        dir2_number = os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(path2))))

        if year_month1 != year_month2:
            return path1 if year_month1 > year_month2 else path2
        else:
            return path1 if dir1_number > dir2_number else path2

    def parse_year_month(self, year_month):
        try:
            date = dateparser.parse(year_month, settings={"DATE_ORDER": "YMD"})
            return date.strftime("%Y-%m") if date else None
        except:
            return None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
