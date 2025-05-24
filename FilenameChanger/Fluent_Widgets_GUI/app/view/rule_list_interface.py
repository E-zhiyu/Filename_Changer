import re

from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QButtonGroup, QFrame
from PyQt6.QtCore import Qt, pyqtSignal, QRegularExpression, QPoint, QTimer, QDate

from FilenameChanger.Fluent_Widgets_GUI.qfluentwidgets import (SubtitleLabel, setFont, PushButton, FluentIcon,
                                                               CardWidget, TransparentToolButton, SmoothScrollArea,
                                                               IconWidget, InfoBarIcon, MessageBox, ComboBox,
                                                               MessageBoxBase, LineEdit, RadioButton, CheckBox,
                                                               RoundMenu, Action, BodyLabel, TextBrowser, ZhDatePicker,
                                                               InfoBar, InfoBarPosition, setCustomStyleSheet,
                                                               ToolTipFilter, ToolTipPosition, themeColor, isDarkTheme)

from FilenameChanger.rename_rules.rule_manager import (load_rule, switch_rule, del_rules, save_new_rule, analise_rule,
                                                       revise_rule)

from FilenameChanger.log.log_recorder import *

rule_help_md = """\
## 1.交换分隔符前后内容
- 功能：交换指定分隔符或字符串前后的内容，不包括文件扩展名

## 2.修改扩展名
- 功能：将目标文件夹内文件的扩展名修改为用户自定义的扩展名，不影响文件内容

## 3.修改特定字符串
- 功能：将文件名中所有匹配的字符串修改为用户指定的字符串，匹配字符串支持正则表达式

## 4.日期填充
- 功能：将文件名中的日期替换为指定日期，支持自定义日期留空以删除日期，若文件名存在多个日期则会全部替换为空串后再增加指定日期

## 5.重命名并编号
- 功能：添加编号至文件名，可选择是否重命名后再编号

## 6.字母大小写转换
- 功能：对文件名中的英文字母进行大小写转换，支持全部大写或小写以及首字母大写，可选择仅修改文件名、仅修改扩展名和修改全部

## 7.添加字符串
- 功能：添加自定义字符串到文件头部或者尾部
"""


class SpaceAwareLineEdit(LineEdit):
    """使空格更明显的文本框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        setFont(self, 13)  # 防止空格符显示异常
        self.textChanged.connect(self.visualize_spaces)
        self._actual_text = ""

    def visualize_spaces(self, text):
        # 保存光标位置
        cursor_pos = self.cursorPosition()

        # 计算实际文本（去掉可视化字符）
        if "␣" in text:
            self._actual_text = text.replace("␣", " ")
        else:
            self._actual_text = text

        # 可视化显示
        visualized = self._actual_text.replace(" ", "␣")

        # 阻止信号循环
        self.blockSignals(True)
        self.setText(visualized)
        self.blockSignals(False)

        # 恢复光标位置
        self.setCursorPosition(cursor_pos)

    def text(self):
        """重写text()方法返回实际文本"""
        return self._actual_text


class RuleHelpWindow(MessageBoxBase):
    """显示规则说明的窗口"""

    def __init__(self, parent=None):
        super().__init__(parent)
        """基本设置"""
        self.cancelButton.setHidden(True)
        self.yesButton.setText('确定')

        self.widget.setFixedWidth(600)
        self.widget.setFixedHeight(700)

        """标题标签"""
        self.titleLabel = SubtitleLabel(text='规则说明', parent=self)

        self.viewLayout.addWidget(self.titleLabel)

        """文本内容显示"""
        self.textBrowser = TextBrowser(parent=self)
        self.textScrollArea = SmoothScrollArea(parent=self)

        self.textScrollArea.setWidget(self.textBrowser)  # 将富文本浏览器放入滚动区域
        self.textScrollArea.setWidgetResizable(True)  # 将滚动区域大小设置为可调

        self.viewLayout.addWidget(self.textScrollArea)
        self.textBrowser.setMarkdown(rule_help_md)


class InfoDialog(MessageBoxBase):
    """显示规则详情的界面"""

    def __init__(self, rule, parent=None):
        super().__init__(parent)
        """基本设置"""
        self.widget.setFixedWidth(450)
        self.widget.setMaximumHeight(550)

        self.yesButton.setText('确认')
        self.cancelButton.setHidden(True)

        self.viewLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # 标题标签
        self.titleLabel = SubtitleLabel(text='规则详情', parent=self.widget)
        setFont(self.titleLabel, 30)

        self.viewLayout.addWidget(self.titleLabel, 0, Qt.AlignmentFlag.AlignCenter)

        """规则详情滚动区域"""
        self.scrollArea = SmoothScrollArea(parent=self)
        self.scrollAreaWidget = QFrame(self.scrollArea)
        self.scrollArea.setWidget(self.scrollAreaWidget)
        self.scrollLayout = QVBoxLayout(self.scrollAreaWidget)

        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidget.setStyleSheet('border-radius: 5px;')
        self.viewLayout.addWidget(self.scrollArea)

        """显示规则通用信息"""
        # 规则种类
        self.typeLabel = SubtitleLabel(text='种类：', parent=self.widget)
        self.typeContentLabel = BodyLabel(text=str(rule['type']), parent=self.widget)

        self.typeLayout = QHBoxLayout()
        self.typeLayout.setSpacing(0)
        self.typeLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.typeLayout.addWidget(self.typeLabel)
        self.typeLayout.addWidget(self.typeContentLabel)
        self.scrollLayout.addLayout(self.typeLayout)

        # 规则名称
        self.nameLabel = SubtitleLabel(text='名称：', parent=self.widget)
        self.nameContentLabel = BodyLabel(text=str(rule['name']), parent=self.widget)

        self.nameLayout = QHBoxLayout()
        self.nameLayout.setSpacing(0)
        self.nameLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.nameLayout.addWidget(self.nameLabel)
        self.nameLayout.addWidget(self.nameContentLabel)
        self.scrollLayout.addLayout(self.nameLayout)

        # 规则描述
        self.descLabel = SubtitleLabel(text='规则描述：', parent=self.widget)
        self.descContentLabel = BodyLabel(text=rule['desc'] if rule['desc'] else '<无>', parent=self.widget)

        self.descLayout = QHBoxLayout()
        self.descLayout.setSpacing(0)
        self.descLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.descLayout.addWidget(self.descLabel)
        self.descLayout.addWidget(self.descContentLabel)
        self.scrollLayout.addLayout(self.descLayout)

        """规则关键功能显示"""
        if rule['type'] == 1:
            # 分隔符
            self.splitCharLabel = SubtitleLabel(text='分隔符：', parent=self.widget)
            self.splitCharContentLabel = BodyLabel(text=(rule['split_char']), parent=self.widget)
            self.splitCharLayout = QHBoxLayout()

            self.splitCharLayout.setSpacing(0)
            self.splitCharLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

            self.splitCharLayout.addWidget(self.splitCharLabel)
            self.splitCharLayout.addWidget(self.splitCharContentLabel)
            self.scrollLayout.addLayout(self.splitCharLayout)

            # 是否使用正则表达式
            enable_re = rule.get('enable_re', False)

            self.enableReLabel = SubtitleLabel(text='使用正则表达式：', parent=self.widget)
            if enable_re:
                self.enableReContentLabel = BodyLabel(text='是', parent=self.widget)
            else:
                self.enableReContentLabel = BodyLabel(text='否', parent=self.widget)
            self.enableReLayout = QHBoxLayout()

            self.enableReLayout.setSpacing(0)
            self.enableReLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

            self.enableReLayout.addWidget(self.enableReLabel)
            self.enableReLayout.addWidget(self.enableReContentLabel)
            self.scrollLayout.addLayout(self.enableReLayout)
        elif rule['type'] == 2:
            # 新扩展名
            self.extLabel = SubtitleLabel(text='新扩展名：', parent=self.widget)
            self.extContentLabel = BodyLabel(text=(rule['new_ext']), parent=self.widget)

            self.extLayout = QHBoxLayout()
            self.extLayout.setSpacing(0)
            self.extLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

            self.extLayout.addWidget(self.extLabel)
            self.extLayout.addWidget(self.extContentLabel)
            self.scrollLayout.addLayout(self.extLayout)
        elif rule['type'] == 3:
            # 匹配字符串
            self.targetStrLabel = SubtitleLabel(text='匹配字符串：', parent=self.widget)
            target_str_content = rule['target_str'] if not re.match(r' +', rule['target_str']) else '<空格>'
            self.targetStrContentLabel = BodyLabel(text=target_str_content, parent=self.widget)

            self.targetStrLayout = QHBoxLayout()
            self.targetStrLayout.setSpacing(0)
            self.targetStrLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

            self.targetStrLayout.addWidget(self.targetStrLabel)
            self.targetStrLayout.addWidget(self.targetStrContentLabel)
            self.scrollLayout.addLayout(self.targetStrLayout)

            # 是否启用正则表达式
            self.useReLabel = SubtitleLabel(text='使用正则表达式：', parent=self.widget)
            if rule['use_re']:
                use_re = '是'
            else:
                use_re = '否'
            self.useReContentLabel = BodyLabel(text=use_re, parent=self.widget)

            self.useReLayout = QHBoxLayout()
            self.useReLayout.setSpacing(0)
            self.useReLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

            self.useReLayout.addWidget(self.useReLabel)
            self.useReLayout.addWidget(self.useReContentLabel)
            self.scrollLayout.addLayout(self.useReLayout)

            # 新字符串
            self.newStrLabel = SubtitleLabel(text='新字符串：', parent=self.widget)
            if rule['new_str']:
                new_str_content = rule['new_str'] if not re.match(r' +', rule['new_str']) else '<空格>'
            else:
                new_str_content = '<空>'
            self.newStrContentLabel = BodyLabel(text=new_str_content, parent=self.widget)

            self.newStrLayout = QHBoxLayout()
            self.newStrLayout.setSpacing(0)
            self.newStrLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

            self.newStrLayout.addWidget(self.newStrLabel)
            self.newStrLayout.addWidget(self.newStrContentLabel)
            self.scrollLayout.addLayout(self.newStrLayout)
        elif rule['type'] == 4:
            # 日期
            self.dateLabel = SubtitleLabel(text='填充日期：', parent=self.widget)
            if rule['date_type'] == 0:
                date = '系统日期'
            elif rule['date_type'] == 1:
                date = '文件创建日期'
            elif rule['date_type'] == 2:
                date = '文件修改日期'
            elif rule['date_type'] == 3:
                date = '文件访问日期'
            elif rule['date_type'] == 4:
                date = rule['date'] if rule['date'] else '<空>'
            self.dateContentLabel = BodyLabel(text=date, parent=self.widget)

            self.dateLayout = QHBoxLayout()
            self.dateLayout.setSpacing(0)
            self.dateLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

            self.dateLayout.addWidget(self.dateLabel)
            self.dateLayout.addWidget(self.dateContentLabel)
            self.scrollLayout.addLayout(self.dateLayout)

            # 填充位置
            if date != '<空>':  # 只有当填充日期不为空时才显示
                self.posLabel = SubtitleLabel(text='填充位置：', parent=self.widget)
                if rule['position'] == 'head':
                    pos = '文件名首'
                elif rule['position'] == 'tail':
                    pos = '文件名尾'
                self.posContentLabel = BodyLabel(text=pos, parent=self.widget)

                self.posLayout = QHBoxLayout()
                self.posLayout.setSpacing(0)
                self.posLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

                self.posLayout.addWidget(self.posLabel)
                self.posLayout.addWidget(self.posContentLabel)
                self.scrollLayout.addLayout(self.posLayout)

            # 分隔符
            self.splitCharLabel = SubtitleLabel(text='分隔符：', parent=self.widget)
            if rule['split_char']:
                split_char_content = rule['split_char'] if not re.match(r' +', rule['split_char']) else '<空格>'
            else:
                split_char_content = '<空>'
            self.splitCharContentLabel = BodyLabel(text=split_char_content, parent=self.widget)

            self.splitCharLayout = QHBoxLayout()
            self.splitCharLayout.setSpacing(0)
            self.splitCharLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

            self.splitCharLayout.addWidget(self.splitCharLabel)
            self.splitCharLayout.addWidget(self.splitCharContentLabel)
            self.scrollLayout.addLayout(self.splitCharLayout)
        elif rule['type'] == 5:
            # 新文件名
            newNameLabel = SubtitleLabel(text='文件名：', parent=self.widget)
            if 'new_name' in rule.keys():  # 如果规则含有关键字new_name则显示new_name内容
                newNameContentLabel = BodyLabel(text=rule['new_name'], parent=self.widget)
            else:
                newNameContentLabel = BodyLabel(text='<原文件名>', parent=self.widget)
            newNameLayout = QHBoxLayout()

            newNameLayout.setSpacing(0)
            newNameLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            newNameLayout.addWidget(newNameLabel)
            newNameLayout.addWidget(newNameContentLabel)

            self.scrollLayout.addLayout(newNameLayout)

            # 编号样式
            numTypeLabel = SubtitleLabel(text='编号样式：', parent=self.widget)
            numTypeContentLabel = BodyLabel(text=rule['num_type'], parent=self.widget)
            numTypeLayout = QHBoxLayout()

            numTypeLayout.setSpacing(0)
            numTypeLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            numTypeLayout.addWidget(numTypeLabel)
            numTypeLayout.addWidget(numTypeContentLabel)

            self.scrollLayout.addLayout(numTypeLayout)

            # 起始编号
            startNumLabel = SubtitleLabel(text='起始编号：', parent=self.widget)
            startNumContentLabel = BodyLabel(text=str(rule['start_num']), parent=self.widget)
            startNumLayout = QHBoxLayout()

            startNumLayout.setSpacing(0)
            startNumLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            startNumLayout.addWidget(startNumLabel)
            startNumLayout.addWidget(startNumContentLabel)

            self.scrollLayout.addLayout(startNumLayout)

            # 步长
            stepLengthLabel = SubtitleLabel(text='步长：', parent=self.widget)
            stepLengthContentLabel = BodyLabel(text=str(rule['step_length']), parent=self.widget)
            stepLengthLayout = QHBoxLayout()

            stepLengthLayout.setSpacing(0)
            stepLengthLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            stepLengthLayout.addWidget(stepLengthLabel)
            stepLengthLayout.addWidget(stepLengthContentLabel)

            self.scrollLayout.addLayout(stepLengthLayout)

            # 位置
            if rule['position'] == 'head':
                pos = '文件名首'
            elif rule['position'] == 'tail':
                pos = '文件名尾'
            posLabel = SubtitleLabel(text='位置：', parent=self.widget)
            posContentLabel = BodyLabel(text=pos, parent=self.widget)
            posLayout = QHBoxLayout()

            posLayout.setSpacing(0)
            posLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            posLayout.addWidget(posLabel)
            posLayout.addWidget(posContentLabel)

            self.scrollLayout.addLayout(posLayout)

        elif rule['type'] == 6:
            # 作用域
            actionScopeLabel = SubtitleLabel(text='作用域：', parent=self.widget)
            if rule['action_scope'] == 1:
                action_scope_content = '仅文件名'
            elif rule['action_scope'] == 2:
                action_scope_content = '仅扩展名'
            elif rule['action_scope'] == 3:
                action_scope_content = '全部'
            actionScopeContentLabel = BodyLabel(text=action_scope_content, parent=self.widget)

            actionScopeLayout = QHBoxLayout()
            actionScopeLayout.setSpacing(0)
            actionScopeLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            actionScopeLayout.addWidget(actionScopeLabel)
            actionScopeLayout.addWidget(actionScopeContentLabel)
            self.scrollLayout.addLayout(actionScopeLayout)

            # 功能
            functionLabel = SubtitleLabel(text='功能：', parent=self.widget)
            if rule['function'] == 1:
                function_content = '全部大写'
            elif rule['function'] == 2:
                function_content = '全部小写'
            elif rule['function'] == 3:
                function_content = '首字母大写'
            functionContentLabel = BodyLabel(text=function_content, parent=self.widget)

            functionLayout = QHBoxLayout()
            functionLayout.setSpacing(0)
            functionLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            functionLayout.addWidget(functionLabel)
            functionLayout.addWidget(functionContentLabel)
            self.scrollLayout.addLayout(functionLayout)

        elif rule['type'] == 7:
            # 自定义字符串
            strLabel = SubtitleLabel(text='自定义字符串：', parent=self.widget)
            strContentLabel = BodyLabel(text=rule['string'], parent=self.widget)

            strLayout = QHBoxLayout()
            strLayout.setSpacing(0)
            strLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

            strLayout.addWidget(strLabel)
            strLayout.addWidget(strContentLabel)
            self.scrollLayout.addLayout(strLayout)

            # 位置
            if rule['position'] == 'head':
                pos = '文件名首'
            elif rule['position'] == 'tail':
                pos = '文件名尾'
            posLabel = SubtitleLabel(text='位置：', parent=self.widget)
            posContentLabel = BodyLabel(text=pos, parent=self.widget)
            posLayout = QHBoxLayout()

            posLayout.setSpacing(0)
            posLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            posLayout.addWidget(posLabel)
            posLayout.addWidget(posContentLabel)

            self.scrollLayout.addLayout(posLayout)


class RuleCard(CardWidget):
    """定义规则卡片"""

    def __init__(self, rule, index, isActive=False, parent=None):
        super().__init__(parent=parent)
        """定义该卡片的属性"""
        self.index = index  # 记录规则对应的下标
        self.parentInterface = parent  # 保存父亲界面到属性，便于调用父亲界面的方法
        self.rule = rule  # 保存所有规则参数为一个属性
        self.type = rule['type']  # 单独保存一份规则类型，便于外部函数调用

        self.selected = False  # 初始状态为未被鼠标选中

        """卡片基本设置"""
        self.setFixedHeight(75)  # 设置卡片高度
        self.cardLayout = QHBoxLayout(self)  # 设置卡片的主布局器（水平）

        """规则名和规则描述标签"""
        self.titleLabel = SubtitleLabel(text=self.rule['name'], parent=self)
        self.descLabel = BodyLabel(text=self.rule['desc'] if rule['desc'] else '<无>', parent=self)
        self.labelLayout = QVBoxLayout()

        # 设置属性
        setFont(self.titleLabel, 22)
        setFont(self.descLabel, 16)

        # 添加控件到布局器
        self.labelLayout.addWidget(self.titleLabel)
        self.labelLayout.addWidget(self.descLabel)
        self.cardLayout.addLayout(self.labelLayout)  # 合并标签布局器至主布局器

        """激规则激活状态"""
        self.isActivatedWidget = QWidget(self)  # 定义存放图标和文本标签的容器
        self.activatedLayout = QHBoxLayout(self.isActivatedWidget)
        self.isActivatedIcon = IconWidget()  # 显示激活信息的图标
        self.isActivatedLabel = SubtitleLabel(text='', parent=self)

        setFont(self.isActivatedLabel, 15)
        self.isActivatedWidget.setStyleSheet('background-color:transparent')  # 将背景色设为透明，防止选择规则卡片的时候影响美观
        self.isActivatedIcon.setFixedSize(20, 20)
        self.activatedLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)  # 激活状态布局方式为左对齐
        self.activatedLayout.setSpacing(2)  # 设置激活图标和文本标签的间隔

        # 添加控件到布局器
        self.activatedLayout.addWidget(self.isActivatedIcon)
        self.activatedLayout.addWidget(self.isActivatedLabel)
        self.cardLayout.addWidget(self.isActivatedWidget, 0, Qt.AlignmentFlag.AlignRight)

        """更多按钮"""
        self.moreBtn = TransparentToolButton(FluentIcon.MORE)
        self.moreBtn.setFixedSize(32, 32)
        self.cardLayout.addWidget(self.moreBtn)

        """设置卡片的激活显示状态"""
        self.setActive(isActive)

        """实现更多按钮功能"""
        self.moreBtn.clicked.connect(
            lambda: self.creatMenu(self.moreBtn.mapToGlobal(QPoint(-self.moreBtn.width() - 50, 25))))

        """自定义样式"""
        label_qss = 'QLabel{background-color:transparent;}'
        setCustomStyleSheet(self, label_qss, label_qss)
        self.moreBtn.setStyleSheet('background-color:transparent;')

    def setCardSelected(self, isSelected: bool):
        """切换卡片的选中状态"""
        if isSelected == self.selected:  # 如果带切换的状态与当前状态相同则不进行操作
            return

        color = themeColor()
        self.selected = isSelected

        if isSelected:
            # 设置卡片背景颜色
            self.setStyleSheet("QWidget {background-color:" + f"{color.name()};" +
                               "border-radius: 5px;}")

            if isDarkTheme():
                label_qss = """
                    QLabel {
                        color: black;
                        background-color: transparent;
                    }
                """
                # 设置卡片标签样式
                self.titleLabel.setStyleSheet(label_qss)
                self.descLabel.setStyleSheet(label_qss)
                self.isActivatedLabel.setStyleSheet(label_qss)
                self.moreBtn.setIcon(FluentIcon.MORE.icon(color='black'))
            else:
                self.moreBtn.setIcon(FluentIcon.MORE.icon(color='black'))

        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: transparent;
                    border-radius: 5px;
                }
            """)  # 设置卡片背景

            if isDarkTheme():
                label_qss = """
                    QLabel {
                        color: white;
                        background-color: transparent;
                    }
                """
                self.moreBtn.setIcon(FluentIcon.MORE.icon(color='white'))
            else:
                label_qss = """
                    QLabel {
                        color: black;
                        background-color: transparent;
                    }
                """
                self.moreBtn.setIcon(FluentIcon.MORE.icon(color='black'))
            # 设置卡片标签样式
            self.titleLabel.setStyleSheet(label_qss)
            self.descLabel.setStyleSheet(label_qss)
            self.isActivatedLabel.setStyleSheet(label_qss)

    def setActive(self, isActive: bool):
        """设置激活状态"""
        if isActive:
            self.isActivatedIcon.setIcon(InfoBarIcon.SUCCESS)
            self.isActivatedLabel.setText('已激活')
        else:
            self.isActivatedIcon.setIcon(None)
            self.isActivatedLabel.setText('')

    def creatMenu(self, pos):
        """实现更多按钮的功能"""

        menu = RoundMenu(parent=self)

        # 添加修改规则的动作
        menu.addAction(
            Action(FluentIcon.EDIT, '修改规则',
                   triggered=lambda: self.parentInterface.reviseRule(self.rule, self.index)))

        # 添加显示规则详情的动作
        menu.addAction(
            Action(FluentIcon.ALIGNMENT, '规则详情', triggered=lambda: self.parentInterface.showInfoDialog(self.rule)))

        menu.exec(pos, ani=True)


class PositionBtnLayout(QHBoxLayout):
    """存放位置单选按钮的容器"""

    def __init__(self, parent):
        super().__init__()
        parent.new_layout_list.append(self)  # 将自身添加到父容器的新布局列表中

        """文本标签"""
        self.titleLabel = SubtitleLabel(text='位置')
        self.addWidget(self.titleLabel, 1, Qt.AlignmentFlag.AlignLeft)

        """单选按钮"""
        self.tailBtn = RadioButton('文件名尾')
        self.headBtn = RadioButton('文件名首')
        self.btnGroup = QButtonGroup(parent)
        self.btnGroup.addButton(self.tailBtn)
        self.btnGroup.addButton(self.headBtn)

        self.headBtn.setChecked(True)

        self.addWidget(self.headBtn, 0, Qt.AlignmentFlag.AlignRight)
        self.addWidget(self.tailBtn, 0, Qt.AlignmentFlag.AlignRight)


class RuleInputInterface(MessageBoxBase):
    """规则参数输入窗口"""

    """定义发送给外部变量的信号"""
    submit_data = pyqtSignal(dict)  # 定义发射字典的信号对象，用于发射所有输入的内容

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.num_types = None
        self.errorInfoLabel = BodyLabel(text='你还有必填的选项未填写！')  # 提示错误信息的标签

        """基本设置"""
        self.widget.setMinimumWidth(450)  # 设置对话框最小宽度

        self.yesButton.setText('确认')  # 修改按钮文本
        self.cancelButton.setText('取消')

        self.new_layout_list = []  # 存放新增加的布局，便于重选规则类型后刷新界面布局

        self.yesButton.setEnabled(False)  # 初始将确认按钮设置为禁用状态，防止什么都没输入就点击确认

        """选择规则种类"""
        all_rule_type = (
            '1.交换分隔符前后内容',
            '2.修改后缀名',
            '3.修改特定字符串',
            '4.日期填充',
            '5.文件编号',
            '6.字母大小写转换',
            '7.添加字符串'
        )
        self.ruleTypeComboBox = ComboBox()
        self.ruleTypeLabel = SubtitleLabel(text='规则种类', parent=self.widget)
        self.ruleTypeLayout = QHBoxLayout()

        self.ruleTypeComboBox.addItems(all_rule_type)
        self.ruleTypeComboBox.setPlaceholderText('请选择一个规则类型')  # 设置提示文本
        self.ruleTypeComboBox.setCurrentIndex(-1)  # 设置初始为未选中任何选项
        self.ruleTypeComboBox.setMinimumWidth(200)
        self.ruleTypeComboBox.setMaximumWidth(350)

        self.ruleTypeLayout.addWidget(self.ruleTypeLabel)
        self.ruleTypeLayout.addWidget(self.ruleTypeComboBox)
        self.viewLayout.addLayout(self.ruleTypeLayout)

        self.ruleTypeComboBox.currentIndexChanged.connect(lambda: self.refreshLayout())

        """规则名称"""
        self.ruleNameLabel = SubtitleLabel(text='名称', parent=self.widget)
        self.ruleNameLineEdit = LineEdit()
        self.ruleNameLayout = QHBoxLayout()

        self.ruleNameLineEdit.setPlaceholderText('输入规则名称（必填）')
        self.ruleNameLineEdit.setFixedWidth(200)
        self.ruleNameLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.ruleNameLayout.addWidget(self.ruleNameLabel)
        self.ruleNameLayout.addWidget(self.ruleNameLineEdit)
        self.viewLayout.addLayout(self.ruleNameLayout)

        """规则描述"""
        self.ruleDescLabel = SubtitleLabel(text='规则描述', parent=self.widget)
        self.ruleDescLineEdit = LineEdit()
        self.ruleDescLayout = QHBoxLayout()

        self.ruleDescLineEdit.setPlaceholderText('请输入规则描述')
        self.ruleDescLineEdit.setFixedWidth(200)
        self.ruleDescLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.ruleDescLayout.addWidget(self.ruleDescLabel)
        self.ruleDescLayout.addWidget(self.ruleDescLineEdit)
        self.viewLayout.addLayout(self.ruleDescLayout)

    def validate(self):
        """重写验证输入数据的方法"""

        """将需要检测的文本框的内容存放至列表"""
        if not self.ruleNameLineEdit.text():
            self.errorInfoLabel.setText('未输入规则名称！')
            self.errorInfoLabel.setHidden(False)
            return False

        if self.new_rule_type == 1:
            if not self.splitCharLineEdit.text():
                self.errorInfoLabel.setText('未输入分隔符！')
                self.errorInfoLabel.setHidden(False)
                return False

        elif self.new_rule_type == 2:
            if not self.extLineEdit.text():
                self.errorInfoLabel.setText('未输入新扩展名！')
                self.errorInfoLabel.setHidden(False)
                return False

        elif self.new_rule_type == 3:
            if not self.oldStrLineEdit.text():
                self.errorInfoLabel.setText('未输入匹配字符串！')
                self.errorInfoLabel.setHidden(False)
                return False

        elif self.new_rule_type == 4:
            if self.dateTypeComboBox.currentIndex() == 4:
                if (self.customDatePicker.text()
                        and not re.findall(r'[-_ ]?\d{4} ?\d{1,2} ?\d{1,2}[-_ ]?', self.customDatePicker.text())):
                    self.errorInfoLabel.setText('自定义日期格式无效！')
                    self.errorInfoLabel.setHidden(False)
                    return False

        elif self.new_rule_type == 5:
            if not self.newNameLineEdit.text() and self.fileNameComboBox.currentIndex() == 1:
                self.errorInfoLabel.setText('未输入新文件名！')
                self.errorInfoLabel.setHidden(False)
                return False

        elif self.new_rule_type == 7:
            if not self.strInputLineEdit.text():
                self.errorInfoLabel.setText('未输入自定义字符串')
                self.errorInfoLabel.setHidden(False)
                return False

        return True

    def refreshLayout(self):
        """选择的规则类型改变时改变窗口布局"""
        self.yesButton.setEnabled(True)  # 一旦选择了规则类型就将该按钮设置为可用
        self.new_rule_type = self.ruleTypeComboBox.currentIndex() + 1

        """创建输入框限制器，防止输入文件名不能存在的字符"""
        char_regex = QRegularExpression(r'[^\\/:*?"<>|]+')  # 限制器内容
        char_validator = QRegularExpressionValidator(char_regex)  # 限制器对象

        """删除旧的控件"""
        for layout in self.new_layout_list:
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            layout.deleteLater()
        self.new_layout_list.clear()

        """消除规则名称和描述"""
        self.ruleNameLineEdit.setText('')
        self.ruleDescLineEdit.setText('')

        """添加新的布局"""
        if self.new_rule_type == 1:
            """分隔符输入"""
            splitCharLayout = QHBoxLayout()
            self.new_layout_list.append(splitCharLayout)
            splitCharInputLayout = QVBoxLayout()
            self.new_layout_list.append(splitCharInputLayout)
            splitCharLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

            # 文本标签
            splitCharLabel = SubtitleLabel(text='分隔符', parent=self)
            splitCharLayout.addWidget(splitCharLabel)

            # 输入框
            self.splitCharLineEdit = SpaceAwareLineEdit()
            self.splitCharLineEdit.setPlaceholderText('请输入分隔符（必填）')
            self.splitCharLineEdit.setFixedWidth(200)
            splitCharInputLayout.addWidget(self.splitCharLineEdit)
            self.splitCharLineEdit.setValidator(char_validator)  # 设置限制器

            # 启用正则表达式复选框
            self.enableReCheckBox = CheckBox(text='使用正则表达式', parent=self.widget)
            splitCharInputLayout.addWidget(self.enableReCheckBox)

            # 将新控件的水平布局添加到主布局
            splitCharLayout.addLayout(splitCharInputLayout)
            self.viewLayout.addLayout(splitCharLayout)

        elif self.new_rule_type == 2:
            """新扩展名输入"""
            extLayout = QHBoxLayout()
            extLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            self.new_layout_list.append(extLayout)

            # 文本标签
            extLabel = SubtitleLabel(text='新扩展名', parent=self)
            extLayout.addWidget(extLabel)

            # 输入框
            self.extLineEdit = LineEdit()
            self.extLineEdit.setPlaceholderText('请输入新的扩展名（必填）')
            self.extLineEdit.setFixedWidth(200)
            extLayout.addWidget(self.extLineEdit)
            self.extLineEdit.setValidator(char_validator)  # 设置限制器

            # 将新布局添加至主布局
            self.viewLayout.addLayout(extLayout)

        elif self.new_rule_type == 3:
            """匹配字符串输入"""
            oldStrLayout = QHBoxLayout()
            oldStrInputLayout = QVBoxLayout()
            oldStrLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            self.new_layout_list.append(oldStrLayout)
            self.new_layout_list.append(oldStrInputLayout)

            # 文本标签
            oldStrLabel = SubtitleLabel(text='匹配字符串', parent=self)
            oldStrLayout.addWidget(oldStrLabel)

            # 输入框
            self.oldStrLineEdit = SpaceAwareLineEdit()
            self.oldStrLineEdit.setPlaceholderText('请输入匹配字符串（必填）')
            self.oldStrLineEdit.setFixedWidth(200)
            oldStrInputLayout.addWidget(self.oldStrLineEdit)

            # 正则表达式复选框
            self.useReCheckBox = CheckBox('使用正则表达式', parent=self)
            oldStrInputLayout.addWidget(self.useReCheckBox)

            # 将旧字符串相关布局添加到主布局
            oldStrLayout.addLayout(oldStrInputLayout)
            self.viewLayout.addLayout(oldStrLayout)

            """新字符串输入"""
            newStrLayout = QHBoxLayout()
            newStrLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            self.new_layout_list.append(newStrLayout)

            # 文本标签
            newStrLabel = SubtitleLabel(text='新字符串', parent=self)
            newStrLayout.addWidget(newStrLabel)

            # 输入框
            self.newStrLineEdit = LineEdit()
            self.newStrLineEdit.setPlaceholderText('请输入新字符串')
            self.newStrLineEdit.setFixedWidth(200)
            newStrLayout.addWidget(self.newStrLineEdit)
            self.newStrLineEdit.setValidator(char_validator)  # 设置限制器

            # 将旧字符串相关布局添加到主布局
            self.viewLayout.addLayout(newStrLayout)

        elif self.new_rule_type == 4:
            """日期填充选择"""
            dateLayout = QHBoxLayout()
            dateTypeLayout = QVBoxLayout()  # 日期种类下拉框和自定义日期输入框的布局器
            self.new_layout_list.append(dateLayout)
            self.new_layout_list.append(dateTypeLayout)

            dateTypeLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

            # 文本标签
            dateLabel = SubtitleLabel(text='填充的日期', parent=self)
            dateLayout.addWidget(dateLabel)

            # 日期种类下拉框
            self.dateTypeComboBox = ComboBox()
            date_type = ('系统日期', '文件创建日期', '文件修改日期', '文件访问日期', '自定义日期')
            self.dateTypeComboBox.addItems(date_type)
            self.dateTypeComboBox.setFixedWidth(150)

            dateTypeLayout.addWidget(self.dateTypeComboBox, 0, Qt.AlignmentFlag.AlignRight)

            # 自定义填充日期
            self.customDatePicker = ZhDatePicker()
            self.customDatePicker.setFixedWidth(150)
            self.customDatePicker.setVisible(False)  # 默认为不可见，只有下拉框选择自定义才会显示

            dateTypeLayout.addWidget(self.customDatePicker)

            def setDateLineEditVisible(comboBox, dateLineEdit):
                """根据下拉框选择的内容修改日期输入框的可见性"""
                if comboBox.currentIndex() == 4:
                    dateLineEdit.setVisible(True)
                else:
                    dateLineEdit.setVisible(False)

            self.dateTypeComboBox.currentIndexChanged.connect(
                lambda: setDateLineEditVisible(self.dateTypeComboBox, self.customDatePicker))

            # 将日期输入布局添加至主布局
            dateLayout.addLayout(dateTypeLayout)
            self.viewLayout.addLayout(dateLayout)

            """填充位置选择"""
            self.posLayout = PositionBtnLayout(self)
            self.viewLayout.addLayout(self.posLayout)

            """日期分隔符选择"""
            splitCharLayout = QHBoxLayout()
            self.new_layout_list.append(splitCharLayout)
            splitCharInputLayout = QVBoxLayout()
            self.new_layout_list.append(splitCharInputLayout)

            # 文本标签
            splitCharLabel = SubtitleLabel(text='年月日分隔符', parent=self)
            splitCharLayout.addWidget(splitCharLabel)

            # 下拉框
            self.split_char_type = ('-', '_', '空格', '年月日', '自定义')
            self.splitCharComboBox = ComboBox()
            self.splitCharComboBox.addItems(self.split_char_type)
            self.splitCharComboBox.setFixedWidth(110)
            splitCharInputLayout.addWidget(self.splitCharComboBox)

            # 自定义分隔符输入框
            self.customSplitCharLineEdit = SpaceAwareLineEdit()
            splitCharInputLayout.addWidget(self.customSplitCharLineEdit, 0)

            self.customSplitCharLineEdit.setFixedWidth(110)
            self.customSplitCharLineEdit.setPlaceholderText('请输入分隔符')
            self.customSplitCharLineEdit.setValidator(char_validator)
            self.customSplitCharLineEdit.setVisible(False)  # 默认不显示，当选择自定义分隔符才显示

            def setSplitCharLineEditVisible(comboBox, dateLineEdit):
                """根据下拉框选择的内容修改分隔符输入框的可见性"""
                if comboBox.currentIndex() == 4:
                    dateLineEdit.setVisible(True)
                else:
                    dateLineEdit.setVisible(False)

            self.splitCharComboBox.currentIndexChanged.connect(
                lambda: setSplitCharLineEditVisible(self.splitCharComboBox, self.customSplitCharLineEdit))

            # 将日期分隔符输入的布局添加至主布局
            splitCharLayout.addLayout(splitCharInputLayout)
            self.viewLayout.addLayout(splitCharLayout)

        elif self.new_rule_type == 5:
            """文件名填充"""
            fileNameLayout = QHBoxLayout()
            fileNameInputLayout = QVBoxLayout()
            self.new_layout_list.append(fileNameLayout)

            # 文本标签
            newNameLabel = SubtitleLabel(text='文件名', parent=self)
            fileNameLayout.addWidget(newNameLabel)

            # 文件名填充下拉框
            self.fileNameComboBox = ComboBox()
            file_name = ('原文件名', '自定义文件名')
            self.fileNameComboBox.addItems(file_name)
            self.fileNameComboBox.setFixedWidth(150)
            self.fileNameComboBox.setCurrentIndex(0)
            fileNameInputLayout.addWidget(self.fileNameComboBox, 0, Qt.AlignmentFlag.AlignRight)

            # 输入框
            self.newNameLineEdit = LineEdit()
            self.newNameLineEdit.setPlaceholderText('请输入新文件名（必填）')
            self.newNameLineEdit.setFixedWidth(200)
            fileNameInputLayout.addWidget(self.newNameLineEdit)
            self.newNameLineEdit.setValidator(char_validator)
            self.newNameLineEdit.setVisible(False)  # 默认设置为不可见

            def switchNewNameLineEditVisible():
                if self.fileNameComboBox.currentIndex() == 1:
                    self.newNameLineEdit.setVisible(True)
                else:
                    self.newNameLineEdit.setVisible(False)

            self.fileNameComboBox.currentIndexChanged.connect(switchNewNameLineEditVisible)

            # 将新水平布局添加至主布局
            fileNameLayout.addLayout(fileNameInputLayout)
            self.viewLayout.addLayout(fileNameLayout)

            """编号样式选择"""
            numTypeLayout = QHBoxLayout()
            self.new_layout_list.append(numTypeLayout)

            # 文本标签
            numTypeLabel = SubtitleLabel(text='编号样式', parent=self)
            numTypeLayout.addWidget(numTypeLabel)

            # 下拉选择框
            self.numTypeComboBox = ComboBox()
            self.numTypeComboBox.setFixedWidth(60)
            self.num_types = ('1.', '1-', '1_', '(1)', '[1]', '{1}')
            self.numTypeComboBox.addItems(self.num_types)
            numTypeLayout.addWidget(self.numTypeComboBox)

            # 将水平布局添加至主布局
            self.viewLayout.addLayout(numTypeLayout)

            """起始编号输入"""
            startNumLayout = QHBoxLayout()
            self.new_layout_list.append(startNumLayout)

            # 文本标签
            startNumLabel = SubtitleLabel(text='起始编号', parent=self)
            startNumLayout.addWidget(startNumLabel)

            # 输入框
            self.startNumLineEdit = LineEdit()
            self.startNumLineEdit.setPlaceholderText('输入起始编号')
            self.startNumLineEdit.setFixedWidth(125)
            startNumLayout.addWidget(self.startNumLineEdit)

            num_regex = QRegularExpression(r'\d+')  # 限制只能输入数字
            num_validator = QRegularExpressionValidator(num_regex)
            self.startNumLineEdit.setValidator(num_validator)

            self.viewLayout.addLayout(startNumLayout)

            """步长输入"""
            stepLengthLayout = QHBoxLayout()
            self.new_layout_list.append(stepLengthLayout)

            # 文本标签
            stepLengthLabel = SubtitleLabel(text='步长', parent=self)
            stepLengthLayout.addWidget(stepLengthLabel)

            # 输入框
            self.stepLengthLineEdit = LineEdit()
            self.stepLengthLineEdit.setPlaceholderText('输入步长')
            self.stepLengthLineEdit.setFixedWidth(125)
            stepLengthLayout.addWidget(self.stepLengthLineEdit)

            step_regex = QRegularExpression(r'^[^0]\d*$')  # 限制不能以0开头并且只能输入数字
            step_validator = QRegularExpressionValidator(step_regex)
            self.stepLengthLineEdit.setValidator(step_validator)

            self.viewLayout.addLayout(stepLengthLayout)

            """位置选择"""
            self.posLayout = PositionBtnLayout(self)
            self.viewLayout.addLayout(self.posLayout)

        elif self.new_rule_type == 6:
            """作用域选择"""
            actionScopeLayout = QHBoxLayout()
            self.new_layout_list.append(actionScopeLayout)

            # 文本标签
            actionScopeLabel = SubtitleLabel(text='作用域', parent=self)
            actionScopeLayout.addWidget(actionScopeLabel)

            # 单选按钮
            actionScopeBtnLayout = QHBoxLayout()
            actionScopeBtnLayout.setAlignment(Qt.AlignmentFlag.AlignRight)
            actionScopeBtnLayout.setSpacing(5)
            self.new_layout_list.append(actionScopeBtnLayout)

            fileNameBtn = RadioButton('仅文件名')
            extBtn = RadioButton('仅扩展名')
            bothBtn = RadioButton('全部')
            self.actionScopeGroup = QButtonGroup(self)
            self.actionScopeGroup.addButton(fileNameBtn, 1)
            self.actionScopeGroup.addButton(extBtn, 2)
            self.actionScopeGroup.addButton(bothBtn, 3)
            fileNameBtn.setChecked(True)  # 默认选中文件名按钮

            actionScopeBtnLayout.addWidget(fileNameBtn)
            actionScopeBtnLayout.addWidget(extBtn)
            actionScopeBtnLayout.addWidget(bothBtn)

            actionScopeLayout.addLayout(actionScopeBtnLayout)
            self.viewLayout.addLayout(actionScopeLayout)

            """作用模式选择"""
            functionLayout = QHBoxLayout()
            self.new_layout_list.append(functionLayout)

            # 文本标签
            functionLabel = SubtitleLabel(text='模式', parent=self)
            functionLayout.addWidget(functionLabel)

            # 单选按钮
            functionBtnLayout = QHBoxLayout()
            functionBtnLayout.setAlignment(Qt.AlignmentFlag.AlignRight)
            functionBtnLayout.setSpacing(5)
            self.new_layout_list.append(functionBtnLayout)

            upperBtn = RadioButton('全部大写')
            lowerBtn = RadioButton('全部小写')
            titleBtn = RadioButton('单词首字母大写')
            self.functionGroup = QButtonGroup(self)
            self.functionGroup.addButton(upperBtn, 1)
            self.functionGroup.addButton(lowerBtn, 2)
            self.functionGroup.addButton(titleBtn, 3)
            upperBtn.setChecked(True)

            functionBtnLayout.addWidget(upperBtn)
            functionBtnLayout.addWidget(lowerBtn)
            functionBtnLayout.addWidget(titleBtn)

            functionLayout.addLayout(functionBtnLayout)
            self.viewLayout.addLayout(functionLayout)

        elif self.new_rule_type == 7:
            """自定义字符串"""
            strLayout = QHBoxLayout()
            self.new_layout_list.append(strLayout)

            # 文本标签
            strTitleLabel = SubtitleLabel(text='自定义字符串', parent=self)
            strLayout.addWidget(strTitleLabel, 0, Qt.AlignmentFlag.AlignLeft)

            # 自定义字符串输入框
            self.strInputLineEdit = LineEdit()
            self.strInputLineEdit.setPlaceholderText('请输入自定义字符串')
            self.strInputLineEdit.setFixedWidth(200)
            self.strInputLineEdit.setValidator(char_validator)
            strLayout.addWidget(self.strInputLineEdit, 0, Qt.AlignmentFlag.AlignRight)

            self.viewLayout.addLayout(strLayout)

            """填充位置选择"""
            self.posLayout = PositionBtnLayout(self)
            self.viewLayout.addLayout(self.posLayout)

        """验证不通过时的警告文本框"""
        setFont(self.errorInfoLabel, 15)
        self.errorInfoLabel.setStyleSheet("color: rgb(255, 100, 100);")
        self.errorInfoLabel.setHidden(True)  # 默认设置为不可见

        self.viewLayout.addWidget(self.errorInfoLabel, 0, Qt.AlignmentFlag.AlignCenter)


class RuleListInterface(QWidget):
    """定义规则列表界面布局"""
    rule_dict = None

    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        self.setObjectName('RuleListInterface')

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

        """规则说明按钮"""
        self.ruleHelpBtn = PushButton(FluentIcon.HELP, '规则说明')

        self.ruleHelpBtn.setFixedWidth(107)

        self.widgetVLayout.addWidget(self.ruleHelpBtn)

        """功能按钮"""
        # 添加规则按钮
        self.addRuleBtn = PushButton(FluentIcon.ADD, '添加规则')
        self.addRuleBtn.setToolTip('添加一条新规则')
        self.addRuleBtn.installEventFilter(ToolTipFilter(self.addRuleBtn, showDelay=300, position=ToolTipPosition.TOP))

        # 激活规则按钮
        self.activateRuleBtn = PushButton(FluentIcon.COMPLETED, '激活规则')
        self.activateRuleBtn.setToolTip('将选中的规则设置为活跃规则')
        self.activateRuleBtn.installEventFilter(
            ToolTipFilter(self.activateRuleBtn, showDelay=300, position=ToolTipPosition.TOP))

        # 删除规则按钮
        self.delRuleBtn = PushButton(FluentIcon.DELETE.icon(color='red'), '删除规则')
        self.delRuleBtn.setToolTip('删除选中的规则')
        self.delRuleBtn.installEventFilter(ToolTipFilter(self.delRuleBtn, showDelay=300, position=ToolTipPosition.TOP))

        self.btnLayout = QHBoxLayout()  # 控制顶部规则编辑按钮的布局
        self.btnLayout.setSpacing(4)
        self.btnLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)  # 按钮布局器默认左对齐

        self.btnLayout.addWidget(self.addRuleBtn, 0)
        self.btnLayout.addWidget(self.activateRuleBtn, 0)
        self.btnLayout.addWidget(self.delRuleBtn, 0)
        self.widgetVLayout.addLayout(self.btnLayout, 0)  # 将按钮布局器合并至总容器的布局器

        """规则卡片展示区域"""
        self.ruleScrollArea = SmoothScrollArea(self.totalWidget)  # 创建平滑滚动区域
        self.ruleCardWidget = QFrame(self.ruleScrollArea)  # 创建存放所有规则卡片的容器
        self.ruleCardLayout = QVBoxLayout(self.ruleCardWidget)  # 规则卡片的垂直布局器

        self.ruleScrollArea.setWidget(self.ruleCardWidget)  # 将规则卡片容器放入滚动区域，使其可以滚动
        self.ruleScrollArea.setWidgetResizable(True)
        self.ruleScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)  # 水平滚动条永远不显示
        self.ruleCardWidget.setStyleSheet('border-radius: 5px;')

        self.ruleCardLayout.setAlignment(Qt.AlignmentFlag.AlignTop)  # 设置卡片对齐方式为顶对齐
        self.ruleCardLayout.setSpacing(7)  # 设置卡片布局器间隔：每个卡片间隔距离为7

        self.widgetVLayout.addWidget(self.ruleScrollArea)

        """初始化规则卡片展示区域"""
        self.ruleCardList = []  # 存放规则卡片的列表
        self.currentIndex = -1  # 当前鼠标选中的卡片的下标
        self.initRuleViewArea()  # 初始化布局

        """实现控件功能"""
        self.achieve_functions()

    def initRuleViewArea(self):
        """初始化规则卡片显示区域"""
        logging.info('开始更新规则卡片布局')
        self.rule_dict = load_rule()  # 更新现存规则
        rule_list = self.rule_dict['rules']
        selected_index = self.rule_dict['selected_index']
        self.currentIndex = -1  # 先将目前选中的卡片下标置为-1，否则会有下标越界风险

        """删除原有的规则卡片"""
        while self.ruleCardLayout.count():
            item = self.ruleCardLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.ruleCardList.clear()  # 清空列表中已保存的规则卡片

        """添加新的布局"""
        if self.rule_dict['rules']:
            self.ruleCardLayout.setAlignment(Qt.AlignmentFlag.AlignTop)  # 卡片默认顶部对齐

            index = 0
            for rule in rule_list:  # 添加至卡片列表，便于其他函数调用
                if index == selected_index:
                    activated = True
                else:
                    activated = False

                card = RuleCard(rule, index, activated, parent=self)
                card.clicked.connect(lambda index=card.index: self.setSelected(index))  # 将点击卡片的动作连接至选中卡片方法
                self.ruleCardList.append(card)  # 将规则以卡片的形式添加至卡片列表
                self.ruleCardLayout.addWidget(card, 0)  # 依此将卡片添加至卡片布局器中

                index += 1
        else:
            ruleEmptyLabel = SubtitleLabel(text='规则列表空空如也', parent=self.ruleCardWidget)
            self.ruleCardLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.ruleCardLayout.addWidget(ruleEmptyLabel, 0, Qt.AlignmentFlag.AlignCenter)

    def setSelected(self, index):
        """
        切换卡片选中状态
        参数 index：调用该方法的卡片下标，即鼠标点击的卡片下标
        """
        # 先将当前已选中的卡片切换为未选中状态
        if self.currentIndex >= 0:
            self.ruleCardList[self.currentIndex].setCardSelected(False)

        # 再将选中的卡片切换为选中状态
        self.currentIndex = index
        if self.currentIndex > -1:
            self.ruleCardList[self.currentIndex].setCardSelected(True)

    def achieve_functions(self):
        """实现各控件功能"""

        # 显示规则说明
        def show_rule_help():
            """显示规则说明窗口"""
            ruleHelpWindow = RuleHelpWindow(self)
            ruleHelpWindow.exec()

        self.ruleHelpBtn.clicked.connect(show_rule_help)

        # 激活规则功能实现
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

                # 创建激活成功的提示框
                InfoBar.success(
                    title='成功',
                    content='已激活选中的规则',
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self
                )

                # 将选中规则下标归位
                self.setSelected(-1)
            else:
                InfoBar.warning(
                    title='提示',
                    content='请先选择一条规则',
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self
                )

        self.activateRuleBtn.clicked.connect(activate_rule_callback)

        # 删除规则功能实现
        def del_rule_callback():
            """删除规则"""
            if self.currentIndex != -1:  # 防止没有选择规则就删除规则
                confirm_window = MessageBox('删除规则', '确认删除选中的规则吗？', parent=self)
                confirm_window.yesButton.setText('确认')
                confirm_window.cancelButton.setText('取消')

                logging.info('用户点击删除规则按钮，确认操作中……')
                if confirm_window.exec():
                    logging.info('用户确认删除规则')

                    flag = del_rules(self.rule_dict, self.currentIndex)
                    if flag == 1:
                        v_pos = self.ruleScrollArea.verticalScrollBar().value()
                        self.initRuleViewArea()  # （删除规则）刷新规则卡片布局
                        self.ruleScrollArea.verticalScrollBar().setValue(v_pos)

                        InfoBar.success(
                            title='成功',
                            content='已删除选中的规则',
                            position=InfoBarPosition.TOP,
                            duration=2000,
                            parent=self
                        )
                    elif flag == 0:
                        InfoBar.error(
                            title='错误',
                            content='无法删除最后一个规则',
                            position=InfoBarPosition.TOP,
                            duration=2000,
                            parent=self
                        )

                    self.setSelected(-1)  # 无论是否删除成功都取消选中卡片
                else:
                    logging.info('用户取消删除规则')
            else:
                # 未选中卡片时显示气泡弹窗
                InfoBar.warning(
                    title='提示',
                    content='请先选择一条规则',
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self
                )

        self.delRuleBtn.clicked.connect(del_rule_callback)

        # 添加规则
        def add_rule_callback():
            """添加规则"""
            logging.info('进行操作：添加规则')
            addRuleWindow = RuleInputInterface(self)
            addRuleWindow.submit_data.connect(lambda: save_new_rule(self.rule_dict, rule))  # 将发射的信号传递给信号处理函数
            if addRuleWindow.exec():
                logging.info('用户确认添加规则')
                rule = analise_rule(addRuleWindow)  # 解析添加规则时输入的内容
                addRuleWindow.submit_data.emit(rule)  # 发送规则种类、名称和描述的信号

                self.initRuleViewArea()  # （添加规则）刷新规则卡片布局
                QTimer.singleShot(10, lambda: self.ruleScrollArea.verticalScrollBar().setValue(
                    self.ruleScrollArea.verticalScrollBar().maximum()))  # 增加10ms延迟，防止UI未更新完全就滚动

                # 创建成功添加规则的消息框
                InfoBar.success(
                    title='成功',
                    content='已添加一条新规则',
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self
                )
            else:
                logging.info('用户取消添加规则')

        self.addRuleBtn.clicked.connect(add_rule_callback)

    # 规则卡片“更多”按钮菜单的各种功能实现
    def showInfoDialog(self, rule):
        """显示规则详情界面"""
        infoDialog = InfoDialog(rule, parent=self)
        infoDialog.exec()

    def reviseRule(self, rule, index):
        """修改规则"""
        logging.info('进行操作：修改规则')
        reviseRuleWindow = RuleInputInterface(self)

        """设置输入窗口的基本信息"""
        type = rule['type']
        name = rule['name']
        desc = rule['desc']

        reviseRuleWindow.ruleTypeComboBox.setCurrentIndex(type - 1)
        reviseRuleWindow.ruleNameLineEdit.setText(name)
        reviseRuleWindow.ruleDescLineEdit.setText(desc)

        """设置输入窗口的规则关键参数"""
        if type == 1:
            split_char = rule['split_char']
            enable_re = rule.get('enable_re', False)

            reviseRuleWindow.splitCharLineEdit.setText(split_char)

            if enable_re:
                reviseRuleWindow.enableReCheckBox.setChecked(True)
        elif type == 2:
            new_ext = rule['new_ext']

            reviseRuleWindow.extLineEdit.setText(new_ext)
        elif type == 3:
            target_str = rule['target_str']
            new_str = rule['new_str']

            reviseRuleWindow.oldStrLineEdit.setText(target_str)
            reviseRuleWindow.useReCheckBox.setChecked(rule.get('use_re', False))
            reviseRuleWindow.newStrLineEdit.setText(new_str)
        elif type == 4:
            split_char = rule['split_char']
            position = rule['position']
            customize_date = rule.get('date', '')
            date_type = rule.get('date_type', 4 if customize_date else 0)

            if split_char in reviseRuleWindow.split_char_type:
                reviseRuleWindow.splitCharComboBox.setCurrentIndex(
                    reviseRuleWindow.split_char_type.index(split_char))
            else:
                reviseRuleWindow.splitCharComboBox.setCurrentIndex(4)
                reviseRuleWindow.customSplitCharLineEdit.setText(split_char)

            if position == 'head':
                reviseRuleWindow.posLayout.headBtn.setChecked(True)
            elif position == 'tail':
                reviseRuleWindow.posLayout.tailBtn.setChecked(True)

            reviseRuleWindow.dateTypeComboBox.setCurrentIndex(date_type)

            try:
                year, month, day = customize_date.split()
                if customize_date:
                    reviseRuleWindow.customDatePicker.setDate(QDate(int(year), int(month), int(day)))
            except ValueError:
                pass
        elif type == 5:
            new_name = rule.get('new_name', '')
            num_type = rule['num_type']
            start_num = str(rule['start_num'])
            step_length = str(rule['step_length'])
            position = rule['position']
            use_original_name = rule.get('use_original_name', False)

            if use_original_name:
                reviseRuleWindow.fileNameComboBox.setCurrentIndex(0)
            else:
                reviseRuleWindow.fileNameComboBox.setCurrentIndex(1)

            if position == 'head':
                reviseRuleWindow.posLayout.headBtn.setChecked(True)
            elif position == 'tail':
                reviseRuleWindow.posLayout.tailBtn.setChecked(True)

            reviseRuleWindow.newNameLineEdit.setText(new_name)
            reviseRuleWindow.numTypeComboBox.setCurrentIndex(reviseRuleWindow.num_types.index(num_type))
            reviseRuleWindow.startNumLineEdit.setText(start_num)
            reviseRuleWindow.stepLengthLineEdit.setText(step_length)
        elif type == 6:
            action_scope = rule['action_scope']
            function = rule['function']

            reviseRuleWindow.actionScopeGroup.button(action_scope).setChecked(True)
            reviseRuleWindow.functionGroup.button(function).setChecked(True)
        elif type == 7:
            string = rule['string']
            position = rule['position']

            reviseRuleWindow.strInputLineEdit.setText(string)

            if position == 'head':
                reviseRuleWindow.posLayout.headBtn.setChecked(True)
            elif position == 'tail':
                reviseRuleWindow.posLayout.tailBtn.setChecked(True)

        """窗口关闭后执行的操作"""
        reviseRuleWindow.submit_data.connect(
            lambda: revise_rule(self.rule_dict, revised_rule, index))  # 设置信号传值连接到的函数

        if reviseRuleWindow.exec():  # 显示窗口
            logging.info('用户确认修改规则')
            revised_rule = analise_rule(reviseRuleWindow)
            reviseRuleWindow.submit_data.emit(revised_rule)  # 发送信号给规则保存函数

            v_pos = self.ruleScrollArea.verticalScrollBar().value()
            self.initRuleViewArea()  # （修改规则）刷新规则卡片布局
            self.ruleScrollArea.verticalScrollBar().setValue(v_pos)

            # 创建修改成功的消息框
            InfoBar.success(
                title='成功',
                content='已成功修改指定规则',
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )
        else:
            logging.info('用户取消修改规则')
