# -*- coding: utf-8 -*-
from enum import Enum

from desertbot.user import IRCUser


class ResponseType(Enum):
    PRIVMSG = 1
    ACTION = 2
    NOTICE = 3
    RAW = 4


class IRCResponse(object):
    def __init__(self, responseType, response, user, target):
        """
        @type responseType: ResponseType
        @type response: unicode
        @type user: IRCUser
        @type target: unicode
        """
        self.type = responseType
        if not isinstance(response, unicode):
            self.response = unicode(response, "utf-8")
        else:
            self.response = response
        self.user = user
        if not isinstance(target, unicode):
            self.target = unicode(target, "utf-8")
        else:
            self.target = target
