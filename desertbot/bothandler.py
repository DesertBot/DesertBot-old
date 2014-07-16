# -*- coding: utf-8 -*-
import sys

import os
from twisted.internet import reactor
from twisted.python import log
from desertbot.bot import DesertBotFactory
from desertbot.config import Config


class BotHandler(object):
    def __init__(self, cmdArgs):
        self.configs = {}
        for configFileName in cmdArgs.configs:
            if not configFileName.endswith(".yaml"):
                config = Config("{}.yaml".format(configFileName))
            else:
                config = Config(configFileName)
            if config.loadConfig():
                self.configs[config.configFileName] = config
        self.botfactories = {}
        for configFileName, configObject in self.configs.iteritems():
            self.startBotFactory(configObject)
        reactor.run()

    def startBotFactory(self, config):
        """
        @type config: Config
        """
        if config.configFileName in self.botfactories:
            # already on this server for some reason
            return False
        else:
            botfactory = DesertBotFactory(self, config)
            reactor.connectTCP(config["server"], config["port"], botfactory)
            self.botfactories[config.configFileName] = botfactory
            return True

    def stopBotFactory(self, configFileName, quitMessage=None):
        if quitMessage is None or not isinstance(quitMessage, unicode):
            quitMessage = u"FINE. I'LL GO.".encode("utf-8")
        else:
            quitMessage = quitMessage.encode("utf-8")
        if configFileName not in self.botfactories:
            # Not on this server at all!
            return False
        else:
            try:
                self.botfactories[configFileName].shouldReconnect = False
                self.botfactories[configFileName].bot.quit(quitMessage)
                self._unloadModules(self.botfactories[configFileName])
            except:
                # Bot is probably stuck mid-reconnection
                self.botfactories[configFileName].stopTrying()
            self.unregisterFactory(configFileName)
            return True

    def unregisterFactory(self, configFileName):
        if configFileName in self.botfactories:
            del self.botfactories[configFileName]

            if len(self.botfactories) == 0:
                # no more open connections
                reactor.callLater(2.0, reactor.stop)

    def restart(self, quitMessage=u'Restarting...'):
        quitMessage = quitMessage.encode("utf-8")
        for server, botfactory in self.botfactories.iteritems():
            botfactory.shouldReconnect = False
            botfactory.bot.quit(quitMessage)
            self._unloadModules(botfactory)
        reactor.callLater(2.0, self._replaceInstance)

    def shutdown(self, quitMessage=u"Shutting down..."):
        quitMessage = quitMessage.encode("utf-8")
        for server, botfactory in self.botfactories.iteritems():
            botfactory.shouldReconnect = False
            botfactory.bot.quit(quitMessage)
            self._unloadModules(botfactory)
        self.botfactories = {}
        reactor.callLater(4.0, reactor.stop)

    def _replaceInstance(self):
        reactor.stop()
        python = sys.executable
        os.execl(python, python, *sys.argv)

    def _unloadModules(self, botfactory):
        for module in botfactory.bot.moduleHandler.loadedModules.values():
            try:
                module.onModuleUnloaded(botfactory.bot)
            except Exception as e:
                errorMsg = "An error occured while unloading \"{}\" ({})".format(module.name, e)
                log.err(errorMsg)
        for post in botfactory.bot.moduleHandler.loadedPostProcesses.values():
            try:
                post.onModuleUnloaded(botfactory.bot)
            except Exception as e:
                errorMsg = "An error occured while unloading \"{}\" ({})".format(post.name, e)
                log.err(errorMsg)
