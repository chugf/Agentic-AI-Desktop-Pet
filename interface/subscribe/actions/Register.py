class Register:
    def __init__(self, config):
        self.config = config

    # 注册
    def SetDragAction(self, func: callable):
        self.config.register("drag_action", func)

    def SetClickAction(self, func: callable):
        self.config.register("click_action", func)

    def SetMouseDragAction(self, func: callable):
        self.config.register("mouse_drag_action", func)

    def SetAIOutput(self, func: callable):
        self.config.register("ai_output", func)

    # 注销
    def UnsetDragAction(self):
        self.config.unregister("drag_action")

    def UnsetClickAction(self):
        self.config.unregister("click_action")

    def UnsetMouseDragAction(self):
        self.config.unregister("mouse_drag_action")

    def UnsetAIOutput(self):
        self.config.unregister("ai_output")

    def UnsetALL(self):
        self.UnsetDragAction()
        self.UnsetClickAction()
        self.UnsetMouseDragAction()
        self.UnsetAIOutput()
