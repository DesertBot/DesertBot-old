# -*- coding: utf-8 -*-
from twisted.plugin import getPlugins
from desertbot.moduleinterface import IModule
from desertbot.desertbot import DesertBot
from desertbot.response import IRCResponse
from desertbot.message import IRCMessage
import desertbot.modules

class ModuleHandler(object):
    def __init__(self, bot):
        """
        @type bot: DesertBot
        """
        self.bot = bot
        self.loadedModules = {}
    
    def sendResponse(self, response):
        """
        @type response: IRCResponse
        """
        pass

    def handleMessage(self, message):
        """
        @type message: IRCMessage
        """
        pass
  
    def loadModule(self, name):
        """
        @type name: unicode
        """
        if name not in self.loadedModules:
            for module in getPlugins(IModule, desertbot.modules):
                if module.name == name:
                    self.loadedModules[name] = module
    
    def unloadModule(self, name):
        """
        @type name: unicode
        """
        if name in self.loadedModules:
            del self.loadedModules[name]
    
    def loadAllModules(self):
        for module in getPlugins(IModule, desertbot.modules):
            self.loadedModules[module.name] = module
