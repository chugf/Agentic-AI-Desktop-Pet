class Config:
    def __init__(self):
        self._config = {
            "drag_action": [],
            "click_action": [],
            "mouse_drag_action": []
        }

    def register(self, relative: str, value: str):
        if isinstance(self._config[relative], str):
            self._config[relative] = value
        elif isinstance(self._config[relative], list):
            self._config[relative].append(value)

    def unregister(self, relative: str):
        if isinstance(self._config[relative], str):
            self._config[relative] = ""
        elif isinstance(self._config[relative], list):
            self._config[relative].clear()

    @property
    def drag_action(self):
        return self._config["drag_action"]

    @property
    def click_action(self):
        return self._config["click_action"]

    @property
    def mouse_drag_action(self):
        return self._config["mouse_drag_action"]
