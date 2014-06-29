# -*- coding: utf-8 -*-
from twisted.python import log
from zope.interface import implements
from twisted.plugin import IPlugin

from desertbot.moduleinterface import IModule, Module, ModuleType, AccessLevel
from desertbot.message import IRCMessage
from desertbot.response import IRCResponse, ResponseType


class ModuleLoader(Module):
    implements(IPlugin, IModule)

    name = u"moduleloader"
    triggers = [u"load", u"unload", u"reload"]
    moduleType = ModuleType.COMMAND
    helpText = u"load/reload <command>, unload <command> - handles loading/unloading/reloading of " \
               u"" \
               u"commands. " \
               u"Use 'all' with load/reload to reload all active commands"
    accessLevel = AccessLevel.ADMINS

    def onTrigger(self, message):
        """
        @type message: IRCMessage
        """
        if len(message.parameterList) == 0:
            return IRCResponse(ResponseType.PRIVMSG, u"You didn't specify a module name!",
                               message.user, message.replyTo)

        returns = {}
        for moduleName in message.parameterList:
            if message.command.lower() == u"load" or message.command.lower() == u"reload":
                isModule = self.bot.moduleHandler.loadModule(moduleName)
                if not isModule[0]:
                    returns[moduleName] = self.bot.moduleHandler.loadPostProcess(moduleName)
                else:
                    returns[moduleName] = isModule
            if message.command.lower() == u"unload":
                if moduleName.lower() in self.bot.moduleHandler.loadedModules:
                    returns[moduleName] = self.bot.moduleHandler.unloadModule(moduleName)
                elif moduleName.lower() in self.bot.moduleHandler.loadedPostProcesses:
                    returns[moduleName] = self.bot.moduleHandler.unloadPostProcess(moduleName)
                else:
                    returns[moduleName] = False, u"No module named \"{}\" is loaded!".format(
                        moduleName)
                    log.err(
                        "Tried to unload module \"{}\" but it is not loaded!".format(moduleName))

        successes = []
        failures = []
        for moduleName, returnTuple in returns.iteritems():
            if not returnTuple[0]:
                failures.append(u"\"{}, {}\"".format(moduleName, returnTuple[1]))
            else:
                successes.append(moduleName)

        if len(failures) == 0:
            return IRCResponse(ResponseType.PRIVMSG,
                               u"{} loaded successfully!".format(u", ".join(successes)),
                               message.user, message.replyTo)
        elif len(successes) == 0:
            return IRCResponse(ResponseType.PRIVMSG,
                               u"{} failed to load.".format(u", ".join(failures)), message.user,
                               message.replyTo)
        else:
            return [IRCResponse(ResponseType.PRIVMSG,
                                u"{} loaded successfully!".format(u", ".join(successes)),
                                message.user, message.replyTo),
                    IRCResponse(ResponseType.PRIVMSG,
                                u"{} failed to load.".format(u", ".join(failures)), message.user,
                                message.replyTo)]


moduleLoader = ModuleLoader()