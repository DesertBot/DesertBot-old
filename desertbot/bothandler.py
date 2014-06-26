# -*- coding: utf-8 -*-
import os, sys
from desertbot.bot import DesertBotFactory
from desertbot.config import Config
from twisted.internet import reactor


class BotHandler(object):
    def __init__(self, cmdArgs):
        self.configs = {}
        for server in cmdArgs.servers:
            config = Config("{}.yaml".format(server))
            if config.loadConfig():
                self.configs[server] = config
        self.botfactories = {}
        for server, configObject in self.configs.iteritems():
            self.startBotFactory(configObject)
        reactor.run()

    def startBotFactory(self, config):
        """
        @type config: Config
        """
        if config["server"] in self.botfactories:
            #already on this server for some reason
            return False
        else: 
            botfactory = DesertBotFactory(config)
            reactor.connectTCP(config["server"], config["port"], botfactory)
            self.botfactories[config["server"]] = botfactory
            return True

    def stopBotFactory(self, server, quitMessage=None):
        if quitMessage is None or not isinstance(quitMessage, unicode):
            self.quitMessage = u"FINE. I'LL GO."
        else:
            self.quitMessage = quitMessage
        if server not in self.botfactories:
            #Not on this server at all!
            return False
        else:
            try:
                self.botfactories[server].bot.quit(quitMessage)
                for module in self.botfactories[server].bot.moduleHandler.loadedModules.values():
                    module.onModuleUnloaded()
                for post in self.botfactories[server].bot.moduleHandler.loadedPostProcesses.values():
                    post.onModuleUnloaded()
            except:
                #Bot is probably stuck mid-reconnection
                self.botfactories[server].stopTrying()
            self.unregisterFactory(server)
            return True

    def unregisterFactory(self, server):
        if server in self.botfactories:
            del self.botfactories[server]

            if len(self.botfactories) == 0:
                #no more open connections
                reactor.callLater(2.0, reactor.stop)

    def restart(self, quitMessage=u'Restarting...'):
        for server, botfactory in self.botfactories.iteritems():
            botfactory.bot.quit(quitMessage)
            for module in botfactory.bot.moduleHandler.loadedModules.values():
                module.onModuleUnloaded()
            for post in botfactory.bot.moduleHandler.loadedPostProcesses.values():
                post.onModuleUnloaded()
        reactor.callLater(2.0, self.replaceInstance)

    def replaceInstance(self):
        reactor.stop()
        python = sys.executable
        os.execl(python, python, *sys.argv)
