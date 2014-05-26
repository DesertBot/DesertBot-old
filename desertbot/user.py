class IRCUser(object):
    def __init__(self, nickname):
        self.nickname = nickname
        self.username = None
        self.hostname = None
        self.realname = None
        self.server = None
        self.hops = 0
        self.oper = False
        self.away = False
