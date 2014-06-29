# -*- coding: utf-8 -*-
import subprocess
import re

from zope.interface import implements
from twisted.plugin import IPlugin

from desertbot.moduleinterface import IModule, Module, ModuleType, AccessLevel
from desertbot.message import IRCMessage
from desertbot.response import IRCResponse, ResponseType


class Update(Module):
    implements(IPlugin, IModule)

    name = u"update"
    triggers = [u"update"]
    moduleType = ModuleType.COMMAND
    accessLevel = AccessLevel.ADMINS
    helpText = u"update - updates the bot with the latest code from github"

    def onTrigger(self, message):
        """
        @type message: IRCMessage
        """
        subprocess.call(["git", "fetch"])

        output = subprocess.check_output(["git", "whatchanged", "..origin/master"])
        changes = re.findall("\n\n\s{4}(.+?)\n\n", output)

        if len(changes) == 0:
            return IRCResponse(ResponseType.PRIVMSG, u"The bot is already up to date!",
                               message.user, message.replyTo)

        changes = list(reversed(changes))
        response = u"New commits: {}".format(u" | ".join(changes))

        subprocess.call(["git", "pull"])

        return IRCResponse(ResponseType.PRIVMSG, response, message.user, message.replyTo)


update = Update()
