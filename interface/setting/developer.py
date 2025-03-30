from PyQt5.QtWidgets import QFrame

engine = runtime = logs = intelligence = interface = None
desktop = conversation = setting = visualization = picture = None
languages = configure = module_info = param_dict = None


def reload_module(engine_module, runtime_module, logs_module, intelligence_module, interface_module):
    global engine, runtime, logs, intelligence, interface
    engine = engine_module
    runtime = runtime_module
    logs = logs_module
    intelligence = intelligence_module
    interface = interface_module


def reload_program(desktop_ui, conversation_ui, setting_ui, visualization_ui, picture_ui):
    global desktop, conversation, setting, visualization, picture
    desktop = desktop_ui
    conversation = conversation_ui
    setting = setting_ui
    visualization = visualization_ui
    picture = picture_ui


def reload_file(languages_file, configure_file, module_info_file, param_dict_file):
    global languages, configure, module_info, param_dict
    languages = languages_file
    configure = configure_file
    module_info = module_info_file
    param_dict = param_dict_file


class Developer(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("79JWnYp65lhmjxPa1zTru+NR43o86dPk3Lj821+Tlld0DRaZIHMRAs+uOYavQi1t")
