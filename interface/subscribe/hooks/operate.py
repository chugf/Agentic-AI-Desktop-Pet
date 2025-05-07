from PyQt5.QtWidgets import QWidget


class Operate:
    def __init__(self, config):
        self.config = config

    def GetSettingInterface(self) -> QWidget:
        return self.config['setting']

    def GetConversationInterface(self) -> QWidget:
        return self.config['conversation']
