import os
import re
import sys
import dateparser

from PyQt5.QtCore import Qt, QAbstractTableModel
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QTableView, QMenu, QFileDialog, QSplitter, QTreeView, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QFrame

from openpyxl import load_workbook
from overviewdata import read_excel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("测试")
        self.initMenuBar()
        self.initMainWindows()
        self.showMaximized()
        self.root_folder_path = ""
        self.search_input.textChanged.connect(self.filterTreeView)

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
        self.tree_view.clicked.connect(self.treeItemClicked) # 点击事件

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

        # 增加QTablew

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
        model = QStandardItemModel()

        # 加载根目录
        root_item = QStandardItem(os.path.basename(folder_path))
        root_item.setData(folder_path, Qt.UserRole)  # 设置根节点的路径属性
        root_item.setEditable(False)  # 设置根节点不可编辑
        model.appendRow(root_item)

        dir_projects = self.loadProjects(folder_path)
        self.loadSubDirectories(root_item, dir_projects)

        self.tree_view.setModel(model)
        self.tree_view.header().setVisible(False)
        self.tree_view.expandAll()

    def loadSubDirectories(self, parent_item, projects_info):
        """
        递归加载子目录
        """
        if not projects_info:
            return None
        else:
           for first_key in projects_info.keys():
               # 加载第一层级目录，工程大项
               item = QStandardItem(first_key)
               item.setData(first_key, Qt.UserRole)
               parent_item.appendRow(item)

               for second_key in projects_info[first_key].keys():
                   # 加载第二层级目录，工程小项及路径属性
                   project_path = projects_info[first_key][second_key]
                   sub_Item = QStandardItem(second_key)
                   sub_Item.setData(project_path, Qt.UserRole)
                   item.appendRow(sub_Item)

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
        """
        加载目录下的所有工程信息
        @param folder_path: 目录路径
        @return: 有效试验数据字典
        """

        result = {}
        pattern = r'\d+\.\d+\.\d+'

        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            return result

        # 遍历目录下的所有文件夹 找到符合正则表达式的试验文件夹
        for root, dirs, files in os.walk(folder_path):
            for dir_name in dirs:
                if re.match(pattern, dir_name):
                    # 10.1.1 => 10 and 1.1 试验大组和试验小组拆分
                    parts = dir_name.split(".", 1)
                    first_dir = parts[0]
                    secrond_dir = parts[1]
                    secrond_result = {}

                    # 如果实验大组存在，判断实验小组是否存在，存在则比较路径，不存在则添加
                    if first_dir in result:
                        if secrond_dir in result[first_dir]:
                            path1 = result[first_dir][secrond_dir]
                            path2 = os.path.join(root, dir_name)

                            result_path = self.compareDirs(path1, path2)
                            new_path = result_path if result_path is not None else path1

                            result[first_dir][secrond_dir] = new_path.replace("\\", "/")
                        else:
                            dir_path = os.path.join(root, dir_name)
                            result[first_dir][secrond_dir] = dir_path.replace("\\", "/")
                    else:
                        dir_path = os.path.join(root, dir_name)
                        secrond_result[secrond_dir] = dir_path.replace("\\", "/")
                        result[first_dir] = secrond_result

        return result

    def compareDirs(self, path1, path2):
        """
        比较两个目录，返回最新的目录
        Args:
            path1 (str): 目录1的路径
            path2 (str): 目录2的路径

        Returns:
            str: 最新试验的目录路径
        """

        # 截取目录路径中的年月信息
        dir1_parent = os.path.dirname(os.path.dirname(os.path.dirname(path1)))
        dir2_parent = os.path.dirname(os.path.dirname(os.path.dirname(path2)))

        dir1_year_month = os.path.basename(dir1_parent)
        dir2_year_month = os.path.basename(dir2_parent)

        year_month1 = self.parse_year_month(dir1_year_month)
        year_month2 = self.parse_year_month(dir2_year_month)

        # 截取目录路径中的试验编号信息
        dir1_number = os.path.basename(os.path.dirname(os.path.dirname(path1)))
        dir2_number = os.path.basename(os.path.dirname(os.path.dirname(path2)))

        # 比较日期和试验编号，如果日期不同，返回日期最新的目录，如果日期相同，返回试验编号最大的目录
        if year_month1 != year_month2:
            return path1 if year_month1 > year_month2 else path2
        else:
            return path1 if dir1_number > dir2_number else path2

    def parse_year_month(self, year_month):
        """
        解析年月信息
        Args:
            year_month (str): 路径的年月信息

        Returns:
            str: xxxx-xx格式的年月信息
        """
        try:
            date = dateparser.parse(year_month, settings={"DATE_ORDER": "YMD"})
            return date.strftime("%Y-%m") if date else None
        except:
            return None

    def treeItemClicked(self, index):
        """树节点点击事件(二级节点，加载面板数据，状态栏显示当前文件路径)

        Args:
            index (_type_): 节点index
        """
        item = self.tree_view.model().itemFromIndex(index)
        if item.parent() and not item.hasChildren():
            # 仅处理二级节点（试验小项）的点击事件
            file_path = item.data(Qt.UserRole)
            # 获取试验名称
            project_name = os.path.basename(file_path)

            data = read_excel(file_path)  # 从 Excel 中读取数据，得到一个二维列表
            self.loadExcelData(data)  # 将数据加载到表格控件中

    def loadExcelData(self, excel_data):
        """
        将 Excel 数据加载到表格控件中
        @param excel_data: Excel 数据
        """
        # 清除表格中的数据
        widget = self.tab_widget.widget(0)
        for child in widget.children():
            if isinstance(child, QTableView):
                child.setParent(None)

        model = ExcelTableModel()
        table_view = QTableView()
        table_view.setModel(model)
        widget.layout().addWidget(table_view)

        for row in range(len(excel_data)):
            for col in range(len(excel_data[row])):
                item = QStandardItem(excel_data[row][col])
                model.setItem(row, col, item)

        table_view.resizeColumnsToContents()
        table_view.resizeRowsToContents()
        table_view.horizontalHeader().setStretchLastSection(True)
        table_view.verticalHeader().setSectionResizeMode(QTableView.ResizeToContents)


class ExcelTableModel(QStandardItemModel):
    """Excel model

    Args:
        QStandardItemModel (_type_): _description_
    """
    def __init__(self, parent=None):
        super().__init__(parent)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            item = self.itemFromIndex(index)
            if item:
                return item.text()

        return super().data(index, role)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.horizontalHeaderItem(section).text()
            elif orientation == Qt.Vertical:
                return self.verticalHeaderItem(section).text()

        return super().headerData(section, orientation, role)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
