class OutputHandler(object):
    def __init__(self, connection):
        self.connection = connection

    def cmdINVITE(self, user, channel):
        self.connection.sendMessage("INVITE", user, channel)

    def cmdJOIN(self, channel, key=""):
        if channel[0] not in self.connection.supportHelper.chanTypes:
            channel = "#{}".format(channel)
        self.connection.sendMessage("JOIN", channel, key)

    def cmdKICK(self, channel, user, reason=""):
        self.connection.sendMessage("KICK", channel, user, ":{}".format(reason))

    def cmdMODE(self, target, modes="", params=""):
        if params and isinstance(params, str):
            params = [params]
        self.connection.sendMessage("MODE", target, modes, params)

    def cmdNAMES(self, channel):
        self.connection.sendMessage("NAMES", channel)

    def cmdNICK(self, nick):
        self.connection.sendMessage("NICK", nick)

    def cmdNOTICE(self, target, message):
        self.connection.sendMessage("NOTICE", target, ":{}".format(message))

    def cmdPART(self, channel, reason=""):
        self.connection.sendMessage("PART", channel, ":{}".format(reason))

    def cmdPASS(self, password):
        self.connection.sendMessage("PASS", ":{}".format(password))

    def cmdPING(self, message):
        self.connection.sendMessage("PING", ":{}".format(message))

    def cmdPRIVMSG(self, target, message):
        self.connection.sendMessage("PRIVMSG", target, ":{}".format(message))

    def cmdPONG(self, message):
        self.connection.sendMessage("PONG", ":{}".format(message))

    def cmdTOPIC(self, channel, topic):
        self.connection.sendMessage("TOPIC", channel, ":{}".format(topic))

    def cmdQUIT(self, reason):
        self.connection.sendMessage("QUIT", ":{}".format(reason))

    def cmdUSER(self, ident, gecos):
        # RFC2812 allows usermodes to be set, but this isn't implemented much in IRCds at all.
        # Pass 0 for usermodes instead.
        self.connection.sendMessage("USER", ident, "0", "*", ":{}".format(gecos))

    def cmdWHO(self, mask):
        if not mask:
            mask = "*"
        self.connection.sendMessage("WHO", mask)

    def ctcpACTION(self, target, action):
        # We're keeping most CTCP stuff out of the core, but actions are used a lot and don't really belong in CTCP.
        self.cmdPRIVMSG(target, "\x01ACTION {}\x01".format(action))
