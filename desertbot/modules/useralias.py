# -*- coding: utf-8 -*-
import json
import os
from zope.interface import implements
from twisted.plugin import IPlugin
from twisted.python import log
from desertbot.moduleinterface import IModule, Module, ModuleType, AccessLevel
from desertbot.message import IRCMessage
from desertbot.response import IRCResponse, ResponseType


class UserAlias(Module):
    implements(IPlugin, IModule)

    name = u"useralias"
    triggers = [u"useralias"]
    moduleType = ModuleType.COMMAND
    accessLevel = AccessLevel.ADMINS

    def getHelp(self, message):
        """
        @type message: IRCMessage
        """
        helpDict = {
            self.name: u"useralias <create/remove> <user> <alias> - create and remove user aliases.",
            u"create": u"useralias create <user> <alias> - remember that <user> is actually <alias>.",
            u"remove": u"useralias remove <user> - forget who <user> actually is."
        }
        if len(message.parameterList) == 1:
            return helpDict[message.parameterList[0]]
        else:
            return helpDict[message.parameterList[1]]

    def onTrigger(self, message):
        """
        @type message: IRCMessage
        """
        subCommands = [u"create", u"remove"]
        if len(message.parameterList) == 0 or message.parameterList[0] not in subCommands:
            return IRCResponse(ResponseType.PRIVMSG, u"Do what with useralias?", message.user, message.replyTo)
        else:
            if message.parameterList[0] == u"create":
                if len(message.parameterList) != 3:
                    return IRCResponse(ResponseType.PRIVMSG, u"Improper use.", message.user, message.replyTo)
                else:
                    self.userAliases[message.parameterList[1]] = message.parameterList[2]
                    return IRCResponse(ResponseType.PRIVMSG,
                                       u"Okay, I will remember that \"{}\" is actually \"{}\".".format(
                                           message.parameterList[1], message.parameterList[2]), message.user,
                                       message.replyTo)
            elif message.parameterList[0] == u"remove":
                if len(message.parameterList) != 2:
                    return IRCResponse(ResponseType.PRIVMSG, u"Improper use.", message.user, message.replyTo)
                else:
                    del self.userAliases[message.parameterList[1]]
                    return IRCResponse(ResponseType.PRIVMSG,
                                       u"Okay, I will forget who \"{}\" actually is.".format(message.parameterList[1]),
                                       message.user, message.replyTo)

    def onModuleLoaded(self):
        configFileName = self.bot.factory.config.configFileName[:-5]
        if os.path.exists(os.path.join("data", configFileName, "userAliases.json")):
            with open(os.path.join("data", configFileName, "userAliases.json")) as jsonFile:
                userAliases = json.load(jsonFile)
            if len(userAliases) != 0:
                self.userAliases = userAliases
                log.msg("Loaded {} userAliases from userAliases file for config \"{}\".".format(len(userAliases),
                                                                                                configFileName))
            else:
                log.msg("UserAliases file for config \"{}\" is empty.".format(configFileName))
                self.userAliases = {}
        else:
            log.err("UserAliases file not found for config \"{}\"!".format(configFileName))
            self.userAliases = {}

    def onModuleUnloaded(self):
        configFileName = self.bot.factory.config.configFileName[:-5]
        if not os.path.exists(os.path.join("data", configFileName, "userAliases.json")):
            os.makedirs(os.path.join("data", configFileName))
        with open(os.path.join("data", configFileName, "userAliases.json"), "w") as jsonFile:
            json.dump(self.userAliases, jsonFile)

userAlias = UserAlias()
