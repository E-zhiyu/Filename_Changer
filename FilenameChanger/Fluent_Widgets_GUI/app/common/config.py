# coding:utf-8
from FilenameChanger.Fluent_Widgets_GUI.qfluentwidgets import (qconfig, QConfig, OptionsConfigItem, OptionsValidator)

from FilenameChanger import config_path


class Config(QConfig):
    """应用的设置项"""

    # main window
    dpiScale = OptionsConfigItem(
        "MainWindow", "DpiScale", "Auto", OptionsValidator([1, 1.25, 1.5, 1.75, 2, "Auto"]), restart=True)


cfg = Config()
qconfig.load(config_path, cfg)
