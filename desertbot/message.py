class IRCMessage(object):
    def __init__(self, messageType, user, channel, messageText):
        self.messageType = messageType
        self.user = user
        self.channel = channel
        self.messageText = messageText
