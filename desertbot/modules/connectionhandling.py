# -*- coding: utf-8 -*-
from zope.interface import implements
from twisted.plugin import IPlugin
from desertbot.moduleinterface import IModule, Module, ModuleType, AccessLevel
from desertbot.message import IRCMessage
from desertbot.response import IRCResponse, ResponseType


class ConnectionHandling(Module):
    implements(IPlugin, IModule)

    name = u"connectionhandling"
    triggers = [u"connect", u"quit", u"quitfrom", u"restart", u"shutdown"]
    moduleType = ModuleType.COMMAND
    accessLevel = AccessLevel.ADMINS
    helpText = u"connect <server> <channel> / quit / quitfrom <server> / restart / shutdown - handle bot connections"

    def onTrigger(self, message):
        """
        @type message: IRCMessage
        """
        if message.command.lower() == u"connect":
            pass
        if message.command.lower() == u"quit":
            pass
        if message.command.lower() == u"quitfrom":
            pass
        if message.command.lower() == u"restart":
            pass
        if message.command.lower() == u"shutdown":
            pass

connectionhandling = ConnectionHandling()