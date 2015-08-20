from desertbot.utils import ModeType


class IRCChannel(object):
    def __init__(self, name, connection):
        self.name = name
        self.connection = connection
        self.modes = {}
        self.users = {}
        self.ranks = {}
        self.topic = None
        self.topicSetter = None
        self.topicTimestamp = 0
        self.creationTime = 0
        self.userlistComplete = True

    def setModes(self, modes, params):
        adding = True
        supportedChanModes = self.connection.supportHelper.chanModes
        supportedStatuses = self.connection.supportHelper.statusModes
        modesAdded = []
        paramsAdded = []
        modesRemoved = []
        paramsRemoved = []
        for mode in modes:
            if mode == "+":
                adding = True
            elif mode == "-":
                adding = False
            elif mode not in supportedChanModes and mode not in supportedStatuses:
                self.connection.bot.log.warn("{connection.name} Received unknown MODE char {mode} in MODE string {"
                                             "modes}.", connection=self.connection, mode=mode, modes=modes)
                # We received a mode char that's unknown to use, so we abort parsing to prevent desync.
                return None
            elif mode in supportedStatuses:
                user = params.pop(0)
                if user not in self.users:
                    self.connection.bot.log.warn("{connection.name} Received status MODE for unknown user {user} in "
                                                 "channel {channel}.", connection=self.connection, user=user,
                                                 channel=self.name)
                else:
                    if adding:
                        self.ranks[user] += mode
                        modesAdded.append(mode)
                        paramsAdded.append(user)
                    elif not adding and mode in self.ranks[user]:
                        self.ranks[user] = self.ranks[user].replace(mode, "")
                        modesRemoved.append(mode)
                        paramsRemoved.append(user)
            elif supportedChanModes[mode] == ModeType.LIST:
                param = params.pop(0)
                if mode not in self.modes:
                    self.modes[mode] = set()
                if adding:
                    self.modes[mode].add(param)
                    modesAdded.append(mode)
                    paramsAdded.append(param)
                elif not adding and param in self.modes[mode]:
                    self.modes[mode].remove(param)
                    modesRemoved.append(mode)
                    paramsRemoved.append(param)
            elif supportedChanModes[mode] == ModeType.PARAM_SET:
                if adding:
                    param = params.pop(0)
                    self.modes[mode] = param
                    modesAdded.append(mode)
                    paramsAdded.append(param)
                elif not adding and mode in self.modes:
                    del self.modes[mode]
                    modesRemoved.append(mode)
                    paramsRemoved.append(None)
            elif supportedChanModes == ModeType.PARAM_UNSET:
                param = params.pop(0)
                if adding:
                    self.modes[mode] = param
                    modesAdded.append(mode)
                    paramsAdded.append(param)
                elif not adding and mode in self.modes:
                    del self.modes[mode]
                    modesRemoved.append(mode)
                    paramsRemoved.append(param)
            elif supportedChanModes[mode] == ModeType.NO_PARAM:
                if adding:
                    self.modes[mode] = None
                    modesAdded.append(mode)
                    paramsAdded.append(None)
                elif not adding and modes in self.modes:
                    del self.modes[mode]
                    modesRemoved.append(mode)
                    paramsRemoved.append(None)
        return {
            "added": modesAdded,
            "removed": modesRemoved,
            "addedParams": paramsAdded,
            "removedParams": paramsRemoved
        }

    def getHighestStatusOfUser(self, user):
        if user.nick not in self.ranks:
            return ""
        
        for status in self.connection.supportHelper.statusOrder:
            if status in self.ranks[user.nick]:
                return self.connection.supportHelper.statusModes[status]
        return ""

    def userIsChanOp(self, user):
        if user.nick not in self.ranks:
            return False

        for status in self.connection.supportHelper.statusModes:
            if status in self.ranks[user.nick]:
                return True
            if status == "o": # We consider anyone with +o or higher to be an op
                break
        return False
