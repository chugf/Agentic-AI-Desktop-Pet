class Register:
    def __init__(self, config):
        self.config = config

    def SetDragAction(self, func: callable):
        self.config.register("drag_action", func)

    def SetClickAction(self, func: callable):
        self.config.register("click_action", func)

    def SetMouseDragAction(self, func: callable):
        self.config.register("mouse_drag_action", func)
