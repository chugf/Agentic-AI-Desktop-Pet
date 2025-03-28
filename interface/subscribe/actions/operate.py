class Operate:
    def __init__(self, config):
        self.config = config

    def GetDragAction(self):
        return self.config.drag_action

    def GetClckAction(self):
        return self.config.click_action

    def GetMouseDragAction(self):
        return self.config.mouse_drag_action

    def GetAIOutput(self):
        return self.config.ai_output
