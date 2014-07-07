# -*- coding: utf-8 -*-
from zope.interface import implements
from twisted.plugin import IPlugin

from desertbot.moduleinterface import IModule, Module, ModuleType, AccessLevel
from desertbot.message import IRCMessage
from desertbot.response import IRCResponse, ResponseType


class Nick(Module):
    implements(IPlugin, IModule)

    name = u"nick"
    triggers = [u"nick"]
    moduleType = ModuleType.COMMAND
    accessLevel = AccessLevel.ADMINS
    helpText = u"nick <newnick> - changes the bot's nick to newnick."

    def onTrigger(self, message):
        """
        @type message: IRCMessage
        """

        if len(message.parameterList) == 0:
            return IRCResponse(ResponseType.PRIVMSG,
                               u"You didn't give a nick for me to change to.",
                               message.user, message.replyTo)

        self.bot.setNick(message.parameterList[0].encode('utf-8'))


nick = Nick()
