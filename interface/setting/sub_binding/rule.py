from PyQt5.QtWidgets import QFrame


class RuleBinding(QFrame):
    def __init__(self, languages, configure, param_dict):
        super().__init__()
        self.languages = languages
        self.configure = configure
        self.param_dict = param_dict
        self.setObjectName("RuleBinding")
