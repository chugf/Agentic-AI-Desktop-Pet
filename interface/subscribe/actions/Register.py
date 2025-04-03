class Register:
    def __init__(self, config):
        self.config = config

    # 注册
    def SetDragEnterAction(self, func: callable):
        self.config.register("drag_enter_action", func)

    def SetDragLeaveAction(self, func: callable):
        self.config.register("drag_leave_action", func)

    def SetDragMoveAction(self, func: callable):
        self.config.register("drag_move_action", func)

    def SetDropAction(self, func: callable):
        self.config.register("drag_drop_action", func)

    def SetClickAction(self, func: callable):
        self.config.register("click_action", func)

    def SetMouseEnterAction(self, func: callable):
        self.config.register("mouse_enter_action", func)

    def SetMouseLeaveAction(self, func: callable):
        self.config.register("mouse_leave_action", func)

    def SetMouseMoveAction(self, func: callable):
        self.config.register("mouse_move_action", func)

    def SetMouseDragAction(self, func: callable):
        self.config.register("mouse_drag_action", func)

    def SetMouseReleaseAction(self, func: callable):
        self.config.register("mouse_release_action", func)

    def SetAIOutput(self, func: callable):
        self.config.register("ai_output", func)

    # 注销
    def UnsetDragEnterAction(self):
        self.config.unregister("drag_enter_action")

    def UnsetDragLeaveAction(self):
        self.config.unregister("drag_leave_action")

    def UnsetDragMoveAction(self):
        self.config.unregister("drag_move_action")

    def UnsetDragDropAction(self):
        self.config.unregister("drag_drop_action")

    def UnsetClickAction(self):
        self.config.unregister("click_action")

    def UnsetMouseEnterAction(self):
        self.config.unregister("mouse_enter_action")

    def UnsetMouseLeaveAction(self):
        self.config.unregister("mouse_leave_action")

    def UnsetMouseMoveAction(self):
        self.config.unregister("mouse_move_action")

    def UnsetMouseDragAction(self):
        self.config.unregister("mouse_drag_action")

    def UnsetAIOutput(self):
        self.config.unregister("ai_output")

    def UnsetALL(self):
        self.UnsetDragEnterAction()
        self.UnsetDragLeaveAction()
        self.UnsetDragMoveAction()
        self.UnsetDragDropAction()
        self.UnsetClickAction()
        self.UnsetMouseEnterAction()
        self.UnsetMouseLeaveAction()
        self.UnsetMouseMoveAction()
        self.UnsetMouseDragAction()
        self.UnsetAIOutput()
