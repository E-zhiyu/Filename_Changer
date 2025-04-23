from PyQt6.QtWidgets import QFrame


class InfoInterface(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName('InfoInterface')  # 设置对象名
