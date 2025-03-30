import typing
import hashlib

from ..customize import widgets

from PyQt5.Qt import QRect, QWidget, QThread, pyqtSignal
from qfluentwidgets import BodyLabel, LineEdit, PasswordLineEdit, PrimaryPushButton, \
    FluentIcon, TextEdit


class Loading(QThread):
    result = pyqtSignal(dict)

    def __init__(self, parent: QWidget,
                 runtime_module, type_: typing.Literal['sms', 'policy', 'vertify']):
        self.runtime = runtime_module
        self.type_ = type_
        super().__init__(parent)

    def run(self):
        if self.type_ == 'sms':
            self.result.emit(self.runtime.user_register(self.parent().input_email.text()))
        elif self.type_ == 'policy':
            self.result.emit({'message': self.runtime.get_policy()})
        elif self.type_ == 'vertify':
            self.result.emit(self.runtime.user_vertify(
                self.parent().input_email.text(), self.parent().input_vertify_code.text(),
                hashlib.md5(str(self.parent().input_password.text()).encode("utf-8")).hexdigest()))


class Register(QWidget):
    def __init__(self, languages, configure, runtime_module):
        super().__init__()
        self.runtime = runtime_module
        self.languages = languages
        self.configure = configure
        self.setObjectName("Register")

        BodyLabel(languages[146], self).setGeometry(QRect(5, 5, 100, 35))
        self.input_email = LineEdit(self)
        self.input_email.setClearButtonEnabled(True)
        self.input_email.setGeometry(QRect(110, 5, 400, 35))

        BodyLabel(languages[150], self).setGeometry(QRect(5, 45, 100, 35))
        self.input_vertify_code = LineEdit(self)
        self.input_vertify_code.setClearButtonEnabled(True)
        self.input_vertify_code.setGeometry(QRect(110, 45, 270, 35))
        self.click_vertify_code = PrimaryPushButton(languages[151], self)
        self.click_vertify_code.setGeometry(QRect(380, 45, 120, 35))
        self.click_vertify_code.clicked.connect(self.get_vertify_code)

        BodyLabel(languages[147], self).setGeometry(QRect(5, 80, 100, 35))
        self.input_password = PasswordLineEdit(self)
        self.input_password.setClearButtonEnabled(True)
        self.input_password.setGeometry(QRect(110, 80, 400, 35))

        policy = TextEdit(self)
        policy.setReadOnly(True)
        policy_thread = Loading(self, self.runtime, 'policy')
        policy_thread.result.connect(lambda message: policy.setMarkdown(message['message']))
        policy_thread.start()
        policy.setGeometry(QRect(0, 125, 620, 205))

        self.click_register = PrimaryPushButton(FluentIcon.SEND, languages[149], self)
        self.click_register.setGeometry(QRect(0, 345, 620, 35))
        self.click_register.clicked.connect(self.register)

    def pop(self, message: dict):
        if message['status']:
            widgets.pop_success(self, self.languages[149], message['message'])
        else:
            widgets.pop_error(self, self.languages[149], message['message'])

    def register(self):
        vertify = Loading(self, self.runtime, 'vertify')
        vertify.result.connect(self.pop)
        vertify.start()

    def get_vertify_code(self):
        sms = Loading(self, self.runtime, 'sms')
        sms.result.connect(self.pop)
        sms.start()
