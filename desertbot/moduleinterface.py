from enum import Enum
from zope.interface import Attribute, Interface


class IModule(Interface):
    name = Attribute("The module name.")
    trigger = Attribute("The command or message regex the module will trigger on.")
    messageTypes = Attribute("The message types this module will trigger on.")
    moduleType = Attribute("The module's type.")
    modulePriority = Attribute("The module's priority.")
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
    trigger = ""
    messageTypes = []
    moduleType = ModuleType.PASSIVE
    modulePriority = ModulePriority.NORMAL
    helpText = ""
    
    def onTrigger(message):
        pass
    
    def onModuleLoaded():
        pass
    
    def onModuleUnloaded():
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
