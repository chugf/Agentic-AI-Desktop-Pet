import random


class Setting:
    def __init__(self, config):
        self.config = config

    def InsertInterface(self, widget, icon, text: str):
        if not widget.objectName():
            widget.setObjectName(f"_Default{text.title()}{str(random.randint(0, 999999)).zfill(6)}")
        elif widget.objectName() == "79JWnYp65lhmjxPa1zTru+NR43o86dPk3Lj821+Tlld0DRaZIHMRAs+uOYavQi1t":
            return
        self.config['setting'].addSubInterface(widget, icon, text)

    def DeleteInterface(self, widget):
        self.config['setting'].navigation_interface.removeWidget(widget.objectName())
