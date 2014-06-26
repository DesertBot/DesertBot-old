# -*- coding: utf-8 -*-
from zope.interface import Attribute, Interface
from response import ResponseType


class ModulePriority(object):
    HIGH = -2
    ABOVENORMAL = -1
    NORMAL = 0
    BELOWNORMAL = 1
    LOW = 2
    
    
class IPost(Interface):
    name = Attribute("The module name.")
    responseTypes = Attribute("The response types this module will trigger on.")
    modulePriority = Attribute("The module's priority.")
    runInThread = Attribute("Specifies if this module should be run in a separate thread.")
    helpText = Attribute("The text that will be sent when a user requests help for this module.")
    
    def onTrigger(response):
        """
        This function will be executed when the API triggers this module.
        """
    
    def shouldTrigger(response):
        """
        This function determines if this module should trigger on a response.
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
    name = u""
    responseTypes = [ResponseType.PRIVMSG, ResponseType.ACTION, ResponseType.NOTICE]
    modulePriority = ModulePriority.NORMAL
    runInThread = False
    helpText = u""
    
    def onTrigger(self, response):
        pass
    
    def shouldTrigger(self, response):
        if response.ResponseType in self.responseTypes:
            return True
            
    def onModuleLoaded(self):
        pass
        
    def onModuleUnloaded(self):
        pass
