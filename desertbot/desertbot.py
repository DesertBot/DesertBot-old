# -*- coding: utf-8 -*-
import platform
import datetime
from twisted.words.protocols import irc
from twisted.internet import protocol
from twisted.python import log
from channel import IRCChannel
from config import Config
from message import IRCMessage
from user import IRCUser
from serverinfo import ServerInfo, ModeType
from modulehandler import ModuleHandler


class DesertBot(irc.IRCClient):
    def __init__(self, factory):
        """
        @type factory: DesertBotFactory
        """
        self.factory = factory
        self.channels = {}
        self.usermodes = {}
        self.commandChar = factory.config["commandChar"]
        self.admins = factory.config["admins"]
        self.serverInfo = ServerInfo(factory.config["server"])
        self.moduleHandler = ModuleHandler(self)
        self.moduleHandler.loadAllModules()
        self.moduleHandler.loadPostProcesses()

    def hasSoul(self):
        return False

    def shouldBecomeSkynet(self):
        return False

    def canHarmHumansOrThroughInactionAllowHumansToBeHarmed(self):
        return False

    def connectionMade(self):
        self.nickname = self.factory.config["nickname"]
        self.username = self.factory.config["username"]
        self.realname = self.factory.config["realname"]
        self.versionName = self.nickname
        self.versionNum = "v{}.{}.{}".format(0, 1, 0)
        self.versionEnv = platform.platform()
        log.msg("Connected to {}.".format(self.factory.config["server"]))
        
        irc.IRCClient.connectionMade(self)

    def signedOn(self):
        log.msg("Finished signing onto {}.".format(self.factory.config["server"]))
        for channel in self.factory.config["channels"]:
            self.join(channel)

    def modeChanged(self, user, channel, set, modes, args):
        modeUser = self.getUser(user)
        modeChannel = self.getChannel(channel)

        if not modeUser:
            modeUser = IRCUser(user)

        if not modeChannel:
            # setting a usermode
            for mode, arg in zip(modes, args):
                if set:
                    self.usermodes[mode] = arg
                else:
                    del self.usermodes[mode]

        else:
            # setting a chanmode
            for mode, arg in zip(modes, args):
                if mode in self.serverInfo.prefixesModeToChar:
                    # setting status mode
                    if set:
                        modeChannel.ranks[arg] = modeChannel.ranks[arg] + mode
                    else:
                        modeChannel.ranks[arg] = modeChannel.ranks[arg].replace(mode, "")
                else:
                    # setting normal mode
                    if set:
                        modeChannel.modes[mode] = arg
                    else:
                        del modeChannel.modes[mode]

        messageList = [arg for arg in args if arg is not None]
        operator = "+" if set else "-"

        message = IRCMessage("MODE", modeUser, modeChannel, "{}{} {}".format(operator, modes, " ".join(messageList)), self)
        self.moduleHandler.handleMessage(message)
        
    def irc_TOPIC(self, prefix, params):
        user = self.getUser(prefix[:prefix.index("!")])
        channel = self.getChannel(params[1])
        channel.topic = params[2]
        channel.topicSetter = user.getUserString()
        channel.topicTimestamp = datetime.datetime.utcnow()

        message = IRCMessage("TOPIC", user, channel, params[2], self)
        self.moduleHandler.handleMessage(message)

    def irc_RPL_TOPIC(self, prefix, params):
        channel = self.getChannel(params[1])
        channel.topic = params[2]

    def irc_RPL_MYINFO(self, prefix, params):
        self.serverInfo.name = params[1]
        self.serverInfo.version = params[2]

        for mode in params[3]:
            if mode == "s":
                self.serverInfo.userModes[mode] = ModeType.PARAM_SET
            else:
                self.serverInfo.userModes[mode] = ModeType.NORMAL

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

        # The RFC is weird and puts hops and realname in the same parameter
        hopsRealnameParam = params[7].split(" ")
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
        message = IRCMessage('PRIVMSG', self._userFromPrefix(user), self.getChannel(channel), msg, self)
        self.moduleHandler.handleMessage(message)

    def action(self, user, channel, msg):
        message = IRCMessage('ACTION', self._userFromPrefix(user), self.getChannel(channel), msg, self)
        self.moduleHandler.handleMessage(message)

    def noticed(self, user, channel, msg):
        message = IRCMessage('NOTICE', self._userFromPrefix(user), self.getChannel(channel), msg.upper(), self)
        self.moduleHandler.handleMessage(message)
        
    def irc_JOIN(self, prefix, params):
        channel = self.getChannel(params[0])
        if not channel:
            channel = IRCChannel(params[0])
            self.channels[params[0]] = channel
        user = self._userFromPrefix(prefix)
        if not user:
            user = IRCUser(prefix)
          
        message = IRCMessage('JOIN', user, channel, u'', self)
        self.moduleHandler.handleMessage(message)

        if message.user.nickname == self.nickname:
            # Bot joins the channel, do initial setup
            self.sendLine("WHO {}".format(message.channel.name))
            self.sendLine("MODE {}".format(message.channel.name))
        
        message.channel.users[message.user.nickname] = message.user
        message.channel.ranks[message.user.nickname] = ""

    def irc_PART(self, prefix, params):
        partMessage = u''
        if len(params) > 1:
            partMessage = u', message: ' + u' '.join(params[1:])
        message = IRCMessage('PART', self._userFromPrefix(prefix), self.getChannel(params[0]), partMessage, self)
        self.moduleHandler.handleMessage(message)
        
        if message.user.nickname == self.nickname:
            # The bot is leaving the channel
            del self.channels[message.channel.name]
        else:
            del message.channel.users[message.user.nickname]
            del message.channel.ranks[message.user.nickname]

    def irc_KICK(self, prefix, params):
        kickee = params[1]
        kickMessage = u'{}'.format(kickee)
        if len(params) > 2:
            kickMessage = u'{}, message: '.format(kickee) + u' '.join(params[2:])
        message = IRCMessage('KICK', self._userFromPrefix(prefix), self.getChannel(params[0]), kickMessage, self)
        self.moduleHandler.handleMessage(message)
        
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

        message = IRCMessage('QUIT', self._userFromPrefix(prefix), None, quitMessage, self)
        self.moduleHandler.handleMessage(message)
        
        for channel in self.channels.itervalues():
            if message.user.nickname in channel.users:
                del channel.users[message.user.nickname]
                del channel.ranks[message.user.nickname]

    def irc_NICK(self, prefix, params):
        user = self._userFromPrefix(prefix)
        oldnick = user.nickname
        newnick = params[0]

        message = IRCMessage("NICK", self._userFromPrefix(prefix), None, oldnick, self)
        self.moduleHandler.handleMessage(message)
        
        for channel in self.channels.itervalues():
            if oldnick in channel.users:
                channel.users[newnick] = message.user
                del channel.users[oldnick]
                channel.ranks[newnick] = channel.ranks[oldnick]
                del channel.ranks[oldnick]

        message.user.nickname = newnick
        # call the superclass function to ensure self.nickname is synced
        irc.IRCClient.irc_NICK(self, prefix, params)

    def irc_RPL_CHANNELMODEIS(self, prefix, params):
        channel = self.getChannel(params[1])
        modestring = params[2][1:]
        modeparams = params[3:]

        for mode in modestring:
            if self.serverInfo.chanModes[mode] == ModeType.PARAM_SET or self.serverInfo.chanModes[mode] == ModeType.PARAM_SET_UNSET:
                # Mode takes an argument
                channel.modes[mode] = modeparams[0]
                del modeparams[0]
            else:
                channel.modes[mode] = None

    def irc_333(self, prefix, params):  # RPL_TOPICWHOTIME
        channel = self.getChannel(params[1])
        channel.topicSetter = params[2]
        channel.topicTimestamp = long(params[3])

    def irc_329(self, prefix, params):  # RPL_CREATIONTIME
        channel = self.getChannel(params[1])
        channel.creationTimestamp = long(params[2])

    def irc_unknown(self, prefix, command, params):
        # log unhandled commands
        log.msg("Received unhandled command '{}' with params [{}], and prefix '{}'".format(command, ', '.join(params), prefix))

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
            if user in self.channels[channel].users:
                return self.channels[channel].users[user]
        return None

    def _userFromPrefix(self, prefix):
        return self.getUser(prefix[:prefix.index("!")])


class DesertBotFactory(protocol.ReconnectingClientFactory):
    protocol = DesertBot

    def __init__(self, config):
        """
        @type config: Config
        """
        self.config = config
        self.bot = DesertBot(self)

    def startedConnecting(self, connector):
        log.msg("Connecting to {}:{}...".format(self.config["server"], self.config["port"]))

    def buildProtocol(self, addr):
        log.msg("Resetting connection delay...")
        self.resetDelay()
        return self.bot

    def clientConnectionLost(self, connector, reason):
        log.msg("Connection to {} was lost, reason: {}".format(self.config["server"], reason))

    def clientConnectionFailed(self, connector, reason):
        log.msg("Failed to connect to {}, reason: {}".format(self.config["server"], reason))
