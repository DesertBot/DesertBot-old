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
    triggers = [u"next", u"nextfan"]
    moduleType = ModuleType.COMMAND

    def getHelp(self, message):
        """
        @type message: IRCMessage
        """
        helpDict = {
            u"next": u"next [timezone] - fetches the next event from the LRR streaming calendar",
            u"nextfan": u"nextfan [timezone] - fetches the next event from the "
                        u"LRR Fan-streamers calendar",
        }
        return helpDict[message.parameterList[0]]

    def onTrigger(self, message):
        """
        @type message: IRCMessage
        """
        cal = self.bot.moduleHandler.getModule("googlecalendar")
        if not cal:
            log.err("The \"googlecalendar\" module is required for \"next\" to work.")
            return

        calendar = None
        if message.command == u"next":
            calendar = "loadingreadyrun.com_72jmf1fn564cbbr84l048pv1go@group.calendar.google.com"
        elif message.command == u"nextfan":
            calendar = "caffeinatedlemur@gmail.com"

        if len(message.parameterList) > 0:  # timezone specified?
            nextEvent = cal.getNextEvent(calendar, message.parameterList[0])
        else:
            nextEvent = cal.getNextEvent(calendar)

        if nextEvent is None:
            return IRCResponse(ResponseType.PRIVMSG,
                               u"There don't appear to be any upcoming streams scheduled.",
                               message.user,
                               message.replyTo)

        shortDate = nextEvent["start"].strftime("%a %I:%M %p %Z")
        return IRCResponse(ResponseType.PRIVMSG,
                           u"Next scheduled stream: {} at {} ({})".format(nextEvent["summary"],
                                                                          shortDate,
                                                                          nextEvent["till"]),
                           message.user,
                           message.replyTo)

nextModule = Next()