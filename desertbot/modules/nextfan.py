# -*- coding: utf-8 -*-
from collections import OrderedDict
import datetime
from dateutil.tz import tzutc

from zope.interface import implements
from twisted.plugin import IPlugin
from twisted.python import log
from desertbot.moduleinterface import IModule, Module, ModuleType
from desertbot.message import IRCMessage
from desertbot.response import IRCResponse, ResponseType


class NextFanstream(Module):
    implements(IPlugin, IModule)

    name = u"nextfan"
    triggers = [u"nextfan"]
    moduleType = ModuleType.COMMAND
    helpText = u"nextfan - fetches the next event from the LRR Fan-streamers calendar"

    def onTrigger(self, message):
        """
        @type message: IRCMessage
        """
        cal = self.bot.moduleHandler.getModule("googlecalendar")
        if not cal:
            log.err("The \"googlecalendar\" module is required for \"next\" to work.")
            return

        nextEvent = cal.getNextEvent("caffeinatedlemur@gmail.com")

        if nextEvent is None:
            return IRCResponse(ResponseType.PRIVMSG,
                               u"There don't appear to be any upcoming streams scheduled.",
                               message.user,
                               message.replyTo)

        return IRCResponse(ResponseType.PRIVMSG,
                           u"Next scheduled fanstream: {} in {}".format(nextEvent["summary"],
                                                                        nextEvent["till"]),
                           message.user,
                           message.replyTo)

nextFanstream = NextFanstream()