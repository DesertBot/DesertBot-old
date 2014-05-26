from twisted.words.protocols import irc
from twisted.internet import protocol, reactor
from message import IRCMessage
from user import IRCUser
from channel import IRCChannel


class DesertBot(irc.IRCClient):
    channels = {}
    nickname = "DesertBot"
    def __init__(self):
        pass

    def signedOn(self):
        for channel in self.channels.keys():
            self.join(channel)

    def nickChanged(self, nick):
        self.nickname = nick

    def privmsg(self, user, channel, msg):
        message = IRCMessage('PRIVMSG', self.getUser(user, channel), self.getChannel(channel), msg)
        pass

    def action(self, user, channel, msg):
        message = IRCMessage('ACTION', self.getUser(user, channel), self.getChannel(channel), msg)
        pass

    def noticed(self, user, channel, msg):
        message = IRCMessage('NOTICE', self.getUser(user, channel), self.getChannel(channel), msg.upper())
        pass

    def irc_JOIN(self, prefix, params):
        message = IRCMessage('JOIN', self.getUser(prefix, params[0]), self.getChannel(params[0]), '')
        pass

    def irc_PART(self, prefix, params):
        partMessage = u''
        if len(params) > 1:
            partMessage = u', message: ' + u' '.join(params[1:])
        message = IRCMessage('PART', self.getUser(prefix, params[0]), self.getChannel(params[0]), partMessage)
        pass

    def irc_KICK(self, prefix, params):
        kickMessage = u''
        if len(params) > 2:
            kickMessage = u', message: ' + u' '.join(params[2:])
        message = IRCMessage('KICK', self.getUser(prefix, params[0]), self.getChannel(params[0]), kickMessage)
        kickee = params[1]
        pass

    def irc_QUIT(self, prefix, params):
        quitMessage = u''
        if len(params) > 0:
            quitMessage = u', message: ' + u' '.join(params[0])
        for key in self.channels:
            channel = self.channels[key]
            message = IRCMessage('QUIT', self.getUser(prefix, channel), channel, quitMessage)
            pass

    def getChannel(self, channel):
        """
        @type channel: str
        @rtype: IRCChannel
        """
        if channel in self.channels:
            return self.channels[channel]
        return None

    def getUser(self, user, channel):
        """
        @type user: str
        @type channel: str
        @rtype: IRCUser
        """
        if user in self.channels[channel]:
            return self.channels[channel].users[user]
        return None

class DesertBotFactory(protocol.ReconnectingClientFactory):
    def __init__(self):
        pass

    def startedConnecting(self, connector):
        pass

    def buildProtocol(self, addr):
        self.resetDelay()
        return self.protocol

    def clientConnectionLost(self, connector, unused_reason):
        pass

    def clientConnectionFailed(self, connector, reason):
        pass