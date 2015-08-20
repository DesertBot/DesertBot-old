from desertbot.channel import IRCChannel
from desertbot.user import IRCUser
from desertbot.utils import ModeType, parseUserPrefix, timeutils


class InputHandler(object):
    def __init__(self, connection):
        self.connection = connection
        self.moduleHandler = connection.bot.moduleHandler

    def handleCommand(self, command, prefix, params):
        parsedPrefix = parseUserPrefix(prefix)
        nick = parsedPrefix[0]
        ident = parsedPrefix[1]
        host = parsedPrefix[2]

        method = getattr(self, "_handle{}".format(command), None)
        if method:
            method(nick, ident, host, params)
        else:
            self.handleUnknown(command, prefix, params)

    def handleNumeric(self, numeric, prefix, params):
        method = getattr(self, "_handleNumeric{}".format(numeric), None)
        if method:
            method(prefix, params)
        else:
            self.handleUnknown(numeric, prefix, params)

    def handleUnknown(self, command, prefix, params):
        pass

    def _handleERROR(self, nick, ident, host, params):
        self._logInfo("Connection terminated ({}).".format(params[0]))

    def _handleINVITE(self, nick, ident, host, params):
        if nick in self.connection.users:
            inviter = self.connection.users[nick]
        else:
            inviter = IRCUser(nick, ident, host)
        self.moduleHandler.runGenericAction("channelinvite", params[1], inviter)
        self.connection.outputHandler.cmdJOIN(params[1])

    def _handleJOIN(self, nick, ident, host, params):
        if nick not in self.connection.users:
            user = IRCUser(nick, ident, host)
            self.connection.users[nick] = user
        else:
            user = self.connection.users[nick]
        if params[0] not in self.connection.channels:
            channel = IRCChannel(params[0], self.connection)
            self.connection.outputHandler.cmdWHO(params[0])
            self.connection.outputHandler.cmdMODE(params[0])
            self.connection.channels[params[0]] = channel
        else:
            channel = self.connection.channels[params[0]]
        channel.users[nick] = user
        channel.ranks[nick] = ""
        self.moduleHandler.runGenericAction("channeljoin", self.connection.name, channel, user)

    def _handleKICK(self, nick, ident, host, params):
        if params[0] not in self.connection.channels:
            self._logWarning("Received KICK message for unknown channel {}.".format(params[0]))
            return
        channel = self.connection.channels[params[0]]
        if params[1] not in channel.users:
            self._logWarning("Received KICK message for unknown user {} in channel {}.".format(nick, params[0]))
            return
        if nick not in self.connection.users:
            # Technically opers could KICK a user despite not being in the channel themselves
            kicker = IRCUser(nick, ident, host)
        else:
            kicker = self.connection.users[nick]
        kicked = self.connection.users[params[1]]
        reason = ""
        if len(params) > 2:
            reason = params[2]
        # We need to run the action before we actually get rid of the user
        self.moduleHandler.runGenericAction("channelkick", self.connection.name, channel, kicker, kicked, reason)
        if kicked.nick == self.connection.nick:
            del self.connection.channels[params[0]]
        else:
            del channel.users[kicked.nick]
            del channel.ranks[kicked.nick]

    def _handleMODE(self, nick, ident, host, params):
        if nick in self.connection.users:
            user = self.connection.users[nick]
        else:
            user = IRCUser(nick, ident, host)
        if len(params) > 2:
            modeParams = params[2:]
        else:
            modeParams = []
        if params[0][0] in self.connection.supportHelper.chanTypes:
            if params[0] not in self.connection.channels:
                self._logWarning("Received MODE message for unknown channel {}.".format(params[0]))
                return
            channel = self.connection.channels[params[0]]
            modes = channel.setModes(params[1], modeParams)
            if not modes:
                return
            if len(modes["added"]) > 0:
                self.moduleHandler.runGenericAction("modeschanged-channel", self.connection.name, user, channel,
                                               modes["added"], modes["addedParams"], True)
            if len(modes["removed"]) > 0:
                self.moduleHandler.runGenericAction("modeschanged-channel", self.connection.name, user, channel,
                                               modes["removed"], modes["removedParams"], False)
        elif params[0] == self.connection.nick:
            modes = self.connection.setUserModes(params[1])
            if not modes:
                return
            if len(modes["added"]) > 0:
                self.moduleHandler.runGenericAction("modeschanged-user", self.connection.name, modes["added"], True)
            if len(modes["removed"]) > 0:
                self.moduleHandler.runGenericAction("modeschanged-user", self.connection.name, modes["removed"], False)

    def _handleNICK(self, nick, ident, host, params):
        if nick not in self.connection.users:
            self._logWarning("Received NICK message for unknown user {}.".format(nick))
            return
        user = self.connection.users[nick]
        newNick = params[0]
        user.nick = newNick
        self.connection.users[newNick] = user
        for channel in self.connection.channels.itervalues():
            if nick in channel.users:
                channel.users[newNick] = user
                channel.ranks[newNick] = channel.ranks[nick]
                del channel.users[nick]
                del channel.ranks[nick]
        if nick == self.connection.nick:
            self.connection.nick = newNick
        self.moduleHandler.runGenericAction("changenick", self.connection.name, user, nick, newNick)

    def _handleNOTICE(self, nick, ident, host, params):
        user = None
        if params[0][0] in self.connection.supportHelper.chanTypes:
            if params[0] in self.connection.channels:
                source = self.connection.channels[params[0]]
            else:
                # We got a notice for an unknown channel. Create a temporary IRCChannel object for it.
                source = IRCChannel(params[0], self)
            if nick in self.connection.users:
                user = self.connection.users[nick]
            else:
                user = IRCUser(nick, ident, host)
        elif nick in self.connection.users:
            source = self.connection.users[nick]
        else:
            # We got a notice from an unknown user. Create a temporary IRCUser object for them.
            source = IRCUser(nick, ident, host)
        if isinstance(source, IRCChannel):
            self.moduleHandler.runGenericAction("notice-channel", self.connection.name, source, user, params[1])
        else:
            self.moduleHandler.runGenericAction("notice-user", self.connection.name, source, params[1])

    def _handlePART(self, nick, ident, host, params):
        if params[0] not in self.connection.channels:
            self._logWarning("Received PART message for unknown channel {}.".format(params[0]))
            return
        channel = self.connection.channels[params[0]]
        if nick not in channel.users:
            self._logWarning("Received PART message for unknown user {} in channel {}.".format(nick, params[0]))
            return
        reason = ""
        if len(params) > 1:
            reason = params[1]
        user = self.connection.users[nick]
        # We need to run the action before we actually get rid of the user
        self.moduleHandler.runGenericAction("channelpart", self.connection.name, channel, user, reason)
        if nick == self.connection.nick:
            del self.connection.channels[params[0]]
        else:
            del channel.users[nick]
            del channel.ranks[nick]

    def _handlePING(self, nick, ident, host, params):
        self.connection.outputHandler.cmdPONG(" ".join(params))

    def _handlePRIVMSG(self, nick, ident, host, params):
        user = None
        if params[0][0] in self.connection.supportHelper.chanTypes:
            if params[0] in self.connection.channels:
                source = self.connection.channels[params[0]]
            else:
                # We got a message for an unknown channel. Create a temporary IRCChannel object for it.
                source = IRCChannel(params[0], self.connection)
            if nick in self.connection.users:
                user = self.connection.users[nick]
            else:
                user = IRCUser(nick, ident, host)
        elif nick in self.connection.users:
            source = self.connection.users[nick]
            user = source
        else:
            # We got a message from an unknown user. Create a temporary IRCUser object for them.
            source = IRCUser(nick, ident, host)
        if params[1][0] == "\x01":
            message = params[1][1:len(params[1]) - 1]
            self.moduleHandler.runGenericAction("ctcp-message", self.connection.name, source, user, message)
        elif isinstance(source, IRCChannel):
            self.moduleHandler.runGenericAction("message-channel", self.connection.name, source, user, params[1])
        else:
            self.moduleHandler.runGenericAction("message-user", self.connection.name, source, params[1])

    def _handleQUIT(self, nick, ident, host, params):
        if nick not in self.connection.users:
            self._logWarning("Received a QUIT message for unknown user {}.".format(nick))
            return
        reason = ""
        if len(params) > 0:
            reason = params[0]
        user = self.connection.users[nick]
        self.moduleHandler.runGenericAction("userquit", self.connection.name, user, reason)
        for channel in self.connection.channels.itervalues():
            if nick in channel.users:
                del channel.users[nick]
                del channel.ranks[nick]

    def _handleTOPIC(self, nick, ident, host, params):
        if params[0] not in self.connection.channels:
            self._logWarning("Received TOPIC message for unknown channel {}.".format(params[0]))
            return
        channel = self.connection.channels[params[0]]
        if nick not in self.connection.users:
            # A user that's not in the channel can change the topic so let's make a temporary user.
            user = IRCUser(nick, ident, host)
        else:
            user = self.connection.users[nick]
        oldTopic = channel.topic
        channel.topic = params[1]
        channel.topicSetter = user.fullUserPrefix()
        channel.topicTimestamp = timeutils.timestamp(timeutils.now())
        self.moduleHandler.runGenericAction("changetopic", self.connection.name, channel, user, oldTopic, params[1])

    def _handleNumeric001(self, prefix, params):
        # 001: RPL_WELCOME
        self.connection.loggedIn = True
        self.connection.bot.moduleHandler.runGenericAction("welcome", self.connection.name)
        channels = self.connection.bot.config.serverItemWithDefault(self.connection.name, "channels", {})
        for channel, key in channels.iteritems():
            self.connection.outputHandler.cmdJOIN(channel, key if key else "")

    def _handleNumeric004(self, prefix, params):
        # 004: RPL_MYINFO
        self.connection.supportHelper.serverName = params[1]
        self.connection.supportHelper.serverVersion = params[2]
        self.connection.supportHelper.userModes = params[3]

    def _handleNumeric005(self, prefix, params):
        # 005: RPL_ISUPPORT
        tokens = {}
        # The first param is our prefix and the last one is ":are supported by this server"
        for param in params[1:len(params) - 1]:
            keyValuePair = param.split("=")
            if len(keyValuePair) > 1:
                tokens[keyValuePair[0]] = keyValuePair[1]
            else:
                tokens[keyValuePair[0]] = ""
        if "CHANTYPES" in tokens:
            self.connection.supportHelper.chanTypes = tokens["CHANTYPES"]
        if "CHANMODES" in tokens:
            self.connection.supportHelper.chanModes.clear()
            groups = tokens["CHANMODES"].split(",")
            for mode in groups[0]:
                self.connection.supportHelper.chanModes[mode] = ModeType.LIST
            for mode in groups[1]:
                self.connection.supportHelper.chanModes[mode] = ModeType.PARAM_UNSET
            for mode in groups[2]:
                self.connection.supportHelper.chanModes[mode] = ModeType.PARAM_SET
            for mode in groups[3]:
                self.connection.supportHelper.chanModes[mode] = ModeType.NO_PARAM
        if "NETWORK" in tokens:
            self.connection.supportHelper.network = tokens["NETWORK"]
        if "PREFIX" in tokens:
            self.connection.supportHelper.statusModes.clear()
            self.connection.supportHelper.statusSymbols.clear()
            modes = tokens["PREFIX"][1:tokens["PREFIX"].find(")")]
            symbols = tokens["PREFIX"][tokens["PREFIX"].find(")") + 1:]
            self.connection.supportHelper.statusOrder = modes
            for i in range(len(modes)):
                self.connection.supportHelper.statusModes[modes[i]] = symbols[i]
                self.connection.supportHelper.statusSymbols[symbols[i]] = modes[i]
        self.connection.supportHelper.rawTokens.update(tokens)

    def _handleNumeric324(self, prefix, params):
        # 324: RPL_CHANNELMODEIS
        channel = self.connection.channels[params[1]]
        modeParams = params[3].split() if len(params) > 3 else []
        modes = channel.setModes(params[2], modeParams)
        if not modes:
            return
        self.moduleHandler.runGenericAction("modes-channel", self.connection.name, channel, modes["added"],
                                       modes["addedParams"])

    def _handleNumeric329(self, prefix, params):
        # 329: RPL_CREATIONTIME
        channel = self.connection.channels[params[1]]
        channel.creationTime = int(params[2])

    def _handleNumeric332(self, prefix, params):
        # 332: RPL_TOPIC
        channel = self.connection.channels[params[1]]
        channel.topic = params[2]

    def _handleNumeric333(self, prefix, params):
        # 333: RPL_TOPICWHOTIME
        channel = self.connection.channels[params[1]]
        channel.topicSetter = params[2]
        channel.topicTimestamp = int(params[3])

    def _handleNumeric352(self, prefix, params):
        # 352: RPL_WHOREPLY
        if params[5] not in self.connection.users:
            self._logWarning("Received WHO reply for unknown user {}.".format(params[5]))
            return
        user = self.connection.users[params[5]]
        user.ident = params[2]
        user.host = params[3]
        user.server = params[4]
        flags = list(params[6])
        if flags.pop(0) == "G":
            user.isAway = True
        if len(flags) > 0 and flags[0] == "*":
            user.isOper = True
            flags.pop(0)
        if params[1] in self.connection.channels:
            channel = self.connection.channels[params[1]]
            channel.ranks[params[5]] = ""
            for status in flags:
                channel.ranks[params[5]] += self.connection.supportHelper.statusSymbols[status]
        hopsGecos = params[7].split()
        user.hops = int(hopsGecos[0])
        if len(hopsGecos) > 1:
            user.gecos = hopsGecos[1]
        else:
            user.gecos = "No info"

    def _handleNumeric353(self, prefix, params):
        # 353: RPL_NAMREPLY
        channel = self.connection.channels[params[2]]
        if channel.userlistComplete:
            channel.userlistComplete = False
            channel.users.clear()
            channel.ranks.clear()
        for userPrefix in params[3].split():
            parsedPrefix = parseUserPrefix(userPrefix)
            nick = parsedPrefix[0]
            ranks = ""
            while nick[0] in self.connection.supportHelper.statusSymbols:
                ranks += self.connection.supportHelper.statusSymbols[nick[0]]
                nick = nick[1:]
            if nick in self.connection.users:
                user = self.connection.users[nick]
                user.ident = parsedPrefix[1]
                user.host = parsedPrefix[2]
            else:
                user = IRCUser(nick, parsedPrefix[1], parsedPrefix[2])
                self.connection.users[nick] = user
            channel.users[nick] = user
            channel.ranks[nick] = ranks

    def _handleNumeric366(self, prefix, params):
        # 366: RPL_ENDOFNAMES
        channel = self.connection.channels[params[1]]
        channel.userlistComplete = True

    def _handleNumeric433(self, prefix, params):
        # 433: ERR_NICKNAMEINUSE
        newNick = "{}_".format(self.connection.nick)
        self._logInfo("Nickname {} is in use, retrying with {} ...".format(self.connection.nick, newNick))
        self.connection.nick = newNick
        self.connection.outputHandler.cmdNICK(self.connection.nick)

    def _logInfo(self, info):
        self.connection.bot.log.info("{connection.name} {info}", connection=self.connection, info=info)

    def _logWarning(self, warning):
        self.connection.bot.log.warn("{connection.name} {warning}", connection=self.connection, warning=warning)
