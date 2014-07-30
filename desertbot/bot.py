from pydle import Client

class DesertBot(Client):
    def on_connect(self):
        self.join('#desertbot')
