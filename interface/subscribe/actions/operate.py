class Operate:
    def __init__(self, config):
        self.config = config

    def GetDragEnterAction(self):
        return self.config['drag_enter_action']

    def GetDragLeaveAction(self):
        return self.config['drag_leave_action']

    def GetDragMoveAction(self):
        return self.config['drag_move_action']

    def GetDropAction(self):
        return self.config['drag_drop_action']

    def GetClckAction(self):
        return self.config['click_action']

    def GetMouseEnterAction(self):
        return self.config['mouse_enter_action']

    def GetMouseLeaveAction(self):
        return self.config['mouse_leave_action']

    def GetMouseMoveAction(self):
        return self.config['mouse_move_action']

    def GetMouseDragAction(self):
        return self.config['mouse_drag_action']

    def GetMouseReleaseAction(self):
        return self.config['mouse_release_action']

    def GetAIOutput(self):
        return self.config['ai_output']
