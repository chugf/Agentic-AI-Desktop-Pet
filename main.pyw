import sys
import time
import datetime
import random
import threading
import webbrowser

# 数据处理 Data Processing
import os
import re
import struct
import json
import typing
# 音频数据处理 audio data processing
import wave
import pyaudio
import io

# 日志数据
import logs

# AI
try:
    import intelligence
    Client = intelligence.voice.Client()
    MODULE_INFO = Client.command({"module_info": None})

except ImportError:
    intelligence.VoiceSwitch = False
    Client = intelligence = None
    MODULE_INFO = {}

except ConnectionRefusedError:
    intelligence.VoiceSwitch = False
    Client = None
    MODULE_INFO = {}

try:
    import runtime

except ImportError:
    runtime = None

# WindowsAPI
import ctypes
import win32gui
import win32con
import win32api

# 引入live2d库 Import Live2D
import live2d.v3 as live2d
from live2d.v3.params import StandardParams

# 界面库和OpenGL库 GUI
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.scrolledtext import ScrolledText

import OpenGL.GL as GL

from PyQt5.Qt import Qt, QTimerEvent, QCursor, QThread, pyqtSignal, QRect, QFont, QTimer
from PyQt5.QtWidgets import QOpenGLWidget, QApplication, QMessageBox, QMenu, QAction, \
    QTextEdit, QPushButton


GWL_EXSTYLE = -20
WS_EX_TRANSPARENT = 0x00000020
speech_rec = None
with open("./resources/configure.json", "r", encoding="utf-8") as f:
    configure = json.load(f)
    configure_default = configure["default"]
    configure_settings = configure["settings"]
    configure_model = configure['model']

    if configure_default == "tongyi":
        configure_default = "vanilla"

    configure_actions = configure['model'][configure_default]['action']
    configure_adults = configure['model'][configure_default]['adult']
    configure_voices = configure['model'][configure_default]['voice']

    action_TouchHead = configure_actions['ActionTouchHead']
    f.close()
if intelligence:
    intelligence.text.reload_memories(configure['default'])
    intelligence.ALI_API_KEY = configure_settings['cloud']['aliyun']
    intelligence.XF_API_ID = configure_settings['cloud']['xunfei']['id']
    intelligence.XF_API_KEY = configure_settings['cloud']['xunfei']['key']
    intelligence.XF_API_SECRET = configure_settings['cloud']['xunfei']['secret']


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


# Live2D 操作线程 Liv2D Operation Thread
class IterateAddParameterValue(QThread):
    """根据最小值和最大值进行迭代的线程 According to the minimum and maximum values to iterate"""
    def __init__(self, parent, param: str, value: int, minimum: int, maximum: int, weight, duration):
        super().__init__(parent)
        self.id_param = self.parent().stop_playing_animation[1]
        self.param = param
        self.value = value
        self.minimum = int(minimum)
        self.maximum = int(maximum)
        self.weight = weight
        self.duration = duration

    def run(self):
        for value in range(self.minimum, self.maximum, self.value):
            if (
                    self.parent().stop_playing_animation[0] and
                    self.parent().stop_playing_animation[1] != self.id_param or
                    not self.parent().stop_playing_animation[1] and "Reverse" not in self.id_param):
                break
            live2d.clearBuffer()
            self.parent().pet_model.Update()
            self.parent().pet_model.AddParameterValue(self.param, value)
            self.parent().pet_model.Draw()
            self.parent().maximum_param_counter = value
            time.sleep(self.duration)
        if "Reverse" in self.id_param:
            self.parent().maximum_param_counter = max([self.minimum + 1, self.maximum])


class AutoBlinkEye(QThread):
    """自动眨眼线程"""
    def __init__(self, parent, param_dict):
        super().__init__(parent)
        self.param_dict = param_dict

    def run(self):
        def updater():
            """更新眼睛的函数 Update the eyes function"""
            live2d.clearBuffer()
            self.parent().pet_model.SetParameterValue(StandardParams.ParamEyeLOpen, int(value) / 10, 1.)
            self.parent().pet_model.Draw()
            self.parent().pet_model.SetParameterValue(StandardParams.ParamEyeROpen, int(value) / 10, 1.)
            self.parent().pet_model.Draw()
            time.sleep(0.12 / int(maximum * 10))

        minimum = self.param_dict[StandardParams.ParamEyeLOpen]['min']
        maximum = (self.param_dict[StandardParams.ParamEyeROpen]['max'] +
                   self.param_dict[StandardParams.ParamEyeLOpen]['max']) // 2
        while True:
            self.parent().is_playing_animation = True
            self.parent().has_played_animation = True

            for value in range(int(maximum * 10), int(minimum * 10) - 1, -1):
                updater()
            for value in range(int(minimum * 10), int(maximum * 10) + 1):
                updater()

            self.parent().is_playing_animation = False
            self.parent().has_played_animation = False

            time.sleep(random.uniform(4, 8))


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
        if isinstance(self.resource_data, bytes):
            wave_source = io.BytesIO(self.resource_data)
            mode = "rb"
        else:
            wave_source = self.resource_data
            mode = "r"

        if self.parent().speaking_lists[self.current_speak_index - 1] and self.current_speak_index != 0:
            self.parent().speaking_list[self.current_speak_index - 1] = False

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
    result = pyqtSignal(list)

    def __init__(self, parent: QOpenGLWidget):
        super().__init__(parent)

    def run(self):
        global speech_rec
        speech_rec = intelligence.speech_recognition(
            self.result.emit,
            self.parent().recognition_failure, self.parent().recognition_closure)
        speech_rec.start_recognition()


class MediaUnderstandThread(QThread):
    result = pyqtSignal(list)

    def __init__(self, parent: QOpenGLWidget, image_bytes: bytes,
                 texts: str | None = None, is_search_online: bool = False):
        """根据媒体理解线程 Media Understand Thread"""
        super().__init__(parent)
        self.image_bytes = image_bytes
        self.is_search_online = is_search_online
        self.texts = texts

    def run(self):
        if self.texts is None:
            self.texts = random.choice(["你觉得我在干什么？", "你有什么想法呀？", "你觉得这个图片怎么样？", "请评价一下这图片"])
        try:
            answer = intelligence.media_understand(self.texts, self.image_bytes, self.is_search_online)
        except Exception as e:
            logger(f"子应用 - 媒体文件理解 调用失败\n"
                   f"   Message: {e}", logs.HISTORY_PATH)
            self.result.emit([f"AI媒体文件理解 调用失败 AI Answer failed to call\n{type(e).__name__}: {e}",
                              f"AI媒体文件理解 调用失败 AI Answer failed to call\n{type(e).__name__}: {e}"])
            return
        logger("子应用 - AI图文理解 调用成功 Sub Application - AI Media Understand Call Success\n"
               f"   Message: {answer}", logs.HISTORY_PATH)
        self.result.emit(answer)


class TextGenerateThread(QThread):
    """文本生成器线程 Text Generation Thread"""
    result = pyqtSignal(tuple)

    def __init__(self, parent: QOpenGLWidget, text: str, is_search_online: bool = False):
        super().__init__(parent)
        self.text = text
        self.is_search_online = is_search_online

    def run(self):
        try:
            answer = intelligence.text_generator(self.text, self.is_search_online)
        except Exception as e:
            logger(f"子应用 - AI剧情问答 调用失败\n"
                   f"   Message: {e}", logs.HISTORY_PATH)
            self.result.emit([f"AI问答 调用失败 AI Answer failed to call\n{type(e).__name__}: {e}",
                              f"AI问答 调用失败 AI Answer failed to call\n{type(e).__name__}: {e}"])
            return
        logger(f"子应用 - AI剧情问答 调用成功\n"
               f"   Message: {answer}", logs.HISTORY_PATH)
        self.result.emit(answer)


class VoiceGenerateThread(QThread):
    """AI 文字转语音 (GSV) AI text-to-speech (GSV) module"""
    result = pyqtSignal(list)

    def __init__(self, parent: QOpenGLWidget, text: str):
        super().__init__(parent)
        self.text = text

    def run(self):
        # 数据预处理 data pre-processing
        # 排除表情等无需发音的内容 Exclude expressions such as emotion
        text = re.sub(r'(\(.*）\))', '', self.text)
        text = re.sub(r'(（.*）)', '', text)
        text = re.sub(r'(\[.*])', '', text)
        text = re.sub(r'(【.*】)', '', text)
        # 翻译和语言 Translation and language
        language = "zh"
        if configure['settings']['tts'] == "local":
            if "trans" not in configure['settings']['disable']:
                if "spider" in configure_settings['translate']:
                    if "bing" in configure_settings['translate']:
                        text = intelligence.machine_translate(text)
                        language = "ja"
                elif "ai" in configure_settings['translate']:
                    if "tongyi" in configure_settings['translate']:
                        text = intelligence.tongyi_translate(text)
                        language = "ja"

            intelligence.voice_change(configure['voice_model'], MODULE_INFO)
            wav_bytes = intelligence.gsv_voice_generator(
                text, language, MODULE_INFO, configure['voice_model'],
                url=str(configure['settings']['local']['gsv']).format(
                    ip=__import__("socket").gethostbyname(__import__("socket").gethostname()),
                    year=time.strftime("%Y")))
            # 计算长度 Calculate length
            riff_header = wav_bytes[:12]
            if not riff_header.startswith(b'RIFF') or not riff_header[8:12] == b'WAVE':
                raise ValueError("Invalid RIFF/WAVE header")

            pos = 12
            fmt_chunk_data = None
            data_chunk_size = None

            # 遍历所有块直到找到fmt和data块 find fmt and data chunks
            while pos < len(wav_bytes):
                chunk_id = wav_bytes[pos:pos + 4]
                chunk_size = struct.unpack_from('<I', wav_bytes, pos + 4)[0]
                pos += 8  # 跳过chunk id和size Break past chunk id and size

                if chunk_id == b'fmt ':
                    fmt_chunk_data = wav_bytes[pos:pos + chunk_size]
                elif chunk_id == b'data':
                    data_chunk_size = chunk_size
                    break  # 找到data块后可以停止搜索 stop searching

                pos += chunk_size
                if chunk_size % 2 != 0:
                    pos += 1

            if fmt_chunk_data is None or data_chunk_size is None:
                raise ValueError("fmt or data chunk missing in WAV file")

            # 解析fmt块数据 Parse fmt chunk data
            _, channels, sample_rate, byte_rate, block_align, bits_per_sample = struct.unpack_from('<HHIIHH',
                                                                                                   fmt_chunk_data)

            # 计算音频长度（秒） Calculate audio duration
            duration = int(data_chunk_size / (sample_rate * channels * (bits_per_sample / 8)) * 1000)
        else:
            wav_bytes, duration = intelligence.ali_voice_generator(text)

        logger(f"子应用 - AI语音(GSV) 调用成功\n"
               f"   Duration {duration}\n", logs.HISTORY_PATH)
        self.result.emit([wav_bytes, duration])


# 鼠标监听器 Mouse listener
class MouseListener:
    """用于在全局鼠标穿透下进行监听 Used for global mouse penetration to listen"""
    def __init__(self):
        self.listener_thread = None
        self.isListening = False
        self.is_left_button_pressed = False
        self.is_right_button_pressed = False

    def start_listening(self):
        self.isListening = True
        self.listener_thread = threading.Thread(target=self.listen)
        self.listener_thread.start()

    def stop_listening(self):
        self.__init__()

    def listen(self):
        state_left = 0
        state_right = 0
        while self.isListening:
            current_state_left = win32api.GetKeyState(win32con.VK_LBUTTON)
            current_state_right = win32api.GetKeyState(win32con.VK_RBUTTON)
            if current_state_left != state_left:
                state_left = current_state_left
                if current_state_left < 0:
                    self.is_left_button_pressed = True
                else:
                    self.is_left_button_pressed = False
            if current_state_right != state_right:
                state_right = current_state_right
                if current_state_right < 0:
                    self.is_right_button_pressed = True
                else:
                    self.is_right_button_pressed = False
            threading.Event().wait(0.01)


# 设置
class Setting(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI-Agent  桌面宠物设置 | Desktop Pet Settings")
        self.geometry("600x450")
        self.attributes("-alpha", 0.9)
        self.attributes("-topmost", True)

        self.note = ttk.Notebook(self)

        self.general_frame = tk.Frame(self)
        self.switch_frame = tk.Frame(self)
        self.intelligence_frame = tk.Frame(self)
        self.animation_frame = tk.Frame(self)
        self.character_frame = tk.Frame(self)
        self.about_frame = tk.Frame(self)
        self.note.add(self.general_frame, text="常规 General")

        tk.Label(self.general_frame, text="宠物形象 Pet Character：").place(x=5, y=5)
        clist = os.listdir("./resources/model")
        clist.append("tongyi")
        self.pet_character = ttk.Combobox(self.general_frame, values=clist, state="readonly")
        self.pet_character.set(configure['default'])
        self.pet_character.bind("<<ComboboxSelected>>",
                                lambda event: self.change_character(self.pet_character.get()))
        self.pet_character.place(x=200, y=5)

        self.pet_nickname_entry = ttk.Entry(self.general_frame, width=23)
        self.pet_nickname_entry.insert(0, configure['name'])
        self.pet_nickname_entry.bind("<Key>", lambda event: self.change_character(self.pet_character.get()))
        self.pet_nickname_entry.place(x=380, y=5)

        tk.Label(self.general_frame, text="翻译工具 Translation Tool：").place(x=5, y=35)
        self.translation_class = ttk.Combobox(self.general_frame, values=["爬虫 Spider", "人工智能 AI"], state="readonly")
        self.translation_class.current(0)
        if "spider" in configure_settings['translate']:
            self.translation_class.current(0)
            self.translation_tool = ttk.Combobox(self.general_frame, values=["必应 Bing"],
                                                 state="readonly")
        elif "ai" in configure_settings['translate']:
            self.translation_class.current(1)
            self.translation_tool = ttk.Combobox(self.general_frame, values=["通义千问 Tongyi"],
                                                 state="readonly")
        else:
            self.translation_tool = ttk.Combobox(self.general_frame, values=[], state="readonly")

        self.translation_class.bind("<<ComboboxSelected>>", self.change_translation_tool)
        self.translation_tool.bind("<<ComboboxSelected>>", lambda event: self.change_translate())
        self.translation_class.place(x=200, y=35)
        if "bing" in configure_settings['translate']:
            self.translation_tool.current(0)
        elif "tongyi" in configure_settings['translate']:
            self.translation_tool.current(0)
        self.translation_tool.place(x=380, y=35)

        tk.Label(self.general_frame, text="成人模式 Adult Mode: ").place(x=5, y=70)
        self.adult_lists = ttk.Combobox(self.general_frame, values=list(configure_adults['AdultDescribe'].values()),
                                        state="readonly")
        if configure['adult_level'] > 0:
            self.adult_lists.current(configure['adult_level'] - 1)
        else:
            self.adult_lists.configure(state=tk.DISABLED)
        self.adult_lists.place(x=200, y=70)

        tk.Label(self.general_frame, text="语音模型 Voice Module：").place(x=5, y=100)
        self.voice_text_entry = ttk.Entry(self.general_frame, width=65)
        self.voice_text_entry.place(x=5, y=130)
        self.voice_model_lists = ttk.Combobox(self.general_frame, values=list(MODULE_INFO.keys()),
                                              state="readonly")
        self.voice_model_lists.set(configure['voice_model'])
        self.voice_model_lists.place(x=200, y=100)
        self.play_refer_audio = ttk.Button(self.general_frame, text="试听 Audition",
                                           command=self.play_refer_audio)
        self.play_refer_audio.place(x=380, y=100)
        self.voice_model_lists.bind("<<ComboboxSelected>>", self.change_refer_text)

        self.note.add(self.switch_frame, text="开关 Switch")

        self.switches = tk.LabelFrame(self.switch_frame, text="开关列表 Switch Lists", width=590, height=100)
        self.switches.place(x=5, y=5)

        self.compatible_value = tk.BooleanVar(self)
        self.compatible_value.set(configure['settings']['compatibility'])
        self.compatible_button = ttk.Checkbutton(self.switches, text="录屏兼容 Capture Compatibility",
                                                 variable=self.compatible_value, onvalue=True, offvalue=False,
                                                 command=lambda: self.io_configure(
                                                     "{compatibility}", "settings.compatibility", bool))
        self.compatible_button.place(x=10, y=5)

        self.adult_value = tk.IntVar(self)
        self.adult_value.set(configure['adult_level'])
        self.adult_button = ttk.Checkbutton(self.switches, text="成人模式 Adult Mode",
                                            variable=self.adult_value,
                                            onvalue=1 if configure['adult_level'] == 0 else configure['adult_level'],
                                            offvalue=0,
                                            command=lambda: self.io_configure(
                                                "{adult}", "adult_level", int))
        self.adult_button.place(x=400, y=5)

        self.speech_recognition_value = tk.BooleanVar(self)
        self.speech_recognition_value.set(True if "rec" not in configure['settings']['disable'] else False)
        self.speech_recognition_button = ttk.Checkbutton(self.switches, text="语音识别 Speech Recognition",
                                                         variable=self.speech_recognition_value, onvalue=True,
                                                         offvalue=False,
                                                         command=lambda: self.io_configure("rec"))
        self.speech_recognition_button.place(x=10, y=30)

        self.ai_voice_value = tk.BooleanVar(self)
        self.ai_voice_value.set(True if "tts" not in configure['settings']['disable'] else False)
        self.ai_voice_button = ttk.Checkbutton(self.switches, text="AI语音 AI Voice",
                                               variable=self.ai_voice_value, onvalue=True, offvalue=False,
                                               command=lambda: self.io_configure("tts"))
        self.ai_voice_button.place(x=400, y=30)

        self.online_search_value = tk.BooleanVar(self)
        self.online_search_value.set(True if "online" not in configure['settings']['disable'] else False)
        self.online_search_button = ttk.Checkbutton(self.switches, text="在线搜索 Online Search",
                                                    variable=self.online_search_value, onvalue=True, offvalue=False,
                                                    command=lambda: self.io_configure("online"))
        self.online_search_button.place(x=10, y=55)

        self.translate_value = tk.BooleanVar(self)
        self.translate_value.set(True if "trans" not in configure['settings']['disable'] else False)
        self.translate_button = ttk.Checkbutton(self.switches, text="翻译 Translate",
                                                variable=self.translate_value, onvalue=True, offvalue=False,
                                                command=lambda: self.io_configure("trans"))
        self.translate_button.place(x=400, y=55)

        self.advanced_switch_frame = tk.LabelFrame(self.switch_frame,
                                                   text="高级开关 Advanced Switch", width=590, height=200)
        tk.Label(self.advanced_switch_frame, text="从\t        到\t\t 之间随机选取作为时间间隔").place(x=230, y=5)
        self.media_understand_value = tk.BooleanVar(self)
        self.media_understand_value.set(True if "media" not in configure['settings']['disable'] else False)
        self.media_understand_button = ttk.Checkbutton(self.advanced_switch_frame, text="媒体理解 Media Understand",
                                                       variable=self.media_understand_value, onvalue=True,
                                                       offvalue=False,
                                                       command=lambda: self.io_configure("media"))
        self.media_understand_minimum = ttk.Spinbox(
            self.advanced_switch_frame,
            from_=0, to=86400, width=7,
            command=lambda: self.change_configure(
                int(self.media_understand_minimum.get()), "settings.understand.min"))
        self.media_understand_minimum.set(configure['settings']['understand']['min'])
        self.media_understand_minimum.place(x=250, y=5)
        self.media_understand_maximum = ttk.Spinbox(
            self.advanced_switch_frame,
            from_=0, to=86400, width=6,
            command=lambda: self.change_configure(
                int(self.media_understand_maximum.get()), "settings.understand.max"))
        self.media_understand_maximum.set(configure['settings']['understand']['max'])
        self.media_understand_maximum.place(x=340, y=5)
        self.media_understand_button.place(x=5, y=5)

        self.globe_mouse_penetration_value = tk.BooleanVar(self)
        self.globe_mouse_penetration_value.set(True if configure['settings']['penetration']['enable'] else False)
        self.globe_mouse_penetration_button = ttk.Checkbutton(
            self.advanced_switch_frame,
            text="全局鼠标穿透 Global Mouse Penetration",
            variable=self.globe_mouse_penetration_value, onvalue=True,
            offvalue=False,
            command=lambda: self.change_configure(
                self.globe_mouse_penetration_value.get(),
                "settings.penetration.enable"
            ))
        self.globe_mouse_penetration_button.place(x=5, y=30)

        tk.Label(self.advanced_switch_frame, text="取\n消\n时\n间").place(x=50, y=55)
        self.penetration_start_value = tk.StringVar(self)
        if configure['settings']['penetration']['start']:
            self.penetration_start_value.set(configure['settings']['penetration']['start'])
        else:
            self.penetration_start_value.set("next")
        self.penetration_start_next_time = ttk.Radiobutton(
            self.advanced_switch_frame,
            text="下次启动时 When starting next time",
            variable=self.penetration_start_value,
            value="next",
            command=lambda: self.change_configure(
                self.penetration_start_value.get(),
                "settings.penetration.start"
            ))
        self.penetration_start_next_time.place(x=80, y=55)

        self.penetration_start_random = ttk.Radiobutton(
            self.advanced_switch_frame,
            text="随机 Random",
            variable=self.penetration_start_value,
            value="random",
            command=lambda: self.change_configure(
                self.penetration_start_value.get(),
                "settings.penetration.start"
            ))
        self.penetration_start_random.place(x=380, y=55)

        self.penetration_start_left_click_bottom = ttk.Radiobutton(
            self.advanced_switch_frame,
            text="左击底部 Left-click bottom",
            variable=self.penetration_start_value,
            value="left-bottom",
            command=lambda: self.change_configure(
                self.penetration_start_value.get(),
                "settings.penetration.start"
            ))
        self.penetration_start_left_click_bottom.place(x=80, y=80)

        self.penetration_start_left_click_top = ttk.Radiobutton(
            self.advanced_switch_frame,
            text="左击顶部 Left-click top",
            variable=self.penetration_start_value,
            value="left-top",
            command=lambda: self.change_configure(
                self.penetration_start_value.get(),
                "settings.penetration.start"
            ))
        self.penetration_start_left_click_top.place(x=380, y=80)

        self.penetration_start_right_click_bottom = ttk.Radiobutton(
            self.advanced_switch_frame,
            text="右击底部 Right-click bottom",
            variable=self.penetration_start_value,
            value="right-bottom",
            command=lambda: self.change_configure(
                self.penetration_start_value.get(),
                "settings.penetration.start"
            ))
        self.penetration_start_right_click_bottom.place(x=80, y=105)

        self.penetration_start_right_click_top = ttk.Radiobutton(
            self.advanced_switch_frame,
            text="右击顶部 Right-click top",
            variable=self.penetration_start_value,
            value="right-top",
            command=lambda: self.change_configure(
                self.penetration_start_value.get(),
                "settings.penetration.start"
            ))
        self.penetration_start_right_click_top.place(x=380, y=105)
        # self.penetration_want_custom = ttk.Radiobutton(
        #     self.advanced_switch_frame,
        #     text="我想什么时候 I want when",
        #     variable=self.penetration_start_value,
        #     value="want",
        #     command=lambda: self.change_configure(
        #         self.penetration_start_value.get(),
        #         "settings.penetration.start"
        #     ))
        # self.penetration_want_custom.place(x=80, y=80)

        self.advanced_switch_frame.place(x=5, y=110)

        self.note.add(self.intelligence_frame, text="人工智能 AI")

        self.cloud_infer = tk.LabelFrame(self.intelligence_frame, text="云端推理 Cloud Infer", width=590, height=150)

        tk.Label(self.cloud_infer, text="阿里云 API_KEY：").place(x=5, y=5)
        self.aliyun_apikey_entry = ttk.Entry(self.cloud_infer, width=50, show="*")
        self.aliyun_apikey_entry.insert(0, configure_settings['cloud']['aliyun'])
        self.aliyun_apikey_entry.place(x=150, y=5)

        tk.Label(self.cloud_infer, text="讯飞 API_ID：").place(x=5, y=35)
        self.xunfei_apiid_entry = ttk.Entry(self.cloud_infer, width=50, show="*")
        self.xunfei_apiid_entry.insert(0, configure_settings['cloud']['xunfei']['id'])
        self.xunfei_apiid_entry.place(x=150, y=35)

        tk.Label(self.cloud_infer, text="讯飞 API_KEY：").place(x=5, y=65)
        self.xunfei_apikey_entry = ttk.Entry(self.cloud_infer, width=50, show="*")
        self.xunfei_apikey_entry.insert(0, configure_settings['cloud']['xunfei']['key'])
        self.xunfei_apikey_entry.place(x=150, y=65)

        tk.Label(self.cloud_infer, text="讯飞 API_SECRET：").place(x=5, y=95)
        self.xunfei_apisecret_entry = ttk.Entry(self.cloud_infer, width=50, show="*")
        self.xunfei_apisecret_entry.insert(0, configure_settings['cloud']['xunfei']['secret'])
        self.xunfei_apisecret_entry.place(x=150, y=95)

        self.cloud_infer.place(x=5, y=5)

        self.local_infer = tk.LabelFrame(self.intelligence_frame, text="本地推理 Local Infer", width=590, height=160)

        tk.Label(self.local_infer, text="通义千问 Tongyi").place(x=5, y=5)
        self.qwen_api_url = ttk.Entry(self.local_infer, width=50)
        self.qwen_api_url.insert(0, configure_settings['local']['qwen'])
        self.qwen_api_url.place(x=150, y=5)

        tk.Label(self.local_infer, text="GPT-SoVITS (TTS)").place(x=5, y=35)
        self.gsv_api_url = ttk.Entry(self.local_infer, width=50)
        self.gsv_api_url.insert(0, configure_settings['local']['gsv'])
        self.gsv_api_url.place(x=150, y=35)

        tk.Label(self.local_infer, text="语音识别 Recognition").place(x=5, y=65)
        self.recognition_api_url = ttk.Entry(self.local_infer, width=50)
        self.recognition_api_url.insert(0, configure_settings['local']['rec'])
        self.recognition_api_url.place(x=150, y=65)

        tk.Label(self.local_infer,
                 text="格式化说明：\n"
                      "     1. {year}表当前年份"
                      "\t 2. {ip}表当前设备IP", justify=tk.LEFT, anchor=tk.W, fg="green").place(x=5, y=95)

        self.local_infer.place(x=5, y=160)

        tk.Label(self.intelligence_frame, text="文本转语音 (TTS): ").place(x=5, y=320)
        self.tts_value = tk.StringVar(self)
        self.tts_value.set(configure['settings']['tts'])
        self.tts_cloud = ttk.Radiobutton(self.intelligence_frame, text="云端 Cloud",
                                         variable=self.tts_value, value="cloud")
        self.tts_cloud.place(x=200, y=320)

        self.tts_local = ttk.Radiobutton(self.intelligence_frame, text="本地 Local",
                                         variable=self.tts_value, value="local")
        self.tts_local.place(x=300, y=320)

        tk.Label(self.intelligence_frame, text="文本输出 (Text)：").place(x=5, y=350)
        self.text_value = tk.StringVar(self)
        self.text_value.set(configure['settings']['text'])
        self.text_cloud = ttk.Radiobutton(self.intelligence_frame, text="云端 Cloud",
                                          variable=self.text_value, value="cloud")
        self.text_cloud.place(x=200, y=350)

        self.text_local = ttk.Radiobutton(self.intelligence_frame, text="本地 Local",
                                          variable=self.text_value, value="local")
        self.text_local.place(x=300, y=350)

        tk.Label(self.intelligence_frame, text="语音识别 (Recognition)").place(x=5, y=380)
        self.rec_value = tk.StringVar(self)
        self.rec_value.set(configure['settings']['rec'])
        self.rec_cloud = ttk.Radiobutton(self.intelligence_frame, text="云端 Cloud",
                                         variable=self.rec_value, value="cloud")
        self.rec_cloud.place(x=200, y=380)

        self.rec_local = ttk.Radiobutton(self.intelligence_frame, text="本地 Local",
                                         variable=self.rec_value, value="local")
        self.rec_local.place(x=300, y=380)
        ttk.Button(self.local_infer, text="保存设置 Save Settings", command=self.save_settings).place(x=430, y=100)

        # self.note.add(self.animation_frame, text="动画绑定 Animation Bind")
        # tk.Label(self.animation_frame, text="敬请期待 Coming Soon", font=("微软雅黑", 30)).pack()

        self.note.add(self.character_frame, text="角色设定 Character Sets")

        self.sets_tree = ttk.Treeview(self.character_frame,
                                      columns=("Character", "Role", "Prompt"), show="headings",
                                      selectmode="browse")
        self.sets_tree.heading("Character", text="角色 Characater", anchor='center')
        self.sets_tree.column("Character", width=70, anchor='center')
        self.sets_tree.heading("Role", text="权限 Role")
        self.sets_tree.column("Role", width=40, anchor='center')
        self.sets_tree.heading("Prompt", text="描述 Prompt")
        self.sets_tree.column("Prompt", width=390)
        self.sets_tree.bind("<Double-1>", self.on_double_click)
        self.sets_tree.place(x=5, y=5, w=590, h=300)
        self.add_one_prompt = ttk.Button(
            self.character_frame, text="添加词条 Add Prompt", command=lambda: self.change_prompt("add"))
        self.add_one_prompt.place(x=5, y=310)
        self.remove_one_prompt = ttk.Button(
            self.character_frame, text="删除词条 Remove Prompt", command=lambda: self.change_prompt("remove"))
        self.remove_one_prompt.place(x=220, y=310)
        self.refresh_prompts_button = ttk.Button(
            self.character_frame, text="刷新词条 Refresh Prompts", command=lambda: self.refresh_prompt())
        self.refresh_prompts_button.place(x=435, y=310)

        self.note.add(self.about_frame, text="关于 About")
        tk.Label(self.about_frame, text="AI 桌宠相关说明 AI Desktop Pet explanation", font=('微软雅黑', 20)).pack()

        self.use_open_sources = tk.LabelFrame(self.about_frame, text="引用开源库 Quote Open Sources", width=590, height=100)
        self.quote_live2d_py = tk.Label(self.use_open_sources, text='Live2D-Py(MIT)', fg="blue", font=('微软雅黑', 13))
        self.quote_live2d_py.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/Arkueid/live2d-py.git"))
        self.quote_live2d_py.place(x=5, y=0)
        self.quote_pyqt5 = tk.Label(self.use_open_sources, text='PyQt5(LGPL v3.0)', fg="blue", font=('微软雅黑', 13))
        self.quote_pyqt5.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/PyQt5/PyQt.git"))
        self.quote_pyqt5.place(x=180, y=0)
        self.quote_opengl = tk.Label(self.use_open_sources, text='OpenGL(Apache 2.0)', fg="blue", font=('微软雅黑', 13))
        self.quote_opengl.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/McNopper/OpenGL.git"))
        self.quote_opengl.place(x=365, y=0)
        self.quote_python = tk.Label(self.use_open_sources, text='Python(PSF)', fg="blue", font=('微软雅黑', 13))
        self.quote_python.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/python/cpython.git"))
        self.quote_python.place(x=5, y=30)
        self.quote_ffmpeg = tk.Label(self.use_open_sources, text='FFmpeg(LGPL v2.1+)', fg="blue", font=('微软雅黑', 13))
        self.quote_ffmpeg.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/FFmpeg/FFmpeg.git"))
        self.quote_ffmpeg.place(x=180, y=30)
        self.quote_self = tk.Label(self.use_open_sources, text='AI Desktop Pet(LGPL v3.0)', fg="blue", font=('微软雅黑', 13))
        self.quote_self.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/grass-tech/aidesktoppet.git"))
        self.quote_self.place(x=365, y=30)
        self.use_open_sources.place(x=5, y=50)

        self.refresh_prompt()

        self.refresh_gui()

        self.note.pack(fill=tk.BOTH, expand=True)

    def refresh_gui(self):
        self.globe_mouse_penetration_value.set(configure['settings']['penetration']['enable'])
        self.penetration_start_value.set(configure['settings']['penetration']['start'])
        self.after(100, self.refresh_gui)

    def refresh_prompt(self):
        self.sets_tree.delete(*self.sets_tree.get_children())
        if configure['default'] == "tongyi":
            return
        if not os.path.exists(f"./intelligence/prompts/{configure['default']}.json"):
            with open(f"./intelligence/prompts/{configure['default']}.json", "w", encoding="utf-8") as lf:
                json.dump({}, lf, ensure_ascii=False, indent=3)
                lf.close()
        with open(f"./intelligence/prompts/{configure['default']}.json", "r", encoding="utf-8") as df:
            for role, content in json.load(df).items():
                self.sets_tree.insert("", "end", values=(configure['default'], role, content))
            f.close()

    def change_prompt(self, run_type: typing.Literal['add', 'remove']):
        if configure['default'] == "tongyi":
            return
        if run_type == "add":
            self.sets_tree.insert("", "end", values=(f"{configure['default']}", "Role", "Content"))
        else:
            self.sets_tree.delete(self.sets_tree.selection()[0])
        be_updated_prompts = {}
        for child_id in self.sets_tree.get_children():
            prompts = self.sets_tree.item(child_id)['values']
            be_updated_prompts.update({prompts[1]: prompts[2]})
        with open(f"./intelligence/prompts/{configure['default']}.json", "w", encoding="utf-8") as sf:
            json.dump(be_updated_prompts, sf, ensure_ascii=False, indent=4)
            sf.close()
        if run_type == "remove":
            if not be_updated_prompts:
                os.remove(f"./intelligence/prompts/{configure['default']}.json")

    def on_double_click(self, event):
        selected_item = self.sets_tree.selection()[0]
        column = self.sets_tree.identify_column(event.x)
        col_index = int(column.replace('#', '')) - 1

        entry_edit = ScrolledText(self, width=15, bg="black", fg='#00FF00')

        def set_entry_position():
            return self.sets_tree.bbox(selected_item, column)

        bbox = set_entry_position()
        entry_edit.place(x=bbox[0] + 5, y=bbox[1] + 30, w=bbox[2], h=bbox[3] + 20)

        entry_edit.insert(1.0, self.sets_tree.item(selected_item)['values'][col_index])
        entry_edit.focus()

        def save_edit():
            self.sets_tree.item(
                selected_item,
                values=list(
                    self.sets_tree.item(selected_item)['values'])[:col_index] + [
                    entry_edit.get(1.0, tk.END).replace("\n", "")
                ] + list(
                    self.sets_tree.item(selected_item)['values'])[col_index + 1:])
            entry_edit.place_forget()
            be_updated_prompts = {}
            for child_id in self.sets_tree.get_children():
                prompts = self.sets_tree.item(child_id)['values']
                be_updated_prompts.update({prompts[0]: {prompts[1]: prompts[2]}})
            for character, prompt in be_updated_prompts.items():
                with open(f"./intelligence/prompts/{character}.json", "w", encoding="utf-8") as df:
                    json.dump(prompt, df, indent=3, ensure_ascii=False)
                    df.close()

        entry_edit.bind("<FocusOut>", lambda e: save_edit())
        entry_edit.bind("<Return>", lambda e: save_edit())

    def change_character(self, character):
        configure['default'] = character
        configure['name'] = self.pet_nickname_entry.get()
        configure['voice_model'] = self.voice_model_lists.get()

        intelligence.text.reload_memories(character)

        with open("./resources/configure.json", "w", encoding="utf-8") as sf:
            json.dump(configure, sf, indent=3, ensure_ascii=False)
            sf.close()

    def change_refer_text(self, event):
        refer_text = Client.command(
            {"get_refer_text": self.voice_model_lists.get()})[self.voice_model_lists.get()]
        self.voice_text_entry.delete(0, tk.END)
        self.voice_text_entry.insert(0, refer_text)
        configure['voice_model'] = self.voice_model_lists.get()

        with open("./resources/configure.json", "w", encoding="utf-8") as sf:
            json.dump(configure, sf, indent=3, ensure_ascii=False)
            sf.close()

    def play_refer_audio(self):
        if self.tts_value.get() == "local":
            if not intelligence.VoiceSwitch:
                return
            lang, t = self.voice_text_entry.get().split(":")
            intelligence.voice_change(self.voice_model_lists.get(), MODULE_INFO)
            audio_bytes = intelligence.gsv_voice_generator(t, lang, MODULE_INFO, self.voice_model_lists.get())
        else:
            audio_bytes, duration = intelligence.ali_voice_generator(self.voice_text_entry.get())

        with wave.open(io.BytesIO(audio_bytes), 'rb') as wf:
            p = pyaudio.PyAudio()
            stream = p.open(format=p.get_format_from_width(wf.getsampwidth()), channels=wf.getnchannels(),
                            rate=wf.getframerate(), output=True)
            data = wf.readframes(1024)
            while data:
                stream.write(data)
                data = wf.readframes(1024)
            stream.stop_stream()
            stream.close()
            p.terminate()

    def save_settings(self):
        configure['settings']['tts'] = self.tts_value.get()
        configure['settings']['text'] = self.text_value.get()
        configure['settings']['rec'] = self.rec_value.get()
        configure['settings']['local']['qwen'] = self.qwen_api_url.get()
        configure['settings']['local']['gsv'] = self.gsv_api_url.get()
        configure['settings']['local']['rec'] = self.recognition_api_url.get()
        configure['settings']['cloud']['aliyun'] = self.aliyun_apikey_entry.get()
        configure['settings']['cloud']['xunfei']['id'] = self.xunfei_apiid_entry.get()
        configure['settings']['cloud']['xunfei']['key'] = self.xunfei_apikey_entry.get()
        configure['settings']['cloud']['xunfei']['secret'] = self.xunfei_apisecret_entry.get()

        with open("./resources/configure.json", "w", encoding="utf-8") as sf:
            json.dump(configure, sf, indent=3, ensure_ascii=False)
            sf.close()

    def change_translate(self):
        configure['settings']['translate'] = \
            (f"{re.sub(r'[\u4e00-\u9fa5]+[\s+]', '', self.translation_class.get()).lower()}."
             f"{re.sub(r'[\u4e00-\u9fa5]+[\s+]', '', self.translation_tool.get()).lower()}")
        with open("./resources/configure.json", "w", encoding="utf-8") as cf:
            json.dump(configure, cf, ensure_ascii=False, indent=3)
            cf.close()

    def change_translation_tool(self, event):
        if self.translation_class.get() == "爬虫 Spider":
            self.translation_tool.configure(values=["必应 Bing"])
        elif self.translation_class.get() == "人工智能 AI":
            self.translation_tool.configure(values=["通义千问 Tongyi"])
        self.translation_tool.current(0)
        self.change_translate()

    def change_configure(self, value, relative):
        temp_dict = configure

        for key in relative.split(".")[:-1]:
            if key not in temp_dict:
                temp_dict[key] = {}
            temp_dict = temp_dict[key]

        if relative.split("."):
            if "penetration" in relative and "start" in relative:
                temp_dict["start"] = self.penetration_start_value.get()
            last_key = relative.split(".")[-1]
            temp_dict[last_key] = value

        with open("./resources/configure.json", "w", encoding="utf-8") as cf:
            json.dump(configure, cf, ensure_ascii=False, indent=3)
            cf.close()

    def io_configure(self, value: str, relative=None, behave: object = int):
        if "{" in value and "}" in value:
            temp_dict = configure

            for key in relative.split(".")[:-1]:
                if key not in temp_dict:
                    temp_dict[key] = {}
                temp_dict = temp_dict[key]

            if relative.split("."):
                last_key = relative.split(".")[-1]
                if temp_dict[last_key]:
                    if value == "{adult}":
                        self.adult_lists.configure(state=tk.DISABLED)
                    temp_dict[last_key] = 0 if behave == int else False
                else:
                    if value == "{adult}":
                        self.adult_lists.configure(state="readonly")
                    temp_dict[last_key] = 1 if behave == int else True
        else:
            if value not in configure['settings']['disable']:
                configure_settings['disable'].append(value)
                if relative is not None:
                    relative()
            else:
                configure_settings['disable'].remove(value)
                if relative is not None:
                    relative()

        with open("./resources/configure.json", "w", encoding="utf-8") as cf:
            json.dump(configure, cf, ensure_ascii=False, indent=3)
            cf.close()


# 主程序
class DesktopTop(QOpenGLWidget):
    def __init__(self):
        super().__init__()
        # 窗口大小
        width = 400
        height = 400
        # 设置属性 Set Attribute
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        # self.setWindowOpacity(0.4)
        self.setMouseTracking(True)
        # 调整大小 Set Resize
        self.resize(width, height)

        # 基础变量和开关 Variables and Switches
        self.speaking_lists: list[bool] = []
        self.maximum_param_counter = self.turn_count = self.among = 0
        self.click_in_area = self.click_x = self.click_y = -1
        self.is_penetration = self.has_played_animation = self.is_playing_animation = self.is_movement = False
        self.stop_playing_animation: list[bool | str] = [False, ""]
        self.enter_position = self.drag_position = None
        self.random_cancel_penetration = self.resources_image = self.direction = self.last_pos = None
        self.pet_model: live2d.LAppModel | None = None
        self.param_dict: dict = {}

        # 屏幕中心坐标 Center of the screen
        self.screen_geometry = QApplication.desktop().availableGeometry()
        x = (self.screen_geometry.width() - self.width()) // 2
        y = self.screen_geometry.height() - self.height()
        self.move(x, y + 15)  # 15是距离任务栏的距离 15 is distance from the taskbar

        self.recognize_thread = RecognitionThread(self)
        self.recognize_thread.result.connect(self.recognition_success)

        # 界面构建 GUI build
        # 对话输入框 Conversation input box
        self.conversation_entry = QTextEdit(self)
        self.conversation_entry.installEventFilter(self)
        self.conversation_entry.setPlaceholderText(f"{configure['name']}等待您的聊天……")
        self.conversation_entry.setGeometry(QRect((width - 350) // 2, height - 75, 200, 75))
        # 发送聊天按钮 Send chat button
        self.conversation_button = QPushButton(self)
        self.conversation_button.setText("聊天(Shift + Enter)")
        self.conversation_button.setGeometry(QRect((width - 350) // 2 + 200, height - 75, 150, 25))
        # 清除记忆的按钮 Clear memories button
        self.clear_memories_button = QPushButton(self)
        self.clear_memories_button.setText("清除记忆(Alt + C)")
        self.clear_memories_button.setGeometry(QRect((width - 350) // 2 + 200, height - 50, 150, 25))
        # 媒体按钮 Media button
        self.media_button = QPushButton(self)
        self.media_button.setText("截屏(Alt + S)")
        self.media_button.setGeometry(QRect((width - 350) // 2 + 200, height - 25, 150, 25))
        # 聊天框 Chat box
        self.chat_box = QTextEdit(self)
        self.chat_box.setReadOnly(True)
        self.chat_box.setFont(QFont("微软雅黑", 11))
        self.chat_box.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.chat_box.setGeometry(QRect((width - 350) // 2, height - 175, 350, 100))
        # 设置样式 Set style
        self.conversation_entry.setStyleSheet("background-color: rgba(255, 255, 255, 150);")
        self.conversation_button.setStyleSheet("background-color: rgba(255, 255, 255, 150);")
        self.media_button.setStyleSheet("background-color: rgba(255, 255, 255, 150);")
        self.clear_memories_button.setStyleSheet("background-color: rgba(255, 255, 255, 150);")
        self.chat_box.setStyleSheet("background-color: rgba(255, 255, 255, 180); border: 1px solid black;")

        # 绑定函数 Bind functions
        self.conversation_button.clicked.connect(lambda checked: self.have_conversation(None))
        self.media_button.clicked.connect(self.capture_screen)
        self.clear_memories_button.clicked.connect(self.clear_memories)
        # 设置不可见 Set non-visible
        self.conversation_entry.setVisible(False)
        self.conversation_button.setVisible(False)
        self.media_button.setVisible(False)
        self.clear_memories_button.setVisible(False)
        self.chat_box.setVisible(False)

        self.is_transparent_raise = False

        # 定时器
        self.look_timer = QTimer(self)
        self.look_timer.timeout.connect(self.look_for_me)
        if "media" not in configure['settings']['disable']:
            self.look_timer.start(random.randint(
                    configure['settings']['understand']['min'] // 2,
                    configure['settings']['understand']['max'] // 2) * 1000)

        # 桌宠预备 Pet Preparation
        SpeakThread(
            self,
            f"./resources/voice/{configure_default}/welcome/{random.choice(configure_voices['welcome'])}"
        ).start()

        self.show()

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
            QMessageBox.warning(
                self,
                "警告 Warning",
                "无法开启透明部分鼠标穿透\n请将此错误报告给作者 \n"
                f"Failed to set window transparent for mouse events\n"
                f"Please report this error to the author\n\n"
                f"=====================================\n"
                f"错误信息 Error information： \n{type(e).__name__}: {e}\n"
                f"=====================================\n\n"
                f"你将不能点击透明部分的区域！\n"
                f"You will not be able to click on the transparent area!\n")

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
        if intelligence.MediaUnderstandSwitch:
            image_bytes = runtime.capture()
            RFST = MediaUnderstandThread(self, image_bytes)
            RFST.result.connect(lambda text: self.conversation_display(text, True))
            RFST.start()
            if "media" not in configure['settings']['disable']:
                self.look_timer.start(random.randint(
                    configure['settings']['understand']['min'],
                    configure['settings']['understand']['max']) * 1000)

    def capture_screen(self):
        if "media" in configure['settings']['disable']:
            return
        self.conversation_entry.setText(str(self.conversation_entry.toPlainText()) + "$[图片]$")
        self.resources_image = runtime.capture()

    # 语音识别 Recognition
    def recognize(self):
        if "rec" in configure['settings']['disable']:
            return
        if self.recognize_thread.isRunning():
            self.recognize_thread.wait()
        self.recognize_thread.start()

    def recognition_success(self, result: list[dict]):
        speech_rec.statued()

        chars = ""
        for data in result:
            for w in data['cw']:
                if str(w['w']).strip():
                    symbol_pattern = r'^[!"#$%&\'()*+,\-./:;<=>?@[\\\]^_`{|}~]|[\u3000-\u303F\uFF00-\uFFEF]'
                    if re.match(symbol_pattern, w['w'][0]):
                        chars += w['w'][1:]
                    else:
                        chars += w['w']
        if configure['name'] in chars or configure_default in chars:
            # 临时对话不启用一些界面 Temporary dialog does not enable some interfaces
            self.conversation_entry.setVisible(False)
            self.conversation_button.setVisible(False)
            self.media_button.setVisible(False)
            self.clear_memories_button.setVisible(False)
            self.chat_box.setVisible(True)

            self.have_conversation(chars, True)
        logger(f"子应用 - 语音识别 语音呼唤成功\n"
               f"Sub-Application - Voice Recognition Success: {chars}\n"
               f"  Message: {chars}\n\n"
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
        if self.conversation_entry.isVisible():
            self.conversation_entry.setVisible(False)
            self.conversation_button.setVisible(False)
            self.clear_memories_button.setVisible(False)
            self.media_button.setVisible(False)
            self.chat_box.setVisible(False)
        else:
            self.conversation_entry.setVisible(True)
            self.conversation_button.setVisible(True)
            self.clear_memories_button.setVisible(True)
            self.media_button.setVisible(True)
            self.chat_box.setVisible(True)

    def conversation_display(self, text: tuple, temp_action: bool = False):
        def __exec(information: list):
            """
            :param information: 0 -> wav_bytes 1 -> duration
            """
            def __closure():
                # 闭包函数
                nonlocal text_begin, is_emotion
                flot_timer.stop()
                if isinstance(text_begin, int):
                    if text_begin < len(common_text) - 1:
                        text_begin += 1
                        self.chat_box.setVisible(True)
                        self.chat_box.setText(str(self.chat_box.toPlainText()) + common_text[text_begin:text_begin + 1])
                        self.chat_box.moveCursor(self.chat_box.textCursor().End)
                        # 处理括号之间的表情等内容 Process the contents between brackets
                        if common_text[text_begin:text_begin + 1] in (")", "]", "）", "】") and is_emotion:
                            is_emotion = False
                        if common_text[text_begin:text_begin + 1] in ("(", "[", "（", "【") or is_emotion:
                            is_emotion = True
                            flot_timer.start(35)
                        else:
                            is_emotion = False
                            flot_timer.start(125)
                    else:
                        text_begin = "END"
                        flot_timer.start(1000 + (
                            max(0, int(information[1] - (time.time() - start_time) * 1000))
                            if intelligence.VoiceSwitch else
                            100
                            )
                        )

                else:
                    self.chat_box.clear()
                    self.chat_box.setHtml(markdown_text)
                    self.chat_box.moveCursor(self.chat_box.textCursor().End)
                    if text_begin == "Endless":
                        self.chat_box.setVisible(False)
                        self.conversation_entry.setVisible(False)
                        self.conversation_button.setVisible(False)
                        self.clear_memories_button.setVisible(False)
                        self.media_button.setVisible(False)
                        self.chat_box.clear()
                        text_begin = "END"
                    elif not temp_action:
                        self.conversation_entry.setVisible(True)
                        self.conversation_button.setVisible(True)
                        self.media_button.setVisible(True)
                        self.clear_memories_button.setVisible(True)
                    elif temp_action:
                        text_begin = "Endless"
                        flot_timer.start(3000)

            self.chat_box.clear()
            start_time = time.time()
            text_begin = -1
            is_emotion = False
            if intelligence.VoiceSwitch and 'tts' not in configure['settings']['disable']:
                SpeakThread(self, information[0]).start()

            flot_timer = QTimer(self)
            flot_timer.timeout.connect(__closure)
            flot_timer.start(5)

        common_text = text[0]
        markdown_text = text[1]

        if intelligence.VoiceSwitch and 'tts' not in configure['settings']['disable']:
            VGT = VoiceGenerateThread(self, common_text)
            VGT.result.connect(__exec)
            VGT.start()
        else:
            __exec([None, 0])

    def have_conversation(self, text: str | None = None, temp_action: bool = False):
        """进行聊天 Send conversation"""
        chat_message = str(self.conversation_entry.toPlainText()) if text is None else text
        if intelligence is None:
            return
        if not chat_message.strip():
            return
        self.conversation_button.setVisible(False)
        self.media_button.setVisible(False)
        self.clear_memories_button.setVisible(False)
        self.chat_box.setText(f"{configure['name']}思考中...\n{configure['name']} is thinking...")

        if self.resources_image is None and "$[图片]$" not in self.conversation_entry.toPlainText():
            text_generate = TextGenerateThread(
                self, chat_message,
                True if "online" not in configure['settings']['disable'] else False,
            )
        else:
            text_generate = MediaUnderstandThread(
                self, self.resources_image, chat_message.replace("$[图片]$", ""),
                True if "online" not in configure['settings']['disable'] else False,
            )
            self.resources_image = None
        text_generate.start()
        text_generate.result.connect(lambda texts: self.conversation_display(texts, temp_action))

    def clear_memories(self):
        """清除记忆 Clear memories"""
        if intelligence is None:
            return
        intelligence.text.clear_memories()
        self.chat_box.clear()

    # 事件 Events
    # 右键菜单事件 Right-click menu events
    def contextMenuEvent(self, event):
        def io_configure(value: str, relative=None, behave: object = int):
            if "{" in value and "}" in value:
                temp_dict = configure

                for key in relative.split(".")[:-1]:
                    if key not in temp_dict:
                        temp_dict[key] = {}
                    temp_dict = temp_dict[key]

                if relative.split("."):
                    last_key = relative.split(".")[-1]
                    if temp_dict[last_key]:
                        temp_dict[last_key] = 0 if behave == int else False
                    else:
                        temp_dict[last_key] = 1 if behave == int else True
            else:
                if value not in configure['settings']['disable']:
                    configure_settings['disable'].append(value)
                    if relative is not None:
                        relative()
                else:
                    configure_settings['disable'].remove(value)
                    if relative is not None:
                        relative()

            with open("./resources/configure.json", "w", encoding="utf-8") as cf:
                json.dump(configure, cf, ensure_ascii=False, indent=3)
                cf.close()

        def change_configure(relative, value):
            temp_dict = configure

            for key in relative.split(".")[:-1]:
                if key not in temp_dict:
                    temp_dict[key] = {}
                temp_dict = temp_dict[key]

            if relative.split("."):
                last_key = relative.split(".")[-1]
                temp_dict[last_key] = value

            with open("./resources/configure.json", "w", encoding="utf-8") as cf:
                json.dump(configure, cf, ensure_ascii=False, indent=3)
                cf.close()

        content_menu = QMenu(self)

        settings_action = QAction("设置 Settings", self)
        settings_action.triggered.connect(lambda: Setting().mainloop())
        content_menu.addAction(settings_action)

        content_menu.addSeparator()

        conversation_action = QAction("进行对话 Have Conversations", self)
        conversation_action.triggered.connect(self.open_close_conversation)
        content_menu.addAction(conversation_action)

        content_menu.addSeparator()

        # IO控制 IO control
        # 录屏兼容模式 Capture compatibility mode
        compatibility_action = QAction(
            f"{'√' if configure['settings']['compatibility'] else ''} 录屏兼容 Capture Compatible", self)
        compatibility_action.triggered.connect(lambda: io_configure(
            "{compatibility}", "settings.compatibility", bool))
        content_menu.addAction(compatibility_action)

        globe_mouse_penetration_action = QAction(
            f"{'√' if 'gmpene' not in configure['settings']['disable'] else ''} 全局鼠标穿透 Global Mouse Penetration", self)
        globe_mouse_penetration_action.triggered.connect(lambda: io_configure("gmpene"))
        content_menu.addAction(globe_mouse_penetration_action)

        # 语音识别 Recognition
        recognition_action = QAction(
            f"{'√' if 'rec' not in configure['settings']['disable'] else ''} 语音识别 Recognition", self)
        recognition_action.triggered.connect(lambda: io_configure("rec"))
        content_menu.addAction(recognition_action)

        # AI语音 AI voice
        ai_voice = QAction(f"{'√' if 'tts' not in configure['settings']['disable'] else ''} AI语音 AI Voice", self)
        ai_voice.triggered.connect(lambda: io_configure("tts"))
        content_menu.addAction(ai_voice)

        # 联网搜索 Online search
        online_search = QAction(
            f"{'√' if 'online' not in configure['settings']['disable'] else ''} 联网搜索 Online Search", self)
        online_search.triggered.connect(lambda: io_configure("online"))
        content_menu.addAction(online_search)

        # 翻译 Translate
        translate = QAction(f"{'√' if 'trans' not in configure['settings']['disable'] else ''} 翻译 Translate",
                            self)
        translate.triggered.connect(lambda: io_configure("trans"))
        content_menu.addAction(translate)

        # 分割线
        content_menu.addSeparator()

        # 选择菜单 Switch menu
        # 切换角色菜单 Switch character menu
        change_character_menu = QMenu("切换角色 Change Character", self)
        for index, character in enumerate(os.listdir("./resources/model")):
            character_action = QAction(
                f"{'√' if character == configure_default else ' '} {character}({configure['name']})", self)
            character_action.triggered.connect(lambda checked, c=character: change_configure("default", c))
            change_character_menu.addAction(character_action)

        content_menu.addMenu(change_character_menu)

        # 自动翻译菜单 Auto translation menu
        translation_menu = QMenu("自动翻译 Auto Trans", self)
        translation_tool_menu = QMenu("翻译工具 Trans Tools", self)

        # 爬虫翻译 Spider Translate
        translation_tool_spider_menu = QMenu(
            f"{'√' if 'spider' in configure['settings']['translate'] else ' '} 爬虫 Spider", self)
        translation_tool_spider_bing = QAction(
            f"{'√' if 'bing' in configure['settings']['translate'] else ' '} 必应 Bing", self)
        translation_tool_spider_menu.addAction(translation_tool_spider_bing)
        translation_tool_spider_bing.triggered.connect(lambda: change_configure("settings.translate", "spider.bing"))
        translation_tool_menu.addMenu(translation_tool_spider_menu)

        translation_menu.addMenu(translation_tool_menu)
        content_menu.addMenu(translation_menu)

        # AI翻译 AI Translate
        translation_tool_ai_menu = QMenu(
            f"{'√' if 'ai' in configure['settings']['translate'] else ' '} 人工智能 AI", self)
        translation_tool_ai_qwen = QAction(
            f"{'√' if 'tongyi' in configure['settings']['translate'] else ' '} 通义 Tongyi", self)
        translation_tool_ai_menu.addAction(translation_tool_ai_qwen)
        translation_tool_ai_qwen.triggered.connect(lambda: change_configure("settings.translate", "ai.tongyi"))

        translation_tool_menu.addMenu(translation_tool_ai_menu)
        content_menu.addMenu(translation_menu)

        # 语音模型切换菜单 Voice model switch menu
        voice_model_menu = QMenu("语音模型 Voice Model", self)
        for model in MODULE_INFO.keys():
            model_action = QAction(f"{'√' if model == configure['voice_model'] else ' '} {model}", self)
            model_action.triggered.connect(lambda checked, m=model: change_configure("voice_model", m))
            voice_model_menu.addAction(model_action)
        if "tts" not in configure['settings']['disable']:
            content_menu.addMenu(voice_model_menu)

        # 成人模式菜单 Adult content menu
        adult_content_menu = QMenu("成人模式 Adult Content", self)
        for level in range(configure_adults['AdultLevelMinimum'],
                           configure_adults['AdultLevelMaximum'] + 1):
            adult_content_action = QAction(
                f"{'√' if configure['adult_level'] == level else ' '} 等级 Level {level} - "
                f"{configure_adults['AdultDescribe'][str(level)]}", self)
            adult_content_menu.addAction(adult_content_action)
            adult_content_action.triggered.connect(lambda checked, lev=level: change_configure("adult_level", lev))
        if configure['adult_level']:
            content_menu.addMenu(adult_content_menu)

        content_menu.exec_(self.mapToGlobal(event.pos()))

    # 过滤器事件 Filter events
    def eventFilter(self, obj, event):
        if obj is self.conversation_entry and event.type() == event.KeyPress:
            # 是否按下 Shift + Enter When Shift + Enter is pressed
            if event.key() in (Qt.Key_Enter, Qt.Key_Return):
                if event.modifiers() & Qt.ShiftModifier and self.conversation_button.isVisible():
                    self.conversation_button.click()
                    return True
                else:
                    return False
        return super().eventFilter(obj, event)

    # 定时器事件 Timer events
    def timerEvent(self, a0: QTimerEvent | None) -> None:
        def save_change():
            self.is_penetration = False
            configure['settings']['penetration']['start'] = "next"
            configure['settings']['penetration']['enable'] = False
            with open("./resources/configure.json", "w", encoding="utf-8") as sf:
                json.dump(configure, sf, indent=3, ensure_ascii=False)
                sf.close()
            self.set_mouse_transparent(False)

        if not self.isVisible():
            return
        # 判断兼容性 Compatibility
        if configure_settings["compatibility"] is False and self.among == 100:
            # 判断顺序是否低于任务栏 Check whether the order is below the taskbar
            hwnd = self.winId().__int__()
            taskbar_hwnd = win32gui.FindWindow("Shell_TrayWnd", None)
            if win32gui.GetWindowRect(hwnd)[1] < win32gui.GetWindowRect(taskbar_hwnd)[1]:
                self.set_window_below_taskbar()

        # 检查识别器 Check the recognizer
        if not self.recognize_thread.isRunning() and "rec" not in configure['settings']['disable']:
            self.recognize()
        elif speech_rec is not None and "rec" in configure['settings']['disable']:
            speech_rec.closed()

        # 释放资源 Release resources
        # 检查说话列表的可用性 Check the availability of the speaking list
        if len(self.speaking_lists) == self.speaking_lists.count(False) and not self.speaking_lists:
            # 清除缓存 Clear empty cache
            self.speaking_lists.clear()

        # 自动眨眼 Auto Blink
        if not self.has_played_animation:
            x, y = QCursor.pos().x() - self.x(), QCursor.pos().y() - self.y()
            self.pet_model.Update()
            self.pet_model.Drag(x, y)
            self.pet_model.Draw()

        # 定时器检查 Timer checker
        if "media" in configure['settings']['disable']:
            if self.look_timer.isActive():
                self.look_timer.stop()
        else:
            if not self.look_timer.isActive():
                self.look_timer.start(random.randint(
                    configure['settings']['understand']['min'],
                    configure['settings']['understand']['max']) * 1000)

        local_x, local_y = QCursor.pos().x() - self.x(), QCursor.pos().y() - self.y()
        # 检查是否开启全局鼠标穿透 Check whether global mouse transparency is enabled
        if configure['settings']['penetration']['enable']:
            self.set_mouse_transparent(True)
            self.is_penetration = True
            # 如果start有以下几种情况，则取消全局鼠标穿透 if start has the following four situations, cancel global mouse transparency
            # 当空的时候取消 When it is empty, cancel global mouse transparency
            if configure['settings']['penetration']['start'].strip() == "" and self.among == 0:
                save_change()
            # 下次启动时取消全局鼠标穿透 if the start is next, cancel global mouse transparency
            elif configure['settings']['penetration']['start'] == "next" and self.among == 0:
                save_change()
            # 随机取消全局鼠标穿透 if the start is random, cancel global mouse transparency
            elif configure['settings']['penetration']['start'] == 'random':
                if self.random_cancel_penetration is not None:
                    if self.random_cancel_penetration < datetime.datetime.now():
                        save_change()
                else:
                    self.random_cancel_penetration = datetime.datetime.now() + datetime.timedelta(
                        minutes=random.randint(5, 30))
            # 鼠标左键或右键在顶部按下时取消全局鼠标穿透 if the start is left-top or right-top, cancel global mouse transparency
            elif configure['settings']['penetration']['start'] in ('left-top', 'right-top'):
                if not MouseListener.isListening:
                    MouseListener.start_listening()
                if configure['settings']['penetration']['start'] == "left-top":
                    pressed = MouseListener.is_left_button_pressed
                elif configure['settings']['penetration']['start'] == "right-top":
                    pressed = MouseListener.is_right_button_pressed
                else:
                    pressed = False
                if self.is_in_live2d_area(local_x, local_y) and pressed and \
                        80 > local_y > 0:
                    MouseListener.stop_listening()
                    save_change()
            # 鼠标左键或右键在底部按下时取消全局鼠标穿透 if the start is left-bottom or right-bottom, cancel global mouse transparency
            elif configure['settings']['penetration']['start'] in ('left-bottom', 'right-bottom'):
                if not MouseListener.isListening:
                    MouseListener.start_listening()
                if configure['settings']['penetration']['start'] == "left-bottom":
                    pressed = MouseListener.is_left_button_pressed
                elif configure['settings']['penetration']['start'] == "right-bottom":
                    pressed = MouseListener.is_right_button_pressed
                else:
                    pressed = False
                if not MouseListener.isListening:
                    MouseListener.start_listening()
                if self.is_in_live2d_area(local_x, local_y) and pressed and \
                        self.height() > local_y > self.height() - 80:
                    MouseListener.stop_listening()
                    save_change()
        else:
            save_change()

        if self.among == 0:
            self.pet_model.StartMotion("TapBody", 0, live2d.MotionPriority.FORCE,
                                       onFinishMotionHandler=lambda: print("end"))
        elif self.among > 100:
            self.among = 0
        self.among += 1

        # 检查点击区域 Check the click area
        if self.is_in_live2d_area(local_x, local_y) and not self.is_penetration:
            self.set_mouse_transparent(False)
            self.click_in_area = True
        elif not self.is_penetration:
            self.set_mouse_transparent(True)
            # 判断是否是在播放动画时 Check if the animation is being played
            if self.is_playing_animation:
                # 如果是耳朵 下垂的动画就执行反转动画 if it is the ears down animation, then reverse the animation
                if action_TouchHead['param'] in self.stop_playing_animation[1] and action_TouchHead['reverse']:
                    if "Forward" in self.stop_playing_animation[1]:
                        self.stop_playing_animation = [True, f"{action_TouchHead['param']}:Reverse"]
                        IterateAddParameterValue(self, action_TouchHead['param'],
                                                 -1, self.maximum_param_counter, 0, 1,
                                                 0.006).start()
                    else:
                        self.stop_playing_animation = [True, f"{action_TouchHead['param']}:Forward"]
                        IterateAddParameterValue(self, action_TouchHead['param'],
                                                 1, 0, self.maximum_param_counter, 1,
                                                 0.006).start()
                self.stop_playing_animation = [False, ""]
                self.is_playing_animation = False

            self.turn_count = 0
            self.click_in_area = False

        self.update()

    def is_in_live2d_area(self, click_x, click_y):
        """检查是否在模型内 Check whether the mouse is in the model"""
        h = self.height()
        alpha = GL.glReadPixels(click_x * 1.0, (h - click_y) * 1.0, 1, 1, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE)[3]
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
        def checker(x_min: int, x_max: int, y_min: int, y_max: int, turn_count: int) -> bool:
            """检查是否满足框内要求 Check whether the box is satisfied"""
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
                    new_pos = event.globalPos() - self.drag_position
                    new_pos.setY(max(self.screen_geometry.height() - self.height(), new_pos.y()))
                    self.move(new_pos)
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

            if self.click_in_area and not self.is_movement:
                # 摸头互动 Touch interaction
                if checker(129, 202, 0, 50, 4):
                    self.has_played_animation = self.is_playing_animation = True
                    self.click_in_area = False

                    # 播放正向动画 Play the forward animation
                    self.stop_playing_animation = [True, f"{action_TouchHead['param']}:Forward"]
                    self.maximum_param_counter = self.param_dict['EarDown']['max']
                    IterateAddParameterValue(self, f"{action_TouchHead['param']}",
                                             1, 0, self.maximum_param_counter, 1,
                                             0.0053).start()

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        def checker(x_min, x_max, y_min, y_max):
            """检查点击位置是否符合标准 Check whether the click position meets the standard"""
            return x_min <= click_x <= x_max and y_min <= click_y <= y_max

        click_x, click_y = event.globalPos().x() - self.x(), event.globalPos().y() - self.y()
        if event.button() == Qt.LeftButton and self.click_in_area:
            print("meet the requirements")
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

    # OpenGL 事件 OpenGL events
    def initializeGL(self):
        GL.glEnable(GL.GL_DEPTH_TEST)

        live2d.glewInit()
        self.pet_model = live2d.LAppModel()
        self.pet_model.LoadModelJson("./resources/model/vanilla/Vanilla.model3.json")
        for i in range(self.pet_model.GetParameterCount()):
            param = self.pet_model.GetParameter(i)
            self.param_dict.update({param.id: {"value": param.value, "max": param.max, "min": param.min}})
        AutoBlinkEye(self, self.param_dict).start()
        self.startTimer(int(1000 / 900))

    def resizeGL(self, width, height):
        self.pet_model.Resize(width, height)

    def paintGL(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        live2d.clearBuffer()
        # 加载模型 Load Model
        self.pet_model.Draw()


live2d.setLogEnable(False)
live2d.init()
MouseListener = MouseListener()
logger("桌宠初始化完成 Live2D初始化完成\n"
       "DesktopPet initialized successfully, Live2D initialized successfully.\n", logs.HISTORY_PATH)
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DesktopTop()
    sys.exit(app.exec_())
