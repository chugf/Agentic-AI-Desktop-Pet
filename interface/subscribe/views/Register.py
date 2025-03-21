class RegisterSetting:
    def __init__(self, config):
        self.config = config

    def register(self, master):
        self.config.register("setting", master)
