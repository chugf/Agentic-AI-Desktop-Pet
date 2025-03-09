from . import views


class _Config:
    def __init__(self):
        self._config = {
            "name": None,
            "character": None,
            "voice_model": None,

            "_Pet": None,
            "_Window": None
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

    @property
    def attribute_pet(self):
        return self._config['_Pet']

    @property
    def attribute_window(self):
        return self._config['_Window']


class Live2D:
    def GetLive2D(self):
        return _Config.attribute_pet


class Window:
    def GetWindowPosition(self) -> tuple:
        return (_Config.attribute_window.width(), _Config.attribute_window.height(),
                _Config.attribute_window.x(), _Config.attribute_window.y())


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


class AttributeRegister:
    def SetWindow(self, window):
        _Config.register("_Window", window)

    def SetPet(self, pet: callable):
        _Config.register("_Pet", pet)


_Config = _Config()