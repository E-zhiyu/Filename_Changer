from PyQt6.QtGui import QPalette, QRegularExpressionValidator, QAction, QCursor
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QWidget, QApplication, QButtonGroup, QLayout, QDialog
from PyQt6.QtCore import Qt, pyqtSignal, QRegularExpression, QPoint

from FilenameChanger.Fluent_Widgets_GUI.qfluentwidgets import (SubtitleLabel, setFont, PushButton, FluentIcon,
                                                               CardWidget, SearchLineEdit, TransparentToolButton,
                                                               SmoothScrollArea, IconWidget, InfoBarIcon, MessageBox,
                                                               ComboBox, MessageBoxBase, LineEdit, RadioButton,
                                                               RoundMenu, Action, BodyLabel)

from FilenameChanger.rename_rules.rule_manager import load_config, switch_rule, del_rules, save_new_rule, analise_rule

from FilenameChanger.log.log_recorder import *


class InfoDialog(MessageBoxBase):
    """显示规则详情的界面"""

    def __init__(self, rule, parent=None):
        super().__init__(parent)
        """基本设置"""
        self.widget.setMinimumWidth(400)  # 设置最小窗口宽度

        self.yesButton.setText('确认')
        self.cancelButton.setHidden(True)

        self.viewLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # 标题标签
        self.titleLabel = SubtitleLabel(text='规则详情', parent=self.widget)
        setFont(self.titleLabel, 30)

        self.viewLayout.addWidget(self.titleLabel, 0, Qt.AlignmentFlag.AlignCenter)

        """显示规则通用信息"""
        # 规则种类
        self.typeLabel = SubtitleLabel(text='种类：', parent=self.widget)
        self.typeContentLabel = BodyLabel(text=str(rule['type']), parent=self.widget)

        self.typeLayout = QHBoxLayout()
        self.typeLayout.setSpacing(0)
        self.typeLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.typeLayout.addWidget(self.typeLabel)
        self.typeLayout.addWidget(self.typeContentLabel)
        self.viewLayout.addLayout(self.typeLayout)

        # 规则名称
        self.nameLabel = SubtitleLabel(text='名称：', parent=self.widget)
        self.nameContentLabel = BodyLabel(text=str(rule['name']), parent=self.widget)

        self.nameLayout = QHBoxLayout()
        self.nameLayout.setSpacing(0)
        self.nameLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.nameLayout.addWidget(self.nameLabel)
        self.nameLayout.addWidget(self.nameContentLabel)
        self.viewLayout.addLayout(self.nameLayout)

        # 规则描述
        self.descLabel = SubtitleLabel(text='规则描述：', parent=self.widget)
        self.descContentLabel = BodyLabel(text=str(rule['desc']), parent=self.widget)

        self.descLayout = QHBoxLayout()
        self.descLayout.setSpacing(0)
        self.descLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.descLayout.addWidget(self.descLabel)
        self.descLayout.addWidget(self.descContentLabel)
        self.viewLayout.addLayout(self.descLayout)

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
            self.viewLayout.addLayout(self.splitCharLayout)
        elif rule['type'] == 2:
            # 新扩展名
            self.extLabel = SubtitleLabel(text='新扩展名：', parent=self.widget)
            self.extContentLabel = BodyLabel(text=(rule['new_ext']), parent=self.widget)

            self.extLayout = QHBoxLayout()
            self.extLayout.setSpacing(0)
            self.extLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

            self.extLayout.addWidget(self.extLabel)
            self.extLayout.addWidget(self.extContentLabel)
            self.viewLayout.addLayout(self.extLayout)
        elif rule['type'] == 3:
            # 目标字符串
            self.targetStrLabel = SubtitleLabel(text='原字符串：', parent=self.widget)
            self.targetStrContentLabel = BodyLabel(text=(rule['target_str']), parent=self.widget)

            self.targetStrLayout = QHBoxLayout()
            self.targetStrLayout.setSpacing(0)
            self.targetStrLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

            self.targetStrLayout.addWidget(self.targetStrLabel)
            self.targetStrLayout.addWidget(self.targetStrContentLabel)
            self.viewLayout.addLayout(self.targetStrLayout)

            # 新字符串
            self.newStrLabel = SubtitleLabel(text='新字符串：', parent=self.widget)
            self.newStrContentLabel = BodyLabel(text=(rule['new_str']), parent=self.widget)

            self.newStrLayout = QHBoxLayout()
            self.newStrLayout.setSpacing(0)
            self.newStrLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

            self.newStrLayout.addWidget(self.newStrLabel)
            self.newStrLayout.addWidget(self.newStrContentLabel)
            self.viewLayout.addLayout(self.newStrLayout)
        elif rule['type'] == 4:
            # 日期
            self.dateLabel = SubtitleLabel(text='填充日期：', parent=self.widget)
            if rule['date']:
                date = rule['date']
            else:
                date = '动态填充系统日期'
            self.dateContentLabel = BodyLabel(text=date, parent=self.widget)

            self.dateLayout = QHBoxLayout()
            self.dateLayout.setSpacing(0)
            self.dateLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

            self.dateLayout.addWidget(self.dateLabel)
            self.dateLayout.addWidget(self.dateContentLabel)
            self.viewLayout.addLayout(self.dateLayout)

            # 填充位置
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
            self.viewLayout.addLayout(self.posLayout)

            # 分隔符
            self.splitCharLabel = SubtitleLabel(text='分隔符：', parent=self.widget)
            self.splitCharContentLabel = BodyLabel(text=(rule['split_char']), parent=self.widget)

            self.splitCharLayout = QHBoxLayout()
            self.splitCharLayout.setSpacing(0)
            self.splitCharLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

            self.splitCharLayout.addWidget(self.splitCharLabel)
            self.splitCharLayout.addWidget(self.splitCharContentLabel)
            self.viewLayout.addLayout(self.splitCharLayout)


class RuleCard(CardWidget):
    """定义规则卡片"""

    def __init__(self, rule, index, isActive=False, parent=None):
        super().__init__(parent=parent)
        self.index = index
        """定义该卡片的属性"""
        self.parentInterface = parent  # 保存父亲界面到属性，便于调用父亲界面的方法
        self.rule = rule  # 保存所有规则参数为一个属性
        self.type = rule['type']  # 单独保存一份规则类型，便于外部函数调用

        self.selected = False  # 初始状态为未被鼠标选中

        """卡片基本设置"""
        self.setFixedHeight(73)  # 设置卡片高度
        self.mainHLayout = QHBoxLayout(self)  # 设置卡片的主布局器（水平）

        """规则名和规则描述标签"""
        self.titleLabel = SubtitleLabel(text=self.rule['name'], parent=self)
        self.contentLabel = SubtitleLabel(text=self.rule['desc'], parent=self)
        self.labelLayout = QVBoxLayout()

        # 设置属性
        self.titleLabel.setStyleSheet('background-color:transparent')  # 将标签的背景色设为透明，防止选择卡片的时候影响美观
        self.contentLabel.setStyleSheet('background-color:transparent')  # 将标签的背景色设为透明，防止选择卡片的时候影响美观
        setFont(self.titleLabel, 22)
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
        self.activatedLayout.setSpacing(2)  # 设置激活图标和文本标签的间隔

        # 添加控件到布局器
        self.activatedLayout.addWidget(self.isActivatedIcon)
        self.activatedLayout.addWidget(self.isActivatedLabel)
        self.mainHLayout.addWidget(self.isActivatedWidget, 0, Qt.AlignmentFlag.AlignRight)

        """更多按钮"""
        self.moreBtn = TransparentToolButton(FluentIcon.MORE)
        self.moreBtn.setFixedSize(32, 32)
        self.mainHLayout.addWidget(self.moreBtn)

        """设置卡片的激活显示状态"""
        self.setActive(isActive)

        """实现更多按钮功能"""
        self.moreBtn.clicked.connect(
            lambda: self.creatMenu(self.moreBtn.mapToGlobal(QPoint(-self.moreBtn.width() - 50, 25))))

    def setCardSelected(self, isSelected: bool):
        """切换卡片的选中状态"""
        if isSelected == self.selected:  # 如果带切换的状态与当前状态相同则不进行操作
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
                    background: #ff009faa;
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

    def creatMenu(self, pos):
        """实现更多按钮的功能"""

        menu = RoundMenu(parent=self)

        # 添加显示规则详情的动作
        menu.addAction(
            Action(FluentIcon.ALIGNMENT, '规则详情', triggered=lambda: self.parentInterface.showInfoDialog(self.rule)))

        # 添加修改规则的动作
        menu.addAction(
            Action(FluentIcon.EDIT, '修改规则', triggered=lambda: self.parentInterface.reviseRule(self.rule)))

        menu.exec(pos, ani=True)


class ruleInputInterface(MessageBoxBase):
    """规则参数输入窗口"""

    """定义发送给外部变量的信号"""
    submit_data = pyqtSignal(dict)  # 定义发射字典的信号对象，用于发射所有输入的内容
    new_control = {}  # 存放新增加的控件，便于外部函数调用
    must_filled_text_list = []  # 必须填写的文本的列表

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.errorInfoLabel = SubtitleLabel(text='你还有必填的选项未填写！')  # 提示错误信息的标签

        """基本设置"""
        self.widget.setMinimumWidth(400)  # 设置对话框最小宽度
        self.base_height = 250
        self.widget.setMinimumHeight(self.base_height)  # 设置基本高度

        self.yesButton.setText('确认')  # 修改按钮文本
        self.cancelButton.setText('取消')

        self.new_layout_list = []  # 存放新增加的布局，便于重选规则类型后刷新界面布局

        self.yesButton.setEnabled(False)  # 初始将确认按钮设置为禁用状态，防止什么都没输入就点击确认

        """选择规则种类"""
        all_rule_type = ('1.交换分隔符前后内容', '2.修改后缀名', '3.修改特定字符串', '4.文件名添加或删除日期')
        self.ruleTypeComboBox = ComboBox()
        self.ruleTypeLabel = SubtitleLabel(text='规则种类', parent=self.widget)
        self.ruleTypeLayout = QHBoxLayout()

        self.ruleTypeComboBox.addItems(all_rule_type)
        self.ruleTypeComboBox.setPlaceholderText('请选择一个规则类型')  # 设置提示文本
        self.ruleTypeComboBox.setCurrentIndex(-1)  # 设置初始为未选中任何选项
        self.ruleTypeComboBox.setFixedWidth(200)

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
        self.ruleDescLineEdit.setFixedWidth(250)
        self.ruleDescLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.ruleDescLayout.addWidget(self.ruleDescLabel)
        self.ruleDescLayout.addWidget(self.ruleDescLineEdit)
        self.viewLayout.addLayout(self.ruleDescLayout)

    def validate(self):
        """重写验证输入数据的方法"""
        self.must_filled_text_list.clear()  # 先清除上一次待检测的内容

        """将需要检测的文本框的内容存放至列表"""
        self.must_filled_text_list.append(self.ruleNameLineEdit.text())
        if self.new_rule_type == 1:
            self.must_filled_text_list.append(self.new_control['splitCharLineEdit'].text())
        elif self.new_rule_type == 2:
            self.must_filled_text_list.append(self.new_control['extLineEdit'].text())
        elif self.new_rule_type == 3:
            self.must_filled_text_list.append(self.new_control['oldStrLineEdit'].text())
            self.must_filled_text_list.append(self.new_control['newStrLineEdit'].text())
        elif self.new_rule_type == 4:
            self.must_filled_text_list.append(self.new_control['splitCharLineEdit'].text())
            if self.new_control['customDateBtn'].isChecked():
                self.must_filled_text_list.append(self.new_control['customDateLineEdit'].text())

        """对列表中的内容进行检测，为空则不通过"""
        for text in self.must_filled_text_list:
            if not text:
                self.errorInfoLabel.setHidden(False)
                return False
        else:
            return True

    def refreshLayout(self):
        """选择的规则类型改变时改变窗口布局"""
        self.yesButton.setEnabled(True)  # 一旦选择了规则类型就将该按钮设置为可用
        self.new_rule_type = int(self.ruleTypeComboBox.currentText()[:1])
        self.new_control.clear()

        """创建输入框限制器，防止输入文件名不能存在的字符"""
        regex = QRegularExpression(r'[^\/:*?"<>|]+')  # 限制器内容
        validator = QRegularExpressionValidator(regex)  # 限制器对象

        """删除旧的控件"""
        for layout in self.new_layout_list:
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            layout.deleteLater()
        self.new_layout_list.clear()

        if self.new_rule_type == 1:

            """设置新的窗口高度"""
            new_height = self.base_height + 1 * 40
            self.widget.setMinimumHeight(new_height)

            """分隔符输入"""
            splitCharLayout = QHBoxLayout()
            splitCharLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            self.new_layout_list.append(splitCharLayout)

            # 文本标签
            splitCharLabel = SubtitleLabel(text='分隔符', parent=self)
            splitCharLayout.addWidget(splitCharLabel)

            # 输入框
            splitCharLineEdit = LineEdit()
            splitCharLineEdit.setPlaceholderText('请输入分隔符（必填）')
            splitCharLineEdit.setFixedWidth(170)
            splitCharLayout.addWidget(splitCharLineEdit)
            self.new_control['splitCharLineEdit'] = splitCharLineEdit
            splitCharLineEdit.setValidator(validator)  # 设置限制器

            # 将新控件的水平布局添加到主布局
            self.viewLayout.addLayout(splitCharLayout)

        elif self.new_rule_type == 2:
            """设置新的窗口高度"""
            new_height = self.base_height + 1 * 40
            self.widget.setMinimumHeight(new_height)

            """新扩展名输入"""
            extLayout = QHBoxLayout()
            extLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            self.new_layout_list.append(extLayout)

            # 文本标签
            extLabel = SubtitleLabel(text='新扩展名', parent=self)
            extLayout.addWidget(extLabel)

            # 输入框
            extLineEdit = LineEdit()
            extLineEdit.setPlaceholderText('请输入新的扩展名（必填）')
            extLineEdit.setFixedWidth(200)
            extLayout.addWidget(extLineEdit)
            self.new_control['extLineEdit'] = extLineEdit
            extLineEdit.setValidator(validator)  # 设置限制器

            # 将新布局添加至主布局
            self.viewLayout.addLayout(extLayout)

        elif self.new_rule_type == 3:
            """设置新的窗口高度"""
            new_height = self.base_height + 2 * 40
            self.widget.setMinimumHeight(new_height)

            """原字符串输入"""
            oldStrLayout = QHBoxLayout()
            oldStrLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            self.new_layout_list.append(oldStrLayout)

            # 文本标签
            oldStrLabel = SubtitleLabel(text='原字符串', parent=self)
            oldStrLayout.addWidget(oldStrLabel)

            # 输入框
            oldStrLineEdit = LineEdit()
            oldStrLineEdit.setPlaceholderText('请输入原字符串（必填）')
            oldStrLineEdit.setFixedWidth(200)
            oldStrLayout.addWidget(oldStrLineEdit)
            self.new_control['oldStrLineEdit'] = oldStrLineEdit
            oldStrLineEdit.setValidator(validator)  # 设置限制器

            # 将旧字符串相关布局添加到主布局
            self.viewLayout.addLayout(oldStrLayout)

            """新字符串输入"""
            newStrLayout = QHBoxLayout()
            newStrLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            self.new_layout_list.append(newStrLayout)

            # 文本标签
            newStrLabel = SubtitleLabel(text='新字符串', parent=self)
            newStrLayout.addWidget(newStrLabel)

            # 输入框
            newStrLineEdit = LineEdit()
            newStrLineEdit.setPlaceholderText('请输入新字符串')
            newStrLineEdit.setFixedWidth(200)
            newStrLayout.addWidget(newStrLineEdit)
            self.new_control['newStrLineEdit'] = newStrLineEdit
            newStrLineEdit.setValidator(validator)  # 设置限制器

            # 将旧字符串相关布局添加到主布局
            self.viewLayout.addLayout(newStrLayout)

        elif self.new_rule_type == 4:
            """设置新的窗口高度"""
            new_height = self.base_height + 4 * 40
            self.widget.setMinimumHeight(new_height)

            """日期填充选择"""
            dateLayout = QHBoxLayout()
            self.new_layout_list.append(dateLayout)

            # 文本标签
            dateLabel = SubtitleLabel(text='填充的日期', parent=self)
            dateLayout.addWidget(dateLabel)

            # 单选按钮，选择填充系统日期还是自定义日期
            radioLayout = QVBoxLayout()  # 垂直布局两个单选按钮
            radioLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
            self.new_layout_list.append(radioLayout)

            sysDateBtn = RadioButton('动态填充系统日期')
            dateBtnGroup = QButtonGroup(self)  # 创建按钮组
            sysDateBtn.setChecked(True)  # 默认填充重命名时的系统日期
            dateBtnGroup.addButton(sysDateBtn)

            radioLayout.addWidget(sysDateBtn)
            self.new_control['sysDateBtn'] = sysDateBtn

            # 自定义填充日期
            customDateBtn = RadioButton('自定义')
            dateBtnGroup.addButton(customDateBtn)

            customDateLayout = QHBoxLayout()  # 输入框和自定义日期按钮的水平布局
            customDateLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            self.new_layout_list.append(customDateLayout)

            dateLineEdit = LineEdit()
            dateLineEdit.setPlaceholderText('年月日用空格隔开')
            dateLineEdit.setFixedWidth(150)

            # 为自定义日期输入框添加日期格式限制
            format_regex = QRegularExpression(r'\d{1,4} \d{1,2} \d{1,2}')
            date_validator = QRegularExpressionValidator(format_regex)
            dateLineEdit.setValidator(date_validator)  # 设置输入的格式限制

            customDateLayout.addWidget(customDateBtn)
            self.new_control['customDateBtn'] = customDateBtn
            customDateLayout.addWidget(dateLineEdit, 0, Qt.AlignmentFlag.AlignLeft)
            self.new_control['customDateLineEdit'] = dateLineEdit
            radioLayout.addLayout(customDateLayout)

            dateLayout.addLayout(radioLayout)

            # 将日期输入布局添加至主布局
            self.viewLayout.addLayout(dateLayout)

            """填充位置选择"""
            posLayout = QHBoxLayout()
            posLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            self.new_layout_list.append(posLayout)

            # 文本标签
            posLabel = SubtitleLabel(text='日期插入位置', parent=self)
            posLayout.addWidget(posLabel)

            # 单选按钮
            headBtn = RadioButton('文件名首')
            tailBtn = RadioButton('文件名尾')
            posBtnGroup = QButtonGroup(self)  # 创建一个按钮组，组内的单选按钮是互斥的
            posBtnGroup.addButton(headBtn)
            posBtnGroup.addButton(tailBtn)

            headBtn.setChecked(True)  # 设置默认选中的按钮

            posLayout.addWidget(headBtn)
            self.new_control['headBtn'] = headBtn
            posLayout.addWidget(tailBtn)
            self.new_control['tailBtn'] = tailBtn

            # 将日期位置输入布局添加至主布局
            self.viewLayout.addLayout(posLayout)

            """日期分隔符输入"""
            splitCharLayout = QHBoxLayout()
            splitCharLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            self.new_layout_list.append(splitCharLayout)

            # 文本标签
            splitCharLabel = SubtitleLabel(text='日期分隔符', parent=self)
            splitCharLayout.addWidget(splitCharLabel)

            # 输入框
            splitCharLineEdit = LineEdit()
            splitCharLineEdit.setPlaceholderText('请输入年月日间的分隔符（必填）')
            splitCharLineEdit.setFixedWidth(200)
            splitCharLayout.addWidget(splitCharLineEdit)
            self.new_control['splitCharLineEdit'] = splitCharLineEdit
            splitCharLineEdit.setValidator(validator)  # 设置限制器

            # 将日期分隔符输入的布局添加至主布局
            self.viewLayout.addLayout(splitCharLayout)

        """验证不通过时的警告文本框"""
        setFont(self.errorInfoLabel, 15)
        self.errorInfoLabel.setStyleSheet("color: red;")
        self.errorInfoLabel.setHidden(True)  # 默认设置为不可见

        self.viewLayout.addWidget(self.errorInfoLabel, 0, Qt.AlignmentFlag.AlignCenter)


class RuleListInterface(QFrame):
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

        """功能按钮"""
        self.addRuleBtn = PushButton(FluentIcon.ADD, '添加规则')
        self.activateRuleBtn = PushButton(FluentIcon.COMPLETED, '激活规则')
        self.delRuleBtn = PushButton(FluentIcon.DELETE.icon(color='red'), '删除规则')
        self.btnLayout = QHBoxLayout()  # 控制顶部规则编辑按钮的布局

        self.btnLayout.setSpacing(4)
        self.btnLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)  # 按钮布局器默认左对齐

        self.btnLayout.addWidget(self.addRuleBtn, 0)
        self.btnLayout.addWidget(self.activateRuleBtn, 0)
        self.btnLayout.addWidget(self.delRuleBtn, 0)
        self.widgetVLayout.addLayout(self.btnLayout, 0)  # 将按钮布局器合并至总容器的布局器

        """搜索框"""
        """self.searchLineEdit = SearchLineEdit()  # 实例化搜索框

        self.searchLineEdit.setFixedWidth(300)
        self.searchLineEdit.setPlaceholderText('搜索规则名称')  # 设置输入提示语

        self.widgetVLayout.addWidget(self.searchLineEdit, 0)  # 将搜索框添加至总容器布局器"""

        """规则卡片展示区域"""
        self.ruleScrollArea = SmoothScrollArea(self.totalWidget)  # 创建平滑滚动区域
        self.ruleCardWidget = QWidget(self.ruleScrollArea)  # 创建存放所有规则卡片的容器
        self.ruleCardLayout = QVBoxLayout(self.ruleCardWidget)  # 规则卡片的垂直布局器

        self.ruleScrollArea.setWidget(self.ruleCardWidget)  # 将规则卡片容器放入滚动区域，使其可以滚动

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
        self.rule_dict = load_config()  # 更新现存规则
        """删除原有的规则卡片"""
        while self.ruleCardLayout.count():
            item = self.ruleCardLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        """添加新的布局"""
        self.ruleScrollArea.setWidgetResizable(True)
        self.ruleScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)  # 水平滚动条永远不显示

        self.widgetVLayout.addWidget(self.ruleScrollArea)
        if self.rule_dict['rules']:
            self.ruleCardLayout.setAlignment(Qt.AlignmentFlag.AlignTop)  # 卡片默认顶部对齐

            self.addRuleCard()  # 将规则卡片列表中的卡片添加到界面中
        else:
            ruleEmptyLabel = SubtitleLabel(text='当前规则列表为空，请先添加规则', parent=self.ruleCardWidget)

            self.ruleCardLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            self.ruleCardLayout.addWidget(ruleEmptyLabel, 0, Qt.AlignmentFlag.AlignCenter)

    def addRuleCard(self):
        """将规则卡片列表中的卡片添加到界面中"""
        self.ruleCardList.clear()  # 先清空列表中已保存的规则卡片

        rule_list = self.rule_dict['rules']
        selected_index = self.rule_dict['selected_index']

        index = 0
        for rule in rule_list:  # 添加至卡片列表，便于其他函数调用
            if index == selected_index:
                activated = True
            else:
                activated = False
            self.ruleCardList.append(RuleCard(rule, index, activated, parent=self))  # 将规则以卡片的形式添加至卡片列表
            index += 1

        for card in self.ruleCardList:
            self.ruleCardLayout.addWidget(card, 0)  # 依此将卡片添加至卡片布局器中
            card.clicked.connect(lambda index=card.index: self.setSelected(index))  # 将点击卡片的动作连接至选中卡片函数

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
        """实现各控件功能"""

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
                        title = '成功'
                        message = '已删除选中的规则'

                        while self.ruleCardLayout.count():  # 逐个删除已存在的规则卡片
                            item = self.ruleCardLayout.takeAt(0)  # 每次取最前面的规则卡片
                            if item.widget():
                                item.widget().deleteLater()

                        self.addRuleCard()  # 重新将规则文件中的规则以卡片形式添加到展示区域
                    elif flag == 0:
                        title = '失败'
                        message = '无法删除最后一个规则'
                    message_window = MessageBox(title=title, content=message, parent=self)
                    message_window.yesButton.setText('确认')
                    message_window.cancelButton.hide()
                    message_window.exec()
                    self.currentIndex = -1
                else:
                    logging.info('用户取消删除规则')

        self.delRuleBtn.clicked.connect(del_rule_callback)

        def add_rule_callback():
            """添加规则"""
            addRuleWindow = ruleInputInterface(self)
            addRuleWindow.submit_data.connect(lambda: save_new_rule(self.rule_dict, rule))  # 将发射的信号传递给信号处理函数
            if addRuleWindow.exec():
                rule = analise_rule(addRuleWindow)  # 解析输入的内容
                addRuleWindow.submit_data.emit(rule)  # 发送规则种类、名称和描述的信号
                self.initRuleViewArea()  # 刷新规则卡片布局

        self.addRuleBtn.clicked.connect(add_rule_callback)

    # 规则卡片“更多”按钮菜单的各种功能实现
    def showInfoDialog(self, rule):
        """显示规则详情界面"""
        infoDialog = InfoDialog(rule, parent=self)
        infoDialog.exec()

    def reviseRule(self, rule):
        """修改规则"""
        reviseRuleWindow = ruleInputInterface(self)

        # 设置输入窗口的基本信息
        type = rule['type']
        name = rule['name']
        desc = rule['desc']

        reviseRuleWindow.ruleTypeComboBox.setCurrentIndex(type - 1)
        reviseRuleWindow.ruleNameLineEdit.setText(name)
        reviseRuleWindow.ruleDescLineEdit.setText(desc)

        # 设置输入窗口的规则关键参数
        if type == 1:
            split_char = rule['split_char']

            reviseRuleWindow.new_control['splitCharLineEdit'].setText(split_char)
        elif type == 2:
            new_ext = rule['new_ext']

            reviseRuleWindow.new_control['extLineEdit'].setText(new_ext)
        elif type == 3:
            target_str = rule['target_str']
            new_str = rule['new_str']

            reviseRuleWindow.new_control['oldStrLineEdit'].setText(target_str)
            reviseRuleWindow.new_control['newStrLineEdit'].setText(new_str)
        elif type == 4:
            split_char = rule['split_char']
            position = rule['position']
            date = rule['date']

            reviseRuleWindow.new_control['splitCharLineEdit'].setText(split_char)
            if position == 'head':
                reviseRuleWindow.new_control['headBtn'].setChecked(True)
            elif position == 'tail':
                reviseRuleWindow.new_control['tailBtn'].setChecked(True)
            reviseRuleWindow.new_control['customDateLineEdit'].setText(date)
            if date:
                reviseRuleWindow.new_control['customDateBtn'].setChecked(True)
                reviseRuleWindow.new_control['sysDateBtn'].setChecked(False)
            else:
                reviseRuleWindow.new_control['sysDateBtn'].setChecked(True)

        reviseRuleWindow.submit_data.connect(lambda: save_new_rule(self.rule_dict, rule))  # 将发射的信号传递给信号处理函数

        if reviseRuleWindow.exec():  # 显示窗口
            rule = analise_rule(reviseRuleWindow)
            reviseRuleWindow.submit_data.emit(rule)  # 发送信号给规则保存函数
            self.rule_dict = load_config()  # 刷新规则
            self.initRuleViewArea()  # 刷新规则卡片布局
