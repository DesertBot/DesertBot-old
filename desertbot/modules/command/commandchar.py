# -*- coding: utf-8 -*-
from zope.interface import implements
from twisted.plugin import IPlugin
from desertbot.moduleinterface import IModule, Module, ModuleType, AccessLevel
from desertbot.message import IRCMessage
from desertbot.response import IRCResponse, ResponseType


class CommandChar(Module):
    implements(IPlugin, IModule)

    name = u"commandchar"
    triggers = [u"commandchar"]
    moduleType = ModuleType.COMMAND
    accessLevel = AccessLevel.ADMINS

    helpText = u"commandchar <char> - changes the prefix character for bot commands"

    def onTrigger(self, message):
        """
        @type message: IRCMessage
        """
        if len(message.parameterList) > 0:
            message.bot.commandChar = message.parameterList[0]
            return IRCResponse(ResponseType.PRIVMSG,
                               u"Command prefix char changed to \"{}\"!".format(message.bot.commandChar),
                               message.user, message.replyTo)
        else:
            return IRCResponse(ResponseType.PRIVMSG,
                               u"Change my command prefix char to what?",
                               message.user, message.replyTo)

commandchar = CommandChar()
