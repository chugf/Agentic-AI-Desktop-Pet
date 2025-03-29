from PyQt5.QtWidgets import QWidget


class VoiceGenerator(QWidget):
    def __init__(self, configure, parent=None):
        super().__init__(parent)
        self.configure = configure
        self.setObjectName("VoiceGenerator")
