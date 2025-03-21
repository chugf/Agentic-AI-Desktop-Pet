class _Config:
    def __init__(self):
        self._config = {
            "setting": ""
        }

    def register(self, relative: str, value):
        if isinstance(self._config[relative], str):
            self._config[relative] = value
        elif isinstance(self._config[relative], list):
            self._config[relative].append(value)

    @property
    def setting(self) -> callable:
        return self._config["setting"]
