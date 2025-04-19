class Control:
    def __init__(self, config):
        self.config = config

    def HideConversationView(self):
        self.config['conversation'].hide()

    def ShowConversationView(self):
        self.config['conversation'].show()

    def HideSettingView(self):
        self.config['setting'].hide()

    def ShowSettingView(self):
        self.config['setting'].show()
