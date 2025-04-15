from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QWidget
from PyQt6.QtCore import Qt

from Fluent_Widgets_GUI.qfluentwidgets import (SubtitleLabel, setFont, PushButton, FluentIcon, CardWidget,
                                               SearchLineEdit, TransparentToolButton, SmoothScrollArea)

from rename_rules.rule_manager import load_config


class RuleListInterface(QFrame):
    """定义规则列表界面布局"""

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.setObjectName('RuleListInterface')

        """实例化各种控件"""
        self.totalWidget = QWidget(self)
        self.label = SubtitleLabel(text, self)
        self.addBtn = PushButton(FluentIcon.ADD, '添加规则')
        self.selectRuleBtn = PushButton(FluentIcon.CHECKBOX, '选中规则')
        self.searchLineEdit = SearchLineEdit()
        self.ruleView = QWidget(self.totalWidget)  # 额外新建一个容器存放规则展示区域
        self.ruleScrollArea = SmoothScrollArea()
        self.ruleScrollWidget = QWidget(self.ruleScrollArea)

        self.ruleCards = []
        self.currentIndex = -1

        """实例化布局器"""
        self.totalVBoxLayout = QVBoxLayout()
        self.widgetVLayout = QVBoxLayout(self.totalWidget)
        self.btnLayout = QHBoxLayout()  # 控制顶部规则编辑按钮的布局
        self.setLayout(self.totalVBoxLayout)  # 设置总布局器
        self.ruleCardLayout = QVBoxLayout(self.ruleScrollWidget)  # 规则卡片的垂直布局器

        """设置控件属性"""
        setFont(self.label, 30)
        self.addBtn.setFixedWidth(120)
        self.selectRuleBtn.setFixedWidth(120)
        self.searchLineEdit.setFixedWidth(300)
        self.searchLineEdit.setPlaceholderText('搜索规则名称')

        """设置控件对齐方式"""
        self.widgetVLayout.setSpacing(10)
        self.widgetVLayout.setContentsMargins(0, 0, 0, 0)
        self.widgetVLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.btnLayout.setSpacing(4)
        self.btnLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.ruleCardLayout.setSpacing(10)

        """将控件添加至布局器"""
        self.totalVBoxLayout.addWidget(self.totalWidget)
        self.widgetVLayout.addWidget(self.label, 0)
        self.widgetVLayout.addLayout(self.btnLayout, 0)
        self.widgetVLayout.addWidget(self.searchLineEdit, 0)
        self.btnLayout.addWidget(self.addBtn, 0)
        self.btnLayout.addWidget(self.selectRuleBtn, 0)

        """初始化规则卡片展示区域"""
        self.__initRuleList()

    def __initRuleList(self):
        self.ruleScrollArea.setWidget(self.ruleScrollWidget)
        self.ruleScrollArea.setWidgetResizable(True)
        self.ruleScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)  # 水平滚动条永远不显示

        self.widgetVLayout.addWidget(self.ruleScrollArea)

        rule_dict = load_config()
        rule_num = rule_dict['num']
        selected_index = rule_dict['selected_index']
        rule_list = rule_dict['rules']

        for rule in rule_list:
            type = rule['type']
            name = rule['name']
            desc = rule['desc']
            self.ruleCards.append(RuleCard(type, name, desc))  # 将规则以卡片的形式添加至列表

        for cards in self.ruleCards:
            self.ruleCardLayout.addWidget(cards, 0)


class RuleCard(CardWidget):
    """定义规则卡片"""

    def __init__(self, type, name, content, parent=None):
        super().__init__(parent)
        """定义规则属性"""
        self.type = type
        """定义各种控件"""
        self.titleLabel = SubtitleLabel(name, self)
        self.contentLabel = SubtitleLabel(content, self)
        self.moreBtn = TransparentToolButton(FluentIcon.MORE)

        """定义布局器"""
        self.mainHLayout = QHBoxLayout(self)
        self.labelLayout = QVBoxLayout()

        """设置布局器对齐方式"""
        self.labelLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.labelLayout.setSpacing(5)

        """设置控件属性"""
        self.setFixedHeight(73)  # 设置卡片高度
        self.moreBtn.setFixedSize(32, 32)

        """将控件添加至布局器"""
        self.mainHLayout.addLayout(self.labelLayout)
        self.mainHLayout.addWidget(self.moreBtn)
        self.labelLayout.addWidget(self.titleLabel)
        self.labelLayout.addWidget(self.contentLabel)
