# -*- coding: utf-8 -*-
from zope.interface import implements
from twisted.plugin import IPlugin
from twisted.python import log

from desertbot.moduleinterface import IModule, Module, ModuleType, AccessLevel
from desertbot.message import IRCMessage
from desertbot.response import IRCResponse, ResponseType
from desertbot.config import Config

class Part(Module):
    implements(IPlugin, IModule)

    name = u"part"
    triggers = [u"part", u"partfrom"]
    moduleType = ModuleType.COMMAND
    accessLevel = AccessLevel.ADMINS
    helpText = u"part [message] / partfrom <channel> [message]"

    def onTrigger(self, message):
        """
        @type message: IRCMessage
        """
        if message.command == u"part":
            partMessage = None
            if len(message.parameterList) > 0:
                partMessage = message.parameters.encode('utf-8')
                
            self.bot.leave(message.replyTo, reason=partMessage)
            
        elif message.command == u"partfrom":
            if len(message.parameterList) == 0:
                return IRCResponse(ResponseType.Say,
                                   u"You didn't give a channel for me to partfrom",
                                   message.user, message.replyTo)
                                   
            channel = message.parameterList[0]
            partMessage = None
            if len(message.parameterList) > 1:
                partMessage = u" ".join(message.parameterList[1:]).encode('utf-8')
                
            self.bot.leave(channel, reason=partMessage)

part = Part()
        
