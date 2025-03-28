from .Config import _Config
from . import setting
from . import Register


class Setting(setting.Setting):
    def __init__(self):
        super().__init__(_Config)


class RegisterSetting(Register.RegisterSetting):
    def __init__(self):
        super().__init__(_Config)


_Config = _Config()
Setting = Setting()
RegisterSetting = RegisterSetting()
