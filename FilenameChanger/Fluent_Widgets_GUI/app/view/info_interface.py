from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QWidget, QVBoxLayout

from FilenameChanger.Fluent_Widgets_GUI.qfluentwidgets import (SubtitleLabel, PushButton, FluentIcon, MessageBoxBase,
                                                               SmoothScrollArea, TextBrowser, HyperlinkButton)
from FilenameChanger.Fluent_Widgets_GUI.qfluentwidgets import setFont

from FilenameChanger import version, author

help_content_md = """\
# 使用方法

## 文件重命名

- 点击侧边导航栏的“规则列表”按钮跳转到“规则列表”界面
- 点击添加规则，选择一个规则类型，将所有必填选项填写完毕后点击确定即可添加新规则
- 鼠标点击新增的规则卡片，点击上方的“激活规则”按钮将其设置为激活状态（添加的第一个规则会自动激活）
- 通过侧边导航栏回到主界面，点击输入框右边的文件夹按钮选择文件夹
- 选择文件夹后程序将自动检测路径是否可用，若通过检测则会将重命名按钮设置为可用状态
- 点击文件夹按钮右边的列表按钮，在弹出的文件列表界面选择需要重命名的文件
- 点击“文件重命名”按钮，确认操作无误后点击弹出的消息框的“确认”按钮，程序将对文件夹内的文件进行重命名  
  
## 撤销重命名
- 点击主页的“撤销重命名”按钮，若原来的文件夹存在则会将文件夹内的文件名恢复到上一次重命名前的状态，同时删除一条重命名历史记录，此操作不需要依赖任何重命名规则

## 规则编辑

### 修改规则
- 点击规则卡片最右边的“更多”按钮
- 点击弹出菜单中的“修改规则”按钮

### 查看规则详情
- 点击规则卡片最右边的”更多“按钮
- 点击弹出菜单中的“规则详情”即可呼出规则详情界面
- 输入修改后的规则参数，点击“确定”即可完成规则修改

## 历史记录
- 用户可以前往“历史记录”界面查看重命名的历史记录，点击历史记录卡片右方的按钮可以查看文件名更改的详细信息
- 小提示：从v2.1.0开始历史记录将包含重命名日期，若使用的是旧版的历史记录文件则会显示“未知时间”字样，这是正常现象

### 历史记录删除和清空
- 用户点击一个历史记录卡片后点击“删除历史记录”按钮，确认操作后将会删除选中的历史记录
- 用户点击“清空历史记录”按钮将会删除所有历史记录

# 注意事项
- 为了确保文件重命名不会损害您的设备，本程序将不会修改任何隐藏文件、只读文件和系统文件，尽管如此，我仍建议您将需要重命名的文件单独存放至一个干净的文件夹内，以免造成不可挽回的后果。
"""
changeLog_content_md = """\
# v2.3.0

### 新增内容
- 第一类规则的分隔符支持正则表达式
- 增加文件列表界面，用户可以在该界面选择需要重命名的文件

### 优化和修复
- 修复规则输入界面部分输入框仍能输入"\\"的BUG
- 规则详情界面限定了宽度，防止因描述过长导致界面过分拉伸
- 部分需要区分空格的输入框空格更加明显
- 规则描述为空时对应规则卡片和规则详情会显示"<无>"
- 现在添加、修改、删除规则不会强制滚动到规则卡片展示区域顶部了

# v2.2.0

### 新增内容
- 现在程序有它自己的图标了
- 第三类规则（替换字符串）增加对正则表达式的支持
- 历史记录详情界面会显示重命名时出错的文件和出错原因
- 增加第五类规则：重命名并编号
- 第四类规则（日期替换）增加对文件创建、修改、访问日期的支持
- 第四类规则（日期替换）支持填充YYYY年MM月DD日格式
- 历史记录卡片增加“打开文件夹”按钮，点击即可用文件资源管理器打开对应文件夹
- 增加第六类规则：字母大小写转换

### 优化和修复
- 修复历史记录卡片在浅色模式选中时会显示标签轮廓的BUG
- 修复重命名导致文件名重复时程序崩溃的BUG
- 修复第四类规则无法移除不在文件名开头的日期的BUG
- 修复对被占用的文件重命名时崩溃的BUG
- 规则详情界面增加滚动区域，解决详情界面无法容纳所有规则参数的问题
- 将规则切换为其他种类时规则名称和描述会自动清空
- 查看第三、四类规则详情时空格和空串会分别显示<空格>和<空>，而不是什么都不显示
- 第四类规则详情的“填充位置”只会在填充日期不为空时显示

### 更改内容
- 第三类规则（替换字符串）现在会替换所有符合要求的字符串，以前只会替换一处
- 现在越新的历史记录会越靠前
- 第四类规则从“添加或删除日期”更名为“日期替换”，更改该规则逻辑为将文件名中的日期替换为指定日期，自定义日期可留空以删除文件名中的日期

# v2.1.0

### 新增内容
- 新增规则卡片“更多”按钮，可以呼出菜单进行更多操作
- 新增规则详情界面，可通过规则卡片“更多”按钮的菜单呼出
- 新增修改规则的功能，可通过“更多”按钮菜单呼出
- 规则列表界面添加“规则说明”按钮，点击后能够弹出解释各种规则的功能的窗口
- 现在历史记录将会记录系统日期
- 增加历史记录界面，用户可以查看和删除历史记录

### 优化和修复
- 修复使用填充系统日期的第四类规则重命名会导致程序崩溃的BUG
- 修复多次添加规则导致程序崩溃的BUG
- 修复添加规则后又删除该规则导致程序崩溃的BUG
- 修改了没有规则时规则列表的提示语
- 修改规则卡片中规则描述的字体粗细
- 移除了删除规则成功的消息框
- 优化规则输入界面的布局，现在第四类规则的分隔符输入框的提示语能够完全显示了，补充第三类规则新字符串输入框提示语的“必填”字样
- 如果重命名前后所有文件的新旧文件名都相同，则会弹出相应弹窗提示用户为什么没有产生新的重命名记录
- 优化日志记录的内容，提高日志文件的可读性


# v2.0.0

### 新增内容
- 新增关于软件的界面，可以查看更新日志和帮助文档
- 没有规则时会在规则列表显示“当前没有任何规则”字样

### 优化和修复
- 修复添加规则界面直接点击“确定”导致程序崩溃的BUG，现在只有选择规则类型后才能点击确定按钮
- 修复规则列表为空时进行重命名操作导致程序崩溃的BUG
- 优化添加规则界面的输入框，对输入内容进行了一些限制（例如不能存在于文件名中的字符）
- 新增规则时若还有未输入的必填项，则点击确定按钮时会提示先填写必填项再点击确定

# v2.0.0-pre1

### 新增内容
- 新增图形化窗口，操作更加简单！

### 优化和修复
- 优化新文件名的生成方式，减小内存开销
- 优化重命名记录的逻辑，现在只记录成功重命名的文件
- 修复第一类规则重命名后会导致文件名出现过多空格的BUG

# v1.4.1

### 新增内容
- 第四类规则能够自定义填充的日期，若不填充自定义日期则动态填充系统日期

### 优化和修复
- 修复对没有扩展名的文件重命名时会崩溃的BUG
- 优化日志记录，现在会记录当前激活的规则的序号和种类

# v1.4.0

### 新增功能
- 新增第四类规则：检测文件名是否含有日期，有则移除，没有则添加当前日期，可选择添加到头部或尾部

### 优化和修复
- 日志优化，现在日志文件会以日期命名，以便查看当天程序运行状况
- 现在重命名的确认操作在扫描文件夹之前，避免用户停留在确认步骤时修改目标文件夹导致实际文件名与扫描到的文件名不匹配

# v1.3.0

### 新增功能
- 新增重命名记录功能，记录重命名前后的文件名以便撤销重命名操作
- 新增撤销重命名功能，帮助用户快速恢复重命名前的状态

# v1.2.1

### 优化和修复
- 修复用户输入空文件夹路径导致程序崩溃的BUG
- 优化交互逻辑，现在执行完操作后会停顿0.5秒再回到主菜单

# v1.2.0

### 新增功能
- 新增第二、三类规则：批量修改扩展名、批量修改文件名中特定字符串

### BUG修复
- 修复删除已激活规则前面的规则会导致选中最后一个规则的BUG

# v1.1.1

### BUG修复
- 修复删除已选中的规则时不会自动切换至可用规则BUG（这可能导致下标越界使得程序崩溃）

# v1.1.0

### 新增内容
- 现在可以保存多个重命名规则
- 新增规则查看、删除和激活的功能
- 新增日志功能

### 优化
- 优化提示语，使得格式更加统一
- 优化规则文件内容格式，以支持多重规则
- 在操作选择界面可以取消本次操作并返回主菜单

# v1.0.0
这已经是最早的版本了！

### 主要功能
- 根据规则中的分隔符拆分文件名并交换位置
- 用户自定义分隔符
"""


class TextInterface(MessageBoxBase):
    """更新日志界面"""

    def __init__(self, title, text, parent=None):
        super().__init__(parent=parent)
        self.cancelButton.setHidden(True)  # 不需要取消按钮
        self.yesButton.setText('确定')

        self.widget.setMinimumWidth(600)  # 设置最小窗口宽度
        self.widget.setFixedHeight(700)  # 设置固定窗口高度

        """标题标签"""
        self.titleLabel = SubtitleLabel(text=title, parent=self.widget)

        self.viewLayout.addWidget(self.titleLabel)

        """文本内容显示"""
        self.textBrowser = TextBrowser(self)  # 存放更新日志的容器
        self.textScrollArea = SmoothScrollArea(parent=self.widget)
        self.textScrollArea.setWidget(self.textBrowser)  # 将更新日志容器放入滚动界面

        self.textScrollArea.setWidgetResizable(True)  # 将大小设置为可变

        self.viewLayout.addWidget(self.textScrollArea)

        self.textBrowser.setMarkdown(text)  # 将内容添加至文本框


class InfoInterface(QWidget):
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
        self.urlBtn = HyperlinkButton(icon=FluentIcon.LINK, url='https://github.com/E-zhiyu/Filename_Changer',
                                      text='查看源代码')

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
            changeLog = TextInterface(title='更新日志', text=changeLog_content_md, parent=self)
            changeLog.exec()

        self.changeLogBtn.clicked.connect(changeLogBtn_function)

        # 实现帮助按钮功能
        def helpBtn_function():
            help = TextInterface(title='帮助界面', text=help_content_md, parent=self)
            help.exec()

        self.helpBtn.clicked.connect(helpBtn_function)
