from enum import Enum


class ServerInfo(object):
    def __init__(self, servername):
        """
        @type servername: str
        """
        self.name = servername
        self.version = None
        self.network = "Unknown"
        self.chanTypes = "#"
        self.nickLength = 32

        self.userModes = \
            {
                "i" : ModeType.NORMAL,
                "o" : ModeType.NORMAL,
                "s" : ModeType.LIST,
                "w" : ModeType.NORMAL
            }

        self.chanModes = \
            {
                "b" : ModeType.LIST,
                "i" : ModeType.NORMAL,
                "k" : ModeType.PARAM_SET_UNSET,
                "l" : ModeType.PARAM_SET,
                "m" : ModeType.NORMAL,
                "n" : ModeType.NORMAL,
                "p" : ModeType.NORMAL,
                "s" : ModeType.NORMAL,
                "t" : ModeType.NORMAL
            }

        self.prefixesModeToChar = {"o":"@", "v":"+"}
        self.prefixesCharToMode = {"@":"o", "+":"v"}
        self.prefixOrder = "ov"


class ModeType(Enum):
    LIST = 1
    PARAM_SET = 2
    PARAM_SET_UNSET = 3
    NORMAL = 4
