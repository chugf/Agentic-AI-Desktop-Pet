from ..customize import function

from .sub_local import text
from .sub_local import voice

from PyQt5.Qt import QRect
from PyQt5.QtWidgets import QWidget, QStackedWidget

from qfluentwidgets import BodyLabel, LineEdit, ComboBox, \
    Pivot


class IntelligenceLocale(QWidget):
    def __init__(self, languages, configure):
        super().__init__()
        self.languages = languages
        self.configure = configure
        self.setObjectName("IntelligenceLocal")

        # 文本输出自定义URL
        BodyLabel(self.languages[32], self).setGeometry(QRect(10, 42, 100, 35))
        self.input_text_url = LineEdit(self)
        self.input_text_url.setText(self.configure["settings"]['local']['text'])
        self.input_text_url.setGeometry(QRect(120, 42, 300, 35))
        self.input_text_url.textChanged.connect(
            lambda value: function.change_configure(value, "settings.local.text", self.configure))

        # 图像处理自定义URL
        BodyLabel(self.languages[134], self).setGeometry(QRect(10, 87, 100, 35))
        self.input_image_url = LineEdit(self)
        self.input_image_url.setText(self.configure["settings"]['local']['media'])
        self.input_image_url.setGeometry(QRect(120, 87, 300, 35))
        self.input_image_url.textChanged.connect(
            lambda value: function.change_configure(value, "settings.local.media", self.configure))

        # AI语音
        BodyLabel(self.languages[14], self).setGeometry(QRect(10, 132, 100, 35))
        self.input_voice_url = LineEdit(self)
        self.input_voice_url.setText(self.configure["settings"]['local']['gsv'])
        self.input_voice_url.setGeometry(QRect(120, 132, 300, 35))
        self.input_voice_url.textChanged.connect(
            lambda value: function.change_configure(value, "settings.local.gsv", self.configure))

        # 格式化说明
        BodyLabel(self.languages[86], self).setGeometry(QRect(430, 47, 250, 35))
        BodyLabel(self.languages[87], self).setGeometry(QRect(430, 82, 250, 35))
        BodyLabel(self.languages[88], self).setGeometry(QRect(430, 117, 250, 35))

        # 语音识别
        # # 语音识别工具
        BodyLabel(self.languages[13], self).setGeometry(QRect(10, 177, 100, 35))
        self.input_recognition_tool = ComboBox(self)
        self.input_recognition_tool.addItems(['Whisper'])
        self.input_recognition_tool.setGeometry(QRect(120, 177, 100, 35))
        self.input_recognition_tool.currentTextChanged.connect(
            lambda value: function.change_configure(value, "settings.local.rec.tool", self.configure))
        # # 语音识别URL
        self.input_recognition_url = LineEdit(self)
        self.input_recognition_url.setText(self.configure["settings"]['local']['rec']['url'])
        self.input_recognition_url.setGeometry(QRect(220, 177, 200, 35))
        self.input_recognition_url.textChanged.connect(
            lambda value: function.change_configure(value, "settings.local.rec.url", self.configure))

        # 自定义参数合成 Customize parameter synthesis
        self.pivot_parameter = Pivot(self)
        self.stacked_widget = QStackedWidget(self)

        self.text_parameter = text.TextParameter(self.configure, self)
        self.voice_parameter = voice.VoiceParameter(self.configure, self)

        self.addSubInterface(self.text_parameter, "TextParameter", self.languages[138])
        self.addSubInterface(self.voice_parameter, "VoiceParameter", self.languages[139])

        self.pivot_parameter.setGeometry(QRect(10, 222, 100, 35))
        self.stacked_widget.setGeometry(QRect(30, 267, 500, 300))

        self.stacked_widget.setCurrentWidget(self.text_parameter)
        self.pivot_parameter.setCurrentItem(self.text_parameter.objectName())
        self.pivot_parameter.currentItemChanged.connect(
            lambda k: self.stacked_widget.setCurrentWidget(self.findChild(QWidget, k)))

    def addSubInterface(self, widget: QWidget, objectName, text):
        widget.setObjectName(objectName)
        self.stacked_widget.addWidget(widget)
        self.pivot_parameter.addItem(routeKey=objectName, text=text)
