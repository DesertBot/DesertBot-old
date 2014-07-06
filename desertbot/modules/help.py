# -*- coding: utf-8 -*-
from zope.interface import implements
from twisted.plugin import IPlugin

from desertbot.moduleinterface import IModule, Module, ModuleType
from desertbot.response import IRCResponse, ResponseType
from desertbot.message import IRCMessage


class Help(Module):
    implements(IPlugin, IModule)

    name = u"help"
    triggers = [u"help", u"modules"]
    moduleType = ModuleType.COMMAND

    def getHelp(self, message):
        """
        @type message: IRCMessage
        """
        helpDict = {
            u"help": u"help [module/command] - returns the helptext for the given module or command.",
            u"modules": u"modules - returns a list of all loaded modules"
        }
        return helpDict[message.parameterList[0]]

    def onTrigger(self, message):
        """
        @type message: IRCMessage
        """
        if message.command == u"help":
            if len(message.parameterList) == 0:
                modules = []
                for moduleName, module in self.bot.moduleHandler.loadedModules.iteritems():
                    if module.moduleType is not ModuleType.UTILITY:
                        modules.append(moduleName)
                return IRCResponse(ResponseType.PRIVMSG,
                                   u"Loaded modules: {}".format(
                                       u", ".join(sorted(modules))),
                                   message.user, message.replyTo)
            else:
                if message.parameterList[0].lower() in self.bot.moduleHandler.mappedTriggers:
                    return IRCResponse(ResponseType.PRIVMSG,
                                       self.bot.moduleHandler.mappedTriggers[
                                           message.parameterList[0].lower()].getHelp(message),
                                       message.user, message.replyTo)

                if message.parameterList[0].lower() in self.bot.moduleHandler.loadedModules:
                    return IRCResponse(ResponseType.PRIVMSG,
                                       self.bot.moduleHandler.loadedModules[
                                           message.parameterList[0].lower()].getHelp(message),
                                       message.user, message.replyTo)

                elif message.parameterList[0].lower() in self.bot.moduleHandler.loadedPostProcesses:
                    return IRCResponse(ResponseType.PRIVMSG,
                                       self.bot.moduleHandler.loadedPostProcesses[
                                           message.parameterList[0].lower()].getHelp(message),
                                       message.user, message.replyTo)
                else:
                    return IRCResponse(ResponseType.PRIVMSG,
                                       u"There is no module called \"{}\" currently loaded.".format(
                                           message.parameterList[0]),
                                       message.user, message.replyTo)

        elif message.command == u"modules":
            return IRCResponse(ResponseType.PRIVMSG,
                               u"Loaded modules: {}".format(
                                   u", ".join(sorted(self.bot.moduleHandler.loadedModules))),
                                message.user, message.replyTo)


helpModule = Help()
