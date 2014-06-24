# -*- coding: utf-8 -*-

from zope.interface import implements
from twisted.plugin import IPlugin
from desertbot.moduleinterface import IModule, Module


class ExampleModule(Module):
    implements(IPlugin, IModule)
    
    name = u"examplemodule"
    messageTypes = [u"PRIVMSG"]
    helpText = "This example module outputs PRIVMSG-es to console!"
    
    def onTrigger(self, message):
        print message.messageText

exampleModule = ExampleModule()
