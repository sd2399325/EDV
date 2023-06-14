import sys
import time
import json
import os
from pywinauto.application import Application

def get_config_file_path():
    # 获取当前执行的脚本文件路径
    script_path = sys.argv[0]
    # 获取脚本文件所在目录的路径
    script_dir = os.path.dirname(script_path)
    # 拼接config.json文件的路径
    config_file_path = os.path.join(script_dir, "config.json")
    return config_file_path

def run_tfrplot_tool(cfg_file_path):
    config_file_path = get_config_file_path()


    if os.path.exists(config_file_path):
        with open(config_file_path) as f:
            config_data = json.load(f)
            tfrplot_path = config_data.get("wave_app")

    # 启动 TFRplot 应用程序
    app = Application(backend='win32').start(tfrplot_path)

    # 等待应用程序完全启动
    # app.wait_cpu_usage_lower(threshold=0.5, timeout=30, usage_interval=1)

    # 获取 TFRplot 的主窗口
    main_window = app.window(title="TFRplot")
    main_window.set_focus()

    # 获取 TFRplot 进程ID
    pid = main_window.process_id()

    # 连接到指定进程ID的 TFRplot 应用程序
    app = Application(backend='win32').connect(process=pid)

    # 获取 TFRplot 的主窗口
    main_window = app.window(title="TFRplot")
    main_window.set_focus()

    # 使用快捷键 Ctrl+D 呼出加载 CFG 文件的窗体
    main_window.type_keys("^D")  # 模拟按下"Ctrl"键和"D"键

    # 延迟一段时间以确保文件对话框加载完成
    time.sleep(1)

    # 定位文件对话框并设置文件路径
    file_dialog = app.window(title="Select COMTRADE configuration file")
    file_dialog.set_focus()
    file_path_edit = file_dialog.child_window(class_name="Edit")
    file_path_edit.set_text(cfg_file_path)

    # 延迟一段时间以确保按钮可见并可以点击
    time.sleep(1)

    # 点击"Open"按钮
    file_dialog.type_keys("%O")  # 模拟按下"Ctrl"键和"D"键

if __name__ == "__main__":

        cfg_file_path = sys.argv[1]
        run_tfrplot_tool(cfg_file_path)