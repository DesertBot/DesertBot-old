# -*- coding: utf-8 -*-
import json
import os
import re
from zope.interface import implements
from twisted.plugin import IPlugin
from twisted.python import log
from desertbot.moduleinterface import IModule, Module, ModuleType, AccessLevel
from desertbot.message import IRCMessage
from desertbot.response import IRCResponse, ResponseType


class Ignore(Module):
    implements(IPlugin, IModule)

    name = u"ignore"
    triggers = [u"ignore", u"unignore"]
    moduleType = ModuleType.PASSIVE
    accessLevel = AccessLevel.ADMINS
    modulePriority = -40  # Very high priority, should be lower than admin and logging

    def getHelp(self, message):
        """
        @type message: IRCMessage
        """
        helpDict = {
            u"ignore": u"ignore <user> <module> [module] - prevents the specified user "
            u"from using the specified module(s).",
            u"unignore": u"unignore <user> - stops ignoring the specified user."
        }
        return helpDict[message.parameterList[0]]

    def onTrigger(self, message):
        """
        @type message: IRCMessage
        """
        if message.command == u"ignore":
            if len(message.parameterList) == 0:
                return IRCResponse(ResponseType.PRIVMSG, u"Ignore who?", message.user, message.replyTo)
            else:
                message.bot.dataStore["ignores"][message.parameterList[0]] = message.parameterList[1:]
                return IRCResponse(ResponseType.PRIVMSG,
                                   u"Now ignoring: \"{}\".".format(message.parameterList[0]),
                                   message.user, message.replyTo)
        elif message.command == u"unignore":
            if len(message.parameterList) == 0:
                return IRCResponse(ResponseType.PRIVMSG, u"Unignore who?", message.user, message.replyTo)
            elif message.parameterList[0] not in message.bot.dataStore["ignores"]:
                return IRCResponse(ResponseType.PRIVMSG, u"I am not ignoring \"{}\"!".format(message.parameterList[0]),
                                   message.user, message.replyTo)
            else:
                del message.bot.dataStore["ignores"][(message.parameterList[0])]
                return IRCResponse(ResponseType.PRIVMSG, u"No longer ignoring \"{}\".".format(message.parameterList[0]),
                                   message.user, message.replyTo)
        else:
            for userRegex in message.bot.dataStore["ignores"].keys():
                if re.match(userRegex, message.user.getUserString()):
                    if message.bot.dataStore["ignores"][userRegex] == u"all":
                        message.clear()
                    else:
                        for moduleName in message.bot.dataStore["ignores"][userRegex]:
                            module = message.bot.moduleHandler.getModule(moduleName)
                            if module is not None:
                                if message.bot.moduleHandler._shouldTrigger(module, message):
                                    message.clear()

    def onModuleLoaded(self, bot):
        configFileName = bot.factory.config.configFileName[:-5]
        if os.path.exists(os.path.join("data", configFileName, "ignores.json")):
            with open(os.path.join("data", configFileName, "ignores.json")) as jsonFile:
                ignores = json.load(jsonFile)
            if len(ignores) != 0:
                bot.dataStore["ignores"] = ignores
                log.msg("Loaded {} ignores from ignores file for config \"{}\".".format(len(ignores),
                                                                                        configFileName))
            else:
                log.msg("Ignores file for config \"{}\" is empty.".format(configFileName))
                bot.dataStore["ignores"] = {}
        else:
            log.err("Ignores file not found for config \"{}\"!".format(configFileName))
            bot.dataStore["ignores"] = {}

    def onModuleUnloaded(self, bot):
        configFileName = bot.factory.config.configFileName[:-5]
        if not os.path.exists(os.path.join("data", configFileName)):
            os.makedirs(os.path.join("data", configFileName))
        with open(os.path.join("data", configFileName, "admins.json"), "w") as jsonFile:
            json.dump(bot.dataStore["ignores"], jsonFile)


ignore = Ignore()