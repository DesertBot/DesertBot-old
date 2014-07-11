# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup

from zope.interface import implements
from twisted.plugin import IPlugin
from twisted.python import log
from desertbot.moduleinterface import IModule, Module, ModuleType
from desertbot.message import IRCMessage
from desertbot.response import IRCResponse, ResponseType


class NowPlaying(Module):
    implements(IPlugin, IModule)

    name = u"nowplaying"
    triggers = [u"np"]
    moduleType = ModuleType.COMMAND
    helpText = u"np <last.fm user> - retrieves the last song the given last.fm user played"

    baseAPIAddress = "http://ws.audioscrobbler.com/1.0/user/"

    def onTrigger(self, message):
        """
        @type message: IRCMessage
        """
        if len(message.parameterList) == 0:
            return IRCResponse(ResponseType.PRIVMSG,
                               u"You didn't give me a last.fm user to check.",
                               message.user, message.replyTo)

        song = self._getSong(message.parameterList[0])

        if song is not None:
            return IRCResponse(ResponseType.PRIVMSG,
                               u"{} {}".format(song.title.text, song.link.text),
                               message.user, message.replyTo)
        else:
            return IRCResponse(ResponseType.PRIVMSG,
                               u"last.fm user '{}' either doesn't exist "
                               u"or hasn't scrobbled any music".format(message.parameters),
                               message.user, message.replyTo)

    def _getSong(self, user):
        if "urlutils" in self.bot.moduleHandler.loadedModules:
            urlutils = self.bot.moduleHandler.loadedModules["urlutils"]

            url = "http://ws.audioscrobbler.com/1.0/user/" + user + "/recenttracks.rss"

            feed = BeautifulSoup(urlutils.fetchURL(url).text)

            latestSong = feed.find('item')
            return latestSong

        else:
            log.err("WARNING: Module \"urlutils\" is required for the \"nowplaying\" module to "
                    "work.")
            return None

nowplaying = NowPlaying()