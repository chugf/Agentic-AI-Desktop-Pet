class _Config:
    def __init__(self):
        self._config = {
            "name": "",
            "character": "",
            "voice_model": "",

            "_Pet": "",
            "_Window": ""
        }

    def register(self, relative: str, value: str):
        if isinstance(self._config[relative], str):
            self._config[relative] = value
        elif isinstance(self._config[relative], list):
            self._config[relative].append(value)

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
