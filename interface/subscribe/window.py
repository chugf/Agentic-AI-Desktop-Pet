
class Window:
    def __init__(self, config):
        self.config = config
        
    
    def GetWindowPosition(self) -> tuple:
        return (self.config.attribute_window.width(), self.config.attribute_window.height(),
                self.config.attribute_window.x(), self.config.attribute_window.y())
    