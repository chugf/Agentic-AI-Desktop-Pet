# 此行用于接口调用！
from . import views
from . import actions

from .Config import _Config
from . import Register as _Register
from . import character
from . import window
from . import live2d
from . import model


class Character(character.Character):
    def __init__(self):
        super().__init__(_Config)


class Window(window.Window):
    def __init__(self):
        super().__init__(_Config)


class Live2D(live2d.Live2D):
    def __init__(self):
        super().__init__(_Config)


class Model(model.Model):
    def __init__(self):
        super().__init__(_Config)


class Register(_Register.Register):
    def __init__(self):
        super().__init__(_Config)


class RegisterAttribute(_Register.AttributeRegister):
    def __init__(self):
        super().__init__(_Config)


_Config = _Config()
