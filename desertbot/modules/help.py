# -*- coding: utf-8 -*-
from zope.interface import implements
from twisted.plugin import IPlugin

from desertbot.moduleinterface import IModule, Module, ModuleType
from desertbot.message import IRCMessage
from desertbot.response import IRCResponse, ResponseType


class Help(Module):
    implements(IPlugin, IModule)

    name = u"help"
    triggers = [u"help", u"modules", u"commands"]
    moduleType = ModuleType.COMMAND

    def getHelp(self, message):
        """
        @type message: IRCMessage
        """
        helpDict = {
            u"help": u"help [command/module] - returns help text for the given command or module, "
                     u"or a list of modules that you can interact with",
            u"modules": u"modules - returns a list of all loaded modules "
                        u"(some cannot be interacted with directly)",
            u"commands": u"commands <module> - returns a list of commands in the given module",
        }

        return helpDict[message.parameterList[0]]

    def onTrigger(self, message):
        """
        @type message: IRCMessage
        """
        funcDict = {
            u"help": self._help,
            u"modules": self._modules,
            u"commands": self._commands,
        }

        return funcDict[message.command](message)

    def _help(self, message):
        """
        @type message: IRCMessage
        """
        if len(message.parameterList) == 0:
            modules = []
            # only list non-utility modules here (ie, modules the user can actually interact with)
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
                                   u"There is no module named \"{}\" currently loaded.".format(
                                       message.parameterList[0]),
                                   message.user, message.replyTo)

    def _modules(self, message):
        """
        @type message: IRCMessage
        """
        modules = list(self.bot.moduleHandler.loadedModules) + list(self.bot.moduleHandler.loadedPostProcesses)
        return IRCResponse(ResponseType.PRIVMSG,
                           u"Loaded modules: {}".format(
                               u", ".join(sorted(modules))),
                           message.user, message.replyTo)

    def _commands(self, message):
        """
        @type message: IRCMessage
        """
        if len(message.parameterList) == 0:
            return IRCResponse(ResponseType.PRIVMSG,
                               u"You didn't specify a module.".format(
                                   message.parameterList[0]),
                               message.user, message.replyTo)

        module = message.parameterList[0].lower()
        if module in self.bot.moduleHandler.loadedModules:
            triggers = self.bot.moduleHandler.loadedModules[module].triggers
            if len(triggers) > 0:
                return IRCResponse(ResponseType.PRIVMSG,
                                   u"Commands provided by {}: {}".format(
                                       module, u", ".join(sorted(triggers))),
                                   message.user, message.replyTo)
            else:
                return IRCResponse(ResponseType.PRIVMSG,
                                   u"\"{}\" doesn't provide any commands.".format(
                                       message.parameterList[0]),
                                   message.user, message.replyTo)
        else:
            return IRCResponse(ResponseType.PRIVMSG,
                               u"There is no module named \"{}\" currently loaded.".format(
                                   message.parameterList[0]),
                               message.user, message.replyTo)


helpModule = Help()
