import json
import traceback
import typing

# 运行时
import runtime
# 接口
import interface
# 着色器
import shader
# 日志
import logs
# 人工智能
import intelligence
# 引擎
import engine
# 架构
import architecture

# WindowsAPI 和 系统
import sys
import ctypes
import win32gui
import win32con
# 界面和OpenGL
from OpenGL import GL

from PyQt5.Qt import QIcon, QApplication, QTimer, Qt, QRect
from PyQt5.QtWidgets import QWidget, QLabel, QStackedWidget, QHBoxLayout
from qfluentwidgets import FluentIcon, NavigationItemPosition, \
    BodyLabel, TextEdit, LineEdit, PrimaryToolButton, qrouter, NavigationInterface
from qframelesswindow import FramelessWindow, TitleBar

# 初始化变量常亮和配置
PLUGIN_GLOBAL = {"print": "To be updated", "input": "To be updated", "interface": "To be updated"}
GWL_EX_STYLE: int = -20
WS_EX_TRANSPARENT: int = 0x00000020
live2d_parameter: dict = {}
switches_configure: dict = runtime.file.load_switch()
configure: dict = runtime.file.load_configure(interface.subscribe)
languages: list[str] = runtime.file.load_language(configure)
module_info: dict = intelligence.load_gpt_sovits(runtime.parse_local_url(configure['settings']['local']['gsv']))
intelligence.reload_api(configure["settings"]['cloud']['xunfei']['id'], configure["settings"]['cloud']['xunfei']['key'],
                        configure["settings"]['cloud']['xunfei']['secret'], configure["settings"]['cloud']['aliyun'])
runtime.thread.reload_module(intelligence, runtime, logs)


# 设置界面
class CustomTitleBar(TitleBar):
    def __init__(self, parent):
        super().__init__(parent)
        self.icon_label = QLabel(self)
        self.icon_label.setFixedSize(18, 18)
        self.hBoxLayout.insertSpacing(0, 10)
        self.hBoxLayout.insertWidget(1, self.icon_label, 0, Qt.AlignLeft | Qt.AlignBottom)
        self.window().windowIconChanged.connect(self.setIcon)

        self.title_label = QLabel(self)
        self.hBoxLayout.insertWidget(2, self.title_label, 0, Qt.AlignLeft | Qt.AlignBottom)
        self.title_label.setObjectName('titleLabel')
        self.window().windowTitleChanged.connect(self.setTitle)

    def setTitle(self, title):
        self.title_label.setText(title)
        self.title_label.adjustSize()

    def setIcon(self, icon):
        self.icon_label.setPixmap(QIcon(icon).pixmap(18, 18))


class Setting(FramelessWindow):
    def __init__(self, display_x: int | None = None, display_y: int | None = None):
        super().__init__()
        self.setTitleBar(CustomTitleBar(self))
        self.setWindowIcon(QIcon("logo.ico"))
        self.setWindowTitle(languages[0])
        self.titleBar.setAttribute(Qt.WA_StyledBackground)
        self.resize(700, 530)

        self.hBoxLayout = QHBoxLayout(self)
        self.navigation_interface = NavigationInterface(
            self, showMenuButton=True, showReturnButton=True)
        self.stack_widget = QStackedWidget(self)

        # 移动
        available_position = QApplication.desktop().availableGeometry()
        w, h = available_position.width(), available_position.height()
        if display_x is not None and display_y is not None:
            self.move(display_x, display_y)
        else:
            self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

        self.general_page = interface.setting.general.General(
            languages, configure, module_info, live2d_parameter,
            play=self.reference, reload=self.reload_character)
        self.switches_page = interface.setting.switches.Switches(languages, switches_configure, configure)

        self.intelligence_page = interface.setting.intelligence.Intelligence(languages, configure)
        self.local_intelligence_page = interface.setting.sub_intelligence.local.IntelligenceLocale(languages, configure)
        self.cloud_intelligence_page = interface.setting.sub_intelligence.cloud.IntelligenceCloud(languages, configure)

        self.binding_page = interface.setting.binding.Binding(languages, configure, module_info, live2d_parameter)
        self.animation_binding_page = interface.setting.sub_binding.animation.AnimationBinding(
            languages, configure,
            module_info, desktop.model_json_path, architecture.addon,
            record=self.record_animation, live2d=architecture.live2d, pet_model=desktop.pet_model)
        self.rule_binding_page = interface.setting.sub_binding.rule.RuleBinding(languages, configure, module_info,
                                                                                live2d_parameter)
        self.tools_binding_page = interface.setting.sub_binding.tools.ToolsBinding(languages, configure, module_info,
                                                                                   live2d_parameter)
        self.plugin_binding_page = interface.setting.sub_binding.plugin.PluginBinding(self.run_code_for_plugin,
                                                                                      languages, configure)

        self.about_page = interface.setting.about.About(languages, runtime)
        self.record_timer = QTimer(self)

        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.addWidget(self.navigation_interface)
        self.hBoxLayout.addWidget(self.stack_widget)
        self.hBoxLayout.setStretchFactor(self.stack_widget, 1)

        self.titleBar.raise_()
        self.navigation_interface.displayModeChanged.connect(self.titleBar.raise_)

        self.addSubInterface(self.general_page, FluentIcon.SETTING, languages[1])
        self.addSubInterface(self.switches_page, FluentIcon.DEVELOPER_TOOLS, languages[10])

        self.addSubInterface(self.intelligence_page, FluentIcon.EDUCATION, languages[27])
        self.addSubInterface(self.cloud_intelligence_page, FluentIcon.CLOUD, languages[29],
                             parent=self.intelligence_page)
        self.addSubInterface(self.local_intelligence_page, FluentIcon.DOWN, languages[31],
                             parent=self.intelligence_page)

        self.addSubInterface(self.binding_page, FluentIcon.TRANSPARENT, languages[36])
        self.addSubInterface(self.animation_binding_page, FluentIcon.LIBRARY_FILL, languages[42],
                             parent=self.binding_page)
        self.addSubInterface(self.rule_binding_page, FluentIcon.ALIGNMENT, languages[37], parent=self.binding_page)
        self.addSubInterface(self.tools_binding_page, FluentIcon.EMOJI_TAB_SYMBOLS, languages[55],
                             parent=self.binding_page)
        self.addSubInterface(self.plugin_binding_page, FluentIcon.IOT, languages[112], parent=self.binding_page)

        self.addSubInterface(PluginLogCollector, FluentIcon.COMMAND_PROMPT, languages[141],
                             position=NavigationItemPosition.BOTTOM)
        self.addSubInterface(self.about_page, FluentIcon.INFO, languages[66], position=NavigationItemPosition.BOTTOM)

        qrouter.setDefaultRouteKey(self.stack_widget, self.switches_page.objectName())

        self.stack_widget.currentChanged.connect(self.onCurrentInterfaceChanged)
        self.stack_widget.setCurrentIndex(1)

    # 自定义
    def addSubInterface(self, widget, icon, text: str, position=NavigationItemPosition.TOP, parent=None):
        self.stack_widget.addWidget(widget)
        self.navigation_interface.addItem(
            parentRouteKey=None if parent is None else parent.objectName(),
            routeKey=widget.objectName(),
            icon=icon,
            text=text,
            onClick=lambda: self.switchTo(widget),
            position=position,
            tooltip=text
        )

    def switchTo(self, widget):
        self.stack_widget.setCurrentWidget(widget)

    def onCurrentInterfaceChanged(self, index):
        widget = self.stack_widget.widget(index)
        self.navigation_interface.setCurrentItem(widget.objectName())
        qrouter.push(self.stack_widget, widget.objectName())

    # Function
    def record_animation(self):
        def recorder():
            self.animation_binding_page.refresh_position(*configure['record']['position'])
            if not configure['record']['position'].count(-1):
                self.record_timer.stop()
                configure['record']['enable_position'] = False
                with open("./resources/configure.json", "w", encoding="utf-8") as rf:
                    json.dump(configure, rf, ensure_ascii=False, indent=3)
                    rf.close()

        if self.record_timer.isActive():
            self.record_timer.stop()
        else:
            configure['record']['position'] = [-1, -1, -1, -1]
            self.record_timer.timeout.connect(recorder)
            self.record_timer.start(50)

    def reload_character(self, model):
        global desktop
        desktop.close()
        architecture.live2d.dispose()

        architecture.live2d.init()
        runtime.file.load_template_model(configure, model)
        conversation.move(desktop.x(), desktop.y())
        desktop = DesktopPet(desktop.x(), desktop.y())
        desktop.show()
        interface.subscribe.RegisterAttribute().SetWindow(desktop)

        interface.subscribe.actions.Register().UnsetALL()
        self.close()
        self.__init__(self.x(), self.y())
        self.show()

    def exception(self, e_msg):
        print(e_msg)
        interface.setting.customize.widgets.pop_error(self, "TraceBack", e_msg, 5000, Qt.Vertical)

    def examine_and_run(self, codes, type_: typing.Literal['independent', 'enhancement']):
        try:
            if runtime.PythonCodeExaminer(codes).optimize_infinite_loop:
                interface.setting.customize.widgets.pop_warning(self, languages[157], languages[158], 5000)
                return
            safety_level = configure['settings']['safety']
            attr = getattr(runtime.PythonCodeExaminer(codes), f"is_{safety_level}")
            if safety_level != "shut" and (list(attr)[-1] or list(attr)[0]):
                interface.setting.customize.widgets.pop_warning(self, languages[157], languages[159], 5000)
                return

        except Exception:
            self.exception(traceback.format_exc())
            return
        if type_ == 'enhancement':
            try:
                exec(codes, PLUGIN_GLOBAL)
            except Exception:
                self.exception(traceback.format_exc())

        elif type_ == 'independent':
            try:
                thread_run = runtime.thread.RunPythonPlugin(self, codes, PLUGIN_GLOBAL)
                thread_run.error.connect(self.exception)
                thread_run.start()
            except Exception:
                self.exception(traceback.format_exc())

    def run_code_for_plugin(self, codes, run_type=-4):
        # 自动选择
        if run_type == -4:
            try:
                parsed = runtime.PythonCodeParser(codes).has_subscribe
            except Exception:
                self.exception(traceback.format_exc())
                return
            if parsed:
                self.examine_and_run(codes, 'enhancement')

            else:
                self.examine_and_run(codes, 'independent')

        # 程序增强
        elif run_type == -2:
            self.examine_and_run(codes, 'enhancement')

        # 独立程序
        elif run_type == -3:
            self.examine_and_run(codes, 'independent')

    # 测试语音合成组
    def reference(self, text):
        voice_generator = runtime.thread.VoiceGenerateThread(desktop, text.split(":")[-1], text.split(":")[0])
        voice_generator.result.connect(self.play)
        voice_generator.error.connect(self.error)
        voice_generator.start()

    @staticmethod
    def play(audio_bytes):
        runtime.thread.SpeakThread(desktop, audio_bytes).start()

    def error(self, value):
        if value is False:
            self.pop_error(languages[140], languages[140])

    def resizeEvent(self, e):
        self.titleBar.move(46, 0)
        self.titleBar.resize(self.width() - 46, self.titleBar.height())


class Conversation(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(400, 600)

        self.input_answer = TextEdit(self)
        self.input_answer.setGeometry(QRect(0, 0, 400, 60))
        self.input_answer.setReadOnly(True)

        self.click_send = PrimaryToolButton(self)
        self.click_send.setIcon(FluentIcon.SEND)
        self.click_send.setGeometry(QRect(340, 431, 60, 30))
        self.click_send.clicked.connect(lambda: self.send_question())

        self.click_take_photo = PrimaryToolButton(self)
        self.click_take_photo.setIcon(FluentIcon.CAMERA)
        self.click_take_photo.setGeometry(QRect(280, 431, 60, 30))
        self.click_take_photo.clicked.connect(lambda: self.take_photo())
        self.input_question = LineEdit(self)
        self.input_question.setGeometry(QRect(0, 430, 281, 30))

        # 为发送绑定按键
        self.input_question.returnPressed.connect(lambda: self.click_send.click())

        # 不可见
        self.input_question.setVisible(False)
        self.click_send.setVisible(False)
        self.click_take_photo.setVisible(False)
        self.input_answer.setVisible(False)

    @staticmethod
    def take_photo():
        desktop.capture_screen()

    def send_question(self):
        self.input_question.setGeometry(QRect(0, 430, 400, 30))
        self.click_send.setVisible(False)
        self.click_take_photo.setVisible(False)
        desktop.have_conversation(self.input_question.text())


class DesktopPet(shader.ADPOpenGLCanvas):
    def __init__(self, display_x: int | None = None, display_y: int | None = None):
        super().__init__()
        # 设置标题
        self.setWindowTitle("AgenticCompanion - Character Mainloop")
        # 设置图标
        self.setWindowIcon(QIcon("logo.ico"))
        # 设置属性
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMouseTracking(True)
        self.setAcceptDrops(True)
        # 调整大小
        self.setFixedSize(400, 400)

        # 变量初始化
        self.fps_refresh = int(1000 / 900)
        self.turn_count = self.expression_count = 0
        self.model_json_path: str = ""
        self.amount = self.click_in_area = self.click_x = self.click_y = -1
        self.speaking_lists: list[bool] = []
        self.is_playing_expression = self.is_penetration = self.is_playing_animation = self.is_movement = False
        self.enter_position = self.drag_position = None
        self.image_path = self.direction = self.last_pos = None
        self.pet_model: architecture.live2d.LAppModel | None = None

        # 移动位置
        if display_x is not None and display_y is not None:
            self.move(display_x, display_y)
        else:
            # 屏幕中心坐标
            self.screen_geometry = QApplication.desktop().availableGeometry()
            x = (self.screen_geometry.width() - self.width()) // 2
            y = self.screen_geometry.height() - self.height()
            self.move(x, y + 15)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    PluginLogCollector = interface.setting.plog.PluginLogCollector()
    PLUGIN_GLOBAL['interface'] = interface
    PLUGIN_GLOBAL['print'] = PluginLogCollector.print_
    PLUGIN_GLOBAL['input'] = PluginLogCollector.input_

    desktop = DesktopPet()
    desktop.show()
    setting = Setting()
    conversation = Conversation()
    setting.show()

    interface.subscribe.views.RegisterSetting.register(setting)

    sys.exit(app.exec())
