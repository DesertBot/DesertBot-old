from twisted.words.protocols import irc
from twisted.internet import protocol, reactor
from message import IRCMessage
from user import IRCUser
from channel import IRCChannel
from serverinfo import ServerInfo, ModeType
import os
import yaml


class DesertBot(irc.IRCClient):
    def __init__(self, factory):
        """
        @type factory: DesertBotFactory
        """
        self.factory = factory
        self.channels = {}
        self.nickname = factory.config["nickname"]
        self.username = factory.config["username"]
        self.realname = factory.config["realname"]
        self.commandChar = factory.config["commandChar"]
        self.admins = factory.config["admins"]
        self.serverInfo = ServerInfo(factory.config["server"])
        #assuming, for now, that channels and admins would be in the config as lists

    def signedOn(self):
        for channel in self.factory.config["channels"]:
            self.join(channel)

    def nickChanged(self, nick):
        self.nickname = nick

    def modeChanged(self, user, channel, set, modes, args):
        pass

    def irc_TOPIC(self, prefix, params):
        pass

    def irc_RPL_TOPIC(self, prefix, params):
        pass

    def isupport(self, options):
        for item in options:
            if "=" in item:
                token = item.split("=")
                if token[0] == "CHANTYPES":
                    self.serverInfo.chanTypes = token[1]
                elif token[0] == "CHANMODES":
                    modes = token[1].split(",")
                    for mode in modes[0]:
                        self.serverInfo.chanModes[mode] = ModeType.LIST
                    for mode in modes[1]:
                        self.serverInfo.chanModes[mode] = ModeType.PARAM_SET_UNSET
                    for mode in modes[2]:
                        self.serverInfo.chanModes[mode] = ModeType.PARAM_SET
                    for mode in modes[3]:
                        self.serverInfo.chanModes[mode] = ModeType.NORMAL
                elif token[0] == "NETWORK":
                    self.serverInfo.network = token[1]
                elif token[0] == "PREFIX":
                    prefixes = token[1]
                    statusModes = prefixes[:prefixes.find(")")]
                    statusChars = prefixes[prefixes.find(")"):]
                    self.serverInfo.prefixOrder = statusModes
                    for i in range(len(statusModes)):
                        self.serverInfo.prefixesModeToChar[statusModes[i]] = statusChars[i]
                        self.serverInfo.prefixesCharToMode[statusChars[i]] = statusModes[i]
                elif token[0] == "NICKLEN":
                    self.serverInfo.nickLength = int(token[1])

    def irc_RPL_NAMREPLY(self, prefix, params):
        channel = self.getChannel(params[2])
        if channel.namesListCompete:
            channel.namesListCompete = False
            channel.users.clear()
            channel.ranks.clear()

        channelUsers = params[3].strip().split(" ")
        for channelUser in channelUsers:
            rank = ""

            if channelUser[0] in self.serverInfo.prefixesCharToMode:
                rank = self.serverInfo.prefixesCharToMode[channelUser[0]]
                channelUser = channelUser[1:]

            user = self.getUser(channelUser)
            if not user:
                user = IRCUser("{}!{}@{}".format(channelUser, None, None))

            channel.users[user.nickname] = user
            channel.ranks[user.nickname] = rank

    def irc_RPL_ENDOFNAMES(self, prefix, params):
        channel = self.getChannel(params[1])
        channel.namesListCompete = True

    def irc_RPL_WHOREPLY(self, prefix, params):
        channel = self.getChannel(params[1])
        user = channel.users[params[5]]

        if not user:
            user = IRCUser("{}!{}@{}".format(params[5], params[2], params[3]))
        else:
            user.username = params[2]
            user.hostname = params[3]

        user.server = params[4]

        #The RFC is weird and puts hops and realname in the same parameter
        hopsRealnameParam =  params[7].split(" ")
        user.hops = int(hopsRealnameParam[0])
        user.realname = hopsRealnameParam[1]

        flags = params[6]
        statusFlags = None
        if flags[0] == "G":
            user.away = True
        if len(flags) > 1:
            if flags[1] == "*":
                user.oper = True
                statusFlags = flags[2:]
            else:
                statusFlags = flags[1:]
        statusModes = ""
        if statusFlags:
            for flag in statusFlags:
                statusModes = statusModes + self.serverInfo.prefixesCharToMode[flag]
        channel.ranks[user.nickname] = statusModes

    def privmsg(self, user, channel, msg):
        message = IRCMessage('PRIVMSG', self.getUser(user[:user.index("!")]), self.getChannel(channel), msg, self)
        pass

    def action(self, user, channel, msg):
        message = IRCMessage('ACTION', self.getUser(user[:user.index("!")]), self.getChannel(channel), msg, self)
        pass

    def noticed(self, user, channel, msg):
        message = IRCMessage('NOTICE', self.getUser(user[:user.index("!")]), self.getChannel(channel), msg.upper(), self)
        pass

    def irc_JOIN(self, prefix, params):
        message = IRCMessage('JOIN', self.getUser(prefix[:prefix.index("!")]), self.getChannel(params[0]), u'', self)

        if message.user.nickname == self.nickname:
            # Bot joins the channel, do initial setup
            self.sendLine("WHO {}".format(message.channel.name))
            self.sendLine("MODE {}".format(message.channel.name))
        else:
            message.channel.users[message.user.nickname] = message.user
            message.channel.ranks[message.user.nickname] = ""

    def irc_PART(self, prefix, params):
        partMessage = u''
        if len(params) > 1:
            partMessage = u', message: ' + u' '.join(params[1:])
        message = IRCMessage('PART', self.getUser(prefix[:prefix.index("!")]), self.getChannel(params[0]), partMessage, self)

        if message.user.nickname == self.nickname:
            # The bot is leaving the channel
            del self.channels[message.channel.name]
        else:
            del message.channel.users[message.user.nickname]
            del message.channel.ranks[message.user.nickname]

    def irc_KICK(self, prefix, params):
        kickMessage = u''
        if len(params) > 2:
            kickMessage = u', message: ' + u' '.join(params[2:])
        message = IRCMessage('KICK', self.getUser(prefix[:prefix.index("!")]), self.getChannel(params[0]), kickMessage, self)
        kickee = params[1] # TODO: We need to get this into the message, otherwise we won't know who got kicked

        if kickee == self.nickname:
            # The bot is kicked from the channel
            del self.channels[message.channel.name]
        else:
            # Someone else is kicking someone from the channel
            del message.channel.users[kickee]
            del message.channel.ranks[kickee]

    def irc_QUIT(self, prefix, params):
        quitMessage = u''
        if len(params) > 0:
            quitMessage = u', message: ' + u' '.join(params[0])
        for key in self.channels:
            channel = self.channels[key]
            message = IRCMessage('QUIT', self.getUser(prefix[:prefix.index("!")]), channel, quitMessage, self)
            pass

    def getChannel(self, channel):
        """
        @type channel: str
        @rtype: IRCChannel
        """
        if channel in self.channels:
            return self.channels[channel]
        return None

    def getUser(self, user):
        """
        @type user: str
        @rtype: IRCUser
        """
        for channel in self.channels:
            if user in self.channels[channel]:
                return self.channels[channel].users[user]
        return None


class DesertBotFactory(protocol.ReconnectingClientFactory):
    protocol = DesertBot

    def __init__(self, server):
        """
        @type server: str
        """
        config = yaml.load(os.path.join("configs", "{}.yaml".format(server)))
        self.bot = DesertBot(self)
        reactor.connectTCP(config["server"], config["port"], self)

    def startedConnecting(self, connector):
        pass

    def buildProtocol(self, addr):
        self.resetDelay()
        return self.bot

    def clientConnectionLost(self, connector, unused_reason):
        pass

    def clientConnectionFailed(self, connector, reason):
        pass
