import tkinter


class _Config:
    def __init__(self):
        self._config = {
            "setting": None
        }

    def register(self, relative, callback):
        self._config[relative] = callback

    @property
    def setting(self) -> callable:
        return self._config["setting"]


class Setting:
    def InsertNotebook(self, frame: tkinter.Frame, text: str):
        _Config.setting.note.add(frame, text=text)

    def DeleteNotebook(self, frame: tkinter.Frame):
        _Config.setting.note.forget(frame)


class RegisterSetting:
    @staticmethod
    def register(master):
        _Config.register("setting", master)


_Config = _Config()
