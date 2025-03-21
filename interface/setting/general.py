import os
import typing

from .customize import function, constants

from PyQt5.Qt import QRect, Qt
from PyQt5.QtWidgets import QFrame
from qfluentwidgets import ComboBox, LineEdit, PushButton, Slider, BodyLabel, InfoBar, InfoBarPosition


class General(QFrame):
    def __init__(self, languages, configure, module_info, param_dict, **kwargs):
        super().__init__()
        self.languages = languages
        self.configure = configure
        self.module_info = module_info
        self.param_dict = param_dict
        self.setObjectName("General")
        # 默认值 Default Value
        character_lists = os.listdir("./resources/model")
        character_lists.append("origin")
        # 语言选择 Language selector
        BodyLabel(self.languages[116], self).setGeometry(QRect(5, 5, 80, 35))
        self.select_language = ComboBox(self)
        self.select_language.addItems(os.listdir("./resources/languages"))
        self.select_language.setCurrentText(self.configure['settings']['language'])
        self.select_language.setGeometry(QRect(100, 5, 230, 35))
        self.select_language.currentTextChanged.connect(
            lambda value: function.change_configure(value, "settings.language", self.configure))
        # 宠物形象 Character Pet
        BodyLabel(self.languages[2], self).setGeometry(QRect(5, 45, 80, 35))
        self.select_character = ComboBox(self)
        self.select_character.addItems(character_lists)
        self.select_character.setCurrentText(self.configure['default'])
        self.select_character.setGeometry(QRect(100, 45, 230, 35))
        self.select_character.currentTextChanged.connect(
            lambda value: function.change_configure(value, "default", self.configure))
        # 宠物昵称 Pet Nickname
        self.input_pet_nickname = LineEdit(self)
        self.input_pet_nickname.setText(self.configure['name'])
        self.input_pet_nickname.setGeometry(QRect(340, 45, 230, 35))
        self.input_pet_nickname.setClearButtonEnabled(True)
        self.input_pet_nickname.textChanged.connect(
            lambda value: function.change_configure(
                value, "name", self.configure))
        # 翻译引擎 Translation Engine
        BodyLabel(self.languages[4], self).setGeometry(QRect(5, 85, 80, 35))
        self.select_translation_engine = ComboBox(self)
        self.select_translation_engine.addItems([self.languages[120], self.languages[121]])
        self.select_translation_engine.setGeometry(QRect(100, 85, 230, 35))
        # # 翻译工具 Translation Tool
        self.select_translation_tool = ComboBox(self)
        if (translate := self.configure['settings']['translate'].split('.'))[0] == "ai":
            self.select_translation_engine.setCurrentText(self.languages[121])
            self.select_translation_tool.addItems([self.languages[122]])
        elif translate[0] == "spider":
            self.select_translation_engine.setCurrentText(self.languages[120])
            self.select_translation_tool.addItems([self.languages[123]])
        self.select_translation_tool.setGeometry(QRect(340, 85, 230, 35))
        self.select_translation_engine.currentTextChanged.connect(
            lambda value: self.change_translation(value, "object"))
        self.select_translation_tool.currentTextChanged.connect(
            lambda value: self.change_translation(value, "method"))
        # 成人选择 Adult Chose
        BodyLabel(self.languages[5], self).setGeometry(QRect(5, 125, 80, 35))
        self.select_adult_label = ComboBox(self)
        self.select_adult_label.addItems(
            list(self.configure['model'][self.configure['default']]['adult']['AdultDescribe'].values()))
        self.select_adult_label.setCurrentIndex(self.configure['adult_level'] - 1)
        if not self.configure['adult_level']:
            self.select_adult_label.setEnabled(False)
        self.select_adult_label.setGeometry(QRect(100, 125, 230, 35))
        self.select_adult_label.currentIndexChanged.connect(
            lambda value: function.change_configure(
                value + 1, "adult_level", self.configure))
        # AI发声 AI Speak
        BodyLabel(self.languages[6], self).setGeometry(QRect(5, 165, 80, 35))
        self.select_ai_speak = ComboBox(self)
        self.select_ai_speak.addItems(list(self.module_info.keys()))
        self.select_ai_speak.setCurrentText(self.configure['voice_model'])
        self.select_ai_speak.currentTextChanged.connect(self.change_reference)
        self.select_ai_speak.setGeometry(QRect(100, 165, 230, 35))
        self.input_reference_text = LineEdit(self)
        self.input_reference_text.setPlaceholderText("Reference Text here")
        self.input_reference_text.setClearButtonEnabled(True)
        self.input_reference_text.setGeometry(QRect(5, 205, 470, 35))
        self.click_play_reference = PushButton(self.languages[7], self)
        self.click_play_reference.clicked.connect(
            lambda: kwargs.get("play")(self.input_reference_text.text()))
        self.click_play_reference.setGeometry(QRect(490, 205, 80, 35))
        # 水印 Watermark
        BodyLabel(self.languages[8], self).setGeometry(QRect(5, 245, 80, 35))
        self.select_watermark = ComboBox(self)
        self.select_watermark.addItems(list(self.param_dict.keys()))
        self.select_watermark.setCurrentText(self.configure['watermark'].split(";")[0])
        self.select_watermark.setGeometry(QRect(100, 245, 230, 35))
        self.select_watermark.currentTextChanged.connect(
            lambda value: self.change_watermark(value, "name"))
        self.scale_watermark = Slider(Qt.Horizontal, self)
        self.scale_watermark.setRange(0, 100)
        self.scale_watermark.setGeometry(QRect(340, 255, 230, 35))
        self.scale_watermark.valueChanged.connect(
            lambda value: self.change_watermark(value, "value"))
        # 透明度 Opacity
        BodyLabel(self.languages[9], self).setGeometry(QRect(5, 295, 80, 35))
        self.scale_opacity = Slider(Qt.Horizontal, self)
        self.scale_opacity.setRange(5, constants.OPACITY_PRECISION)
        self.scale_opacity.setGeometry(QRect(100, 300, 230, 35))
        self.scale_opacity.setValue(int(self.configure['settings']['transparency'] * constants.OPACITY_PRECISION))
        self.scale_opacity.valueChanged.connect(
            lambda value: function.change_configure(
                value / constants.OPACITY_PRECISION, "settings.transparency", self.configure))
        # 角色相关 Character Related
        self.click_add_character = PushButton(self.languages[124], self)
        self.click_add_character.setGeometry(QRect(450, 420, 80, 35))
        self.click_delete_character = PushButton(self.languages[3], self)
        self.click_delete_character.setGeometry(QRect(550, 420, 80, 35))

        self.fill_information()

    def change_reference(self):
        refer_text = self.module_info[self.select_ai_speak.currentText()][3]
        self.input_reference_text.clear()
        self.input_reference_text.setText(refer_text)
        function.change_configure(self.select_ai_speak.currentText(), "voice_model", self.configure)

    def change_translation(self, value, type_: typing.Literal['object', 'method']):
        if type_ == "object":
            self.select_translation_tool.clear()
            if value == self.languages[121]:
                self.select_translation_tool.addItems([self.languages[122]])
            elif value == self.languages[120]:
                self.select_translation_tool.addItems([self.languages[123]])
            function.change_configure(f"{value.replace(' ', '').split('-')[1]}."
                                      f"{self.select_translation_tool.currentText().replace(' ', '').split('-')[1]}",
                                      "settings.translate", self.configure)
        else:
            function.change_configure(f"{self.select_translation_engine.currentText().replace(' ', '').split('-')[1]}."
                                      f"{value.replace(' ', '').split('-')[1]}",
                                      "settings.translate", self.configure)
    
    def change_watermark(self, value, type_: typing.Literal['name', 'value']):
        if type_ == "name":
            self.scale_watermark.setRange(self.param_dict[value]['min'] * 10,
                                          self.param_dict[value]['max'] * 10)
            self.scale_watermark.setValue(int(float(self.configure['watermark'].split(";")[1]) * 10))
            function.change_configure(f"{value};{self.scale_watermark.value()}", "watermark", self.configure)
        else:
            function.change_configure(f"{self.select_watermark.currentText()};{value / 10}",
                                      "watermark", self.configure)

    def fill_information(self):
        self.scale_watermark.setRange(int(self.param_dict[self.select_watermark.currentText()]['min'] * 10),
                                      int(self.param_dict[self.select_watermark.currentText()]['max'] * 10))
        self.scale_watermark.setValue(int(float(self.configure['watermark'].split(";")[1]) * 10))
