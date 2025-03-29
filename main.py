import time
import traceback

# 系统信息 System Information
import sys
import os

# 数据处理 Data Processing
import re
import random
import typing
import shutil
import json
# 音频数据处理 audio data processing
import wave
import pyaudio
import io

# 接口 Interface
from interface import subscribe
from interface.setting.customize import widgets
# 着色器加载 load shader
import shader
# 日志数据 Logs data
import logs
# AI
try:
    import intelligence

except ImportError:
    intelligence = None
    MODULE_INFO = {}
# 运行时 Runtime
import runtime
# 引擎 Engine
import engine

# WindowsAPI
import locale
import ctypes
import win32gui
import win32con

# 引入live2d库 Import Live2D
try:
    import live2d.v3 as live2d
    import live2d_custom.v3 as live2d_custom
except (OSError, SystemError, ImportError):
    import live2d.v2 as live2d
    import live2d_custom.v2 as live2d_custom

# 界面库和OpenGL库 GUI
from interface.setting import intelligence as ui_intelligence
from interface.setting import general, switches, binding, about, plog
from interface.setting.sub_intelligence import local, cloud
from interface.setting.sub_binding import animation, plugin, rule, tools

from OpenGL import GL
from PyQt5.Qt import Qt, QTimerEvent, QCursor, QThread, pyqtSignal, QRect, QTimer,QIcon, QMimeData, QWidget
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtWidgets import QOpenGLWidget, QApplication, QMessageBox
from qfluentwidgets import RoundMenu, Action, FluentIcon, FluentWindow, NavigationItemPosition,\
    TextEdit, LineEdit, PrimaryToolButton

param_dict = {}
GWL_EXSTYLE = -20
WS_EX_TRANSPARENT = 0x00000020
speech_rec = None
with open("./resources/configure.json", "r", encoding="utf-8") as f:
    def recover_backup():
        global configure
        os.remove("./resources/configure.json")
        shutil.copy2("./logs/backup/configure.json", "./resources/configure.json")
        with open("./resources/configure.json", "r", encoding="utf-8") as scf:
            configure = json.load(scf)
            scf.close()

    try:
        configure = json.load(f)
    except json.JSONDecodeError:
        f.close()
        recover_backup()
    configure_default = configure["default"]

    if configure_default == "origin":
        configure_default = "vanilla"

    configure['model'][configure['default']]['adult'] = configure['model'][configure_default]['adult']
    configure['model'][configure['default']]['voice'] = configure['model'][configure_default]['voice']

    f.close()
    # 写入接口 Write into interface
    subscribe.Register().SetCharacter(configure['default'])
    subscribe.Register().SetVoiceModel(configure['voice_model'])
    subscribe.Register().SetName(configure['name'])

with open("./interface/setting/switch.json", "r", encoding="utf-8") as ccf:
    switch_config = json.load(ccf)
    ccf.close()

# 语言 language
_language = locale.getlocale()[0]
# 自动选择语言 Auto select language
if not configure['settings']['language'].strip():
    configure['settings']['language'] = _language
# 配置语言 Config language
if configure['settings']['language'] in os.listdir("./resources/languages"):
    _language = configure['settings']['language']
else:
    _language = "English_United States"
    configure['settings']['language'] = "English_United States"
with open(f"./resources/languages/{_language}", "r", encoding="utf-8") as lf:
    languages: list[str] = lf.read().split("\n")
    lf.close()


def logger(text, father_dir):
    current_file = f"{father_dir}/{time.strftime('%Y-%m-%d', time.localtime())}.txt"
    if not os.path.exists(father_dir):
        os.mkdir(father_dir)
    if not os.path.isfile(current_file):
        open(current_file, "w", encoding="utf-8").close()
    with open(f"{current_file}", "a", encoding="utf-8") as lf:
        lf.write(f"{{\n"
                 f"\t[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}] \n"
                 f" [LOGGING]: \n{text}\n"
                 f"}}\n")
        lf.close()


def get_audio_path(action: str):
    try:
        return (f"./resources/voice/{configure['default']}/"
                f"{get_configure_actions()[action]['play']}/"
                f"{random.choice(configure['model'][configure['default']]['voice'][configure['model'][
                    configure_default]['action'][action]['play']])
                    if get_configure_actions()[action]['play_type'] == 'random' else
                    get_configure_actions()[action]['play_type']}")
    except (KeyError, IndexError):
        return ""


def load_template_model(model: str):
    with open("./resources/template.json", "r", encoding="utf-8") as tf:
        template = json.load(tf)
        tf.close()
    if not os.path.exists(f"./resources/voice/{model}"):
        os.mkdir(f"./resources/voice/{model}")
        for template_dir in template['voice'].keys():
            try:
                os.mkdir(f"./resources/voice/{model}/{template_dir}")
            except FileExistsError:
                pass
    for emotion_type in os.listdir(f"./resources/voice/{model}"):
        template['voice'][emotion_type] = list(map(lambda v: v.split("\\")[-1], __import__("glob").glob(
            f"./resources/voice/{model}/{emotion_type}/*.wav")))
    configure['model'].update({model: template})
    with open("./resources/configure.json", "w", encoding="utf-8") as sf:
        json.dump(configure, sf, indent=3, ensure_ascii=False)
        sf.close()
    if not os.path.exists(f"./resources/voice/{model}"):
        load_template_model(model)


def delete_character(model: str):
    if os.path.exists(f"./resources/voice/{model}"):
        shutil.rmtree(f"./resources/voice/{model}")
        del configure['model'][model]
        with open("./resources/configure.json", "w", encoding="utf-8") as sf:
            json.dump(configure, sf, indent=3, ensure_ascii=False)
            sf.close()
    if os.path.exists(f"./intelligence/prompts/{model}.json"):
        os.remove(f"./intelligence/prompts/{model}.json")
    shutil.rmtree(f"./resources/model/{model}")


# configure
def get_configure_actions():
    return configure['model'][configure_default]['action']


if intelligence:
    intelligence.text.reload_memories(configure['default'])
    intelligence.ALI_API_KEY = configure["settings"]['cloud']['aliyun']
    intelligence.XF_API_ID = configure["settings"]['cloud']['xunfei']['id']
    intelligence.XF_API_KEY = configure["settings"]['cloud']['xunfei']['key']
    intelligence.XF_API_SECRET = configure["settings"]['cloud']['xunfei']['secret']
    try:
        MODULE_INFO = intelligence.voice.get_module_lists(runtime.parse_local_url(configure['settings']['local']['gsv']))
    except __import__("requests").exceptions.ReadTimeout:
        MODULE_INFO = {}
    if MODULE_INFO:
        VoiceSwitch = True
    else:
        VoiceSwitch = False


# 基本功能线程 Basic Function Thread
class SpeakThread(QThread):
    """说话线程 Speak Thread"""
    information = pyqtSignal(int)

    def __init__(self, parent: QOpenGLWidget, resource_data: bytes | str):
        super().__init__(parent)
        self.parent().speaking_lists.append(True)
        self.current_speak_index = len(self.parent().speaking_lists) - 1
        self.resource_data = resource_data

    def run(self):
        if self.resource_data is None or not self.resource_data.strip():
            return
        if isinstance(self.resource_data, bytes):
            wave_source = io.BytesIO(self.resource_data)
            mode = "rb"
        else:
            wave_source = self.resource_data
            try:
                open(wave_source, "r")
            except (PermissionError, FileNotFoundError):
                self.parent().speaking_lists[self.current_speak_index] = False
                return
            mode = "r"

        if self.parent().speaking_lists[self.current_speak_index - 1] and self.current_speak_index != 0:
            self.parent().speaking_lists[self.current_speak_index - 1] = False

        with wave.open(wave_source, mode) as wf:
            p = pyaudio.PyAudio()
            stream = p.open(format=p.get_format_from_width(wf.getsampwidth()), channels=wf.getnchannels(),
                            rate=wf.getframerate(), output=True)
            data = wf.readframes(1024)
            while data:
                if not self.parent().speaking_lists[self.current_speak_index]:
                    break
                stream.write(data)
                data = wf.readframes(1024)
            stream.stop_stream()
            stream.close()
            p.terminate()
        self.parent().speaking_lists[self.current_speak_index] = False


class RecognitionThread(QThread):
    """语音识别线程 Speech Recognition Thread"""
    result = pyqtSignal(str)

    def __init__(self, parent: QOpenGLWidget):
        super().__init__(parent)

    def run(self):
        global speech_rec
        if configure['settings']['rec'] == "cloud":
            speech_rec = intelligence.xf_speech_recognition(
                self.result.emit,
                self.parent().recognition_failure, self.parent().recognition_closure
            )
        else:
            speech_rec = intelligence.whisper_speech_recognition(
                self.result.emit,
                self.parent().recognition_failure, self.parent().recognition_closure,
                runtime.parse_local_url(configure['settings']['local']['rec']['url'])
            )
        speech_rec.start_recognition()


class MediaUnderstandThread(QThread):
    result = pyqtSignal(str)

    def __init__(self, parent: QOpenGLWidget, image_path: str,
                 texts: str | None = None, is_search_online: bool = False):
        """根据媒体理解线程 Media Understand Thread"""
        super().__init__(parent)
        self.image_path = image_path
        self.is_search_online = is_search_online
        self.texts = texts

    def run(self):
        if self.texts is None:
            self.texts = random.choice(["你觉得我在干什么？", "你有什么想法呀？", "你觉得这个图片怎么样？", "请评价一下这图片"])
        try:
            answer = intelligence.text_generator(f"`{self.image_path}` \n{self.texts}", configure['settings']['intelligence'],
                                                 self.is_search_online, self.result.emit)
        except Exception:
            logger(f"子应用 - 媒体文件理解 调用失败\n"
                   f"   Message: {traceback.format_exc()}", logs.HISTORY_PATH)
            self.result.emit(f"AI媒体文件理解 调用失败 AI Answer failed to call\n{traceback.format_exc()}")
            return
        logger("子应用 - AI图文理解 调用成功 Sub Application - AI Media Understand Call Success\n"
               f"   Message: {answer}", logs.HISTORY_PATH)
        self.result.emit(f"None:{answer}")


class TextGenerateThread(QThread):
    """文本生成器线程 Text Generation Thread"""
    result = pyqtSignal(str)

    def __init__(self, parent: QOpenGLWidget, text: str, is_search_online: bool = False):
        super().__init__(parent)
        self.text = text
        self.is_search_online = is_search_online

    def send(self, text: str, is_finished: bool):
        self.result.emit(text)
        for action_item in subscribe.actions.Operate().GetAIOutput():
            action_item(text, is_finished)

    def run(self):
        try:
            intelligence.ALI_API_KEY = configure["settings"]['cloud']['aliyun']
            answer = intelligence.text_generator(
                self.text,
                configure['settings']['intelligence'],
                self.is_search_online, lambda text: self.send(text, False),
                language=configure['language_mapping'][configure['settings']['language']],
                url=runtime.parse_local_url(configure['settings']['local']['text']
                                            ) if configure['settings']['text']['way'] == "local" else None,)
        except Exception:
            logger(f"子应用 - AI剧情问答 调用失败\n"
                   f"   Message: {traceback.format_exc()}", logs.HISTORY_PATH)
            self.result.emit(f"AI问答 调用失败 AI Answer failed to call\n{traceback.format_exc()}")
            return
        logger(f"子应用 - AI剧情问答 调用成功\n"
               f"   Message: {answer}", logs.HISTORY_PATH)
        self.send(f"None:{answer}", True)


class VoiceGenerateThread(QThread):
    """AI 文字转语音 (GSV) AI text-to-speech (GSV) module"""
    result = pyqtSignal(bytes)
    error = pyqtSignal(bool)

    def __init__(self, parent: QOpenGLWidget, text: str, language: str = "auto"):
        super().__init__(parent)
        self.text = text
        self.language = language

    def run(self):
        # 数据预处理 data pre-processing
        # 移除Markdown Remove Markdown
        text = re.sub(r'(!|)(\[.*?])\(.*?\)', r'', self.text)
        # 排除表情等无需发音的内容 Exclude expressions such as emotion
        text = re.sub(r'(\(.*）\))', '', text)
        text = re.sub(r'(（.*）)', '', text)
        text = re.sub(r'(\[.*])', '', text)
        text = re.sub(r'(【.*】)', '', text)
        # 翻译和语言 Translation and language
        language = "zh"
        if configure['settings']['tts']['way'] == "local":
            if self.language not in ("zh", "en", "ja", "ko", "yue"):
                if configure['settings']['enable']['trans']:
                    if "spider" in configure["settings"]['translate']:
                        if "bing" in configure["settings"]['translate']:
                            text = intelligence.machine_translate(text)
                            language = "ja"
                    elif "ai" in configure["settings"]['translate']:
                        if "tongyi" in configure["settings"]['translate']:
                            text = intelligence.tongyi_translate(text)
                            language = "ja"
            else:
                language = self.language

            intelligence.voice_change(configure['voice_model'], MODULE_INFO,
                                      runtime.parse_local_url(configure['settings']['local']['gsv']))
            wav_bytes = intelligence.gsv_voice_generator(
                text, language, configure['voice_model'], MODULE_INFO,
                configure['settings']['tts']['top_k'], configure['settings']['tts']['top_p'],
                configure['settings']['tts']['temperature'], configure['settings']['tts']['speed'],
                configure['settings']['tts']['batch_size'], configure['settings']['tts']['batch_threshold'],
                parallel_infer=configure['settings']['tts']['parallel'],
                url=runtime.parse_local_url(configure['settings']['local']['gsv']))
        else:
            intelligence.ALI_API_KEY = configure["settings"]['cloud']['aliyun']
            wav_bytes, _ = intelligence.ali_voice_generator(text)
            if wav_bytes is None:
                self.error.emit(False)
                return
        logger(f"子应用 - AI语音(GSV) 调用成功\n", logs.HISTORY_PATH)
        self.result.emit(wav_bytes)


# 设置界面 Setting Window
class Setting(FluentWindow):
    def __init__(self, display_x: int | None = None, display_y: int | None = None):
        super().__init__()
        self.setWindowIcon(QIcon("logo.ico"))
        self.resize(700, 530)
        self.setWindowTitle(languages[0])
        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.run_thread = None
        if display_x is not None and display_y is not None:
            self.move(display_x, display_y)
        else:
            self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

        self.general_page = general.General(languages, configure, MODULE_INFO, param_dict,
                                            play=self.reference, reload=self.reload_character)
        self.switches_page = switches.Switches(languages, switch_config, configure)

        self.intelligence_page = ui_intelligence.Intelligence(languages, configure)
        self.local_intelligence_page = local.IntelligenceLocale(languages, configure)
        self.cloud_intelligence_page = cloud.IntelligenceCloud(languages, configure)

        self.binding_page = binding.Binding(languages, configure, MODULE_INFO, param_dict)
        self.animation_binding_page = animation.AnimationBinding(
            languages, configure, MODULE_INFO, ex.model_json_path, live2d_custom,
            record=self.record_animation, live2d=live2d, pet_model=ex.pet_model,
        )
        self.rule_binding_page = rule.RuleBinding(languages, configure, MODULE_INFO, param_dict)
        self.tools_binding_page = tools.ToolsBinding(languages, configure, MODULE_INFO, param_dict)
        self.plugin_binding_page = plugin.PluginBinding(
            self.run_code_for_plugin, languages, configure)

        self.about_page = about.About(languages, runtime)

        self.addSubInterface(self.general_page, FluentIcon.SETTING, languages[1])
        self.addSubInterface(self.switches_page, FluentIcon.DEVELOPER_TOOLS, languages[10])

        self.addSubInterface(self.intelligence_page, FluentIcon.EDUCATION, languages[27])
        self.addSubInterface(
            self.cloud_intelligence_page, FluentIcon.CLOUD, languages[29], parent=self.intelligence_page)
        self.addSubInterface(
            self.local_intelligence_page, FluentIcon.DOWN, languages[31], parent=self.intelligence_page)

        self.addSubInterface(self.binding_page, FluentIcon.TRANSPARENT, languages[36])
        self.addSubInterface(
            self.animation_binding_page, FluentIcon.LIBRARY_FILL, languages[42], parent=self.binding_page)
        self.addSubInterface(self.rule_binding_page, FluentIcon.ALIGNMENT, languages[37], parent=self.binding_page)
        self.addSubInterface(
            self.tools_binding_page, FluentIcon.EMOJI_TAB_SYMBOLS, languages[55], parent=self.binding_page)
        self.addSubInterface(self.plugin_binding_page, FluentIcon.IOT, languages[112], parent=self.binding_page)

        self.addSubInterface(PluginLogCollector, FluentIcon.COMMAND_PROMPT, languages[141],
                             position=NavigationItemPosition.BOTTOM)
        self.addSubInterface(self.about_page, FluentIcon.INFO, languages[66], position=NavigationItemPosition.BOTTOM)

        self.switchTo(self.general_page)

        self.record_timer = QTimer(self)

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
        global ex, st
        ex.close()
        live2d.dispose()

        live2d.init()
        load_template_model(model)
        cv.move(ex.x(), ex.y())
        ex = DesktopTop(ex.x(), ex.y())
        ex.show()
        subscribe.RegisterAttribute().SetWindow(ex)

        subscribe.actions.Register().UnsetALL()
        self.close()
        self.__init__(self.x(), self.y())
        self.show()

    # Run
    def clear_thread(self, change_button_text):
        self.run_thread = None
        if change_button_text is not None:
            change_button_text(languages[150])

    def run_code_for_plugin(self, codes, change_button_text=None, run_type=-4):
        def exception(e):
            widgets.pop_error(self, "Exception Error",
                              f"{type(e).__name__}: {e}", 3000)
            widgets.pop_warning(self, "TraceBack", traceback.format_exc(), 5000)
            if change_button_text is not None:
                change_button_text(languages[150])
            self.run_thread = None

        def independent_run():
            if change_button_text is not None:
                change_button_text(languages[151])
            try:
                self.run_thread = runtime.ThreadExceptionEnd(lambda: exec(codes, global_),
                                                             lambda: self.clear_thread(change_button_text))
            except Exception as e:
                exception(e)
            self.run_thread.start()

        # 自动选择 Automatic
        if run_type == -4 and self.run_thread is None:
            try:
                parsed = runtime.PythonCodeParser(codes).has_subscribe_for_views or \
                    runtime.PythonCodeParser(codes).has_subscribe_for_actions
            except Exception as e:
                exception(e)
                return
            if parsed:
                try:
                    exec(codes, global_)
                except Exception as e:
                    exception(e)
            else:
                independent_run()
            return

        # 程序增强 enhancement
        if run_type == -2 and self.run_thread is None:
            try:
                exec(codes, global_)
            except Exception as e:
                exception(e)
            return

        # 独立程序 Independent
        if run_type == -3 and self.run_thread is None:
            independent_run()
        elif self.run_thread is not None:
            if change_button_text is not None:
                change_button_text(languages[150])
            result = self.run_thread.stop_thread()
            if result:
                widgets.pop_success(self, languages[149], languages[149])
            else:
                widgets.pop_error(self, languages[148], languages[148])
            self.run_thread = None

    # 测试语音合成组 Test Voice Synthesis Group
    def reference(self, text):
        voice_generator = VoiceGenerateThread(ex, text.split(":")[-1], text.split(":")[0])
        voice_generator.result.connect(self.play)
        voice_generator.error.connect(self.error)
        voice_generator.start()

    def play(self, audio_bytes):
        SpeakThread(ex, audio_bytes).start()

    def error(self, value):
        if value is False:
            self.pop_error(languages[140], languages[140])


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
        ex.capture_screen()

    def send_question(self):
        self.input_question.setGeometry(QRect(0, 430, 400, 30))
        self.click_send.setVisible(False)
        self.click_take_photo.setVisible(False)
        ex.have_conversation(self.input_question.text())


# 主程序
class DesktopTop(shader.ADPOpenGLCanvas):
    def __init__(self, display_x: int | None = None, display_y: int | None = None):
        super().__init__()
        # 设置标题 Set Title
        self.setWindowTitle("AgenticCompanion - Character Mainloop")
        # 设置图标 Set icon
        self.setWindowIcon(QIcon("logo.ico"))
        # 设置属性 Set Attribute
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMouseTracking(True)
        self.setAcceptDrops(True)
        # 调整大小 Set Resize
        self.setFixedSize(400, 400)

        # 基础变量和开关 Variables and Switches
        self.fps_refresh = int(1000 / 900)
        self.turn_count = self.expression_count = 0
        self.model_json_path: str = ""
        self.among = self.click_in_area = self.click_x = self.click_y = -1
        self.speaking_lists: list[bool] = []
        self.is_playing_expression = self.is_penetration = self.is_playing_animation = self.is_movement = False
        self.enter_position = self.drag_position = None
        self.image_path = self.direction = self.last_pos = None
        self.pet_model: live2d.LAppModel | None = None
        self.is_transparent_raise = False

        if display_x is not None and display_y is not None:
            self.move(display_x, display_y)
        else:
            # 屏幕中心坐标 Center of the screen
            self.screen_geometry = QApplication.desktop().availableGeometry()
            x = (self.screen_geometry.width() - self.width()) // 2
            y = self.screen_geometry.height() - self.height()
            self.move(x, y + 15)

        self.recognize_thread = RecognitionThread(self)
        self.recognize_thread.result.connect(self.recognition_success)


        # 定时器
        self.look_timer = QTimer(self)
        self.look_timer.timeout.connect(self.look_for_me)
        if configure['settings']['enable']['media']:
            self.look_timer.start(random.randint(
                    configure['settings']['understand']['min'] // 2,
                    configure['settings']['understand']['max'] // 2) * 1000)

        # 桌宠预备 Pet Preparation
        if configure['model'][configure['default']]['voice']['welcome']:
            SpeakThread(
                self,
                f"./resources/voice/{configure_default}/welcome/"
                f"{random.choice(configure['model'][configure['default']]['voice']['welcome'])}"
            ).start()

    # GUI功能性配置 GUI functional configuration
    def set_mouse_transparent(self, is_transparent: bool):
        """设置鼠标穿透 (透明部分可以直接穿过)"""
        if self.is_transparent_raise:
            return
        window_handle = int(self.winId())
        try:
            SetWindowLong = ctypes.windll.user32.SetWindowLongW
            GetWindowLong = ctypes.windll.user32.GetWindowLongW

            current_exstyle = GetWindowLong(window_handle, GWL_EXSTYLE)
            if is_transparent:
                # 添加WS_EX_TRANSPARENT样式以启用鼠标穿透 Add WS_EX_TRANSPARENT style to enable mouse transparency
                new_exstyle = current_exstyle | WS_EX_TRANSPARENT
            else:
                # 移除WS_EX_TRANSPARENT样式以禁用鼠标穿透 Remove WS_EX_TRANSPARENT style to disable mouse transparency
                new_exstyle = current_exstyle & ~WS_EX_TRANSPARENT

            # 应用新的样式 Apply the new style
            SetWindowLong(window_handle, GWL_EXSTYLE, new_exstyle)
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

    # 功能 Functions
    def look_for_me(self):
        self.look_timer.stop()
        image_path = runtime.capture()
        RFST = MediaUnderstandThread(self, image_path)
        RFST.result.connect(lambda text: self.conversation_display(text, True))
        RFST.start()
        if configure['settings']['enable']['media']:
            self.look_timer.start(random.randint(
                configure['settings']['understand']['min'],
                configure['settings']['understand']['max']) * 1000)

    def capture_screen(self):
        if not configure['settings']['enable']['media']:
            return
        cv.input_question.setText(str(cv.input_question.text()) + "$[图片]$")
        self.image_path = runtime.capture()

    # 语音识别 Recognition
    def recognize(self):
        if not configure['settings']['enable']['rec']:
            return
        if self.recognize_thread.isRunning():
            self.recognize_thread.wait()
        self.recognize_thread.start()

    def recognition_success(self, result: str):
        speech_rec.statued()

        if configure['name'] in result or configure_default in result:
            # 临时对话不启用一些界面 Temporary dialog does not enable some interfaces
            self.change_status_for_conversation("hide", False)
            cv.input_answer.setVisible(True)

            self.have_conversation(result, True)
        logger(f"子应用 - 语音识别 语音呼唤成功\n"
               f"Sub-Application - Voice Recognition Success: {result}\n"
               f"  Message: {result}\n\n"
               f"  Origin: {json.dumps(result, indent=3, ensure_ascii=False)}", logs.API_PATH)

    @staticmethod
    def recognition_failure(error, code):
        logger(f"子应用 - 语音识别 发生错误 {code}:{error}\n"
               f"Sub-Application - Voice Recognition Error: {code}:{error}\n", logs.API_PATH)

    @staticmethod
    def recognition_closure():
        logger("子应用 - 语音识别已关闭\n"
               "Sub-Application - Voice Recognition Closed\n", logs.API_PATH)

    # 对话相关 Conversation related
    def open_close_conversation(self):
        if cv.input_question.isVisible():
            self.change_status_for_conversation("hide")
        else:
            self.change_status_for_conversation("show")

    @staticmethod
    def change_status_for_conversation(status: typing.Literal['hide', 'show'],
                                       enable_chat_box: bool = True):
        status = True if status == "show" else False
        cv.input_question.setVisible(status)
        cv.click_send.setVisible(status)
        cv.click_take_photo.setVisible(status)
        if enable_chat_box:
            cv.input_answer.setVisible(status)

    def conversation_display(self, text: str, temp_action: bool = False):
        def __temp():
            _temp_timer.stop()
            cv.input_answer.setVisible(False)

        if not os.path.isfile(f"./intelligence/rules/{configure['default']}.json"):
            open(f"./intelligence/rules/{configure['default']}.json", "w", encoding="utf-8").close()
        with open(f"./intelligence/rules/{configure['default']}.json", "r", encoding="utf-8") as rf:
            rules = json.load(rf)
            rf.close()

        if text is None:
            return

        if text.split(":")[0] == "None":
            cv.input_question.setGeometry(QRect(0, 430, 281, 30))
            if temp_action:
                _temp_timer = QTimer(self)
                _temp_timer.timeout.connect(__temp)
                _temp_timer.start(5000)
            else:
                self.change_status_for_conversation("show", False)

        if ((VoiceSwitch and configure['settings']['tts']['way'] == "local") or
                configure['settings']['tts']['way'] == "cloud") and configure['settings']['enable']['tts'] and \
                text.split(":")[0] == "None":
            if configure['settings']['enable']['tts']:
                VGT = VoiceGenerateThread(self, ':'.join(text.split(":")[1:]))
                VGT.result.connect(lambda wave_bytes: SpeakThread(self, wave_bytes).start())
                VGT.start()
        else:
            cv.input_answer.clear()
            cv.input_answer.setVisible(True)
            if text.split(":")[0] == "None":
                cv.input_answer.setMarkdown(':'.join(text.split(":")[1:]))
            else:
                cv.input_answer.setMarkdown(text)
            cv.input_answer.moveCursor(cv.input_answer.textCursor().End)
            if text is not None:
                if text[-2:] in rules.keys():
                    self.playAnimationEvent(rules[text[-2:]], "expr")

    def have_conversation(self, text: str | None = None, temp_action: bool = False):
        """进行聊天 Send conversation"""
        chat_message = str(cv.input_question.text()) if text is None else text
        if intelligence is None:
            return
        if not chat_message.strip():
            return
        cv.click_send.setVisible(False)
        cv.click_take_photo.setVisible(False)
        cv.input_answer.setText(f"{configure['name']} {languages[79]}")

        if self.image_path is None and "$[图片]$" not in cv.input_question.text():
            text_generate = TextGenerateThread(
                self, chat_message,
                True if configure['settings']['enable']['online'] else False,
            )
        else:
            text_generate = MediaUnderstandThread(
                self, self.image_path, chat_message.replace("$[图片]$", ""),
                True if configure['settings']['enable']['online'] else False,
            )
            self.image_path = None
        text_generate.start()
        text_generate.result.connect(lambda texts: self.conversation_display(texts, temp_action))

    @staticmethod
    def clear_memories():
        """清除记忆 Clear memories"""
        if intelligence is None:
            return
        intelligence.text.clear_memories()
        cv.input_answer.clear()

    # 自定义事件 Custom events
    # 动画事件 Animation Event
    def finishedAnimationEvent(self):
        self.is_playing_animation = False
        self.turn_count = 0
        self.resetDefaultValueEvent()
        print("END")

    # 重置默认值事件 Reset default value event
    def resetDefaultValueEvent(self):
        for param, values in param_dict.items():
            if param == configure['watermark'].split(";")[0]:
                continue
            self.pet_model.SetParameterValue(param, values['default'], 1)

    # 加载模型事件 Load model event
    def loadModelEvent(self, model):
        try:
            if os.path.exists(f"./resources/model/"
                              f"{model}/"
                              f"{model.title()}.model{'3' if live2d.LIVE2D_VERSION == 3 else ''}"):
                self.model_json_path = (f"./resources/model/"
                                        f"{model}/{model.title()}."
                                        f"model{'3' if live2d.LIVE2D_VERSION == 3 else ''}.json")
                self.pet_model.LoadModelJson(self.model_json_path)
            else:
                self.model_json_path = (f"./resources/model/{model}/"
                                        f"{model}.model{'3' if live2d.LIVE2D_VERSION == 3 else ''}.json")
                self.pet_model.LoadModelJson(self.model_json_path)
        except (KeyError, FileNotFoundError):
            QMessageBox.critical(self, languages[107], languages[109])
            if QMessageBox.question(self, languages[108], languages[110]) == QMessageBox.Yes:
                configure['default'] = 'kasumi2'
                load_template_model(configure['default'])
                QMessageBox.information(self, languages[108], languages[112])
                with open("./resources/configure.json", "w", encoding="utf-8") as sf:
                    json.dump(configure, sf, indent=3, ensure_ascii=False)
                    sf.close()
            self.exit_program()

    # 播放动画事件 Play animation event
    def playAnimationEvent(self, animation_name: str, play_type: typing.Literal['expr', 'anime', 'event'] = 'event'):
        self.is_playing_expression = True
        if play_type != 'event':
            if play_type == 'expr':
                self.pet_model.SetExpression(animation_name)
            else:
                self.pet_model.StartMotion(
                    animation_name.split(":")[0], int(animation_name.split(":")[1]),
                    live2d.MotionPriority.FORCE, onFinishMotionHandler=self.finishedAnimationEvent)
            return
        if (exp := get_configure_actions()[animation_name]['expression'].strip()) != "":
            self.pet_model.SetExpression(exp)
        else:
            group, _, index = get_configure_actions()[animation_name]['motion'].split(":")
            self.pet_model.StartMotion(group, int(index), live2d.MotionPriority.FORCE,
                                       onFinishMotionHandler=self.finishedAnimationEvent)

    # 事件 Events
    # 右键菜单事件 Right-click menu events
    def contextMenuEvent(self, event):
        content_menu = RoundMenu("MENU", parent=self)

        settings_action = Action(FluentIcon.SETTING, languages[68], self)
        settings_action.triggered.connect(lambda: st.show())
        content_menu.addAction(settings_action)

        content_menu.addSeparator()

        conversation_action = Action(FluentIcon.HELP, languages[69], self)
        conversation_action.triggered.connect(self.open_close_conversation)
        content_menu.addAction(conversation_action)

        # 分割线
        content_menu.addSeparator()

        exit_action = Action(FluentIcon.CLOSE, languages[73], self)
        exit_action.triggered.connect(self.exit_program)
        content_menu.addAction(exit_action)

        content_menu.exec_(self.mapToGlobal(event.pos()))

    # 过滤器事件 Filter events
    def eventFilter(self, obj, event):
        if obj is cv.input_question and event.type() == event.KeyPress:
            # 是否按下 Shift + Enter When Shift + Enter is pressed
            if event.key() in (Qt.Key_Enter, Qt.Key_Return):
                if event.modifiers() & Qt.ShiftModifier and cv.click_send.isVisible():
                    cv.click_send.click()
                    return True
                else:
                    return False
        return super().eventFilter(obj, event)

    # 定时器事件 Timer events
    def timerEvent(self, a0: QTimerEvent | None) -> None:
        def save_change():
            self.is_penetration = False
            # 刷新设置的缓存文件 Refresh the cache file
            switch_config['Advanced']['penetration'] = "shut"
            with open("./interface/setting/switch.json", "w", encoding="utf-8") as sccf:
                json.dump(switch_config, sccf, indent=3, ensure_ascii=False)
                sccf.close()
            self.set_mouse_transparent(False)
            self.setCanvasOpacity(configure['settings']['transparency'])

        def check_mouse_pressed(left_condition: str, right_condition: str):
            if not MouseListener.isListening:
                MouseListener.start_listening()
            if switch_config['Advanced']['penetration'] == left_condition:
                pressed = MouseListener.is_left_button_pressed
            elif switch_config['Advanced']['penetration'] == right_condition:
                pressed = MouseListener.is_right_button_pressed
            else:
                pressed = False
            if not MouseListener.isListening:
                MouseListener.start_listening()
            return pressed

        if not self.isVisible():
            return
        # 设置透明度 Set transparency
        self.setCanvasOpacity(configure['settings']['transparency'])
        # 判断兼容性 Compatibility
        if configure["settings"]["compatibility"] is False and self.among == 100:
            # 判断顺序是否低于任务栏 Check whether the order is below the taskbar
            hwnd = self.winId().__int__()
            taskbar_hwnd = win32gui.FindWindow("Shell_TrayWnd", None)
            if win32gui.GetWindowRect(hwnd)[1] < win32gui.GetWindowRect(taskbar_hwnd)[1]:
                self.set_window_below_taskbar()

        # 检查识别器 Check the recognizer
        if not self.recognize_thread.isRunning() and configure['settings']['enable']['rec']:
            self.recognize()
        elif speech_rec is not None and not configure['settings']['enable']['rec']:
            speech_rec.closed()

        # 释放资源 Release resources
        # 检查说话列表的可用性 Check the availability of the speaking list
        if len(self.speaking_lists) == self.speaking_lists.count(False) and not self.speaking_lists:
            # 清除缓存 Clear empty cache
            self.speaking_lists.clear()

        # 定时器检查 Timer checker
        if not configure['settings']['enable']['media']:
            if self.look_timer.isActive():
                self.look_timer.stop()
        else:
            if not self.look_timer.isActive():
                self.look_timer.start(random.randint(
                    configure['settings']['understand']['min'],
                    configure['settings']['understand']['max']) * 1000)

        local_x, local_y = QCursor.pos().x() - self.x(), QCursor.pos().y() - self.y()
        try:
            if configure['settings']['live2d']['enable']['AutoDrag']:
                self.pet_model.Drag(local_x, local_y)
        except SystemError:
            pass
        # 检查是否开启全局鼠标穿透 Check whether global mouse transparency is enabled
        if switch_config['Advanced']['penetration'] != "shut":
            self.setCanvasOpacity(0.4)
            self.set_mouse_transparent(True)
            self.is_penetration = True
            # 如果start有以下几种情况，则取消全局鼠标穿透 if start has the following four situations, cancel global mouse transparency
            # 下次启动时取消全局鼠标穿透 if the start is next, cancel global mouse transparency
            if switch_config['Advanced']['penetration'] == "next" and self.among == -1:
                save_change()
            # 鼠标左键或右键在顶部按下时取消全局鼠标穿透 if the start is left-top or right-top, cancel global mouse transparency
            elif switch_config['Advanced']['penetration'] in ('left-top', 'right-top'):
                if self.is_in_live2d_area(local_x, local_y) and check_mouse_pressed('left-top', 'right-top') and \
                        80 > local_y > 0:
                    MouseListener.stop_listening()
                    save_change()
            # 鼠标左键或右键在底部按下时取消全局鼠标穿透 if the start is left-bottom or right-bottom, cancel global mouse transparency
            elif switch_config['Advanced']['penetration'] in ('left-bottom', 'right-bottom'):
                if self.is_in_live2d_area(local_x, local_y) and check_mouse_pressed('left-bottom', 'right-bottom') and \
                        self.height() > local_y > self.height() - 80:
                    MouseListener.stop_listening()
                    save_change()
        elif switch_config['Advanced']['penetration'] == "shut" and self.among == 0:
            save_change()

        if self.among > 100:
            self.among = 0
        self.among += 1
        # 检查表情 Check Expression
        if self.expression_count >= 300 * self.fps_refresh:
            self.is_playing_expression = False
            self.pet_model.ResetExpression()
        if self.is_playing_expression:
            self.expression_count += self.fps_refresh
        else:
            self.expression_count = 0

        # 检查点击区域 Check the click area
        if self.is_in_live2d_area(local_x, local_y) and not self.is_penetration:
            self.set_mouse_transparent(False)
            self.click_in_area = True
        elif not self.is_penetration:
            self.set_mouse_transparent(True)
            self.turn_count = 0
            self.click_in_area = False

        self.update()

    def is_in_live2d_area(self, click_x: int | None = None, click_y: int | None = None):
        if click_x is None:
            click_x = QCursor.pos().x() - self.x()
        if click_y is None:
            click_y = QCursor.pos().y() - self.y()
        """检查是否在模型内 Check whether the mouse is in the model"""
        h = self.height()
        try:
            alpha = GL.glReadPixels(click_x * QGuiApplication.primaryScreen().devicePixelRatio(),
                                    (h - click_y) * QGuiApplication.primaryScreen().devicePixelRatio(),
                                    1, 1, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE)[3]
        except GL.error.GLError:
            alpha = 0
        return alpha > 0

    # 鼠标拖动事件 Mouse drag events
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
            """检查是否满足框内要求 Check whether the box is satisfied"""
            x_min, x_max, y_min, y_max = get_configure_actions()[parameter]['position']
            return (
                    x_min <= current_x <= x_max and y_min <= current_y <= y_max and
                    not self.is_playing_animation and self.turn_count >= turn_count and self.click_in_area
            )

        x, y = QCursor.pos().x() - self.x(), QCursor.pos().y()
        # 拖动事件 Drag events
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

                    for action_item in subscribe.actions.Operate().GetMouseDragAction():
                        action_item(x, y, new_pos)
                    cv.move(cv_new_pos)
                event.accept()

        # 非接触悬浮鼠标的互动 Non-touch hover mouse interaction
        if self.enter_position and not event.buttons() & Qt.LeftButton:
            # 处理互动事件/动画 Process interaction events/animation
            current_pos = event.pos()
            current_x = current_pos.x()
            current_y = current_pos.y()

            if self.last_pos is not None:
                last_x, last_y = self.last_pos.x(), self.last_pos.y()
                current_x, current_y = current_pos.x(), current_pos.y()

                # 状态 Status
                if current_x > last_x:
                    new_direction = 'right'
                elif current_x < last_x:
                    new_direction = 'left'
                else:
                    new_direction = self.direction

                # 检查方向是否改变 Check whether the direction has changed
                if self.direction is not None and new_direction != self.direction:
                    self.turn_count += 1

                self.direction = new_direction

            self.last_pos = current_pos

            # 互动事件/动画 Interaction events/animation
            if self.click_in_area and not self.is_movement:
                # 摸头互动 Touch interaction
                if checker('ActionTouchHead', 4):
                    SpeakThread(self, get_audio_path('ActionTouchHead')).start()
                    self.click_in_area = False
                    self.is_playing_animation = True
                    # 播放动画 Play animation
                    self.playAnimationEvent('ActionTouchHead')
                # 摸腿互动 Touch leg interaction
                if checker('ActionTouchLeg', 4):
                    SpeakThread(self, get_audio_path('ActionTouchLeg')).start()
                    self.click_in_area = False
                    self.is_playing_animation = True
                    self.playAnimationEvent('ActionTouchLeg')
                # 自定义互动 Custom interaction
                if checker('ActionTouchCustom', 4):
                    SpeakThread(self, get_audio_path('ActionTouchCustom')).start()
                    self.click_in_area = False
                    self.is_playing_animation = True
                    self.playAnimationEvent('ActionTouchCustom')

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        def checker(parameter_action: str):
            """检查点击位置是否符合标准 Check whether the click position meets the standards"""
            x_min, x_max, y_min, y_max = get_configure_actions()[parameter_action]['position']
            return x_min <= click_x <= x_max and y_min <= click_y <= y_max \
                and not self.is_playing_animation

        click_x, click_y = event.globalPos().x() - self.x(), event.globalPos().y() - self.y()
        if event.button() == Qt.LeftButton and self.click_in_area:
            print(f"meet the requirements. CLICK pos: {click_x, click_y}")
            # 记录位置 Record position
            if configure['record']['enable_position']:
                if configure['record']['position'][:2].count(-1) == len(configure['record']['position'][:2]):
                    configure['record']['position'][:2] = [click_x, click_y]
                else:
                    configure['record']['position'][2:] = [click_x, click_y]
                    configure['record']['enable_position'] = False

            # 点击事件/动画 Click event/animation
            # 胸部点击行为 Chest click behavior
            if checker("ActionClickChest"):
                self.is_playing_animation = True
                self.playAnimationEvent('ActionClickChest')
                if configure['adult_level'] > 0:
                    dir_, voice_list = AdultEngine.voice()
                    SpeakThread(self,
                                f"./resources/adult/{configure['default']}/voice/{dir_}/"
                                f"{random.choice(voice_list)}").start()
                else:
                    SpeakThread(self, get_audio_path("ActionClickChest")).start()
            # 帽点击行为 Hat click behavior
            elif checker("ActionClickCap"):
                self.is_playing_animation = True
                self.playAnimationEvent('ActionClickCap')
                SpeakThread(self, get_audio_path("ActionClickCap")).start()
            elif checker("ActionClickCustom"):
                self.is_playing_animation = True
                self.playAnimationEvent('ActionClickCustom')
                SpeakThread(self, get_audio_path("ActionClickCustom")).start()
            for action_item in subscribe.actions.Operate().GetClckAction():
                try:
                    action_item()
                except Exception as e:
                    widgets.pop_error(st, 'Error', str(e))
            event.accept()
        self.is_movement = False

    # 鼠标进入事件 Mouse entry event
    def enterEvent(self, event):
        self.turn_count = 0
        self.enter_position = event.pos()

    # 鼠标离开事件 Mouse leave event
    def leaveEvent(self, event):
        self.is_movement = False
        self.enter_position = None
        self.is_playing_animation = False

    # 拖拽事件 Drag event
    def dragEnterEvent(self, event: QMimeData):
        ActionsEngine.analyze_action(event.mimeData().text())
        ActionsEngine.accept_action()
        event.accept()

    # OpenGL 事件 OpenGL events
    def on_init(self):
        live2d.glewInit()
        self.pet_model = live2d.LAppModel()
        self.loadModelEvent(configure['default'])
        param_dict.clear()
        for i in range(self.pet_model.GetParameterCount()):
            param = self.pet_model.GetParameter(i)
            param_dict.update({str(param.id): {
                "value": param.value, "max": param.max, "min": param.min, "default": param.default,
            }})
        subscribe.RegisterAttribute().SetPet(self.pet_model)
        self.startTimer(self.fps_refresh)

    def on_resize(self, width, height):
        self.pet_model.Resize(width, height)

    def on_draw(self):
        live2d.clearBuffer()
        try:
            self.pet_model.Update()
            # 清除水印 Clear watermark
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
        live2d.dispose()
        self.close()
        try:
            os.remove("./logs/backup/configure.json")
        except FileNotFoundError:
            pass
        shutil.copy2("./resources/configure.json", "./logs/backup/configure.json")
        logger("程序退出 Program exit", logs.HISTORY_PATH)
        os.kill(os.getpid(), __import__("signal").SIGINT)


thread_exception_tool: list = []
live2d.setLogEnable(False)
live2d.init()
MouseListener = runtime.MouseListener()
# 加载引擎
AdultEngine = engine.adult.AdultEngine(configure)
ActionsEngine = engine.actions.ActionsEngine(configure, languages, subscribe)
logger("桌宠初始化完成 Live2D初始化完成\n"
       "DesktopPet initialized successfully, Live2D initialized successfully.\n", logs.HISTORY_PATH)
if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    # 加载桌宠页面 Load desktop pet page
    app = QApplication(sys.argv)
    ex = DesktopTop()
    ex.show()
    subscribe.RegisterAttribute().SetWindow(ex)
    cv = Conversation()
    cv.show()
    cv.move(ex.x(), ex.y() - 60)

    # 插件日志收集器 Plugin log collector
    PluginLogCollector = plog.PluginLogCollector()
    global_ = {
        "subscribe": subscribe,
        "print": PluginLogCollector.print_,
        "input": PluginLogCollector.input_,
    }
    st = Setting()
    subscribe.views.RegisterSetting().register(st)

    # 加载插件 Load plugins
    with open("./plugin/desc.json", 'r', encoding="utf-8") as f:
        plugin_desc = json.load(f)
        f.close()
    for to_be_loaded_plugin in os.listdir("./plugin"):
        if os.path.isfile(f"./plugin/{to_be_loaded_plugin}"): continue
        execute_path = f"./plugin/{to_be_loaded_plugin}/{plugin_desc[to_be_loaded_plugin]["entrance"]}"
        execute_code = (open(execute_path, "r", encoding="utf-8").read(), global_)
        if plugin_desc[to_be_loaded_plugin]["type"] == "enhancement":
            exec(*execute_code)
        elif plugin_desc[to_be_loaded_plugin]["type"] == "assistant":
            thread_exception_tool.append(runtime.ThreadExceptionEnd(lambda: exec(*execute_code)))
        elif plugin_desc[to_be_loaded_plugin]["type"] == "auto":
            if runtime.PythonCodeParser(execute_code[0]).has_subscribe_for_views:
                thread_exception_tool.append(runtime.ThreadExceptionEnd(lambda: exec(*execute_code)))
            else:
                exec(*execute_code)
    for thread in thread_exception_tool:
        thread.start()
    del plugin_desc

    sys.exit(app.exec_())
