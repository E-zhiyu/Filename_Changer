from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QWidget, QVBoxLayout

from FilenameChanger.Fluent_Widgets_GUI.qfluentwidgets import (SubtitleLabel, PushButton, FluentIcon, MessageBoxBase,
                                                               SmoothScrollArea, TextBrowser)
from FilenameChanger.Fluent_Widgets_GUI.qfluentwidgets import setFont

from FilenameChanger import version, author
from Fluent_Widgets_GUI.qfluentwidgets import HyperlinkButton

help_content_md = """\
# 使用方法\n

### 文件重命名\n

- 点击侧边导航栏的“规则列表”按钮跳转到“规则列表”界面。\n  
- 点击添加规则，选择一个规则类型，将所有必填选项填写完毕后点击确定即可添加新规则。\n  
- 鼠标点击新增的规则卡片，点击上方的“激活规则”按钮将其设置为激活状态。\n  
- 通过侧边导航栏回到主界面，点击输入框右边的按钮选择文件夹。\n  
- 选择文件夹后程序将自动检测路径是否可用，若通过检测则会将重命名按钮设置为可用状态。\n  
- 点击“文件重命名”按钮，确认操作无误后点击弹出的消息框的“确认”按钮，程序将对文件夹内的文件进行重命名。\n  
  
  ### 撤销重命名\n
- 点击主页的“撤销重命名”按钮即可撤销一次重命名（前提是原来的文件夹存在），此操作不需要依赖任何重命名规则。\n  
  
  # 注意事项\n
- 为了确保文件重命名不会损害您的设备，本程序将不会修改任何隐藏文件、只读文件和系统文件，尽管如此，我仍建议您将需要重命名的文件单独存放至一个干净的文件夹内，以免造成不可挽回的后果。
"""
changeLog_content_md = """\
# v2.0.0

### 新增内容

- 新增关于软件的界面，可以查看更新日志和帮助文档

- 没有规则时会在规则列表显示“当前没有任何规则”字样

### 优化和修复

- 修复添加规则界面直接点击“确定”导致程序崩溃的BUG，现在只有选择规则类型后才能点击确定按钮

- 修复规则列表为空时进行重命名操作导致程序崩溃的BUG
  
- 优化添加规则界面的输入框，对输入内容进行了一些限制（例如不能存在于文件名中的字符）
  
- 新增规则时若还有未输入的必填项，则点击确定按钮时会提示先填写必填项再点击确定
\n
# v2.0.0-pre1

### 新增内容

- 新增图形化窗口，操作更加简单！

### 优化和修复

- 优化新文件名的生成方式，减小内存开销
  
- 优化重命名记录的逻辑，现在只记录成功重命名的文件
  
- 修复第一类规则重命名后会导致文件名出现过多空格的BUG
\n
# v1.4.1

### 新增内容

- 第四类规则能够自定义填充的日期，若不填充自定义日期则动态填充系统日期

### 优化和修复

- 修复对没有扩展名的文件重命名时会崩溃的BUG
  
- 优化日志记录，现在会记录当前激活的规则的序号和种类
\n
# v1.4.0

### 新增功能

- 新增第四类规则：检测文件名是否含有日期，有则移除，没有则添加当前日期，可选择添加到头部或尾部

### 优化和修复

- 日志优化，现在日志文件会以日期命名，以便查看当天程序运行状况
  
- 现在重命名的确认操作在扫描文件夹之前，避免用户停留在确认步骤时修改目标文件夹导致实际文件名与扫描到的文件名不匹配
\n
# v1.3.0

### 新增功能

- 新增重命名记录功能，记录重命名前后的文件名以便撤销重命名操作
  
- 新增撤销重命名功能，帮助用户快速恢复重命名前的状态
\n
# v1.2.1

### 优化和修复

- 修复用户输入空文件夹路径导致程序崩溃的BUG
  
- 优化交互逻辑，现在执行完操作后会停顿0.5秒再回到主菜单
\n
# v1.2.0

### 新增功能

- 新增第二、三类规则：批量修改扩展名、批量修改文件名中特定字符串

### BUG修复

- 修复删除已激活规则前面的规则会导致选中最后一个规则的BUG
\n
# v1.1.1

### BUG修复

- 修复删除已选中的规则时不会自动切换至可用规则BUG（这可能导致下标越界使得程序崩溃）
\n
# v1.1.0

### 新增内容

- 现在可以保存多个重命名规则
  
- 新增规则查看、删除和激活的功能
  
- 新增日志功能

### 优化

- 优化提示语，使得格式更加统一
  
- 优化规则文件内容格式，以支持多重规则
  
- 在操作选择界面可以取消本次操作并返回主菜单
\n
# v1.0.0

这已经是最早的版本了！

### 主要功能

- 根据规则中的分隔符拆分文件名并交换位置
  
- 用户自定义分隔符"""


class ChangeLogInterface(MessageBoxBase):
    """更新日志界面"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.cancelButton.setHidden(True)  # 不需要取消按钮
        self.yesButton.setText('确定')

        self.widget.setMinimumWidth(600)  # 设置最小窗口宽度
        self.widget.setFixedHeight(700)  # 设置固定窗口高度

        """标题文本标签"""
        self.titleLabel = SubtitleLabel(text='更新日志', parent=self.widget)

        self.viewLayout.addWidget(self.titleLabel)

        """更新日志内容"""
        self.changeLogTextBrowser = TextBrowser()  # 存放更新日志的容器
        self.changeLogScrollArea = SmoothScrollArea(parent=self.widget)
        self.changeLogScrollArea.setWidget(self.changeLogTextBrowser)  # 将更新日志容器放入滚动界面

        self.changeLogScrollArea.setWidgetResizable(True)  # 将大小设置为可变

        self.viewLayout.addWidget(self.changeLogScrollArea)

        self.changeLogTextBrowser.setMarkdown(changeLog_content_md)  # 将内容添加至文本框


class HelpInterface(MessageBoxBase):
    """获取帮助界面"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.cancelButton.setHidden(True)
        self.yesButton.setText('确定')

        self.widget.setMinimumWidth(600)  # 设置最小窗口宽度
        self.widget.setFixedHeight(700)  # 设置固定窗口高度

        self.viewLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        """标题标签"""
        self.howToUseLabel = SubtitleLabel(text='帮助', parent=self.widget)

        setFont(self.howToUseLabel, 25)

        self.viewLayout.addWidget(self.howToUseLabel)

        """内容展示"""
        self.contentScrollArea = SmoothScrollArea()
        self.useTextBrowser = TextBrowser(parent=self.widget)
        self.contentScrollArea.setWidget(self.useTextBrowser)  # 将文本框放入滚动页面

        self.contentScrollArea.setWidgetResizable(True)  # 将大小设置为可变

        self.viewLayout.addWidget(self.contentScrollArea)

        self.useTextBrowser.setMarkdown(help_content_md)


class InfoInterface(QFrame):
    """关于软件的界面"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName('InfoInterface')  # 设置对象名

        """基本布局设置"""
        self.interfaceLayout = QVBoxLayout(self)  # 界面布局器
        self.totalWidget = QWidget(self)  # 总容器
        self.widgetLayout = QVBoxLayout(self.totalWidget)  # 界面的垂直布局器
        self.interfaceLayout.addWidget(self.totalWidget)  # 总容器添加到窗口布局器

        self.widgetLayout.setAlignment(Qt.AlignmentFlag.AlignTop)  # 设置为顶部对齐
        self.interfaceLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(self.interfaceLayout)

        """左上角的标题标签"""
        self.titleLabel = SubtitleLabel(text='关于软件', parent=self)

        setFont(self.titleLabel, 30)

        self.widgetLayout.addWidget(self.titleLabel, 0, Qt.AlignmentFlag.AlignCenter)

        """软件信息标签"""
        self.versionLabel = SubtitleLabel(text=f'版本：{version}', parent=self)
        self.authorLabel = SubtitleLabel(text=f'作者：{author}', parent=self)

        setFont(self.versionLabel, 15)
        setFont(self.authorLabel, 15)

        self.widgetLayout.addWidget(self.versionLabel, 0, Qt.AlignmentFlag.AlignCenter)
        self.widgetLayout.addWidget(self.authorLabel, 0, Qt.AlignmentFlag.AlignCenter)

        """项目地址"""
        self.urlBtn = HyperlinkButton(url='https://github.com/E-zhiyu/Filename_Changer', text='查看源代码')

        self.widgetLayout.addWidget(self.urlBtn, 0, Qt.AlignmentFlag.AlignCenter)

        """更新日志"""
        self.changeLogBtn = PushButton(FluentIcon.DOCUMENT, '更新日志')

        self.widgetLayout.addWidget(self.changeLogBtn, 0, Qt.AlignmentFlag.AlignCenter)

        """获取帮助"""
        self.helpBtn = PushButton(FluentIcon.HELP, '获取帮助')

        self.widgetLayout.addWidget(self.helpBtn, 0, Qt.AlignmentFlag.AlignCenter)

        """实现控件功能"""
        self.achieve_function()

    def achieve_function(self):
        """实现控件功能"""

        # 实现更新日志按钮功能
        def changeLogBtn_function():
            changeLog = ChangeLogInterface(self)
            changeLog.exec()

        self.changeLogBtn.clicked.connect(changeLogBtn_function)

        # 实现帮助按钮功能
        def helpBtn_function():
            help = HelpInterface(self)
            help.exec()

        self.helpBtn.clicked.connect(helpBtn_function)
