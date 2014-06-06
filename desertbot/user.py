# -*- coding: utf-8 -*-
class IRCUser(object):
    def __init__(self, userString):
        exclamationIndex = userString.find("!")
        atIndex = userString.find("@")
        if exclamationIndex == -1 or atIndex == -1:
            self.nickname = userString
            self.username = None
            self.hostname = None
        else:
            self.nickname = userString[:exclamationIndex]
            self.username = userString[exclamationIndex +1:atIndex]
            self.hostname = userString[atIndex+1:]
        self.realname = None
        self.server = None
        self.hops = 0
        self.oper = False
        self.away = False

    def getUserString(self):
        return "{}!{}@{}".format(self.nickname, self.username, self.hostname)
