import os
from PyQt5.QtWidgets import QWidget, QTreeView, QVBoxLayout
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt

class ComtradeViewWidget(QWidget):
    """ComtradeViewWidget 控件类，用于显示 comtrade 文件的内容"""
    def __init__(self, parent=None):
        super().__init__(parent)

        # 创建布局
        layout = QVBoxLayout(self)

        # 创建三个 QTreeView 控件
        self.time_tree = QTreeView()
        self.device_tree = QTreeView()
        self.waveform_tree = QTreeView()

        # 将三个 QTreeView 控件添加到布局中
        layout.addWidget(self.time_tree)
        layout.addWidget(self.device_tree)
        layout.addWidget(self.waveform_tree)

        # 设置 QTreeView 的默认属性
        self.time_tree.setExpandsOnDoubleClick(False)  # 禁止双击收起节点
        self.device_tree.setExpandsOnDoubleClick(False)
        self.waveform_tree.setExpandsOnDoubleClick(False)

    def load_time_folders(self, folder_path):
        # 清空时间列表
        time_model = QStandardItemModel()
        root_item = time_model.invisibleRootItem()
        root_item.setText("事件列表")

        # 遍历路径下的一层时间文件夹
        for folder_name in os.listdir(folder_path):
            folder_path = os.path.join(folder_path, folder_name)
            if os.path.isdir(folder_path):
                time_item = QStandardItem(folder_name)
                root_item.appendRow(time_item)

        # 设置时间列表的数据模型
        self.time_tree.setModel(time_model)
        self.time_tree.expandAll()  # 展开所有节点

