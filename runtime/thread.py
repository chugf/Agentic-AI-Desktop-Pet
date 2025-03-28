import random
import traceback
import re
import wave
import pyaudio
import io

from . import file

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QOpenGLWidget


intelligence = None
runtime = None
logs = None


def reload_module(intelligence_module, runtime_module, logs_module):
    global intelligence, runtime, logs
    intelligence = intelligence_module
    runtime = runtime_module
    logs = logs_module


class RunPythonPlugin(QThread):
    error = pyqtSignal(str)

    def __init__(self, parent: QOpenGLWidget, codes, global_):
        super().__init__(parent)
        self.codes = codes
        self.global_ = global_

    def run(self):
        try:
            exec(self.codes, self.global_)
        except Exception:
            self.error.emit(f"{traceback.format_exc()}")


class SpeakThread(QThread):
    """说话线程 Speak Thread"""
    information = pyqtSignal(int)

    def __init__(self, parent: QOpenGLWidget, resource_data: bytes | str):
        super().__init__(parent)
        self.resource_data = resource_data
        self.parent().speaking_lists.append(True)
        self.current_speak_index = len(self.parent().speaking_lists) - 1

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

    def __init__(self, parent: QOpenGLWidget, configure: dict, speech_rec: callable):
        super().__init__(parent)
        self.speech_rec = speech_rec
        self.configure = configure

    def run(self):
        if self.configure['settings']['rec'] == "cloud":
            self.speech_rec = intelligence.recognition.XFRealTimeSpeechRecognizer(
                self.result.emit, self.parent().recognition_failure,
                self.parent().recognition_closure)
        else:
            self.speech_rec = intelligence.recognition.WhisperRealTimeSpeechRecognizer(
                self.result.emit, self.parent().recognition_failure,
                self.parent().recognition_closure,
                runtime.parse_local_url(self.configure['settings']['local']['rec']['url']))
        self.speech_rec.start_recognition()


class MediaUnderstandThread(QThread):
    result = pyqtSignal(str)

    def __init__(self, parent: QOpenGLWidget, configure: dict, image_path: str, texts: str | None = None,
                 is_search_online: bool = False):
        """根据媒体理解线程 Media Understand Thread"""
        super().__init__(parent)
        self.configure = configure
        self.image_path = image_path
        self.is_search_online = is_search_online
        self.texts = texts

    def run(self):
        if self.texts is None:
            self.texts = random.choice(
                ["你觉得我在干什么？", "你有什么想法呀？", "你觉得这个图片怎么样？", "请评价一下这图片"])
        try:
            answer = intelligence.text_generator(f"`{self.image_path}` \n{self.texts}",
                                                 self.configure['settings']['intelligence'], self.is_search_online,
                                                 self.result.emit)
        except Exception:
            file.logger(f"子应用 - 媒体文件理解 调用失败\n"
                        f"   Message: {traceback.format_exc()}", logs.HISTORY_PATH)
            self.result.emit(f"AI媒体文件理解 调用失败 AI Answer failed to call\n{traceback.format_exc()}")
            return
        file.logger("子应用 - AI图文理解 调用成功 Sub Application - AI Media Understand Call Success\n"
                    f"   Message: {answer}", logs.HISTORY_PATH)
        self.result.emit(f"None:{answer}")


class TextGenerateThread(QThread):
    """文本生成器线程 Text Generation Thread"""
    result = pyqtSignal(str)

    def __init__(self, parent: QOpenGLWidget, configure: dict, subscribe, text: str, is_search_online: bool = False):
        super().__init__(parent)
        self.configure = configure
        self.subscribe = subscribe
        self.text = text
        self.is_search_online = is_search_online

    def send(self, text: str, is_finished: bool):
        self.result.emit(text)
        for action_item in self.subscribe.actions.Operate().GetAIOutput():
            action_item(text, is_finished)

    def run(self):
        try:
            intelligence.ALI_API_KEY = self.configure["settings"]['cloud']['aliyun']
            answer = intelligence.text_generator(self.text, self.configure['settings']['intelligence'],
                                                 self.is_search_online, lambda text: self.send(text, False),
                                                 url=runtime.parse_local_url(
                                                     self.configure['settings']['local']['text']) if
                                                 self.configure['settings']['text']['way'] == "local" else None)
        except Exception:
            file.logger(f"子应用 - AI剧情问答 调用失败\n"
                        f"   Message: {traceback.format_exc()}", logs.HISTORY_PATH)
            self.result.emit(f"AI问答 调用失败 AI Answer failed to call\n{traceback.format_exc()}")
            return
        file.logger(f"子应用 - AI剧情问答 调用成功\n"
                    f"   Message: {answer}", logs.HISTORY_PATH)
        self.send(f"None:{answer}", True)


class VoiceGenerateThread(QThread):
    """AI 文字转语音 (GSV) AI text-to-speech (GSV) module"""
    result = pyqtSignal(bytes)
    error = pyqtSignal(bool)

    def __init__(self, parent: QOpenGLWidget, configure: dict, module_info: dict, text: str, language: str = "auto"):
        super().__init__(parent)
        self.text = text
        self.configure = configure
        self.module_info = module_info
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
        if self.configure['settings']['tts']['way'] == "local":
            if self.language not in ("zh", "en", "ja", "ko", "yue"):
                if self.configure['settings']['enable']['trans']:
                    if "spider" in self.configure["settings"]['translate']:
                        if "bing" in self.configure["settings"]['translate']:
                            text = intelligence.translate.machine_translate(text)
                            language = "ja"
                    elif "ai" in self.configure["settings"]['translate']:
                        if "tongyi" in self.configure["settings"]['translate']:
                            text = intelligence.translate.tongyi_translate(text)
                            language = "ja"
            else:
                language = self.language

            intelligence.voice.change_module(
                self.configure['voice_model'], self.module_info,
                runtime.parse_local_url(self.configure['settings']['local']['gsv']))
            wav_bytes = intelligence.voice.take_a_tts(
                text, language, self.configure['voice_model'],
                self.module_info, self.configure['settings']['tts']['top_k'],
                self.configure['settings']['tts']['top_p'], self.configure['settings']['tts']['temperature'],
                self.configure['settings']['tts']['speed'], self.configure['settings']['tts']['batch_size'],
                self.configure['settings']['tts']['batch_threshold'],
                parallel_infer=self.configure['settings']['tts']['parallel'],
                url=runtime.parse_local_url(self.configure['settings']['local']['gsv']))
        else:
            wav_bytes, _ = intelligence.voice.ali_tts(text)
            if wav_bytes is None:
                self.error.emit(False)
                return
        file.logger(f"子应用 - AI语音(GSV) 调用成功\n", logs.HISTORY_PATH)
        self.result.emit(wav_bytes)
