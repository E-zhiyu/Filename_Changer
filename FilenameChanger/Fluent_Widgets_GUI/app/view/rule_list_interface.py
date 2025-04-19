from PyQt6.QtGui import QPalette
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QWidget, QApplication
from PyQt6.QtCore import Qt

from FilenameChanger.Fluent_Widgets_GUI.qfluentwidgets import (SubtitleLabel, setFont, PushButton, FluentIcon,
                                                               CardWidget, SearchLineEdit, TransparentToolButton,
                                                               SmoothScrollArea, IconWidget, InfoBarIcon)

from FilenameChanger.rename_rules.rule_manager import load_config, switch_rule, del_rules
from Fluent_Widgets_GUI.qfluentwidgets import MessageBox


class RuleCard(CardWidget):
    """定义规则卡片"""

    def __init__(self, rule, isActive=False, parent=None):
        super().__init__(parent=parent)
        """定义该卡片的属性"""
        name = rule["name"]
        desc = rule["desc"]
        self.type = rule["type"]
        self.keyFunctionDict = {k: v for k, v in rule.items() if k not in ["type", "name", "desc"]}
        self.selected = False  # 初始状态为未被鼠标选中

        """卡片基本设置"""
        self.setFixedHeight(73)  # 设置卡片高度
        self.mainHLayout = QHBoxLayout(self)  # 设置卡片的主布局器（水平）

        """规则名和规则描述标签"""
        self.titleLabel = SubtitleLabel(text=name, parent=self)
        self.contentLabel = SubtitleLabel(text=desc, parent=self)
        self.labelLayout = QVBoxLayout()

        # 设置属性
        self.titleLabel.setStyleSheet('background-color:transparent')  # 将标签的背景色设为透明，防止选择卡片的时候影响美观
        self.contentLabel.setStyleSheet('background-color:transparent')  # 将标签的背景色设为透明，防止选择卡片的时候影响美观
        setFont(self.titleLabel, 25)
        setFont(self.contentLabel, 16)

        # 设置布局器对齐方式和间隔
        self.labelLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.labelLayout.setSpacing(5)

        # 添加控件到布局器
        self.labelLayout.addWidget(self.titleLabel)
        self.labelLayout.addWidget(self.contentLabel)
        self.mainHLayout.addLayout(self.labelLayout)  # 合并标签布局器至主布局器

        """激规则激活状态"""
        self.isActivatedWidget = QWidget(self)  # 定义存放图标和文本标签的容器
        self.activatedLayout = QHBoxLayout(self.isActivatedWidget)
        self.isActivatedIcon = IconWidget()  # 显示激活信息的图标
        self.isActivatedLabel = SubtitleLabel(text='', parent=self)

        setFont(self.isActivatedLabel, 15)
        self.isActivatedWidget.setStyleSheet('background-color:transparent')  # 将背景色设为透明，防止选择规则卡片的时候影响美观
        self.isActivatedIcon.setFixedSize(20, 20)
        self.activatedLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)  # 激活状态布局方式为左对齐
        self.activatedLayout.setSpacing(0)  # 完全取消激活状态布局器的控件间隔

        # 添加控件到布局器
        self.activatedLayout.addWidget(self.isActivatedIcon)
        self.activatedLayout.addWidget(self.isActivatedLabel)
        self.mainHLayout.addWidget(self.isActivatedWidget, 0, Qt.AlignmentFlag.AlignRight)

        """更多按钮"""
        self.moreBtn = TransparentToolButton(FluentIcon.MORE)
        self.moreBtn.setFixedSize(32, 32)
        self.mainHLayout.addWidget(self.moreBtn)

        self.setActive(isActive)

    def setCardSelected(self, isSelected: bool):
        """切换卡片的选中状态"""
        # sys_color = QApplication.palette().color(QPalette.ColorRole.WindowText)  # 获取系统文本色

        if isSelected == self.selected:
            return

        self.selected = isSelected

        if not isSelected:
            self.setStyleSheet("""
                QWidget {
                    background: transparent;
                    border-radius: 5px;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget {
                    background: #00c3dc;
                    border-radius: 5px;
                }
            """)

    def setActive(self, isActive: bool):
        """切换激活状态"""
        if isActive:
            self.isActivatedIcon.setIcon(InfoBarIcon.SUCCESS)
            self.isActivatedLabel.setText('已激活')
        else:
            self.isActivatedIcon.setIcon(None)
            self.isActivatedLabel.setText('')


class RuleListInterface(QFrame):
    """定义规则列表界面布局"""

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.setObjectName('RuleListInterface')
        self.rule_dict = load_config()  # 加载规则

        """界面基本布局设置"""
        self.totalWidget = QWidget(self)  # 总容器
        self.interfaceVLayout = QVBoxLayout()  # 整个界面的布局器
        self.setLayout(self.interfaceVLayout)  # 设置界面总布局器（不是总容器的布局器）
        self.widgetVLayout = QVBoxLayout(self.totalWidget)  # 总容器的布局器

        self.widgetVLayout.setSpacing(10)
        self.widgetVLayout.setContentsMargins(0, 0, 0, 0)
        self.widgetVLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.interfaceVLayout.addWidget(self.totalWidget)  # 将总容器添加至界面布局器

        """界面标题标签"""
        self.label = SubtitleLabel(text, self)
        setFont(self.label, 30)

        self.widgetVLayout.addWidget(self.label, 0)  # 将标签添加至总容器的布局器

        """功能按钮"""
        self.addBtn = PushButton(FluentIcon.ADD, '添加规则')
        self.activateRuleBtn = PushButton(FluentIcon.COMPLETED, '激活规则')
        self.delRuleBtn = PushButton(FluentIcon.DELETE.icon(color='red'), '删除规则')
        self.btnLayout = QHBoxLayout()  # 控制顶部规则编辑按钮的布局

        self.btnLayout.setSpacing(4)
        self.btnLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)  # 按钮布局器默认左对齐

        self.btnLayout.addWidget(self.addBtn, 0)
        self.btnLayout.addWidget(self.activateRuleBtn, 0)
        self.btnLayout.addWidget(self.delRuleBtn, 0)
        self.widgetVLayout.addLayout(self.btnLayout, 0)  # 将按钮布局器合并至总容器的布局器

        """搜索框"""
        self.searchLineEdit = SearchLineEdit()  # 实例化搜索框

        self.searchLineEdit.setFixedWidth(300)
        self.searchLineEdit.setPlaceholderText('搜索规则名称')  # 设置输入提示语

        self.widgetVLayout.addWidget(self.searchLineEdit, 0)  # 将搜索框添加至总容器布局器

        """规则卡片展示区域"""
        self.ruleScrollArea = SmoothScrollArea(self.totalWidget)  # 创建平滑滚动区域
        self.ruleCardWidget = QWidget(self.ruleScrollArea)  # 创建存放所有规则卡片的容器
        self.ruleCardLayout = QVBoxLayout(self.ruleCardWidget)  # 规则卡片的垂直布局器

        self.ruleScrollArea.setWidget(self.ruleCardWidget)  # 将规则卡片容器放入滚动区域，使其可以滚动

        # 去掉滚动区域的黑色边框
        # self.ruleScrollArea.enableTransparentBackground()

        self.ruleCardLayout.setAlignment(Qt.AlignmentFlag.AlignTop)  # 设置卡片对齐方式为顶对齐
        self.ruleCardLayout.setSpacing(7)  # 设置卡片布局器间隔：每个卡片间隔距离为7

        """初始化规则卡片展示区域"""
        self.ruleCardList = []  # 存放规则卡片的列表
        self.currentIndex = -1  # 当前鼠标选中的卡片的下标
        self.initRuleViewArea()

        """实现控件功能"""
        self.achieve_functions()

    def initRuleViewArea(self):
        """初始化规则卡片显示区域"""
        self.ruleScrollArea.setWidgetResizable(True)
        self.ruleScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)  # 水平滚动条永远不显示

        self.widgetVLayout.addWidget(self.ruleScrollArea)

        self.addRuleCard()  # 将规则卡片列表中的卡片添加到界面中

    def addRuleCard(self):
        """将规则卡片列表中的卡片添加到界面中"""
        rule_list = self.rule_dict['rules']
        selected_index = self.rule_dict['selected_index']

        index = 0
        for rule in rule_list:  # 添加至卡片列表，便于其他函数调用
            if index == selected_index:
                activated = True
            else:
                activated = False
            self.ruleCardList.append(RuleCard(rule, activated))  # 将规则以卡片的形式添加至卡片列表
            index += 1

        for card in self.ruleCardList:
            self.ruleCardLayout.addWidget(card, 0)  # 依此将卡片添加至卡片布局器中
            card.clicked.connect(
                lambda cardIndex=self.ruleCardList.index(card): self.setSelected(cardIndex))  # 将点击卡片的动作连接至选中卡片函数

    def setSelected(self, index):
        """
        切换卡片选中状态
        参数 index：调用该方法的卡片下标，即鼠标点击的卡片下标
        """
        if self.currentIndex >= 0:  # 先将当前已选中的卡片切换为未选中状态
            self.ruleCardList[self.currentIndex].setCardSelected(False)

        self.currentIndex = index
        self.ruleCardList[self.currentIndex].setCardSelected(True)  # 再将选中的卡片切换为选中状态

    def achieve_functions(self):
        """实现各控件功能的方法"""

        def activate_rule_callback():
            """切换激活的规则"""
            if self.currentIndex != -1:  # 防止用户在未选择卡片的时候点击激活按钮而产生BUG
                # 将旧的规则卡片设置为未激活
                current_index = self.rule_dict['selected_index']
                self.ruleCardList[current_index].setActive(False)

                index = self.currentIndex
                switch_rule(self.rule_dict, index)  # 切换规则并保存至配置文件

                # 并新的规则卡片设置为已激活
                current_index = self.rule_dict['selected_index']
                self.ruleCardList[current_index].setActive(True)

        self.activateRuleBtn.clicked.connect(activate_rule_callback)

        def del_rule_callback():
            """删除规则"""
            if self.currentIndex != -1:  # 防止没有选择规则就删除规则
                confirm_window = MessageBox('删除规则', '确认删除选中的规则吗？', parent=self)
                confirm_window.yesButton.setText('确认')
                confirm_window.cancelButton.setText('取消')
                confirm_window.show()

                if confirm_window.exec():
                    for card in self.ruleCardList:
                        self.ruleCardLayout.removeWidget(card)
                    self.ruleCardList.clear()

                    flag = del_rules(self.rule_dict, self.currentIndex)
                    self.currentIndex = -1

                    self.addRuleCard()

                if flag == 1:
                    title = '成功'
                    message = '已删除选中的规则'
                elif flag == 0:
                    title = '失败'
                    message = '无法删除最后一个规则'
                message_window = MessageBox(title=title, content=message, parent=self)
                message_window.yesButton.setText('确认')
                message_window.cancelButton.hide()
                message_window.show()
                message_window.exec()

        self.delRuleBtn.clicked.connect(del_rule_callback)
