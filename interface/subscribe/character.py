class Character:
    def __init__(self, config):
        self.config = config
    
    def GetCharacter(self):
        return self.config.character

    def GetName(self):
        return self.config.name
    