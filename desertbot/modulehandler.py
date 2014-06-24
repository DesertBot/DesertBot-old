# -*- coding: utf-8 -*-
from twisted.plugin import getPlugins
from desertbot.moduleinterface import IModule, ModuleType, ModulePriority, AccessLevel
from desertbot.desertbot import DesertBot
from desertbot.response import IRCResponse
from desertbot.message import IRCMessage
import desertbot.modules
import re

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

    def _shouldExecute(self, module, message):
        if message.messageType in module.messageTypes:
            if module.moduleType == ModuleType.PASSIVE:
                return True
            elif message.user.nickname == self.bot.nickname:
                return False
            elif module.moduleType == ModuleType.ACTIVE:
                pass
            elif module.moduleType == ModuleType.COMMAND:
                pass
            elif module.moduleType == ModuleType.POSTPROCESS:
                pass
            elif module.moduleType == ModuleType.UTILITY:
                pass

    def _checkCommandAuthorization(self, module, message):
        if module.accessLevel == AccessLevel.ANYONE:
            return True

        if module.accessLevel == AccessLevel.ADMINS:
            for adminRegex in self.bot.admins:
                if re.match(adminRegex, message.user.getUserString()):
                    return True
            return False

    def loadModule(self, name):
        """
        @type name: unicode
        """
        if name.lower() not in self.loadedModules:
            moduleReload = False
            # not a reload, log something for this? A boolean for later return perhaps?
        else:
            moduleReload = True
            # totes a reload. Log/boolean?
        for module in getPlugins(IModule, desertbot.modules):
            if module.name == name.lower():
                self.loadedModules[module.name] = module
                self.loadedModules[module.name].onModuleLoaded()
                if moduleReload:
                    return (True, "{} reloaded!".format(module.name))
                else:
                    return (True, "{} loaded!".format(module.name))
                #TODO Return stuff and also log
        return (False, "No module named '{}' could be found!".format(name))
        #if we get here, there is no such module. Throw exception?

    def unloadModule(self, name):
        """
        @type name: unicode
        """
        if name.lower() in self.loadedModules:
            self.loadedModules[name.lower()].onModuleUnloaded()
            del self.loadedModules[name.lower()]
            return (True, "{} unloaded!".format(name))
            #TODO Return stuff and log
        return (False, "No module named '{}' is loaded!".format(name)
    
    def loadAllModules(self):
        for module in getPlugins(IModule, desertbot.modules):
            self.loadedModules[module.name.lower()] = module
            self.loadedModules[module.name.lower()].onModuleLoaded()
            #TODO Return stuff and log
        return (True, "All modules successfully loaded!")
