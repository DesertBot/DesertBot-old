# -*- coding: utf-8 -*-
from zope.interface import implements
from twisted.plugin import IPlugin

from desertbot.moduleinterface import IModule, Module, ModuleType
from desertbot.message import IRCMessage
from desertbot.response import IRCResponse, ResponseType


class Say(Module):
    implements(IPlugin, IModule)

    name = u"say"
    triggers = [u"say"]
    moduleType = ModuleType.COMMAND
    helpText = u"say <text> - makes the bot repeat the specified text"

    def onTrigger(self, message):
        """
        @type message: IRCMessage
        """
        if len(message.parameterList) > 0:
            return IRCResponse(ResponseType.PRIVMSG, message.parameters, message.user,
                               message.replyTo)
        else:
            return IRCResponse(ResponseType.PRIVMSG, u"Say what?", message.user, message.replyTo)


say = Say()
