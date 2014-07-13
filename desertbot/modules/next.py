# -*- coding: utf-8 -*-
from zope.interface import implements
from twisted.plugin import IPlugin
from twisted.python import log
from desertbot.moduleinterface import IModule, Module, ModuleType
from desertbot.message import IRCMessage
from desertbot.response import IRCResponse, ResponseType


class Next(Module):
    implements(IPlugin, IModule)

    name = u"next"
    triggers = [u"next"]
    moduleType = ModuleType.COMMAND
    helpText = u"next - fetches the next event from the LRR streaming calendar"

    def onTrigger(self, message):
        """
        @type message: IRCMessage
        """
        cal = self.bot.moduleHandler.getModule("googlecalendar")
        if not cal:
            log.err("The \"googlecalendar\" module is required for \"next\" to work.")
            return

        nextEvent = cal.getNextEvent("loadingreadyrun.com_72jmf1fn564cbbr84l048pv1go@group.calendar.google.com")

        if nextEvent is None:
            return IRCResponse(ResponseType.PRIVMSG,
                               u"There don't appear to be any upcoming streams scheduled.",
                               message.user,
                               message.replyTo)

        return IRCResponse(ResponseType.PRIVMSG,
                           u"Next scheduled stream: {} at {} ({})".format(nextEvent["summary"],
                                                                          nextEvent["start"].strftime("%a %I:%M %p %Z"),
                                                                          nextEvent["till"]),
                           message.user,
                           message.replyTo)

nextModule = Next()