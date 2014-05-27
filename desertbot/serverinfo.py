

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

            }

        self.chanModes = \
            {

            }

        self.prefixesModeToChar = {"o":"@", "v":"+"}
        self.prefixesCharToMode = {"@":"o", "+":"v"}
        self.prefixOrder = "ov"

