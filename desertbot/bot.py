from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from desertbot.config import Config
from desertbot.factory import DesertBotFactory
from desertbot.modulehandler import ModuleHandler
from desertbot.utils.timeutils import now
import os, shelve, sys

# Try to enable SSL support
try:
    from twisted.internet import ssl
except ImportError:
    ssl = None


class DesertBot(object):
    def __init__(self, configFile):
        self.config = Config(configFile)
        self.connectionFactory = DesertBotFactory(self)
        self.log = None
        self.moduleHandler = ModuleHandler(self)
        self.servers = {}
        self.storage = None
        self.storageSync = None
        self.startTime = now()

    def startup(self):
        if ssl is None:
            self.log.warn("The PyOpenSSL package was not found. You will not be able to connect to servers using SSL.")
        self.log.info("Loading configuration file...")
        self.config.loadConfig()
        self.log.info("Loading storage...")
        self.storage = shelve.open(self.config.itemWithDefault("storage_path", "desertbot.db"))
        self.storageSync = LoopingCall(self.storage.sync)
        self.storageSync.start(self.config.itemWithDefault("storage_sync_interval", 5), now=False)
        self.log.info("Loading modules...")
        self.moduleHandler.loadAllModules()
        self.log.info("Initiating connections...")
        self._initiateConnections()
        self.log.info("Starting reactor...")
        reactor.run()

    def _initiateConnections(self):
        for server in self.config["servers"].iterkeys():
            self.connectServer(server)

    def connectServer(self, host):
        if host in self.servers:
            error = "A connection to {} was requested, but already exists.".format(host)
            self.log.warn(error)
            return error
        if host not in self.config["servers"]:
            error = "A connection to {} was requested, but there is no config data for this server.".format(host)
            self.log.warn(error)
            return error
        port = int(self.config.serverItemWithDefault(host, "port", 6667))
        if self.config.serverItemWithDefault(host, "ssl", False):
            self.log.info("Attempting secure connection to {host}/{port}...", host=host, port=port)
            if ssl is not None:
                reactor.connectSSL(host, port, self.connectionFactory, ssl.ClientContextFactory())
            else:
                self.log.error("Can't connect to {host}/{port}; PyOpenSSL is required to allow secure connections.",
                               host=host, port=port)
        else:
            self.log.info("Attempting connection to {host}/{port}...", host=host, port=port)
            reactor.connectTCP(host, port, self.connectionFactory)

    def disconnectServer(self, host, quitMessage = "Quitting..."):
        if host not in self.servers:
            error = "A disconnect from {} was requested, but this connection doesn't exist.".format(host)
            self.log.warn(error)
            return error
        self.servers[host].disconnect(quitMessage, True)

    def reconnectServer(self, host, quitMessage = "Reconnecting..."):
        if host not in self.servers:
            error = "A reconnect to {} was requested, but this connection doesn't exist.".format(host)
            self.log.warn(error)
            return error
        self.servers[host].disconnect(quitMessage)

    def shutdown(self, quitMessage = "Shutting down..."):
        serversCopy = self.servers.copy()
        for server in serversCopy.itervalues():
            server.disconnect(quitMessage, True)

    def restart(self, quitMessage = "Restarting..."):
        reactor.addSystemEventTrigger("after", "shutdown", lambda: os.execl(sys.executable, sys.executable, *sys.argv))
        self.shutdown(quitMessage)

    def countConnections(self):
        if len(self.servers) == 0:
            self.log.info("No more connections alive, shutting down...")
            # If we have any connections that have been started but never finished, stop trying
            self.connectionFactory.stopTrying()
            self.log.info("Closing storage...")
            if self.storageSync.running:
                self.storageSync.stop()
            self.storage.close()
            self.log.info("Unloading modules...")
            self.moduleHandler.unloadAllModules()
            self.log.info("Stopping reactor...")
            reactor.stop()
