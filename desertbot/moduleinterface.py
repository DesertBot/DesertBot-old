# -*- coding: utf-8 -*-
from enum import Enum
from zope.interface import Attribute, Interface


class IModule(Interface):
    name = Attribute("The module name.")
    triggers = Attribute("The list of commands or regexes this module will trigger on.")
    messageTypes = Attribute("The message types this module will trigger on.")
    moduleType = Attribute("The module's type.")
    accessLevel = Attribute("The module's accesslevel.")
    modulePriority = Attribute("The module's priority.")
    runInThread = Attribute("Specifies if this module should be run in a separate thread.")
    helpText = Attribute("The text that will be sent when a user requests help for this module.")
    
    def onTrigger(message):
        """
        This function will be executed when the API triggers this module.
        """
    
    def onModuleLoaded():
        """
        This function will be executed when the API loads this module.
        """
        
    def onModuleUnloaded():
        """
        This function will be executed when the API unloads this module.
        """
        
class Module(object):
    name = ""
    triggers = []
    messageTypes = []
    moduleType = ModuleType.PASSIVE
    accessLevel = AccessLevel.ANYONE
    modulePriority = ModulePriority.NORMAL
    runInThread = False
    helpText = ""
    
    def onTrigger(self, message):
        pass
    
    def onModuleLoaded(self):
        pass
    
    def onModuleUnloaded(self):
        pass


class ModuleType(Enum):
    PASSIVE = 1
    ACTIVE = 2
    COMMAND = 3
    POSTPROCESS = 4
    UTILITY = 5
    
    
class ModulePriority(object):
    HIGH = -2
    ABOVENORMAL = -1
    NORMAL = 0
    BELOWNORMAL = 1
    LOW = 2
    
    
class AccessLevel(Enum):
    ANYONE = 1
    ADMINS = 2
