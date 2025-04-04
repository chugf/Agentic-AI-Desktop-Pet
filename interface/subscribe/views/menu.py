from qfluentwidgets import RoundMenu, Action


class ContentMenu:
    def __init__(self, config):
        self._config = config
        self._registered = {}

    def InsertMenu(self, new_menu: RoundMenu):
        new_menu.setObjectName(new_menu.title())
        if new_menu.objectName() in self._registered.keys():
            self._config.unregister("content_menu", self._registered[new_menu.objectName()])
        self._registered.update({new_menu.objectName(): new_menu})
        self._config.register("content_menu", new_menu)

    def InsertAction(self, new_action: Action):
        new_action.setObjectName(new_action.text())
        if new_action.objectName() in self._registered.keys():
            self._config.unregister("content_menu", self._registered[new_action.objectName()])
        self._registered.update({new_action.objectName(): new_action})
        self._config.register("content_menu", new_action)

    def DeleteMenu(self, widget):
        self._registered.pop(widget.objectName())
        self._config.unregister("content_menu", widget)

    def DeleteAction(self, widget):
        self._registered.pop(widget.objectName())
        self._config.unregister("content_menu", widget)
