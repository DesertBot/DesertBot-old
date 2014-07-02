# -*- coding: utf-8 -*-
from zope.interface import implements
from twisted.plugin import IPlugin
from twisted.python import log

from desertbot.moduleinterface import IModule, Module, ModuleType, AccessLevel
from desertbot.message import IRCMessage
from desertbot.response import IRCResponse, ResponseType


class Join(Module):
    implements(IPlugin, IModule)

    name = u"join"
    triggers = [u"join"]
    moduleType = ModuleType.COMMAND
    helpText = u"join <channel> [channel]..."

    def onTrigger(self, message):
        """
        @type message: IRCMessage
        """
        
        if len(message.parameterList) == 0:
            return IRCResponse(ResponseType.PRIVMSG,
                               u"You didn't give a channel for me to join",
                               message.user, message.replyTo)
                               
        for channel in message.parameterList:
            self.bot.join(channel.encode('utf-8'))

join = Join()
        