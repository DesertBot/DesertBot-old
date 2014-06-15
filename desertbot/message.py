# -*- coding: utf-8 -*-
from enum import Enum
from desertbot.user import IRCUser
from desertbot.channel import IRCChannel
from desertbot.desertbot import DesertBot


class IRCMessage(object):
    def __init__(self, messageType, user, channel, messageText, bot):
        """
        @type messageType: str
        @type user: IRCUser | None
        @type channel: IRCChannel | None
        @type messageText: unicode
        @type bot: DesertBot
        """
        self.messageType = messageType
        self.user = user
        self.channel = channel
        self.messageList = messageText.strip().split(" ")
        if not isinstance(messageText, unicode):
            messageText = messageText.encode("utf-8")
        self.messageString = messageText
        if not user and not channel:
            self.replyTo = ''
        elif not channel:
            self.replyTo = self.user.nickname
            self.targetType = TargetType.USER
        else:
            self.replyTo = channel.name
            self.targetType = TargetType.CHANNEL

        if self.messageList[0].startswith(bot.commandChar):
            self.command = self.messageList[0][len(bot.commandChar):].lower()
            self.parameters = u' '.join(self.messageList[1:])

        if self.parameters.strip():
            self.parameterList = self.parameters.split(" ")

            self.parameterList = [param for param in self.parameterList if param != u'']

            if len(self.parameterList) == 1 and not self.parameterList[0]:
                self.parameterList = []


class TargetTypes(Enum):
    CHANNEL = 1
    USER = 2
