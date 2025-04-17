from PyQt6.QtGui import QPalette
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QWidget, QApplication
from PyQt6.QtCore import Qt

from Fluent_Widgets_GUI.qfluentwidgets import (SubtitleLabel, setFont, PushButton, FluentIcon, CardWidget,
                                               SearchLineEdit, TransparentToolButton, SmoothScrollArea, IconWidget,
                                               InfoBarIcon, Theme, isDarkTheme)
from ..common.config import cfg
from ..common.style_sheet import StyleSheet

from rename_rules.rule_manager import load_config, switch_rule


class RuleCard(CardWidget):
    """定义规则卡片"""

    def __init__(self, index, rule_dict, isActivated=False, parent=None):
        super().__init__(parent)
        """定义该卡片的属性"""
        self.index = index  # 记录该卡片在列表中的下标
        self.name = rule_dict["name"]
        self.desc = rule_dict["desc"]
        self.type = rule_dict["type"]
        self.keyFunctionDict = {k: v for k, v in rule_dict.items() if k not in ["type", "name", "desc"]}
        self.selected = False  # 初始状态为未被鼠标选中
        if isActivated:
            activateMessage = '已激活'
            activatedIcon = InfoBarIcon.SUCCESS
        else:
            activateMessage = ''
            activatedIcon = None

        """定义各种控件"""
        self.titleLabel = SubtitleLabel(self.name, self)
        self.contentLabel = SubtitleLabel(self.desc, self)
        self.isActivatedIcon = IconWidget(activatedIcon)
        self.isActivatedLabel = SubtitleLabel(activateMessage, self)
        self.isActivatedWidget = QWidget(self)
        self.moreBtn = TransparentToolButton(FluentIcon.MORE)

        """定义布局器"""
        self.mainHLayout = QHBoxLayout(self)
        self.activatedLayout = QHBoxLayout(self.isActivatedWidget)
        self.labelLayout = QVBoxLayout()

        """设置布局器对齐方式"""
        self.labelLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.activatedLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.activatedLayout.setSpacing(0)
        self.labelLayout.setSpacing(5)

        """设置控件属性"""
        self.setFixedHeight(73)  # 设置卡片高度
        setFont(self.titleLabel, 25)
        setFont(self.contentLabel, 16)
        setFont(self.isActivatedLabel, 15)
        self.isActivatedIcon.setFixedSize(20, 20)
        self.moreBtn.setFixedSize(32, 32)

        """将控件添加至布局器"""
        self.mainHLayout.addLayout(self.labelLayout)
        self.mainHLayout.addWidget(self.isActivatedWidget, 0, Qt.AlignmentFlag.AlignRight)
        self.mainHLayout.addWidget(self.moreBtn)
        self.labelLayout.addWidget(self.titleLabel)
        self.labelLayout.addWidget(self.contentLabel)
        self.activatedLayout.addWidget(self.isActivatedIcon)
        self.activatedLayout.addWidget(self.isActivatedLabel)

    def setCardSelected(self, isSelected: bool):
        """切换卡片的选中状态"""
        sys_color = QApplication.palette().color(QPalette.ColorRole.WindowText)  # 获取系统文本色

        if isSelected == self.selected:
            return

        self.selected = isSelected

        if not isSelected:
            self.setStyleSheet("background-color: transparent;")
        else:
            self.setStyleSheet(f'background-color: #0078d4;')


class RuleListInterface(QFrame):
    """定义规则列表界面布局"""

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.setObjectName('RuleListInterface')

        self.rule_dict = load_config()  # 加载规则

        """实例化各种控件"""
        self.totalWidget = QWidget(self)  # 总容器
        self.label = SubtitleLabel(text, self)
        self.addBtn = PushButton(FluentIcon.ADD, '添加规则')
        self.activateRuleBtn = PushButton(FluentIcon.COMPLETED, '激活规则')
        self.searchLineEdit = SearchLineEdit()
        self.ruleViewArea = QFrame(self.totalWidget)  # 额外新建一个容器作为规则展示区域
        self.ruleScrollArea = SmoothScrollArea()
        self.ruleScrollWidget = QWidget(self.ruleViewArea)  # 将所有规则卡片打包至该容器内

        """实例化布局器"""
        self.totalVBoxLayout = QVBoxLayout()
        self.widgetVLayout = QVBoxLayout(self.totalWidget)
        self.btnLayout = QHBoxLayout()  # 控制顶部规则编辑按钮的布局
        self.setLayout(self.totalVBoxLayout)  # 设置总布局器
        self.ruleCardLayout = QVBoxLayout(self.ruleScrollWidget)  # 规则卡片的垂直布局器
        self.ruleViewLayout = QHBoxLayout(self.ruleViewArea)  # 存放规则卡片区域

        """设置控件属性"""
        setFont(self.label, 30)
        self.addBtn.setFixedWidth(120)
        self.activateRuleBtn.setFixedWidth(120)
        self.searchLineEdit.setFixedWidth(300)
        self.searchLineEdit.setPlaceholderText('搜索规则名称')

        """设置控件对齐方式"""
        self.widgetVLayout.setSpacing(10)
        self.widgetVLayout.setContentsMargins(0, 0, 0, 0)
        self.widgetVLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.btnLayout.setSpacing(4)
        self.btnLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.ruleViewLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)  # 从左至右添加规则卡片区域和规则详情面板
        self.ruleCardLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.ruleCardLayout.setSpacing(7)

        """将控件添加至布局器"""
        self.totalVBoxLayout.addWidget(self.totalWidget)
        self.widgetVLayout.addWidget(self.label, 0)
        self.widgetVLayout.addLayout(self.btnLayout, 0)
        self.widgetVLayout.addWidget(self.searchLineEdit, 0)
        self.btnLayout.addWidget(self.addBtn, 0)
        self.btnLayout.addWidget(self.activateRuleBtn, 0)

        """初始化规则卡片展示区域"""
        self.ruleCardList = []
        self.currentIndex = -1  # 鼠标选中的卡片的下标
        self.initRuleViewArea()

        """实现控件功能"""
        self.achieve_functions()

    def initRuleViewArea(self):
        """初始化规则卡片显示区域"""
        self.ruleScrollArea.setWidget(self.ruleScrollWidget)  # 设置ruleScrollArea的父容器为ruleScrollWidget
        self.ruleScrollArea.setWidgetResizable(True)
        self.ruleScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)  # 水平滚动条永远不显示

        self.widgetVLayout.addWidget(self.ruleViewArea)
        self.ruleViewLayout.addWidget(self.ruleScrollArea)

        self.addRuleCard()  # 将规则卡片列表中的卡片添加到界面中

    def addRuleCard(self):
        """将规则卡片列表中的卡片添加到界面中"""
        rule_list = self.rule_dict['rules']
        selected_index = self.rule_dict['selected_index']

        index = 0
        for rule in rule_list:  # 将所有规则卡片添加至卡片列表，便于其他函数调用
            if index == selected_index:
                activated = True
            else:
                activated = False
            self.ruleCardList.append(RuleCard(index, rule, activated))  # 将规则以卡片的形式添加至列表
            index += 1

        for card in self.ruleCardList:
            self.ruleCardLayout.addWidget(card, 0)
            card.clicked.connect(lambda cardIndex=card.index: self.setSelected(cardIndex))  # 点击卡片后将对应卡片切换为选中状态

    def setSelected(self, index):
        """切换卡片选中状态"""
        if self.currentIndex >= 0:  # 先将当前已选中的卡片切换为未选中状态
            self.ruleCardList[self.currentIndex].setCardSelected(False)

        self.currentIndex = index
        self.ruleCardList[self.currentIndex].setCardSelected(True)  # 再将选中的卡片切换为选中状态

    def refreshRuleList(self):
        """刷新规则卡片界面"""
        for card in self.ruleCardList:
            self.ruleCardLayout.removeWidget(card)
        self.ruleCardList.clear()

        self.rule_dict = load_config()

        self.addRuleCard()

    def achieve_functions(self):
        """实现各控件功能"""

        """激活规则的按钮"""

        def activate_rule():
            index = self.currentIndex
            switch_rule(self.rule_dict, index)
            self.refreshRuleList()

        self.activateRuleBtn.clicked.connect(activate_rule)
