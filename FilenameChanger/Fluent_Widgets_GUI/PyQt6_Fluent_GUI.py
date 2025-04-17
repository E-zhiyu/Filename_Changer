# coding:utf-8
import os
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

from FilenameChanger.Fluent_Widgets_GUI.app.common.config import cfg
from FilenameChanger.Fluent_Widgets_GUI.app.view.main_window import MainWindow

# 启用DPI比例
if cfg.get(cfg.dpiScale) != "Auto":
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
    os.environ["QT_SCALE_FACTOR"] = str(cfg.get(cfg.dpiScale))


def run_with_gui():
    # 创建应用程序
    app = QApplication(sys.argv)
    app.setAttribute(Qt.ApplicationAttribute.AA_DontCreateNativeWidgetSiblings)

    # 创建主窗口
    w = MainWindow()
    w.show()

    app.exec()
