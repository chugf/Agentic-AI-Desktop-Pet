class Operate:
    def __init__(self, config):
        self.config = config

    def GetSettingInterface(self):
        return self.config['setting']

    def GetConversationInterface(self):
        return self.config['conversation']
