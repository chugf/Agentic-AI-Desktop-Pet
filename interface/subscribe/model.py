class Model:
    def __init__(self, config):
        self.config = config

    def GetVoiceModel(self):
        return self.config['voice_model']
    