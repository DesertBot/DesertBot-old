# -*- coding: utf-8 -*-
import json

from zope.interface import implements
from twisted.plugin import IPlugin

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
        # TODO Load admins in from JSON (data/admins.json?) and store as self.bot.admins
        pass

    def onModuleUnloaded(self):
        # TODO Store admins to JSON (data/admins.json?) from self.bot.admins
        pass
        
admin = Admin()
