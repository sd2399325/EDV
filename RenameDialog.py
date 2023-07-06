import sys
import json
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QDialogButtonBox

class RenameDialog(QDialog):

    def __init__(self, current_name, project_path, root_path, level=True):
        super().__init__()
        self.setWindowTitle("重命名")
        self.setFixedSize(200, 200)  # 固定窗体大小
        self.layout = QVBoxLayout()

        # 创建标签和输入框
        self.label = QLabel("请输入新的工程名称：")
        self.line_edit = QLineEdit()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.line_edit)

        # 创建按钮
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

        self.setLayout(self.layout)

        # 保存当前名称和项目路径
        self.current_name = current_name
        self.project_path = project_path
        self.root_path = root_path
        self.level = level

    def accept(self):
        # 获取用户输入的新的工程名称
        new_name = self.line_edit.text()
        # 如果是跟新小项名称，则需要更新配置文件
        if self.level:
            # 更新配置文件中的路径信息
            with open('rename.json', 'r') as f:
                data = json.load(f)

            # 检查是否存在相同的 current_name 和 item_path
            if any(self.project_path == entry["file_path"] for entry in data):
                for entry in data[1:]:
                    if entry["file_path"] == self.project_path:
                        if entry["new_name"] == self.current_name:
                            entry["new_name"] = new_name
                            break
            else:
                # 添加新的重命名信息
                new_entry = {
                    "original_name": self.current_name,
                    "new_name": new_name,
                    "file_path": self.project_path,
                    "root_path": self.root_path
                }
                data.append(new_entry)

            # 更新 rename.json 文件
            with open('rename.json', "w") as f:
                json.dump(data, f, indent=4)

            super().accept()
        else:
            # 更新大项名称配置文件
            with open('renameProject.json', 'r') as f:
                data = json.load(f)
                if len(data) > 1 :
                    for entry in data[1:]:
                        # 检查是否是已经变更过一次的名称
                        if entry["root_path"] == self.root_path and entry["new_project_name"] == self.current_name:
                            entry["new_project_name"] = new_name
                            break
                        else:
                            # 添加新的重命名信息
                            new_entry = {
                                "original_project_name": self.current_name,
                                "new_project_name": new_name,
                                "root_path": self.root_path
                            }

                        data.append(new_entry)
                        break
                else:
                    new_entry = {
                        "original_project_name": self.current_name,
                        "new_project_name": new_name,
                        "root_path": self.root_path
                    }

                    data.append(new_entry)

            with open('renameProject.json', "w") as f:
                json.dump(data, f, indent=4)
            super().accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    current_name = "file1.txt"  # 当前名称
    project_path = "/path/to/file1.txt"  # 项目路径
    root_path = "/path/to"  # 根路径

    dialog = RenameDialog(current_name, project_path, root_path)
    dialog.exec_()

    sys.exit(app.exec_())
