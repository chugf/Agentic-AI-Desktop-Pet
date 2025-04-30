import traceback
import typing
import shutil
import re
import random
import json
import subprocess
from difflib import get_close_matches
from socket import gethostbyname, gethostname
from threading import Thread

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
import os
import sys
import ctypes
import win32gui
import win32con
# 界面和OpenGL
from OpenGL import GL

from PyQt5.Qt import QIcon, QApplication, QTimer, Qt, QRect, QTimerEvent, QCursor, QGuiApplication, \
    QMimeData, QColor, QLinearGradient, QPainter, QBrush, QPixmap, QFileDialog, QLocale
from PyQt5.QtWidgets import QWidget, QLabel, QStackedWidget, QHBoxLayout, QMessageBox
from qfluentwidgets import FluentIcon, NavigationItemPosition, FluentTranslator, \
    TextEdit, LineEdit, PrimaryToolButton, qrouter, NavigationInterface, RoundMenu, Action
from qframelesswindow import FramelessWindow, TitleBar

# 初始化变量常亮和配置
# 检测Python环境变量
try:
    subprocess.check_output(['python', '--version'], stderr=subprocess.STDOUT, text=True)
    IS_PYTHON_EXITS = True
except subprocess.CalledProcessError as e:
    IS_PYTHON_EXITS = False
PLUGIN_GLOBAL = {"print": typing.Any, "input": typing.Any, "interface": typing.Any}
GWL_EX_STYLE: int = -20
WS_EX_TRANSPARENT: int = 0x00000020
live2d_parameter: dict = {}
switches_configure: dict = runtime.file.load_switch()
configure, configure_default = runtime.file.load_configure(interface.subscribe)
rules = runtime.file.load_rules(configure_default)
api_config = runtime.file.load_api()
languages: list[str] = runtime.file.load_language(configure)
module_info: dict = intelligence.load_gpt_sovits(runtime.parse_local_url(configure['settings']['local']['gsv']))
intelligence.text.reload_memories(configure_default)
intelligence.text.reload_tools()
intelligence.reload_api(configure["settings"]['cloud']['xunfei']['id'], configure["settings"]['cloud']['xunfei']['key'],
                        configure["settings"]['cloud']['xunfei']['secret'], configure["settings"]['cloud']['aliyun'])
runtime.thread.reload_module(interface, intelligence, runtime, logs)
engine.webapi.reload_module(intelligence)
engine.webapi.reload_data(configure['settings']['intelligence'],
                          api_config, configure['language_mapping'][configure['settings']['language']],
                          runtime.parse_local_url(configure['settings']['local']['text'])
                          if configure['settings']['text']['way'] == "local" else None)
# 判断架构支持并重载
if os.path.exists(f"./resources/model/{configure_default}/2"):
    architecture.reload(2)
else:
    architecture.reload(3)


class PictureShow(QWidget):
    """展示绘画图片"""
    def __init__(self):
        super().__init__()
        self.image_path = None
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setWindowTitle("PictureShow - Ai Desktop Pet")
        self.setWindowIcon(QIcon('logo.ico'))

        self.image_show = QLabel(self)

    def _save_as(self):
        select_save_folder = QFileDialog.getExistingDirectory(self)
        if select_save_folder:
            shutil.copy(self.image_path, select_save_folder)
            return True
        return False

    def _save_as_and_remove_origin(self):
        if self._save_as():
            os.remove(self.image_path)
            self.close()

    def open(self, file_path):
        self.image_path = file_path

        pixmap = QPixmap(self.image_path)
        try:
            pixmap = pixmap.scaled(pixmap.width() // 3, pixmap.height() // 3,
                                   Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_show.setPixmap(pixmap)
        except Exception:
            self.image_show.setText(f"{traceback.format_exc()}\n"
                                    f"Failed to show\nGo {self.image_path}\nOr go ./logs/picture to see")

        self.resize(pixmap.width(), pixmap.height())
        self.image_show.setScaledContents(True)

    def contextMenuEvent(self, event):
        menu = RoundMenu("MENU", self)

        image_path = os.path.join(os.getcwd(), self.image_path)

        save_as_action = Action(FluentIcon.SAVE_AS, languages[142], self)
        save_as_action.triggered.connect(self._save_as)
        menu.addAction(save_as_action)

        save_as_and_remove_action = Action(FluentIcon.MOVE, languages[143], self)
        save_as_and_remove_action.triggered.connect(self._save_as_and_remove_origin)
        menu.addAction(save_as_and_remove_action)

        open_file_action = Action(FluentIcon.LINK, languages[144], self)
        open_file_action.triggered.connect(lambda: os.startfile(image_path))
        menu.addAction(open_file_action)

        open_folder_action = Action(FluentIcon.FOLDER, languages[145], self)
        open_folder_action.triggered.connect(lambda: os.startfile(os.path.dirname(image_path)))
        menu.addAction(open_folder_action)

        menu.exec_(event.globalPos())


class AudioVisualization(QWidget):
    """音频可视化"""
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowTransparentForInput)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(0.5)

        self.setWindowTitle("AudioVisualization - Ai Desktop Pet")
        self.setWindowIcon(QIcon('logo.ico'))
        self.setFixedSize(400, 200)
        self.rectangles = []

    def draw_rectangle(self, rms):
        if len(self.rectangles) >= 400 // 15:
            self.rectangles.pop(0)
        self.rectangles.append(int(rms))
        self.update()

    @staticmethod
    def get_rainbow_gradient(height):
        colors = [
            QColor(148, 0, 211),
            QColor(75, 0, 130),
            QColor(0, 0, 255),
            QColor(0, 255, 0),
            QColor(255, 255, 0),
            QColor(255, 127, 0),
            QColor(255, 0, 0)
        ]
        gradient = QLinearGradient(0, 0, 0, height)
        gradient.setColorAt(0.0, colors[0])
        gradient.setColorAt(0.15, colors[0])
        gradient.setColorAt(0.15, colors[1])
        gradient.setColorAt(0.3, colors[1])
        gradient.setColorAt(0.3, colors[2])
        gradient.setColorAt(0.45, colors[2])
        gradient.setColorAt(0.45, colors[3])
        gradient.setColorAt(0.6, colors[3])
        gradient.setColorAt(0.6, colors[4])
        gradient.setColorAt(0.75, colors[4])
        gradient.setColorAt(0.75, colors[5])
        gradient.setColorAt(0.9, colors[5])
        gradient.setColorAt(0.9, colors[6])
        gradient.setColorAt(1.0, colors[6])
        return gradient

    def paintEvent(self, event):
        painter = QPainter(self)
        x_offset = 0
        for width in self.rectangles:
            gradient = self.get_rainbow_gradient(width)
            brush = QBrush(gradient)
            painter.setBrush(brush)
            painter.drawRect(x_offset, 20, 15, width)
            x_offset += 15


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
    def __init__(self, display_x: int | None = None, display_y: int | None = None, point_index: int = 0):
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
            intelligence, runtime,
            languages, configure, module_info, live2d_parameter,
            play=self.reference, reload=self.reload_character, live2d=architecture.live2d
        )
        self.switches_page = interface.setting.switches.Switches(languages, switches_configure, configure)

        def change(value, relative):
            interface.setting.customize.function.change_configure(
                value.value, relative, configure
            )
            engine.webapi.reload_data(configure['settings']['intelligence'],
                                      api_config, configure['language_mapping'][configure['settings']['language']],
                                      runtime.parse_local_url(configure['settings']['local']['text'])
                                      if configure['settings']['text']['way'] == "local" else None)

        self.intelligence_page = interface.setting.intelligence.Intelligence(languages, configure, change)
        self.local_intelligence_page = interface.setting.sub_intelligence.local.IntelligenceLocale(
            languages, configure, api_config, change, desktop, self)
        self.cloud_intelligence_page = interface.setting.sub_intelligence.cloud.IntelligenceCloud(
            languages, configure, self.reload_intelligence)

        self.binding_page = interface.setting.binding.Binding(languages, configure, runtime, self.addSubInterface)
        self.character_sets_page = interface.setting.sub_binding.character.Character(
            languages, configure, api_config, intelligence, runtime
        )
        self.animation_binding_page = interface.setting.sub_binding.animation.AnimationBinding(
            languages, configure, desktop.model_json_path, architecture.addon,
            record=self.record_animation, live2d=architecture.live2d, desktop=desktop
        )
        self.rule_binding_page = interface.setting.sub_binding.rule.RuleBinding(
            languages, configure, rules, desktop.model_json_path, architecture.addon, runtime)
        self.tools_binding_page = interface.setting.sub_binding.tools.ToolsBinding(
            languages, configure, live2d_parameter)
        self.plugin_binding_page = interface.setting.sub_binding.plugin.PluginBinding(
            interface, self.run_code_for_plugin, languages, configure)

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

        self.addSubInterface(self.binding_page, FluentIcon.TRANSPARENT, languages[133])
        self.addSubInterface(self.character_sets_page, QIcon("logo.ico"),
                             languages[164], parent=self.binding_page)
        self.addSubInterface(self.animation_binding_page, FluentIcon.LIBRARY_FILL, languages[39],
                             parent=self.binding_page)
        self.addSubInterface(self.rule_binding_page, FluentIcon.ALIGNMENT, languages[49], parent=self.binding_page)
        self.addSubInterface(self.tools_binding_page, FluentIcon.EMOJI_TAB_SYMBOLS, languages[36],
                             parent=self.binding_page)
        self.addSubInterface(self.plugin_binding_page, FluentIcon.IOT, languages[132], parent=self.binding_page)

        self.addSubInterface(PluginLogCollector, FluentIcon.COMMAND_PROMPT, languages[101],
                             position=NavigationItemPosition.BOTTOM)
        self.addSubInterface(self.about_page, FluentIcon.INFO, languages[130], position=NavigationItemPosition.BOTTOM)

        qrouter.setDefaultRouteKey(self.stack_widget, self.general_page.objectName())

        self.stack_widget.currentChanged.connect(self.onCurrentInterfaceChanged)
        self.stack_widget.setCurrentIndex(point_index)

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

    @staticmethod
    def reload_intelligence():
        intelligence.reload_api(configure["settings"]['cloud']['xunfei']['id'],
                                configure["settings"]['cloud']['xunfei']['key'],
                                configure["settings"]['cloud']['xunfei']['secret'],
                                configure["settings"]['cloud']['aliyun'])
        engine.webapi.reload_data(configure['settings']['intelligence'],
                                  api_config, configure['language_mapping'][configure['settings']['language']],
                                  runtime.parse_local_url(configure['settings']['local']['text'])
                                  if configure['settings']['text']['way'] == "local" else None)

    def reload_character(self, value, type_: typing.Literal['language', 'character']):
        global desktop, languages, configure_default, rules
        desktop.internal_record.stop()
        desktop.close()
        if type_ == "character":
            origin = configure_default
            configure_default = value
            # 判断架构支持并重载
            if os.path.exists(f"./resources/model/{configure_default}/2"):
                if architecture.live2d.LIVE2D_VERSION != 2:
                    if interface.setting.customize.widgets.pop_message(self, languages[161], languages[163]):
                        architecture.reload(2)
                    else:
                        configure_default = origin
                        desktop.internal_record.start()
                        desktop.show()
                        return
                else:
                    architecture.reload(2)
            else:
                if architecture.live2d.LIVE2D_VERSION != 3:
                    if interface.setting.customize.widgets.pop_message(self, languages[161], languages[163]):
                        architecture.reload(3)
                    else:
                        configure_default = origin
                        desktop.internal_record.start()
                        desktop.show()
                        return
                else:
                    architecture.reload(3)
            if configure_default not in configure['model'].keys():
                runtime.file.load_template_model(configure, value)
        elif type_ == "language":
            languages = runtime.file.load_language(configure)
        # 重载
        rules = runtime.file.load_rules(configure_default)
        interface.subscribe.hooks.Operate.GetConversationInterface().move(desktop.x(), desktop.y())
        desktop = DesktopPet(desktop.x(), desktop.y())
        desktop.show()
        interface.subscribe.RegisterAttribute.SetWindow(desktop)

        interface.subscribe.actions.Register.UnsetALL()
        self.close()
        self.__init__(self.x(), self.y(), self.stack_widget.currentIndex())
        self.show()
        interface.subscribe.hooks.Register.HookConversationInterface(conversation)

    # Function
    def record_animation(self):
        def recorder():
            self.animation_binding_page.refresh_position(*configure['record']['position'])
            if not configure['record']['position'].count(-1):
                self.record_timer.stop()
                configure['record']['enable_position'] = False
                runtime.file.save_configure(configure)

        if self.record_timer.isActive():
            self.record_timer.stop()
        else:
            configure['record']['position'] = [-1, -1, -1, -1]
            self.record_timer.timeout.connect(recorder)
            self.record_timer.start(50)

    def exception(self, e_msg):
        print(e_msg)
        interface.setting.customize.widgets.pop_error(self, "TraceBack", e_msg, 5000, Qt.Vertical)

    def examine_and_run(self, codes, type_: typing.Literal['independent', 'enhancement']):
        try:
            if runtime.PythonCodeExaminer(codes).optimize_infinite_loop:
                interface.setting.customize.widgets.pop_warning(self, languages[157], languages[158], 5000)
                return
            safety_level = configure['settings']['safety']
            if safety_level != "shut":
                attr = getattr(runtime.PythonCodeExaminer(codes), f"is_{safety_level}")
                if list(attr)[-1] or list(attr)[0]:
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
                if IS_PYTHON_EXITS:
                    with open("logs/plugin_cache_runner.py", "w", encoding="utf-8") as pf:
                        pf.write(codes)
                        pf.close()
                    codes = f"{os.getcwd()}/logs/plugin_cache_runner.py"
                thread_run = runtime.thread.RunPythonPlugin(self, codes, PLUGIN_GLOBAL, IS_PYTHON_EXITS)
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
        voice_generator = runtime.thread.VoiceGenerateThread(
            desktop, configure, module_info, text.split(":")[-1], text.split(":")[0])
        voice_generator.result.connect(self.play)
        voice_generator.error.connect(self.error)
        voice_generator.start()

    @staticmethod
    def play(audio_bytes):
        runtime.thread.SpeakThread(desktop, audio_bytes).start()

    def error(self, value):
        if value is False:
            interface.setting.customize.widgets.pop_error(self, languages[64], languages[64])

    def resizeEvent(self, e):
        self.titleBar.move(46, 0)
        self.titleBar.resize(self.width() - 46, self.titleBar.height())


class Conversation(QWidget):
    """对话界面"""
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowIcon(QIcon("logo.ico"))
        self.setWindowTitle("Enter Conversation - Ai Desktop Pet")
        self.setFixedSize(desktop.width(), 600)

        self.input_answer = TextEdit(self)
        self.input_answer.setGeometry(QRect(0, 0, 370, 60))
        self.input_answer.setReadOnly(True)

        self.icon = "DOWN"
        self.click_pop_answer = PrimaryToolButton(self)
        self.click_pop_answer.setIcon(FluentIcon.ARROW_DOWN)
        self.click_pop_answer.setGeometry(QRect(370, 0, 30, 60))
        self.click_pop_answer.clicked.connect(self.pop_answer)

        self.click_send = PrimaryToolButton(self)
        self.click_send.setIcon(FluentIcon.SEND)
        self.click_send.setGeometry(QRect(340, 431, 60, 30))
        self.click_send.clicked.connect(self.send_question)

        self.click_take_photo = PrimaryToolButton(self)
        self.click_take_photo.setIcon(FluentIcon.CAMERA)
        self.click_take_photo.setGeometry(QRect(280, 431, 60, 30))
        self.click_take_photo.clicked.connect(desktop.capture_screen)
        self.input_question = LineEdit(self)
        self.input_question.setGeometry(QRect(0, 430, 281, 30))
        self.input_question.setPlaceholderText(languages[70])

        # 为发送绑定按键
        self.input_question.returnPressed.connect(self.click_send.click)
        # 不可见
        self.click_pop_answer.setVisible(False)
        self.input_question.setVisible(False)
        self.click_send.setVisible(False)
        self.click_take_photo.setVisible(False)
        self.input_answer.setVisible(False)

    def pop_answer(self):
        """回复框的拉伸动画"""
        def wrapper():
            nonlocal height
            # 根据icon的值增加或减少height
            if icon == "UP":
                height += 15
            elif icon == "DOWN":
                height -= 20
            # 如果height超出范围，则停止计时器
            if (icon == "UP" and height > 400) or (icon == "DOWN" and height < 80):
                timer.stop()
            # 更新UI组件的几何形状
            self.click_pop_answer.setGeometry(QRect(370, 0, 30, height))
            self.input_answer.setGeometry(QRect(0, 0, 370, height))

        # 初始化height的值
        height = int(self.input_answer.height())
        # 根据当前的icon值来设置新的icon值和图标
        if self.icon == "DOWN":
            self.icon = icon = "UP"
            self.click_pop_answer.setIcon(FluentIcon.UP)
        else:
            self.icon = icon = "DOWN"
            self.click_pop_answer.setIcon(FluentIcon.ARROW_DOWN)
        # 创建并启动计时器，每2毫秒调用一次wrapper函数
        timer = QTimer(self)
        timer.timeout.connect(wrapper)
        timer.start(2)

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
        self.has_output_text = ""
        self.fps_refresh = int(1000 / 900)
        self.continuous_conversation = self.rms_volume = self.turn_count = self.expression_count = 0
        self.model_json_path: str = ""
        self.amount = self.click_in_area = self.click_x = self.click_y = -1
        self.speaking_lists: list[bool] = []
        self.is_playing_expression = self.is_penetration = self.is_playing_animation = self.is_movement = False
        self.speech_recognition = self.enter_position = self.drag_position = None
        self.image_path = self.direction = self.last_pos = None
        self.pet_model: architecture.live2d.LAppModel | None = None
        self.is_continuous = self.is_generating = self.is_transparent_raise = False
        # 初始化部分
        self.internal_record = runtime.thread.StartInternalRecording(visualization, 0.002)
        self.recognition_thread = runtime.thread.RecognitionThread(self, configure)
        self.recognition_thread.result.connect(self.recognition_success)

        # 移动位置
        self.screen_geometry = QApplication.desktop().availableGeometry()
        if display_x is not None and display_y is not None:
            self.move(display_x, display_y)
        else:
            # 屏幕中心坐标
            x = (self.screen_geometry.width() - self.width()) // 2
            y = self.screen_geometry.height() - self.height()
            self.move(x, y + 15)

    # GUI功能性配置
    def set_mouse_transparent(self, is_transparent: bool):
        """设置鼠标穿透 (透明部分可以直接穿过)"""
        if self.is_transparent_raise:
            return
        window_handle = int(self.winId())
        try:
            current_ex_style = ctypes.windll.user32.GetWindowLongW(window_handle, GWL_EX_STYLE)
            if is_transparent:
                # 添加WS_EX_TRANSPARENT样式以启用鼠标穿透
                new_ex_style = current_ex_style | WS_EX_TRANSPARENT
            else:
                # 移除WS_EX_TRANSPARENT样式以禁用鼠标穿透
                new_ex_style = current_ex_style & ~WS_EX_TRANSPARENT

            # 应用新的样式
            ctypes.windll.user32.SetWindowLongW(window_handle, GWL_EX_STYLE, new_ex_style)
        except Exception as e:
            self.is_transparent_raise = True
            QMessageBox.warning(self, languages[105], f"{type(e).__name__}: {e}")

    def set_window_below_taskbar(self):
        """设置低于任务栏(高于其它除了任务栏的应用)"""
        hwnd = self.winId().__int__()
        taskbar_hwnd = win32gui.FindWindow("Shell_TrayWnd", None)

        win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, 0, 0, 0, 0,
                              win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE)
        win32gui.SetWindowPos(hwnd, taskbar_hwnd, 0, 0, 0, 0,
                              win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE)

    def is_in_live2d_area(self, click_x: int | None = None, click_y: int | None = None):
        """检查是否在模型内 Check whether the mouse is in the model"""
        if click_x is None:
            click_x = QCursor.pos().x() - self.x()
        if click_y is None:
            click_y = QCursor.pos().y() - self.y()
        h = self.height()
        try:
            alpha = GL.glReadPixels(click_x * QGuiApplication.primaryScreen().devicePixelRatio(),
                                    (h - click_y) * QGuiApplication.primaryScreen().devicePixelRatio(),
                                    1, 1, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE)[3]
        except GL.error.GLError:
            alpha = 0
        return alpha > 0

    # 拍照
    def capture_screen(self):
        if not configure['settings']['enable']['media']:
            return
        interface.subscribe.hooks.Operate.GetConversationInterface().input_question.setText(
            str(interface.subscribe.hooks.Operate.GetConversationInterface().input_question.text()) + "$[图片]$")
        self.image_path = runtime.capture()

    # 语音识别
    def recognize(self):
        if not configure['settings']['enable']['rec']:
            return
        if self.recognition_thread.isRunning():
            self.recognition_thread.wait()
        self.recognition_thread.start()

    def recognition_success(self, result: str):
        self.speech_recognition.statued()

        if self.is_continuous or (configure['name'] in result or configure_default in result):
            if result.strip():
                self.is_continuous = True
            else:
                self.is_continuous = False
                return
            interface.subscribe.hooks.Operate.GetConversationInterface().show()
            self.change_status_for_conversation("show")
            self.have_conversation(result, True)
        runtime.file.logger(f"子应用 - 语音识别 语音呼唤成功\n"
                            f"Sub-Application - Voice Recognition Success: {result}\n"
                            f"  Message: {result}\n\n"
                            f"  Origin: {json.dumps(result, indent=3, ensure_ascii=False)}", logs.API_PATH)

    @staticmethod
    def recognition_failure(error, code):
        configure['settings']['enable']['rec'] = False
        runtime.file.save_configure(configure)
        runtime.file.logger(f"子应用 - 语音识别 发生错误 {code}:{error}\n"
                            f"Sub-Application - Voice Recognition Error: {code}:{error}\n", logs.API_PATH)

    @staticmethod
    def recognition_closure():
        pass

    # 音频可视化
    def audio_visualization(self):
        def draw(wav_bytes: bytes):
            self.rms_volume = runtime.calculate_rms(wav_bytes)
            if self.rms_volume > 0.1:
                visualization.show()
                visualization.draw_rectangle(self.rms_volume)
            else:
                visualization.hide()

        self.internal_record = runtime.thread.StartInternalRecording(visualization, 0.002)
        self.internal_record.data.connect(draw)
        self.internal_record.start()

    # 聊天
    def open_close_conversation(self):
        if interface.subscribe.hooks.Operate.GetConversationInterface().input_question.isVisible():
            self.change_status_for_conversation("hide")
            interface.subscribe.hooks.Operate.GetConversationInterface().hide()
        else:
            interface.subscribe.hooks.Operate.GetConversationInterface().show()
            self.change_status_for_conversation("show")

    @staticmethod
    def change_status_for_conversation(status: typing.Literal['hide', 'show'],
                                       enable_chat_box: bool = True):
        status = True if status == "show" else False
        interface.subscribe.hooks.Operate.GetConversationInterface().input_question.setVisible(status)
        interface.subscribe.hooks.Operate.GetConversationInterface().click_send.setVisible(status)
        interface.subscribe.hooks.Operate.GetConversationInterface().click_take_photo.setVisible(status)
        interface.subscribe.hooks.Operate.GetConversationInterface().click_pop_answer.setVisible(status)
        if enable_chat_box:
            interface.subscribe.hooks.Operate.GetConversationInterface().input_answer.setVisible(status)

    def conversation_display(self, text: str, current_index: int, temp_action: bool = False):
        def __temp():
            _temp_timer.stop()
            if not self.is_generating:
                self.change_status_for_conversation("hide")
                interface.subscribe.hooks.Operate.GetConversationInterface().hide()

        if current_index != self.continuous_conversation:
            return

        if text is None and not temp_action:
            interface.subscribe.hooks.Operate.GetConversationInterface().input_question.setGeometry(QRect(0, 430, 281, 30))
            self.change_status_for_conversation("show", False)
            return

        if text.split(":")[0] == "None":
            self.is_generating = False
            markdown_images = re.findall(r'!\[.*?]\((.*?)\)', text.split(":")[1])
            for markdown_image in markdown_images:
                picture.open(markdown_image)
                picture.show()
                picture.move(self.x() - self.width(), self.y())
            interface.subscribe.hooks.Operate.GetConversationInterface().input_question.setGeometry(QRect(0, 430, 281, 30))
            if temp_action:
                _temp_timer = QTimer(self)
                _temp_timer.timeout.connect(__temp)
                _temp_timer.start(5000)
            else:
                self.change_status_for_conversation("show", False)
        if text.split(":")[0] == "None":
            text = ':'.join(text.split(":")[1:])
        new_add_text = text.replace(self.has_output_text, "")
        exits_element = {k: v for k, v in rules.items() if k in new_add_text}
        if exits_element:
            self.playAnimationEvent(exits_element[list(rules.keys())[0]], "expr")
        if ((module_info and configure['settings']['tts']['way'] == "local") or
                configure['settings']['tts']['way'] == "cloud") and configure['settings']['enable']['tts'] and \
                text.split(":")[0] == "None":
            if configure['settings']['enable']['tts']:
                voice_generator = runtime.thread.VoiceGenerateThread(
                    self, configure, module_info, text)
                voice_generator.result.connect(lambda wave_bytes: runtime.thread.SpeakThread(self, wave_bytes).start())
                voice_generator.start()
        else:
            interface.subscribe.hooks.Operate.GetConversationInterface().input_answer.clear()
            interface.subscribe.hooks.Operate.GetConversationInterface().input_answer.setVisible(True)
            if text.split(":")[0] == "None":
                interface.subscribe.hooks.Operate.GetConversationInterface().input_answer.setMarkdown(text)
                self.has_output_text = ""
            else:
                self.is_generating = True
                interface.subscribe.hooks.Operate.GetConversationInterface().input_answer.setMarkdown(text)
            interface.subscribe.hooks.Operate.GetConversationInterface().input_answer.moveCursor(interface.subscribe.hooks.Operate.GetConversationInterface().input_answer.textCursor().End)
            if text is not None:
                if text[-2:] in rules.keys():
                    self.playAnimationEvent(rules[text[-2:]], "expr")
        self.has_output_text = text

    def have_conversation(self, text: str | None = None, temp_action: bool | None = False):
        """进行聊天 Send conversation"""
        chat_message = str(interface.subscribe.hooks.Operate.GetConversationInterface().input_question.text()) if text is None else text
        if not chat_message.strip():
            return
        # 临时隐藏控件
        if temp_action:
            interface.subscribe.hooks.Operate.GetConversationInterface().input_question.setVisible(False)
        elif temp_action is None:
            interface.subscribe.hooks.Operate.GetConversationInterface().show()
            self.change_status_for_conversation("show")
        interface.subscribe.hooks.Operate.GetConversationInterface().click_send.setVisible(False)
        interface.subscribe.hooks.Operate.GetConversationInterface().click_take_photo.setVisible(False)
        interface.subscribe.hooks.Operate.GetConversationInterface().input_answer.setText(f"{configure['name']} {languages[137]}")

        if self.image_path is None and "$[图片]$" not in interface.subscribe.hooks.Operate.GetConversationInterface().input_question.text():
            text_generate = runtime.thread.TextGenerateThread(
                self, configure, api_config, chat_message,
                True if configure['settings']['enable']['online'] else False,
            )
        else:
            text_generate = runtime.thread.MediaUnderstandThread(
                self, api_config, configure, self.image_path, chat_message.replace("$[图片]$", ""),
                True if configure['settings']['enable']['online'] else False,
            )
            self.image_path = None
        self.is_generating = True
        text_generate.start()
        self.continuous_conversation += 1
        current = self.continuous_conversation
        text_generate.result.connect(lambda texts: self.conversation_display(
            texts, current, temp_action))

    # 自定义事件
    @staticmethod
    def clear_memories():
        """清除记忆 Clear memories"""
        if intelligence is None:
            return
        intelligence.text.clear_memories()
        interface.subscribe.hooks.Operate.GetConversationInterface().input_answer.clear()

    # 动画事件
    def finishedAnimationEvent(self):
        self.is_playing_animation = False
        self.turn_count = 0
        self.resetDefaultValueEvent()
        print("END")

    # 重置默认值事件
    def resetDefaultValueEvent(self):
        for param, values in live2d_parameter.items():
            if param == configure['watermark'].split(";")[0]:
                continue
            self.pet_model.SetParameterValue(param, values['default'], 1)

    # 加载模型事件
    def loadModelEvent(self, model):
        try:
            model_files = os.listdir(f"./resources/model/{model}")
            # 寻找最像模型json文件的那一个文件
            model_json_file = get_close_matches(f"{model}.model.json", model_files)[0]
            self.model_json_path = (f"./resources/model/{model}/"
                                    f"{model_json_file}")
            # 加载架构
            if model_json_file.split(".")[1] == "model3":
                if architecture.live2d.LIVE2D_VERSION != 3:
                    architecture.reload(3)
            elif model_json_file.split(".")[1] == "model":
                if architecture.live2d.LIVE2D_VERSION != 2:
                    architecture.reload(2)
            else:
                raise FileNotFoundError()
            self.pet_model.LoadModelJson(self.model_json_path)
        except (KeyError, FileNotFoundError):
            configure['default'] = 'kasumi2'
            runtime.file.save_configure(configure)
            QMessageBox.critical(self, languages[71], languages[72])
            if QMessageBox.question(self, languages[71], languages[73]) == QMessageBox.Yes:
                runtime.file.load_template_model(configure, 'kasumi2')
                QMessageBox.information(self, languages[71], languages[74])
                runtime.file.save_configure(configure)
            self.exit_program()

    # 播放动画事件
    def playAnimationEvent(self, animation_name: str,
                           play_type: typing.Literal['expr', 'anime', 'event'] = 'event'):
        self.is_playing_expression = True
        if play_type != 'event':
            if play_type == 'expr':
                self.pet_model.SetExpression(animation_name)
            else:
                self.pet_model.StartMotion(
                    animation_name.split(":")[0], int(animation_name.split(":")[1]),
                    architecture.live2d.MotionPriority.FORCE, onFinishMotionHandler=self.finishedAnimationEvent)
            return
        if (exp := runtime.file.get_configure_actions(
                configure, configure_default,
                "nor" if "Touch" in animation_name or "Click" in animation_name else "spec")[
            animation_name]['expression'].strip()) != "":
            self.pet_model.SetExpression(exp)
        else:
            group, _, index = runtime.file.get_configure_actions(
                configure, configure_default,
                "nor" if "Touch" in animation_name or "Click" in animation_name else "spec")[
                animation_name]['motion'].split(":")
            self.pet_model.StartMotion(group, int(index), architecture.live2d.MotionPriority.FORCE,
                                       onFinishMotionHandler=self.finishedAnimationEvent)

    # 事件 Events
    # 右键菜单事件 Right-click menu events
    def contextMenuEvent(self, event):
        def show_setting_logics():
            if interface.subscribe.hooks.Operate.GetSettingInterface().isHidden():
                interface.subscribe.hooks.Operate.GetSettingInterface().show()
            else:
                interface.subscribe.hooks.Operate.GetSettingInterface().showNormal()
            hwnd = win32gui.FindWindow(None, languages[0])
            if hwnd:
                win32gui.SetForegroundWindow(hwnd)

        content_menu = RoundMenu("MENU", parent=self)

        settings_action = Action(FluentIcon.SETTING, languages[129], self)
        settings_action.triggered.connect(show_setting_logics)
        content_menu.addAction(settings_action)

        content_menu.addSeparator()

        conversation_action = Action(FluentIcon.HELP, languages[51], self)
        conversation_action.triggered.connect(self.open_close_conversation)
        content_menu.addAction(conversation_action)

        # 分割线
        content_menu.addSeparator()

        for views_item in interface.subscribe.views.Operate.GetContentMenu():
            if isinstance(views_item, RoundMenu):
                views_item.setParent(self)
                content_menu.addMenu(views_item)
            elif isinstance(views_item, Action):
                views_item.setParent(self)
                content_menu.addAction(views_item)

        content_menu.addSeparator()

        exit_action = Action(FluentIcon.CLOSE, languages[20], self)
        exit_action.triggered.connect(self.exit_program)
        content_menu.addAction(exit_action)

        content_menu.exec_(self.mapToGlobal(event.pos()))

    # 定时器事件 Timer events
    def timerEvent(self, a0: QTimerEvent | None) -> None:
        def save_change():
            self.is_penetration = False
            # 刷新设置的缓存文件
            switches_configure['Advanced']['penetration'] = "shut"
            runtime.file.save_switch(switches_configure)
            self.set_mouse_transparent(False)
            self.setCanvasOpacity(configure['settings']['transparency'])

        def check_mouse_pressed(left_condition: str, right_condition: str):
            if not MouseListener.isListening:
                MouseListener.start_listening()
            if switches_configure['Advanced']['penetration'] == left_condition:
                pressed = MouseListener.is_left_button_pressed
            elif switches_configure['Advanced']['penetration'] == right_condition:
                pressed = MouseListener.is_right_button_pressed
            else:
                pressed = False
            if not MouseListener.isListening:
                MouseListener.start_listening()
            return pressed

        if not self.isVisible():
            return
        # 设置透明度
        self.setCanvasOpacity(configure['settings']['transparency'])
        # 判断兼容性
        if configure["settings"]["compatibility"] is False and self.amount == 100:
            # 判断顺序是否低于任务栏
            hwnd = self.winId().__int__()
            taskbar_hwnd = win32gui.FindWindow("Shell_TrayWnd", None)
            if win32gui.GetWindowRect(hwnd)[1] < win32gui.GetWindowRect(taskbar_hwnd)[1]:
                self.set_window_below_taskbar()

        # 检查识别器
        if not self.recognition_thread.isRunning() and configure['settings']['enable']['rec']:
            self.recognize()
        elif self.speech_recognition is not None and not configure['settings']['enable']['rec']:
            self.speech_recognition.closed()

        # 定时器检查
        # if not configure['settings']['enable']['media']:
        #     if self.look_timer.isActive():
        #         self.look_timer.stop()
        # else:
        #     if not self.look_timer.isActive():
        #         self.look_timer.start(random.randint(
        #             configure['settings']['understand']['min'],
        #             configure['settings']['understand']['max']) * 1000)

        # 释放资源
        # 检查说话列表的可用性
        if len(self.speaking_lists) == self.speaking_lists.count(False) and not self.speaking_lists:
            # 清除缓存
            self.speaking_lists.clear()

        local_x, local_y = QCursor.pos().x() - self.x(), QCursor.pos().y() - self.y()
        if configure['settings']['live2d']['enable']['AutoDrag']:
            self.pet_model.Drag(local_x, local_y)
        # 检查是否开启全局鼠标穿透
        if switches_configure['Advanced']['penetration'] != "shut":
            self.setCanvasOpacity(0.4)
            self.set_mouse_transparent(True)
            self.is_penetration = True
            # 如果start有以下几种情况，则取消全局鼠标穿透
            # 下次启动时取消全局鼠标穿透
            if switches_configure['Advanced']['penetration'] == "next" and self.amount == -1:
                save_change()
            # 鼠标左键或右键在顶部按下时取消全局鼠标穿透
            elif switches_configure['Advanced']['penetration'] in ('left-top', 'right-top'):
                if self.is_in_live2d_area(local_x, local_y) and check_mouse_pressed('left-top', 'right-top') and \
                        80 > local_y > 0:
                    MouseListener.stop_listening()
                    save_change()
            # 鼠标左键或右键在底部按下时取消全局鼠标穿透
            elif switches_configure['Advanced']['penetration'] in ('left-bottom', 'right-bottom'):
                if self.is_in_live2d_area(local_x, local_y) and check_mouse_pressed('left-bottom',
                                                                                    'right-bottom') and \
                        self.height() > local_y > self.height() - 80:
                    MouseListener.stop_listening()
                    save_change()
        elif switches_configure['Advanced']['penetration'] == "shut" and self.amount == 0:
            save_change()

        # 检查是否开启音频可视化
        if configure['settings']['enable']['visualization']:
            if not self.internal_record.isRunning():
                visualization.show()
                self.audio_visualization()
        else:
            self.internal_record.stop()
            visualization.hide()

        # 检查表情
        if self.expression_count >= 300 * self.fps_refresh:
            self.is_playing_expression = False
            self.pet_model.ResetExpression()
        if self.is_playing_expression:
            self.expression_count += self.fps_refresh
        else:
            self.expression_count = 0
        # 检查点击区域
        if self.is_in_live2d_area(local_x, local_y) and not self.is_penetration:
            self.set_mouse_transparent(False)
            self.click_in_area = True
        elif not self.is_penetration:
            self.set_mouse_transparent(True)
            self.turn_count = 0
            self.click_in_area = False

        # 循环次数
        if self.amount > 100:
            self.amount = 0
        self.amount += 1

        self.update()

    # 过滤器事件 Filter events
    def eventFilter(self, obj, event):
        if obj is interface.subscribe.hooks.Operate.GetConversationInterface().input_question and event.type() == event.KeyPress:
            # 是否按下 Shift + Enter
            if event.key() in (Qt.Key_Enter, Qt.Key_Return):
                if event.modifiers() & Qt.ShiftModifier and interface.subscribe.hooks.Operate.GetConversationInterface().click_send.isVisible():
                    interface.subscribe.hooks.Operate.GetConversationInterface().click_send.click()
                    return True
                else:
                    return False
        return super().eventFilter(obj, event)

    # 鼠标拖动事件
    def mousePressEvent(self, event):
        x, y = event.globalPos().x(), event.globalPos().y()
        if self.is_in_live2d_area(QCursor.pos().x() - self.x(), QCursor.pos().y() - self.y()):
            self.click_in_area = True
            self.click_x, self.click_y = x, y
            event.accept()

        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        def checker(parameter: str, turn_count: int) -> bool:
            """检查是否满足框内要求"""
            x_min, x_max, y_min, y_max = runtime.file.get_configure_actions(
                configure, configure_default)[parameter]['position']
            return (
                    x_min <= current_x <= x_max and y_min <= current_y <= y_max and
                    not self.is_playing_animation and self.turn_count >= turn_count and self.click_in_area
            )

        x, y = QCursor.pos().x() - self.x(), QCursor.pos().y()
        # 拖动事件
        if event.buttons() & Qt.LeftButton:
            self.is_movement = True
            if self.drag_position is not None:
                if self.click_in_area:
                    cv_new_pos = event.globalPos() - self.drag_position
                    new_pos = event.globalPos() - self.drag_position
                    if configure['settings']['enable']['locktsk']:
                        new_pos.setY(max(self.screen_geometry.height() - self.height(), new_pos.y()))
                        cv_new_pos.setY(max(self.screen_geometry.height() - self.height() - 60, new_pos.y() - 60))
                    else:
                        cv_new_pos.setY(new_pos.y() - 60)
                    self.move(new_pos)

                    for action_item in interface.subscribe.actions.Operate.GetMouseDragAction():
                        action_item(x, y, self.x(), self.y())

                    picture.move(self.x() - self.width(), self.y())
                    interface.subscribe.hooks.Operate.GetConversationInterface().move(cv_new_pos)
                    cv_new_pos.setY(cv_new_pos.y() + 40)
                    visualization.move(cv_new_pos)
                event.accept()

        # 非接触悬浮鼠标的互动
        if self.enter_position and not event.buttons() & Qt.LeftButton:
            # 处理互动事件/动画
            current_pos = event.pos()
            current_x = current_pos.x()
            current_y = current_pos.y()

            if self.last_pos is not None:
                last_x, last_y = self.last_pos.x(), self.last_pos.y()

                # 状态
                if current_x > last_x:
                    new_direction = 'right'
                elif current_x < last_x:
                    new_direction = 'left'
                else:
                    new_direction = self.direction

                # 检查方向是否改变
                if self.direction is not None and new_direction != self.direction:
                    self.turn_count += 1

                self.direction = new_direction

            self.last_pos = current_pos

            # 互动事件/动画
            if self.click_in_area and not self.is_movement:
                # 摸头互动
                if checker('ActionTouchHead', 4):
                    runtime.thread.SpeakThread(self, runtime.file.get_audio_path(
                        configure, configure_default, 'ActionTouchHead')).start()
                    self.click_in_area = False
                    self.is_playing_animation = True
                    # 播放动画
                    self.playAnimationEvent('ActionTouchHead')
                # 摸腿互动
                if checker('ActionTouchLeg', 4):
                    runtime.thread.SpeakThread(self, runtime.file.get_audio_path(
                        configure, configure_default, 'ActionTouchLeg')).start()
                    self.click_in_area = False
                    self.is_playing_animation = True
                    self.playAnimationEvent('ActionTouchLeg')
                # 自定义互动
                if checker('ActionTouchCustom', 4):
                    runtime.thread.SpeakThread(self, runtime.file.get_audio_path(
                        configure, configure_default, 'ActionTouchCustom')).start()
                    self.click_in_area = False
                    self.is_playing_animation = True
                    self.playAnimationEvent('ActionTouchCustom')

        for action_item in interface.subscribe.actions.Operate.GetMouseMoveAction():
            action_item()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        def checker(parameter_action: str):
            """检查点击位置是否符合标准 Check whether the click position meets the standards"""
            x_min, x_max, y_min, y_max = runtime.file.get_configure_actions(
                configure, configure_default)[parameter_action]['position']
            return x_min <= click_x <= x_max and y_min <= click_y <= y_max \
                and not self.is_playing_animation

        click_x, click_y = event.globalPos().x() - self.x(), event.globalPos().y() - self.y()
        if event.button() == Qt.LeftButton and self.click_in_area:
            print(f"meet the requirements. CLICK pos: {click_x, click_y}")
            # 记录位置
            if configure['record']['enable_position']:
                if configure['record']['position'][:2].count(-1) == len(configure['record']['position'][:2]):
                    configure['record']['position'][:2] = [click_x, click_y]
                else:
                    configure['record']['position'][2:] = [click_x, click_y]
                    configure['record']['enable_position'] = False

            # 点击事件/动画
            # 胸部点击行为
            if checker("ActionClickChest"):
                self.is_playing_animation = True
                self.playAnimationEvent('ActionClickChest')
                if configure['adult_level'] > 0:
                    dir_, voice_list = engine.adult.AdultEngine(configure).voice()
                    runtime.thread.SpeakThread(self,
                                               f"./resources/adult/{configure_default}/voice/{dir_}/"
                                               f"{random.choice(voice_list)}").start()
                else:
                    runtime.thread.SpeakThread(self, runtime.file.get_audio_path(
                        configure, configure_default, "ActionClickChest")).start()
            # 帽点击行为
            elif checker("ActionClickCap"):
                self.is_playing_animation = True
                self.playAnimationEvent('ActionClickCap')
                runtime.thread.SpeakThread(self, runtime.file.get_audio_path(
                        configure, configure_default, "ActionClickCap")).start()
            elif checker("ActionClickCustom"):
                self.is_playing_animation = True
                self.playAnimationEvent('ActionClickCustom')
                runtime.thread.SpeakThread(self, runtime.file.get_audio_path(
                        configure, configure_default, "ActionClickCustom")).start()

            for action_item in interface.subscribe.actions.Operate.GetClckAction():
                try:
                    action_item()
                except Exception as e:
                    interface.setting.customize.widgets.pop_error(setting, 'Error', str(e))
            event.accept()
        for action_item in interface.subscribe.actions.Operate.GetMouseReleaseAction():
            action_item()
        self.is_movement = False

    # 鼠标进入事件 Mouse entry event
    def enterEvent(self, event):
        self.turn_count = 0
        self.enter_position = event.pos()
        for action_item in interface.subscribe.actions.Operate.GetMouseEnterAction():
            action_item()

    # 鼠标离开事件 Mouse leave event
    def leaveEvent(self, event):
        self.is_movement = False
        self.enter_position = None
        self.is_playing_animation = False
        for action_item in interface.subscribe.actions.Operate.GetMouseLeaveAction():
            action_item()

    # 拖拽事件 Drag event
    def dragEnterEvent(self, event: QMimeData):
        action = engine.actions.ActionsEngine(configure, languages, interface)
        action.analyze_action(event.mimeData().text())
        for action_item in interface.subscribe.actions.Operate.GetDragEnterAction():
            action_item(event, action.analyzed_action)
        event.accept()

    def dragLeaveEvent(self, event: QMimeData):
        action = engine.actions.ActionsEngine(configure, languages, interface)
        action.analyze_action(event.mimeData().text())
        for action_item in interface.subscribe.actions.Operate.GetDragLeaveAction():
            action_item(event, action.analyzed_action)
        event.accept()

    def dragMoveEvent(self, event: QMimeData):
        action = engine.actions.ActionsEngine(configure, languages, interface)
        action.analyze_action(event.mimeData().text())
        for action_item in interface.subscribe.actions.Operate.GetDragMoveAction():
            action_item(event, action.analyzed_action)
        event.accept()

    def dropEvent(self, event: QMimeData):
        action = engine.actions.ActionsEngine(configure, languages, interface)
        action.analyze_action(event.mimeData().text())
        for action_item in interface.subscribe.actions.Operate.GetDropAction():
            action_item(event, action.analyzed_action)
        action.accept_action()
        event.accept()

    # OpenGL 事件
    def on_init(self):
        architecture.live2d.glewInit()
        self.pet_model = architecture.live2d.LAppModel()
        self.loadModelEvent(configure_default)
        # 初始化载入
        self.playAnimationEvent("ActionLogin")
        runtime.thread.SpeakThread(self, runtime.file.get_audio_path(
            configure, configure_default, "ActionLogin")).start()
        live2d_parameter.clear()

        for i in range(self.pet_model.GetParameterCount()):
            param = self.pet_model.GetParameter(i)
            live2d_parameter.update({str(param.id): {
                "value": param.value, "max": param.max, "min": param.min, "default": param.default,
            }})
        live2d_parameter.update({"Keep@NullParameter": {"value": 0.0, "max": 0.0, "min": 0.0, "default": 0.0}})
        interface.subscribe.RegisterAttribute.SetPet(self.pet_model)
        self.startTimer(self.fps_refresh)

    def on_resize(self, width, height):
        self.pet_model.Resize(width, height)

    def on_draw(self):
        architecture.live2d.clearBuffer()
        try:
            self.pet_model.Update()
            if "ParamMouthOpenY" in live2d_parameter.keys():
                self.pet_model.AddParameterValue("ParamMouthOpenY", min(
                    live2d_parameter["ParamMouthOpenY"]['max'], self.rms_volume / 100))
            # 清除水印
            try:
                watermark_param = configure['watermark'].split(";")[0]
                watermark_value = configure['watermark'].split(";")[1]
                self.pet_model.SetParameterValue(
                    watermark_param,
                    float(watermark_value) if "." in watermark_value else int(watermark_value), 1)
            except ValueError:
                pass
            # 加载Live2D开关
            self.pet_model.SetAutoBlinkEnable(
                configure['settings']['live2d']['enable']['AutoBlink'])
            self.pet_model.SetAutoBreathEnable(
                configure['settings']['live2d']['enable']['AutoBreath'])
            # 加载模型 Load Model
            self.pet_model.Draw()
        except SystemError:
            pass

    def exit_program(self):
        architecture.live2d.dispose()
        self.close()
        try:
            os.remove("./logs/backup/configure.json")
        except FileNotFoundError:
            pass
        shutil.copy2("./resources/configure.json", "./logs/backup/configure.json")
        runtime.file.logger("程序退出 Program exit", logs.HISTORY_PATH)
        runtime.file.write_file("./engine/static/scripts.js",
                                js_code.replace(f"http://{gethostbyname(gethostname())}:12877",
                                                "{PYTHON_UPLOAD_URL_ADDRESS}"))
        os.kill(os.getpid(), __import__("signal").SIGINT)


if __name__ != "__main__":
    with open('./engine/static/scripts.js', 'r', encoding='utf-8') as f:
        js_code = f.read().replace("{PYTHON_UPLOAD_URL_ADDRESS}", f"http://{gethostbyname(gethostname())}:12877")
        f.close()
    runtime.file.write_file("./engine/static/scripts.js", js_code)
    app = QApplication(sys.argv)

    translator = FluentTranslator(QLocale(QLocale.Chinese, QLocale.China))
    app.installTranslator(translator)

    MouseListener = runtime.MouseListener()

    PluginLogCollector = interface.setting.plog.PluginLogCollector()
    PLUGIN_GLOBAL['interface'] = interface
    PLUGIN_GLOBAL['print'] = PluginLogCollector.print_
    PLUGIN_GLOBAL['input'] = PluginLogCollector.input_

    visualization = AudioVisualization()
    desktop = DesktopPet()
    desktop.show()
    setting = Setting()
    conversation = Conversation()

    # 注册接口
    interface.subscribe.interact.Register.SetLargeLanguageModel(
        lambda text: desktop.have_conversation(text, None)
    )
    interface.subscribe.hooks.Register.HookConversationInterface(conversation)
    interface.subscribe.RegisterAttribute.SetWindow(desktop)
    interface.subscribe.views.Register.register("setting", setting)
    interface.subscribe.views.Register.register("conversation", conversation)
    interface.subscribe.hooks.Register.HookSettingInterface(setting)

    interface.subscribe.hooks.Operate.GetConversationInterface().move(desktop.x(), desktop.y() - 60)
    visualization.move(desktop.x(), desktop.y() - 20)
    picture = PictureShow()

    # 启动网页
    Thread(target=engine.webui.run).start()

else:
    print("?")
    sys.exit(0)
