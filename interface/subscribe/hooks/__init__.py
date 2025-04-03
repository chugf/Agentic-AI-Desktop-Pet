from . import Register as _register
from . import Config as _Config
from . import operate


class Register(_register.Register):
    def __init__(self):
        super().__init__(Config)


class Operate(operate.Operate):
    def __init__(self):
        super().__init__(Config)


Config = _Config.Config()
Register = Register()
Operate = Operate()
