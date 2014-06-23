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
        pass #TODO Toss the IRCMessage at loadedModules and see what happens.
             #TODO a _shouldExecute of some form
  
    def loadModule(self, name):
        """
        @type name: unicode
        """
        if name.lower() not in self.loadedModules:
            # not a reload, log something for this? A boolean for later return perhaps?
        else:
            # totes a reload. Log/boolean?
        for module in getPlugins(IModule, desertbot.modules):
            if module.name == name.lower():
                self.loadedModules[module.name] = module
                self.loadedModules[module.name].onModuleLoaded()
                break
                #TODO Return stuff and also log
        #if we get here, there is no such module. Throw exception?

    def unloadModule(self, name):
        """
        @type name: unicode
        """
        if name.lower() in self.loadedModules:
            self.loadedModules[name.lower()].onModuleUnloaded()
            del self.loadedModules[name.lower()]
            #TODO Return stuff and log
    
    def loadAllModules(self):
        for module in getPlugins(IModule, desertbot.modules):
            self.loadedModules[module.name.lower()] = module
            self.loadedModules[module.name.lower()].onModuleLoaded()
            #TODO Return stuff and log
