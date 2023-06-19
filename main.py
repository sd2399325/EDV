import os
import json
import re
import sys
import threading


from excel import convert_excel_to_html, split_txt_line
from natsort import natsorted
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItem, QStandardItemModel, QPixmap, QIcon, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QTableView, QFileDialog, QSplitter, QTreeView, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QFrame, QLabel, QComboBox,QPushButton, QScrollArea,QMainWindow, QAbstractItemView,QHeaderView, QMenu
from PyQt5.QtWebEngineWidgets import QWebEngineView
from ComtradeWidget import ComtradeWidget
from SettingsDialog import SettingsDialog
from RenameDialog import RenameDialog



class MainWindow(QMainWindow):

    # 定义事件等级枚举值和对应的颜色
    event_levels_colors = {
        '正常': "#e4e4e4",
        '轻微': "#48D1CC",
        '报警': "#FFFF00",
        '严重告警': "#FF8C00",
        '紧急': "#FF0000"
    }

    global_png_dict = {}    # 当前所有图片路径字典
    global_now_png = ""     # 当前图片路径
    current_png_list = []    # 当前图片路径集合
    current_png_index = 0 # 记录当前图片路径在当前图片路径集合中的位置

    def __init__(self):
        super().__init__()


        self.setWindowTitle("测试")
        self.initMenuBar()
        self.initMainWindows()
        self.showMaximized()
        self.root_folder_path = ""
        self.temp_folder_path = ""

    def initMenuBar(self):
        """
        初始化菜单栏
        """
        # 创建菜单栏
        menu_bar = self.menuBar()

        # 创建文件菜单
        file_menu = menu_bar.addMenu("文件")
        open_folder_action = QAction("加载工程目录", self)
        open_folder_action.triggered.connect(self.openFolder)
        file_menu.addAction(open_folder_action)
        load_last_action = QAction("加载上次目录", self)
        load_last_action.triggered.connect(self.load_last_dirs)
        file_menu.addAction(load_last_action)
        setting_action = QAction("设置", self)
        setting_action.triggered.connect(self.openSetting)
        file_menu.addAction(setting_action)

        # 创建帮助菜单
        help_menu = menu_bar.addMenu("帮助")
        help_menu.addAction("查看帮助")
        help_menu.addAction("关于")

    def initMainWindows(self):
        """
        初始化主窗口
        """

        # 创建左侧的TreeView控件
        self.tree_frame = QFrame()
        self.tree_frame.setFrameShape(QFrame.StyledPanel)  # 设置边框样式
        self.tree_layout = QVBoxLayout(self.tree_frame)
        self.search_input = QLineEdit()
        self.tree_view = QTreeView()
        self.tree_layout.addWidget(self.search_input)
        self.tree_layout.addWidget(self.tree_view)
        self.tree_view.clicked.connect(self.treeItemClicked) # 点击事件
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu) # 设置右键菜单
        self.tree_view.customContextMenuRequested.connect(self.show_context_menu) # 右键点击事件
        self.search_input.textChanged.connect(self.filter_TreeView) # 输入框内容改变事件
        search_icon = QIcon("search.png")
        self.search_input.addAction(search_icon, QLineEdit.LeadingPosition)


        # 创建右侧的TabWidget控件
        self.tab_widget = QTabWidget(self)

        # 创建”概述“页控件
        self.webview = QWebEngineView()
        self.tab_widget.addTab(self.webview, "概述")


        # 创建“截屏”页控件
        self.screenshot_widget = QWidget()
        self.screenshot_layout = QVBoxLayout(self.screenshot_widget)

        # 添加显示图片的控件
        self.image_label = QLabel()
        self.image_label.setFixedSize(1440, 900)
        self.screenshot_layout.addWidget(self.image_label)

        # 添加下拉框，上下也按钮和显示页码的控件 的水平布局
        self.screenshot_control_layout = QHBoxLayout()
        self.screenshot_layout.addLayout(self.screenshot_control_layout)

        # 添加下拉框
        left_control_layout = QHBoxLayout()
        left_control_layout.setSpacing(15)
        step_switch_label = QLabel("步骤切换")
        step_switch_label.setMaximumWidth(300)
        interface_switch_label = QLabel("界面切换")
        interface_switch_label.setMaximumWidth(300)
        self.step_switch_dropdown = QComboBox()
        self.step_switch_dropdown.setMaximumWidth(300)
        self.interface_switch_dropdown = QComboBox()
        self.interface_switch_dropdown.setMaximumWidth(300)

        self.step_switch_dropdown.currentIndexChanged.connect(self.on_cbstep_changed)
        self.interface_switch_dropdown.currentIndexChanged.connect(self.on_cbinterface_changed)

        left_control_layout.addWidget(step_switch_label)
        left_control_layout.addWidget(self.step_switch_dropdown)
        left_control_layout.addWidget(interface_switch_label)
        left_control_layout.addWidget(self.interface_switch_dropdown)
        left_control_layout.addStretch()


        # 添加上下页按钮及显示页码的控件
        right_control_layout = QHBoxLayout()
        right_control_layout.setSpacing(15)
        self.prev_button = QPushButton("上一页")
        self.prev_button.setMaximumWidth(300)
        self.next_button = QPushButton("下一页")
        self.next_button.setMaximumWidth(300)
        self.page_label = QLabel()
        self.page_label.setMaximumWidth(300)

        self.tab_widget.addTab(self.screenshot_widget, "截屏")
        self.prev_button.clicked.connect(self.previous_image)
        self.next_button.clicked.connect(self.next_image)

        right_control_layout.addStretch() # 添加弹簧
        right_control_layout.addWidget(self.prev_button)
        right_control_layout.addWidget(self.page_label)
        right_control_layout.addWidget(self.next_button)

        self.screenshot_control_layout.addLayout(left_control_layout)
        self.screenshot_control_layout.addLayout(right_control_layout)

        self.comtrade_widget = ComtradeWidget("f")
        self.tab_widget.addTab(self.comtrade_widget, "录波")

        # 创建“报文”页控件
        self.message_model = QStandardItemModel()
        self.message_model.setHorizontalHeaderLabels(['时间', '主机', '系统告警', '事件等级', '报警组', '事件列表'])
        # 创建QTableView并设置数据模型
        self.message_table = QTableView()
        self.message_table.setModel(self.message_model)
        self.message_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.message_table.horizontalHeader().setStretchLastSection(True)
        self.message_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.message_table.verticalHeader().setVisible(False)
        self.tab_widget.addTab(self.message_table, "报文")
        # 设置Tab页上的字体样式
        self.tab_widget.setStyleSheet("QTabBar::tab { font-size: 16px; width: 100px; height: 30px; }")

        # 创建 QScrollArea 控件并将 tab_widget 放入其中
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.tab_widget)

        splitter = QSplitter(self)
        splitter.addWidget(self.tree_frame)
        splitter.addWidget(scroll_area)

        # 设置QSplitter的布局方式为水平布局
        splitter.setOrientation(Qt.Horizontal)

        # 设置TreeView的宽度为TabWidget宽度的1/5
        splitter.setSizes([self.width() * 0.20, self.width() * 0.80])

        self.setCentralWidget(splitter)

    def openSetting(self):
        dialog = SettingsDialog()
        dialog.exec_()

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
            self.temp_folder_path = os.path.join(folder_path, "temp")
            if not os.path.exists(self.temp_folder_path):
                os.mkdir(os.path.join(self.temp_folder_path))

    def loadTreeView(self, folder_path):
        model = QStandardItemModel()

        # 加载根目录
        # thread1 = threading.Thread(target=self.save_root_path, args=(folder_path))
        # thread1.start()
        # thread1.join()
        self.save_root_path(folder_path)

        root_item = QStandardItem(os.path.basename(folder_path))
        root_item.setData(folder_path, Qt.UserRole)  # 设置根节点的路径属性
        root_item.setEditable(False)  # 设置根节点不可编辑
        model.appendRow(root_item)
        dir_projects = self.loadProjects(folder_path)
        thread2 = threading.Thread(target=self.loadSubDirectories, args=(root_item, dir_projects))

        thread2.start()
        thread2.join()

        self.tree_view.setModel(model)
        self.tree_view.setEditTriggers(QTreeView.NoEditTriggers)
        self.tree_view.header().setVisible(False)
        self.tree_view.expandAll()

    def save_root_path(self, root_path):
        if not root_path:
            return

        # 更新配置文件中的路径信息
        with open('config.json', 'r+') as f:
            config = json.load(f)
            config['root_path'] = root_path
            f.seek(0)
            json.dump(config, f, indent=4)
            f.truncate()



    def loadSubDirectories(self, parent_item, projects_info):
        """
        递归加载子目录
        """
        if not projects_info:
            return None
        else:
           first_keys = natsorted(projects_info.keys())
           for first_key in first_keys:
               # 加载第一层级目录，工程大项
               item = QStandardItem(first_key)
               item.setData(first_key, Qt.UserRole)
               parent_item.appendRow(item)
               new_name_dic = self.change_dirc_keys(projects_info[first_key])
               sort_keys = natsorted(new_name_dic.keys())


               for second_key in sort_keys:
                   # 加载第二层级目录，工程小项及路径属性
                   project_path = new_name_dic[second_key]
                   sub_Item = QStandardItem(second_key)
                   sub_Item.setData(project_path, Qt.UserRole)
                   item.appendRow(sub_Item)

    def filter_TreeView(self, keyword):
        if keyword:
            # 获取根目录下的第一层节点。即工程大项节点。
            root_item = self.tree_view.model().item(0)
            for row in range(root_item.rowCount()):
                #遍历工程大项节点下的所有子节点，并隐藏不包含关键词的节点。
                level1_item = root_item.child(row)
                child_count = level1_item.rowCount()
                for child_row in range(level1_item.rowCount()):
                    level2_item = level1_item.child(child_row)
                    if keyword in level2_item.text():
                        self.show_item_with_keyword(level2_item, keyword)
                    else:
                        self.hide_item_without_keyword(level2_item)
                        child_count -= 1

                if child_count == 0 and keyword not in level1_item.text():
                    self.hide_item_without_keyword(level1_item)
        else:
            self.loadTreeView(self.root_folder_path)

    def show_item_with_keyword(self, item, keyword):
        index = item.index()
        self.tree_view.setRowHidden(index.row(), index.parent(), False)
        for row in range(item.rowCount()):
            child_item = item.child(row)
            if keyword not in child_item.text():
                self.hide_item_without_keyword(child_item)
            else:
                child_index = child_item.index()
                self.tree_view.setRowHidden(child_index.row(), child_index.parent(), False)

    def hide_item_without_keyword(self, item):
        index = item.index()
        self.tree_view.setRowHidden(index.row(), index.parent(), True)
        for row in range(item.rowCount()):
            child_item = item.child(row)
            self.hide_item_without_keyword(child_item)

    def keyword_in_children(self, parent_item, keyword):
        for i in range(parent_item.rowCount()):
            child_item = parent_item.child(i)
            text = child_item.text()
            if keyword in text:
                return True
        return False

    def loadProjects(self, folder_path):
        """
        加载目录下的所有工程信息
        """

        result = {}
        pattern_1 = r'.*试验说明.*'
        pattern_2 = r'\d+\.\d'
        pattern_3 = r'\d+\.\d+\.\d+'

        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            return result

        # 遍历目录下的所有文件夹 找到符合正则表达式的试验文件夹
        for root, dirs, files in os.walk(folder_path):
            for dir_name in dirs:
                if re.match(pattern_3, dir_name) or re.match(pattern_2, dir_name):
                    # 10.1.1 => 10 and 1.1 试验大组和试验小组拆分
                    parts = dir_name.split(".", 1)
                    first_dir = parts[0]
                    secrond_dir = parts[1]
                    secrond_result = {}

                    # 如果实验大组存在，判断实验小组是否存在，存在则比较路径，不存在则添加
                    if first_dir in result:
                        if secrond_dir in result[first_dir]:
                            path2 = os.path.normpath(os.path.join(root, dir_name)).replace("\\", "/")
                            # 清理试验说明路径
                            if re.search(pattern_1, path2):
                                continue

                            path1 = result[first_dir][secrond_dir]
                            result_path = self.compareDirs(path1, path2)
                            new_path = result_path if result_path is not None else path1

                            result[first_dir][secrond_dir] = new_path
                        else:
                            dir_path = os.path.normpath(os.path.join(root, dir_name))
                            # 清理试验说明路径
                            if re.search(pattern_1, dir_path):
                                continue

                            result[first_dir][secrond_dir] = dir_path.replace("\\", "/")
                    else:
                        dir_path = os.path.join(root, dir_name)
                        secrond_result[secrond_dir] = dir_path.replace("\\", "/")
                        result[first_dir] = secrond_result


        self.make_last_json(result)
        return result

    def load_last_dirs(self):
        """
        加载上次打开的目录
        """
        folder_path = self.load_root_path()
        if not folder_path:
            return

        if os.path.exists('lastdirs.json'):
            with open('lastdirs.json', 'r') as f:
                data = json.load(f)

            if data:
                # 加载根目录
                model = QStandardItemModel()
                root_item = QStandardItem(os.path.basename(folder_path))
                root_item.setData(folder_path, Qt.UserRole)  # 设置根节点的路径属性
                root_item.setEditable(False)  # 设置根节点不可编辑
                model.appendRow(root_item)

                thread = threading.Thread(target=self.loadSubDirectories, args=(root_item, data))
                thread.start()
                thread.join()

                self.tree_view.setModel(model)
                self.tree_view.setEditTriggers(QTreeView.NoEditTriggers)
                self.tree_view.header().setVisible(False)
                self.tree_view.expandAll()

    def load_root_path(self):
        # 读取配置文件中的路径信息
        with open('config.json', 'r') as f:
            config = json.load(f)
            wave_app = config.get('root_path')

        # 如果配置文件中存在路径信息，则显示在输入框中
        if wave_app:
            return wave_app
        else:
            return None

    def change_dir_name(self, path, dir_name):
        """
        读取重命名记录json，修改目录显示名称
        """
        result_name =""
        with open('rename.json', 'r') as f:
            data = json.load(f)

        for entry in data:
            if entry["original_name"] == dir_name and entry["file_path"] == path:
                result_name = entry["new_name"]

        return result_name if result_name else dir_name

    def change_dirc_keys(self, projetc_dic):
        if not projetc_dic:
            return None
        new_name_dic = {}
        for key in projetc_dic.keys():
            new_key = self.change_dir_name(projetc_dic[key], key)
            if key != new_key:
                new_name_dic[new_key] = projetc_dic[key]
            else:
                new_name_dic[key] = projetc_dic[key]

        return new_name_dic

    def make_last_json(self,  project_dir_dic):
        if os.path.exists('lastdirs.json'):
            os.remove('lastdirs.json')

         # 创建新的 JSON 文件
        with open("lastdirs.json", "w") as f:
            json.dump(project_dir_dic, f, indent=4)

    def compareDirs(self, path1, path2):
        """
        比较两个目录，返回最新的目录
        """

        year_month1 = ""
        year_month2 = ""
        number1 = ""
        number2 = ""
        pattern = r"(\d{4}-\d{1,2}月)/(\d{4})"
        match1 = re.search(pattern, path1)
        if match1:
            year_month1 = match1.group(1)
            number1 = match1.group(2)

        match2 = re.search(pattern, path2)
        if match2:
            year_month2 = match2.group(1)
            number2 = match2.group(2)


        # 比较日期和试验编号，如果日期不同，返回日期最新的目录，如果日期相同，返回试验编号最大的目录
        if year_month1 != year_month2:
            return path1 if year_month1 > year_month2 else path2
        else:
            return path1 if number1 > number2 else path2

    def treeItemClicked(self, index):
        """树节点点击事件(二级节点，加载面板数据，状态栏显示当前文件路径)
        """
        item = self.tree_view.model().itemFromIndex(index)
        if item.parent() and not item.hasChildren():
            # 仅处理二级节点（试验小项）的点击事件
            file_path = item.data(Qt.UserRole)
            self.global_png_dict ={}
            self.global_last_png = []
            self.global_next_png = []
            self.global_now_png = ""
            thread_step = threading.Thread(target=self.generate_step_options)
            thread_step.start()
            thread_step.join()

            wave_path = os.path.normpath(os.path.join(file_path, "wave"))
            thread_wave = threading.Thread(target=self.comtrade_widget.load_time_tree, args=(wave_path,))
            thread_wave.start()
            thread_wave.join()

            thread_data = threading.Thread(target=self.load_data_from_file, args=(file_path,))
            thread_data.start()
            thread_data.join()

            thread_screenshots = threading.Thread(target=self.load_screenshots_path, args=(file_path,))
            thread_screenshots.start()
            thread_screenshots.join()

            self.load_overview_data(file_path)

    def show_context_menu(self, pos):
        index = self.tree_view.indexAt(pos)
        item = self.tree_view.model().itemFromIndex(index)
        if index.isValid() and item.parent() and not item.hasChildren():
            menu = QMenu(self.tree_view)
            rename_action = menu.addAction("修改项目名称")
            rename_action.triggered.connect(self.rename_item)
            menu.exec_(self.tree_view.viewport().mapToGlobal(pos))

    def rename_item(self):
        selected_indexes = self.tree_view.selectedIndexes()
        if selected_indexes:
            index = selected_indexes[0]
            item = self.tree_view.model().itemFromIndex(index)
            currentname = item.text()
            path = index.data(Qt.UserRole)
            root_index = self.tree_view.model().index(0, 0)  # 获取根节点的索引
            root_path = self.tree_view.model().data(root_index, QtCore.Qt.UserRole)
            dialog = RenameDialog(currentname, path, root_path)
            dialog.exec_()

    def load_overview_data(self, project_path):
        """加载概述数据

        Args:
            file_path (str): 试验大项路径
        """
        # 拆解文件路径，获取文件名
        project_name = os.path.basename(project_path)
        root_path = os.path.dirname(os.path.dirname(project_path))
        excel_path = os.path.normpath(os.path.join(root_path, "试验说明"))
        # 读取excel文件并转存到指定目录的temp.html文件中
        overview_excel_path = self.join_excel_path(excel_path, project_name)
        if not overview_excel_path:
            return None

        if not os.path.exists(overview_excel_path):
            return None

        excel_html_path = os.path.normpath(os.path.join(self.temp_folder_path, "temp.html"))
        convert_excel_to_html(overview_excel_path, excel_html_path)

        # 加载temp.html文件
        html_file_path = os.path.abspath(excel_html_path)
        self.webview.load(QtCore.QUrl.fromLocalFile(html_file_path))
        self.webview.setZoomFactor(1.2)

    def join_excel_path(self, excel_path, project_name):
        for root, dirs, files in os.walk(excel_path):
            for file in files:
                if file.endswith('.xlsx') or file.endswith('.xls'):
                    if project_name == file.split('-')[0]:
                        project_excel_path = os.path.join(root, file)
                        return project_excel_path

        return None

    def generate_step_options(self):
        """生成下拉框的选项"""
        if not self.global_png_dict:
            return None

        # 清空步骤下拉框，防止重复添加，加载数据源并设置默认项
        self.step_switch_dropdown.clear()
        keys = self.global_png_dict.keys()
        self.step_switch_dropdown.addItems(keys)
        self.step_switch_dropdown.setCurrentIndex(0)

        key = next(iter(keys))
        values = self.global_png_dict[key]
        if values:
            category_keys = values.keys()
            if category_keys:
                self.interface_switch_dropdown.clear()
                self.interface_switch_dropdown.addItems(category_keys)
                # self.interface_switch_dropdown.setCurrentIndex(0)

                # 加载截屏文件
                category_key = next(iter(category_keys))
                self.current_png_list = values[category_key]
                self.current_png_index = 0
                self.update_page_label()

    def load_image(self):
        """加载截屏文件"""
        if not self.current_png_list:
            return

        current_png_path = self.current_png_list[self.current_png_index]
        self.load_screenshots_png(current_png_path)

    def load_screenshots_png(self, path):
        """根据路径加载截屏文件"""
        if not os.path.exists(path):
            return

        pixmap = QPixmap(path)

        if pixmap.isNull():
            return

        scaled_pixmap = pixmap.scaled(self.image_label.size(), aspectRatioMode=Qt.KeepAspectRatio)

        self.image_label.setPixmap(scaled_pixmap)

    def update_page_label(self):
        """更新页码信息"""
        page_text = f"{self.current_png_index + 1}/{len(self.current_png_list)}"
        self.page_label.setText(page_text)

    def load_screenshots_path(self, path):
        """加载所有截屏文件路径的字典"""
        step_png_dic = {}
        hmi_path = os.path.normpath(os.path.join(path, "HMI"))  # 拼接HMI路径

        # 遍历HMI文件夹下的所有文件夹-步骤信息
        for folder_name in os.listdir(hmi_path):
            png_dict = {}
            folder_path = os.path.normpath(os.path.join(hmi_path, folder_name))  # 拼接步骤信息路径

            # 判断当前路径是否为文件夹
            if not os.path.isdir(folder_path):
                continue

            for file_name in os.listdir(folder_path):
                if not file_name.endswith('.PNG'):  # 过滤非截屏文件
                    continue

                file_path = os.path.normpath(os.path.join(folder_path, file_name))  # 拼接截屏文件路径
                category = file_name.split('_')[0]  # 提取功能大类名称--画面切换数据源
                 # 将截屏文件路径添加到集合中
                if category not in png_dict:
                    file_paths = []
                    file_paths.append(file_path)
                    png_dict[category] = file_paths
                else :
                    value = png_dict[category]
                    value.append(file_path)
                    png_dict[category] = value  # 将截屏文件路径添加到集合中

            step_png_dic[folder_name] = png_dict

        self.global_png_dict = step_png_dic
        self.generate_step_options()
        return step_png_dic

    def previous_image(self):
        """上一页按钮点击事件"""
        if not self.current_png_list:
            return

        if self.current_png_index > 0:
            self.current_png_index -= 1
            self.load_image()
            self.update_page_label()

    def next_image(self):
        """下一页按钮点击事件"""
        if not self.current_png_list:
            return

        if self.current_png_index < len(self.current_png_list) - 1:
            self.current_png_index += 1
            self.load_image()
            self.update_page_label()

    def on_cbstep_changed(self):
        """步骤下拉框选中内容改变事件"""
        key = self.step_switch_dropdown.currentText()
        # 当发生改变的时候，联动界面切换下拉框
        if key in self.global_png_dict.keys():
            values = self.global_png_dict[key]
            if values:
                category_keys = values.keys()
                if category_keys:
                    self.interface_switch_dropdown.clear()
                    self.interface_switch_dropdown.addItems(category_keys)
                    current_category_key = self.interface_switch_dropdown.currentText()
                    self.current_png_list = values[current_category_key]
                    self.current_png_index = 0
                    self.update_page_label()

    def on_cbinterface_changed(self):
        """界面下拉框选中内容改变事件"""
        key = self.interface_switch_dropdown.currentText()
        if key:
            key_step = self.step_switch_dropdown.currentText()
            values = self.global_png_dict[key_step]
            now_path = values[key][0]
            self.load_screenshots_png(now_path)
            self.global_now_png = now_path
            self.current_png_list = values[key]
            self.current_png_index = 0
            self.update_page_label()

    def load_data_from_file(self, path):
        """读取报文文件内容"""

        # 拼接filename
        rowCount = self.message_model.rowCount()
        if rowCount > 0:
            self.message_model.removeRows(0,rowCount)

        project_name = os.path.basename(path)
        file_name = project_name + ".txt"
        txt_path = os.path.normpath(os.path.join(path, file_name))

        if not os.path.exists(txt_path):
            return None

        with open(txt_path, 'r', encoding='gb2312') as file:
            lines = file.readlines()
            lines = [line.strip() for line in lines]
            lines.pop(0)
            # 按时间先后排序
            lines.sort(key=lambda x: x.split()[0])
            for line in lines:
                items = split_txt_line(line, self.event_levels_colors)

                # 将QStandardItem添加到数据模型中
                self.message_model.appendRow(items)

    def tilePage(self):
        # 将页面缩放级别设置为100%（实际大小）
        self.webview.setZoomFactor(1.0)

        # 调整窗口大小以适应页面
        self.adjustSize()

        # 获取窗口的大小
        window_size = self.size()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
