from enum import Enum

import pydle


class IRCMessage(object):
    def __init__(self, messageType, server, channel, user, text):
        self.messageType = messageType
        self.server = server
        self.channel = channel
        self.user = user
        self.text = test

        if not user and not channel:
            self.replyTo = None
        elif not channel:
            self.replyTo = user
            self.targetType = TargetType.USER
        else:
            self.replyTo = channel
            self.targetType = TargetType.CHANNEL

class TargetType(Enum):
    CHANNEL = 1
    USER = 2
