from PyQt5.QtWidgets import QFrame


class PluginBinding(QFrame):
    def __init__(self, languages, configure, module_info, param_dict):
        super().__init__()
        self.languages = languages
        self.configure = configure
        self.module_info = module_info
        self.param_dict = param_dict
        self.setObjectName("PluginBinding")
