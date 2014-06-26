# -*- coding: utf-8 -*-

from zope.interface import implements
from twisted.plugin import IPlugin
from desertbot.moduleinterface import IModule, Module
from desertbot.message import IRCMessage


class ExampleModule(Module):
    implements(IPlugin, IModule)
    
    name = u"examplemodule"
    messageTypes = [u"PRIVMSG"]
    helpText = u"This example module outputs PRIVMSG-es to console!"
    
    def onTrigger(self, message):
        """
        @type message: IRCMessage
        """
        print message.messageString

exampleModule = ExampleModule()
