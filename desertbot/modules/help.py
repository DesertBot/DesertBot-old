# -*- coding: utf-8 -*-
from zope.interface import implements
from twisted.plugin import IPlugin

from desertbot.moduleinterface import IModule, Module, ModuleType
from desertbot.message import IRCMessage
from desertbot.response import IRCResponse, ResponseType


class Help(Module):
    implements(IPlugin, IModule)
    
    name = u"help"
    triggers = [u"help"]
    moduleType = ModuleType.COMMAND
    
    def onTrigger(self, message):
        if len(message.parameterList) == 0:
            return IRCResponse(ResponseType.PRIVMSG, 
                               u"Loaded modules: {}".format(u", ".join(sorted(self.bot.moduleHandler.loadedModules))),
                               message.user, message.replyTo)
        else:
            if message.parameterList[0].lower() in self.bot.moduleHandler.mappedTriggers:
                return IRCResponse(ResponseType.PRIVMSG, 
                                   self.bot.moduleHandler.mappedTriggers[message.parameterList[0].lower()].getHelp(message),
                                   message.user, message.replyTo)
                                   
            if message.parameterList[0].lower() in self.bot.moduleHandler.loadedModules:
                return IRCResponse(ResponseType.PRIVMSG,
                                   self.bot.moduleHandler.loadedModules[message.parameterList[0].lower()].getHelp(message),
                                   message.user, message.replyTo)
                                   
            elif message.parameterList[0].lower() in self.bot.moduleHandler.loadedPostProcesses:
                return IRCResponse(ResponseType.PRIVMSG,
                                   self.bot.moduleHandler.loadedPostProcesses[message.parameterList[0].lower()].getHelp(message),
                                   message.user, message.replyTo)
            else:
                return IRCResponse(ResponseType.PRIVMSG,
                                   u"There is no module called \"{}\" currently loaded.".format(message.parameterList[0]),
                                   message.user, message.replyTo)
                                   
help = Help()
