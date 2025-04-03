from PyQt5.QtWidgets import QWidget


class Register:
    def __init__(self, config):
        self.config = config

    # 注册
    def HookSettingInterface(self, new_widget: QWidget):
        self.config.register("setting", new_widget)

    def HookConversationInterface(self, new_widget: QWidget):
        self.config.register("conversation", new_widget)
