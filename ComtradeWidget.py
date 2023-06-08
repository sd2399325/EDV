import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeView, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt

class ComtradeWidget(QWidget):
    def __init__(self, wave_path):
        super().__init__()

        # 创建主部件和布局
        main_layout = QHBoxLayout(self)

        # 创建三个垂直布局
        time_layout = QVBoxLayout()
        device_layout = QVBoxLayout()
        waveform_layout = QVBoxLayout()

        # 创建三个 QTreeView 控件和 QLabel 控件
        self.time_tree = QTreeView()
        self.device_tree = QTreeView()
        self.waveform_tree = QTreeView()

        time_label = QLabel("时间列表")
        device_label = QLabel("装置列表")
        waveform_label = QLabel("波形列表")

        # 设置标签的样式
        label_style = "background-color: lightblue; font-size: 14px; font-weight: bold; border-radius: 5px;"
        time_label.setStyleSheet(label_style)
        device_label.setStyleSheet(label_style)
        waveform_label.setStyleSheet(label_style)

        # 设置标签文本居中对齐
        time_label.setAlignment(Qt.AlignCenter)
        device_label.setAlignment(Qt.AlignCenter)
        waveform_label.setAlignment(Qt.AlignCenter)

        # 设置时间列表的根节点为 "事件列表"
        self.time_model = QStandardItemModel()
        root_item = self.time_model.invisibleRootItem()
        root_item.setEditable(False)
        root_item.setText("事件列表")

        # 设置 time_tree 的数据模型
        self.time_tree.setModel(self.time_model)
        self.time_tree.header().setVisible(False)
        self.time_tree.expandAll()  # 展开所有节点
        self.time_tree.setExpandsOnDoubleClick(False)  # 禁止双击收起节点

        # 自定义样式表，调整节点之间的间距和节点文字字体大小
        self.style_sheet = """
            QTreeView::item {
                padding: 8px;  /* 调整节点之间的间距 */
                font-size: 16px;  /* 调整节点文字的字体大小 */
            }
        """
        self.time_tree.setStyleSheet(self.style_sheet)

        # 设置节点点击事件的处理函数
        self.time_tree.clicked.connect(self.load_device_tree)
        self.device_tree.clicked.connect(self.load_waveform_tree)

        # 将控件添加到布局中
        time_layout.addWidget(time_label)
        time_layout.addWidget(self.time_tree)
        device_layout.addWidget(device_label)
        device_layout.addWidget(self.device_tree)
        waveform_layout.addWidget(waveform_label)
        waveform_layout.addWidget(self.waveform_tree)

        # 将垂直布局添加到主布局
        main_layout.addLayout(time_layout)
        main_layout.addLayout(device_layout)
        main_layout.addLayout(waveform_layout)

        # 加载时间列表的数据
        self.load_time_tree(wave_path)

    def load_time_tree(self, wave_path):
        if not os.path.isdir(wave_path):
            return

        # 清空时间列表的数据
        self.time_model.removeRows(0, self.time_model.rowCount())

        # 遍历路径下的一层时间文件夹
        for folder_name in os.listdir(wave_path):
            folder_path = os.path.join(wave_path, folder_name)
            if os.path.isdir(folder_path):
                time_item = QStandardItem()
                time_item.setTextAlignment(Qt.AlignCenter)  # 设置节点居中对齐
                time_item.setText(folder_name)  # 设置时间文件夹名称
                time_item.setData(folder_path, Qt.UserRole)  # 设置节点的绝对路径属性
                self.time_model.appendRow(time_item)

    def load_device_tree(self, index):
        waveform_model = QStandardItemModel()
        self.waveform_tree.setModel(waveform_model)

        # 获取点击的节点
        item = index.model().itemFromIndex(index)
        if item is None:
            return

        # 获取节点的绝对路径属性
        folder_path = item.data(Qt.UserRole)

        # 遍历文件夹路径下的文件夹，最多两层深度
        device_model = QStandardItemModel()
        device_root_item = device_model.invisibleRootItem()
        device_root_item.setEditable(False)

        for folder_name in os.listdir(folder_path):
            subfolder_path = os.path.join(folder_path, folder_name)
            if os.path.isdir(subfolder_path):
                device_item = QStandardItem()
                device_item.setTextAlignment(Qt.AlignCenter)
                device_item.setText(folder_name)
                device_item.setData(subfolder_path, Qt.UserRole)
                device_root_item.appendRow(device_item)

                # 遍历二级文件夹
                for subfolder_name in os.listdir(subfolder_path):
                    subfolder_path2 = os.path.join(subfolder_path, subfolder_name)
                    if os.path.isdir(subfolder_path2):
                        subfolder_item = QStandardItem()
                        subfolder_item.setTextAlignment(Qt.AlignCenter)
                        subfolder_item.setText(subfolder_name)
                        subfolder_item.setData(subfolder_path2, Qt.UserRole)
                        device_item.appendRow(subfolder_item)

        # 设置 device_tree 的数据模型
        self.device_tree.setModel(device_model)
        self.device_tree.header().setVisible(False)
        self.device_tree.setExpandsOnDoubleClick(False)
        self.device_tree.setStyleSheet(self.style_sheet)

    def load_waveform_tree(self, index):
        # 获取点击的节点
        item = index.model().itemFromIndex(index)
        if item is None:
            return

        # 判断节点的层级
        if item.parent() is None:
            # 一级节点，跳出
            return

        # 获取节点的绝对路径属性
        folder_path = item.data(Qt.UserRole)

        # 遍历文件夹路径下的文件夹和文件
        waveform_model = QStandardItemModel()
        waveform_root_item = waveform_model.invisibleRootItem()
        waveform_root_item.setEditable(False)

        for entry_name in os.listdir(folder_path):
            entry_path = os.path.join(folder_path, entry_name)
            entry_item = QStandardItem()
            entry_item.setTextAlignment(Qt.AlignCenter)
            entry_item.setText(entry_name)
            entry_item.setData(entry_path, Qt.UserRole)
            waveform_root_item.appendRow(entry_item)

        # 设置 waveform_tree 的数据模型
        self.waveform_tree.setModel(waveform_model)
        self.waveform_tree.header().setVisible(False)
        self.waveform_tree.setExpandsOnDoubleClick(False)
        self.waveform_tree.setStyleSheet(self.style_sheet)
