# 此行用于接口调用！
from . import views
from . import actions
from . import standards
from . import hooks

from .Config import _Config
from . import Register as _Register
from . import character as _character
from . import window as _window
from . import live2d as _live2d
from . import model as _model


class Character(_character.Character):
    def __init__(self):
        super().__init__(_Config)


class Window(_window.Window):
    def __init__(self):
        super().__init__(_Config)


class Live2D(_live2d.Live2D):
    def __init__(self):
        super().__init__(_Config)


class Model(_model.Model):
    def __init__(self):
        super().__init__(_Config)


class Register(_Register.Register):
    def __init__(self):
        super().__init__(_Config)


class RegisterAttribute(_Register.AttributeRegister):
    def __init__(self):
        super().__init__(_Config)


_Config = _Config()
Character = Character()
Window = Window()
Live2D = Live2D()
Model = Model()
Register = Register()
RegisterAttribute = RegisterAttribute()
