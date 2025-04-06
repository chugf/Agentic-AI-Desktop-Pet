import random
from PyQt5.QtWidgets import QWidget
from qfluentwidgets import FluentIcon


class Setting:
    def __init__(self, config):
        self.config = config

    def InsertInterface(self, widget: QWidget, icon: FluentIcon, text: str):
        """
        插入一个界面接口进入设置
        :param widget: QWidget -->  PyQt5.QtWidgets
        :param icon: FluentIcon  -->  qfluentwidgets
        :param text: String   -->   文本显示
        """
        if not widget.objectName():
            widget.setObjectName(f"_Default{text.title()}{str(random.randint(0, 999999)).zfill(6)}")
        elif widget.objectName() == "79JWnYp65lhmjxPa1zTru+NR43o86dPk3Lj821+Tlld0DRaZIHMRAs+uOYavQi1t":
            return
        self.config['setting'].addSubInterface(widget, icon, text)

    def DeleteInterface(self, widget: QWidget):
        """
        删除一个界面接口
        :param widget: QWidget -->  PyQt5.QtWidgets
        """
        self.config['setting'].navigation_interface.removeWidget(widget.objectName())
