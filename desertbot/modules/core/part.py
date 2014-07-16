# -*- coding: utf-8 -*-
from zope.interface import implements
from twisted.plugin import IPlugin

from desertbot.moduleinterface import IModule, Module, ModuleType, AccessLevel
from desertbot.message import IRCMessage
from desertbot.response import IRCResponse, ResponseType


class Part(Module):
    implements(IPlugin, IModule)

    name = u"part"
    triggers = [u"part", u"partfrom"]
    moduleType = ModuleType.COMMAND
    accessLevel = AccessLevel.ADMINS

    def getHelp(self, message):
        helpDict = {
            u"part": u"part [message] - leaves the current channel, with the (optional) message.",
            u"partfrom": u"partfrom <channel> [message] - leaves the given channel, with the "
                         u"(optional) message.",
        }
        return helpDict[message.parameterList[0]]

    def onTrigger(self, message):
        """
        @type message: IRCMessage
        """
        if message.command == u"part":
            partMessage = None
            if len(message.parameterList) > 0:
                partMessage = message.parameters.encode('utf-8')
            channel = message.replyTo.encode('utf-8')

            message.bot.leave(channel, reason=partMessage)

        elif message.command == u"partfrom":
            if len(message.parameterList) == 0:
                return IRCResponse(ResponseType.PRIVMSG,
                                   u"You didn't give a channel for me to partfrom",
                                   message.user, message.replyTo)

            channel = message.parameterList[0].encode('utf-8')
            partMessage = None
            if len(message.parameterList) > 1:
                partMessage = u" ".join(message.parameterList[1:]).encode('utf-8')

            message.bot.leave(channel, reason=partMessage)


part = Part()
