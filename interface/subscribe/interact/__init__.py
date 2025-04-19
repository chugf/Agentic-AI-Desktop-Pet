from . import ai

from .Register import _Register
from .Config import _Config


class _LargeLanguageModel(ai.LargeLanguageModel):
    def __init__(self, config):
        super().__init__(config)


class __Register(_Register):
    def __init__(self, config):
        super().__init__(config)


_Config = _Config()
LargeLanguageModel = _LargeLanguageModel(_Config)
Register = __Register(_Config)
