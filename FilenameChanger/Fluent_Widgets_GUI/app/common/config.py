# coding:utf-8
import sys
from enum import Enum
from pathlib import Path

from PyQt6.QtCore import QLocale
from FilenameChanger.Fluent_Widgets_GUI.qfluentwidgets import (qconfig, QConfig, ConfigItem, OptionsConfigItem,
                                                               BoolValidator,
                                                               OptionsValidator, RangeConfigItem, RangeValidator,
                                                               FolderListValidator, Theme, ConfigSerializer,
                                                               __version__)

from FilenameChanger import config_path

'''class Language(Enum):
    """ Language enumeration """

    CHINESE_SIMPLIFIED = QLocale(QLocale.Language.Chinese, QLocale.Country.China)
    CHINESE_TRADITIONAL = QLocale(QLocale.Language.Chinese, QLocale.Country.HongKong)
    ENGLISH = QLocale(QLocale.Language.English)
    AUTO = QLocale()'''

'''class LanguageSerializer(ConfigSerializer):
    """ Language serializer """

    def serialize(self, language):
        return language.value.name() if language != Language.AUTO else "Auto"

    def deserialize(self, value: str):
        return Language(QLocale(value)) if value != "Auto" else Language.AUTO'''


def isWin11():
    return sys.platform == 'win32' and sys.getwindowsversion().build >= 22000


class Config(QConfig):
    """应用的设置项"""

    '''# folders
    musicFolders = ConfigItem(
        "Folders", "LocalMusic", [], FolderListValidator())'''

    # main window
    '''micaEnabled = ConfigItem("MainWindow", "MicaEnabled", isWin11(), BoolValidator())'''
    dpiScale = OptionsConfigItem(
        "MainWindow", "DpiScale", "Auto", OptionsValidator([1, 1.25, 1.5, 1.75, 2, "Auto"]), restart=True)
    '''language = OptionsConfigItem(
        "MainWindow", "Language", Language.AUTO, OptionsValidator(Language), LanguageSerializer(), restart=True)'''

    # Material
    '''blurRadius = RangeConfigItem("Material", "AcrylicBlurRadius", 15, RangeValidator(0, 40))'''

    # software update
    '''checkUpdateAtStartUp = ConfigItem("Update", "CheckUpdateAtStartUp", True, BoolValidator())'''


cfg = Config()
cfg.themeMode.value = Theme.AUTO
qconfig.load(Path(config_path), cfg)
