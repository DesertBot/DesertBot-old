# -*- coding: utf-8 -*-
import datetime

from zope.interface import implements
from twisted.plugin import IPlugin
from twisted.python import log

from desertbot.moduleinterface import IModule, Module, ModuleType, AccessLevel
from desertbot.message import IRCMessage
from desertbot.response import IRCResponse, ResponseType
from desertbot.config import Config


class ConnectionHandling(Module):
    implements(IPlugin, IModule)

    name = u"connectionhandling"
    triggers = [u"connect", u"quit", u"quitfrom", u"restart", u"shutdown"]
    moduleType = ModuleType.COMMAND
    accessLevel = AccessLevel.ADMINS
    helpText = u"connect <server> [server] / quit / quitfrom <server> / restart / shutdown - " \
               u"handle bot connections"

    def onTrigger(self, message):
        """
        @type message: IRCMessage
        """
        if message.command == u"connect":
            if len(message.parameterList) == 0:
                return IRCResponse(ResponseType.PRIVMSG, u"Connect where?", message.user,
                                   message.replyTo)
            for server in message.parameterList:
                try:
                    config = Config("{}.yaml".format(server))
                    if config.loadConfig():
                        self.bot.bothandler.configs[server] = config
                        self.bot.bothandler.startBotFactory(config)
                        return IRCResponse(ResponseType.PRIVMSG,
                                           u"Connecting to \"{}\"...".format(server),
                                           message.user, message.replyTo)
                    else:
                        return IRCResponse(ResponseType.PRIVMSG, 
                                           u"Couldn't connect to \"{}\".".format(server),
                                           message.user, message.replyTo)
                except Exception as e:
                    log.err("Failed to connect to \"{}\" ({})".format(server, e))
                    return IRCResponse(ResponseType.PRIVMSG, 
                                       u"Could not connect to \"{}\" ({})".format(server, e),
                                       message.user, message.replyTo)
        if message.command == u"quit":
            if datetime.datetime.utcnow() > self.bot.startTime + datetime.timedelta(seconds = 10):
                self.bot.factory.shouldReconnect = False
                self.bot.bothandler.stopBotFactory(self.bot.factory.config["server"], None)
        if message.command == u"quitfrom":
            if len(message.parameterList) == 0:
                return IRCResponse(ResponseType.PRIVMSG, u"Quit from where?", message.user,
                                   message.replyTo)
            for server in message.parameterList:
                pass
        if message.command == u"restart":
            if datetime.datetime.utcnow() > self.bot.startTime + datetime.timedelta(seconds = 10):
                self.bot.bothandler.restart()
        if message.command == u"shutdown":
            if datetime.datetime.utcnow() > self.bot.startTime + datetime.timedelta(seconds = 10):
                self.bot.bothandler.shutdown()


connectionhandling = ConnectionHandling()
