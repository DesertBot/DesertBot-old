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
    accessLevel = AccessLevel.ADMINS

    def getHelp(self, message):
        helpDict = {
            self.name: u"load/reload <module>, unload <module> - handles "
                       u"loading/unloading/reloading of modules.",
            u"load": u"load <module> [module]... - loads (or reloads) the given module(s). "
                     u"Use 'all' to reload all active modules.",
            u"reload": u"reload <module> [module]... - reloads (or loads) the given module(s). "
                       u"Use 'all' to reload all active modules.",
            u"unload": u"unload <module> [module]... - unloads the given module(s).",
        }
        return helpDict[message.parameterList[0]]

    def onTrigger(self, message):
        """
        @type message: IRCMessage
        """
        if len(message.parameterList) == 0:
            return IRCResponse(ResponseType.PRIVMSG, u"You didn't give a module name!",
                               message.user, message.replyTo)

        returns = {}
        for moduleName in message.parameterList:
            if message.command == u"load" or message.command == u"reload":
                isModule = self.bot.moduleHandler.loadModule(moduleName)
                if not isModule[0]:
                    returns[moduleName] = self.bot.moduleHandler.loadPostProcess(moduleName)
                else:
                    returns[moduleName] = isModule
            if message.command == u"unload":
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
                failures.append(u"{}".format(returnTuple[1]))
            else:
                successes.append(moduleName.lower())

        if len(failures) == 0:
            return IRCResponse(ResponseType.PRIVMSG,
                               u"Module(s) \"{}\" {}loaded successfully!".format(u", "
                                                                                 u"".join(
                                   successes),
                                                                                 "un" if
                                                                                 message.command ==
                                                                                         u"unload" else ""),
                               message.user, message.replyTo)
        elif len(successes) == 0:
            return IRCResponse(ResponseType.PRIVMSG,
                               u"{}".format(u", ".join(failures)), message.user,
                               message.replyTo)
        else:
            return [IRCResponse(ResponseType.PRIVMSG,
                                u"Module(s) \"{}\" {}loaded successfully!".format(u", "
                                                                                  u"".join(
                                    successes),
                                                                                  "un" if
                                                                                  message.command ==
                                                                                          u"unload" else ""),
                                message.user, message.replyTo),
                    IRCResponse(ResponseType.PRIVMSG,
                                u"{}".format(u", ".join(failures)),
                                message.user,
                                message.replyTo)]


moduleLoader = ModuleLoader()
