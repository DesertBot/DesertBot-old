# -*- coding: utf-8 -*-
import subprocess

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
    helpText = u"update - updates the bot with the latest code from GitHub."

    def onTrigger(self, message):
        """
        @type message: IRCMessage
        """
        subprocess.call(["git", "fetch"])

        output = subprocess.check_output(["git", "log", "--no-merges",
                                          "--pretty=format:%s %b", "..origin/master"])
        changes = [s.strip() for s in output.splitlines()]

        if len(changes) == 0:
            return IRCResponse(ResponseType.PRIVMSG, u"The bot is already up to date!",
                               message.user, message.replyTo)

        changes = list(reversed(changes))
        response = u"New commits: {}".format(u" | ".join(changes))

        returnCode = subprocess.call(["git", "merge", "origin/master"])

        if returnCode != 0:
            return IRCResponse(ResponseType.PRIVMSG,
                               u"Merge after update failed, please merge manually.",
                               message.user, message.replyTo)

        subprocess.call(["pip", "install", "-r", "requirements.txt"])

        return IRCResponse(ResponseType.PRIVMSG, response, message.user, message.replyTo)


update = Update()
