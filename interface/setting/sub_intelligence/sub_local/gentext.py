from PyQt5.QtWidgets import QWidget
from qfluentwidgets import BodyLabel


class TextGenerator(QWidget):
    def __init__(self, configure, parent=None):
        super().__init__(parent)
        self.configure = configure
        self.setObjectName("TextGenerator")

