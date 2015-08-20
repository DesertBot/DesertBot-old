from twisted.internet.protocol import ClientFactory, ReconnectingClientFactory
from desertbot.connection import DesertBotConnection


class DesertBotFactory(ReconnectingClientFactory):
    protocol = DesertBotConnection

    def __init__(self, bot):
        self.bot = bot
        self.currentlyDisconnecting = []

    def buildProtocol(self, addr):
        self.resetDelay()
        return self.protocol(self.bot)

    def clientConnectionFailed(self, connector, reason):
        self.bot.log.info("Client connection to {connector.host} failed (Reason: {reason.value}).",
                          connector=connector, reason=reason)
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

    def clientConnectionLost(self, connector, reason):
        # Disable modules
        if connector.host in self.bot.moduleHandler.enabledModules:
            del self.bot.moduleHandler.enabledModules[connector.host]

        del self.bot.servers[connector.host]

        # Check whether or not we should reconnect
        if connector.host in self.currentlyDisconnecting:
            self.bot.log.info("Connection to {connector.host} was closed cleanly.", connector=connector)
            ClientFactory.clientConnectionLost(self, connector, reason)
            self.currentlyDisconnecting.remove(connector.host)
            self.bot.countConnections()
        else:
            ReconnectingClientFactory.clientConnectionLost(self, connector, reason)
