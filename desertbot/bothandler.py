import os, sys
from desertbot.desertbot import DesertBotFactory
from desertbot.config import Config
from twisted.internet import reactor
from twisted.python import log


class BotHandler:
    def __init__(self, cmdArgs):
        self.configs = {}
        for server in cmdArgs.servers:
            self.configs[server] = Config(server)
            self.configs[server].loadConfig()
        self.botfactories = {}
        for server, configObject in self.configs.iteritems():
            self.startBotFactory(configObject)

    def startBotFactory(self, config):
        """
        @type config: Config
        """
        if config["server"] in self.botfactories:
            #already on this server for some reason
            return False
        else:
            botfactory = DesertBotFactory(config)
            self.botfactories[config["server"]] = botfactory
            return True

    def stopBotFactory(self, server, quitMessage=None):
        if quitMessage is None or type(quitMessage) != unicode:
            self.quitMessage = u"FINE. I'LL GO."
        else:
            self.quitMessage = quitMessage
        if server not in self.botfactories:
            #Not on this server at all!
            return False
        else:
            try:
                self.botfactories[server].bot.quit(quitMessage)
                #TODO Unload the modules aswell, incase we have onUnload stuff.
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
            #TODO Once again, unload modules, or at least do module.onUnload()
        reactor.callLater(2.0, self.replaceInstance)

    def replaceInstance(self):
        reactor.stop()
        python = sys.executable
        os.execl(python, python, *sys.argv)
