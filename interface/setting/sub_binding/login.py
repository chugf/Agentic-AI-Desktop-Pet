import typing
import hashlib

from ..customize import widgets

from PyQt5.Qt import QRect, QWidget, QThread, pyqtSignal
from qfluentwidgets import LineEdit, PasswordLineEdit, BodyLabel, TextEdit, PrimaryPushButton, \
    FluentIcon


class Loading(QThread):
    result = pyqtSignal(str)

    def __init__(self, parent: QWidget, runtime_module, type_: typing.Literal['login', 'policy']):
        super().__init__(parent)
        self.runtime = runtime_module
        self.type_ = type_

    def run(self):
        if self.type_ == 'login':
            self.result.emit(self.runtime.user_login(
                self.parent().input_email.text(),
                hashlib.md5(str(self.parent().input_password.text()).encode("utf-8")).hexdigest())['message']
            )
        elif self.type_ == 'policy':
            self.result.emit(self.runtime.get_policy())


class Login(QWidget):
    def __init__(self, languages, configure, runtime_module):
        super().__init__()
        self.runtime = runtime_module
        self.languages = languages
        self.configure = configure
        self.setObjectName("Login")

        BodyLabel(languages[146], self).setGeometry(QRect(5, 5, 100, 35))
        self.input_email = LineEdit(self)
        self.input_email.setClearButtonEnabled(True)
        self.input_email.setGeometry(QRect(110, 5, 400, 35))

        BodyLabel(languages[147], self).setGeometry(QRect(5, 45, 100, 35))
        self.input_password = PasswordLineEdit(self)
        self.input_password.setClearButtonEnabled(True)
        self.input_password.setGeometry(QRect(110, 45, 400, 35))

        policy = TextEdit(self)
        policy.setReadOnly(True)
        policy_thread = Loading(self, self.runtime, 'policy')
        policy_thread.result.connect(policy.setMarkdown)
        policy_thread.start()
        policy.setGeometry(QRect(0, 85, 620, 250))

        self.click_login = PrimaryPushButton(FluentIcon.SEND, languages[148], self)
        self.click_login.setGeometry(QRect(0, 345, 620, 35))
        self.click_login.clicked.connect(self.login)

    def login(self):
        policy_thread = Loading(self, self.runtime, 'login')
        policy_thread.result.connect(
            lambda tip: widgets.pop_message(self, self.languages[148], tip))
        policy_thread.start()
