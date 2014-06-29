# -*- coding: utf-8 -*-
from zope.interface import implements
from twisted.plugin import IPlugin

from desertbot.moduleinterface import IModule, Module, ModuleType
from desertbot.message import IRCMessage
from desertbot.response import IRCResponse, ResponseType


class Do(Module):
    implements(IPlugin, IModule)

    name = u"do"
    triggers = [u"do"]
    moduleType = ModuleType.COMMAND
    helpText = u"do <text> - makes the bot do the specified thing"

    def onTrigger(self, message):
        """
        @type message: IRCMessage
        """
        if len(message.parameterList) > 0:
            return IRCResponse(ResponseType.ACTION, message.parameters, message.user,
                               message.replyTo)
        else:
            return IRCResponse(ResponseType.PRIVMSG, u"Do what?", message.user, message.replyTo)


do = Do()
