import sys

import interfaces

from PyQt5.Qt import QApplication
from qfluentwidgets import FluentWindow, FluentIcon


class PluginManager(FluentWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("插件管理")
        self.setGeometry(100, 100, 700, 600)

        self.plugin_list_interface = interfaces.plugin_list.PluginList()

        self.addSubInterface(self.plugin_list_interface, FluentIcon.HOME, "插件列表")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PluginManager()
    window.show()
    sys.exit(app.exec_())
