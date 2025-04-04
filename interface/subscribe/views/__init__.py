from .Config import _Config
from . import operate
from . import setting
from . import menu
from . import Register


class ContentMenu(menu.ContentMenu):
    def __init__(self):
        super().__init__(_Config)


class Operate(operate.Operate):
    def __init__(self):
        super().__init__(_Config)


class Setting(setting.Setting):
    def __init__(self):
        super().__init__(_Config)


class RegisterSetting(Register.RegisterSetting):
    def __init__(self):
        super().__init__(_Config)


_Config = _Config()
Setting = Setting()
ContentMenu = ContentMenu()
Operate = Operate()
RegisterSetting = RegisterSetting()
