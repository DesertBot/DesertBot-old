# -*- coding: utf-8 -*-
import json
import os

from zope.interface import implements
from twisted.plugin import IPlugin
from twisted.python import log

from desertbot.moduleinterface import IModule, Module, ModuleType, AccessLevel
from desertbot.message import IRCMessage
from desertbot.response import IRCResponse, ResponseType


class Admin(Module):
    implements(IPlugin, IModule)
    
    name = u"admin"
    triggers = [u"admin", u"unadmin", u"admins"]
    moduleType = ModuleType.COMMAND
    accessLevel = AccessLevel.ADMINS
    
    def getHelp(self, message):
        """
        @type message: IRCMessage
        """
        helpDict = {
            self.name: u"admin <user>, unadmin <user>, admins -- adds/removes from admins and lists current ones.",
            u"admin": u"admin <user> -- adds the specified userstring to the admins list.",
            u"unadmin": u"unadmin <user> -- removes the specified userstring from the admins list.",
            u"admins": u"admins -- gives you a list of current admins",
        }
        return helpDict[message.parameterList[0]]
        
    def onTrigger(self, message):
        """
        @type message: IRCMessage
        """
        # TODO Command parsing
        # TODO Make sure we always work against self.bot.admins as the admin-list
        pass
        
    def onModuleLoaded(self):
        configFileName = self.bot.factory.config.configFileName[:-5]
        if os.path.exists(os.path.join("data", configFileName, "admins.json")):
            with open(os.path.join("data", configFileName, "admins.json")) as jsonFile:
                admins = json.load(jsonFile)
            if len(admins) != 0:
                self.bot.admins = admins
                log.msg("Loaded {} admins from admins file for config \"{}\".".format(len(admins), configFileName))
            else:
                log.msg("Admins file for config \"{}\" is empty.".format(configFileName))
                self.bot.admins = []
        else:
            log.err("Admins file not found for config \"{}\"!".format(configFileName))
            self.bot.admins = []

    def onModuleUnloaded(self):
        configFileName = self.bot.factory.config.configFileName[:-5]
        if not os.path.exists(os.path.join("data", configFileName, "admins.json")):
            os.makedirs(os.path.join("data", configFileName))
        with open(os.path.join("data", configFileName, "admins.json"), "w") as jsonFile:
            json.dump(self.bot.admins, jsonFile)

        
admin = Admin()
