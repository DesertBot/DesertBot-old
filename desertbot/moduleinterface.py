# -*- coding: utf-8 -*-
from enum import Enum
from zope.interface import Attribute, Interface


class ModuleType(Enum):
    PASSIVE = 1
    ACTIVE = 2
    COMMAND = 3
    UTILITY = 4


class ModulePriority(object):
    HIGH = -2
    ABOVENORMAL = -1
    NORMAL = 0
    BELOWNORMAL = 1
    LOW = 2


class AccessLevel(Enum):
    ANYONE = 1
    ADMINS = 2


class IModule(Interface):
    name = Attribute("The module name.")
    triggers = Attribute("The list of commands or regexes this module will trigger on.")
    messageTypes = Attribute("The message types this module will trigger on.")
    moduleType = Attribute("The module's type.")
    accessLevel = Attribute("The module's accesslevel.")
    modulePriority = Attribute("The module's priority.")
    runInThread = Attribute("Specifies if this module should be run in a separate thread.")
    helpText = Attribute("The text that will be sent when a user requests help for this module.")

    def hookBot(bot):
        """
        This function will hook a bot reference to the module.
        """

    def getHelp(message):
        """
        This function returns the module's helpText, unless overridden to perform
        more complex help-related tasks.
        """

    def onTrigger(message):
        """
        This function will be executed when the API triggers this module.
        """

    def shouldTrigger(message):
        """
        This function determines if this module should trigger on a message.
        It is only used for UTILITY modules.
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
    triggers = []
    messageTypes = [u"PRIVMSG"]
    moduleType = ModuleType.PASSIVE
    accessLevel = AccessLevel.ANYONE
    modulePriority = ModulePriority.NORMAL
    runInThread = False
    helpText = u""

    def hookBot(self, bot):
        self.bot = bot

    def getHelp(self, message):
        if self.helpText == u"":
            return u"{} doesn't have any help text yet. Tell my admins to stop being lazy!".format(
                self.name)
        return self.helpText

    def onTrigger(self, message):
        pass

    def shouldTrigger(self, message):
        return False

    def onModuleLoaded(self):
        pass

    def onModuleUnloaded(self):
        pass
