# coding:utf-8
from FilenameChanger.Fluent_Widgets_GUI.qfluentwidgets import (qconfig, QConfig, OptionsConfigItem, OptionsValidator,
                                                               ConfigItem, BoolValidator)

from FilenameChanger import config_path


class Config(QConfig):
    """应用的设置项"""

    # 主窗口
    dpiScale = OptionsConfigItem(
        "MainWindow", "DpiScale", "Auto", OptionsValidator([1, 1.25, 1.5, 1.75, 2, "Auto"]), restart=True)

    # 重命名设置项
    folderMode = ConfigItem('RenameConfigs', 'FolderMode', False, BoolValidator())
    secureScanning = ConfigItem('RenameConfigs', 'secureScanning', True, BoolValidator())


cfg = Config()
qconfig.load(config_path, cfg)
