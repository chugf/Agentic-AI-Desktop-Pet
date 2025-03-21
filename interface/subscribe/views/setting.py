import random


class Setting:
    def __init__(self, config):
        self.config = config

    def InsertInterface(self, widget, icon, text: str):
        if not widget.objectName():
            widget.setObjectName(f"_Default{text.title()}{str(random.randint(0, 999999)).zfill(6)}")
        self.config.setting.addSubInterface(widget, icon, text)
