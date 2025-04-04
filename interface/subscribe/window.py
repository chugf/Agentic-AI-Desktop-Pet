
class Window:
    def __init__(self, config):
        self.config = config

    def GetWindowPosition(self) -> tuple:
        return (self.config['_Window'].width(), self.config['_Window'].height(),
                self.config['_Window'].x(), self.config['_Window'].y())

