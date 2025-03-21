import json

from ..customize import function

from PyQt5.Qt import QRect
from PyQt5.QtWidgets import QFrame

from qfluentwidgets import PasswordLineEdit, BodyLabel, ComboBox


class IntelligenceCloud(QFrame):
    def __init__(self, languages, configure):
        super().__init__()
        with open('./resources/intelligence.json', 'r', encoding='utf-8') as itf:
            intelligence = json.load(itf)
            itf.close()

        self.languages = languages
        self.configure = configure
        self.setObjectName("IntelligenceCloud")

        # 阿里云API
        BodyLabel(self.languages[30], self).setGeometry(QRect(10, 10, 120, 35))
        self.input_aliyun_key = PasswordLineEdit(self)
        self.input_aliyun_key.setPlaceholderText("Type Aliyun API-KEY here")
        self.input_aliyun_key.setText(self.configure['settings']['cloud']['aliyun'])
        self.input_aliyun_key.setClearButtonEnabled(True)
        self.input_aliyun_key.setGeometry(QRect(120, 10, 330, 35))
        self.input_aliyun_key.textChanged.connect(
            lambda value: function.change_configure(value, 'settings.cloud.aliyun', self.configure))
        # # 阿里云模型 Aliyun Model
        self.select_aliyun_model = ComboBox(self)
        self.select_aliyun_model.addItems(intelligence)
        self.select_aliyun_model.setCurrentText(self.configure['settings']['intelligence'])
        self.select_aliyun_model.setGeometry(QRect(470, 10, 170, 35))
        self.select_aliyun_model.currentTextChanged.connect(
            lambda value: function.change_configure(value, 'settings.intelligence', self.configure))

        # 讯飞云 API ID - API Key - API Secret
        BodyLabel(self.languages[135], self).setGeometry(QRect(10, 40, 120, 35))
        self.input_xfyun_id = PasswordLineEdit(self)
        self.input_xfyun_id.setPlaceholderText("Type Xfyun API-ID here")
        self.input_xfyun_id.setText(self.configure['settings']['cloud']['xunfei']['id'])
        self.input_xfyun_id.setClearButtonEnabled(True)
        self.input_xfyun_id.setGeometry(QRect(120, 45, 330, 35))
        self.input_xfyun_id.textChanged.connect(
            lambda value: function.change_configure(value, 'settings.cloud.xunfei.id', self.configure))

        BodyLabel(self.languages[136], self).setGeometry(QRect(10, 80, 120, 35))
        self.input_xfyun_key = PasswordLineEdit(self)
        self.input_xfyun_key.setPlaceholderText("Type Xfyun API-Key here")
        self.input_xfyun_key.setText(self.configure['settings']['cloud']['xunfei']['key'])
        self.input_xfyun_key.setClearButtonEnabled(True)
        self.input_xfyun_key.setGeometry(QRect(120, 80, 330, 35))
        self.input_xfyun_key.textChanged.connect(
            lambda value: function.change_configure(value, 'settings.cloud.xunfei.key', self.configure))

        BodyLabel(self.languages[137], self).setGeometry(QRect(10, 115, 120, 35))
        self.input_xfyun_secret = PasswordLineEdit(self)
        self.input_xfyun_secret.setPlaceholderText("Type Xfyun API-Secret here")
        self.input_xfyun_secret.setText(self.configure['settings']['cloud']['xunfei']['secret'])
        self.input_xfyun_secret.setClearButtonEnabled(True)
        self.input_xfyun_secret.setGeometry(QRect(120, 115, 330, 35))
        self.input_xfyun_secret.textChanged.connect(
            lambda value: function.change_configure(value, 'settings.cloud.xunfei.secret', self.configure))

        del intelligence
