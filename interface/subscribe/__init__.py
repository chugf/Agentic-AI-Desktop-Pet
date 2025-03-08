class _Config:
    def __init__(self):
        self._config = {
            "name": None,
            "character": None,
            "voice_model": None
        }

    def register(self, relative: str, value: str):
        self._config[relative] = value

    @property
    def character(self):
        return self._config['character']

    @property
    def voice_model(self):
        return self._config['voice_model']

    @property
    def name(self):
        return self._config['name']


class Character:
    def GetCharacter(self):
        return _Config.character

    def GetName(self):
        return _Config.name


class Model:
    def GetVoiceModel(self):
        return _Config.voice_model


class Register:
    def SetCharacter(self, character):
        _Config.register("character", character)

    def SetVoiceModel(self, voice_model):
        _Config.register("voice_model", voice_model)

    def SetName(self, name):
        _Config.register("name", name)


_Config = _Config()
