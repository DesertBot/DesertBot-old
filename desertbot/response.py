# -*- coding: utf-8 -*-
from enum import Enum
from channel import IRCChannel


class ResponseType(Enum):
    SAY = 1
    DO = 2
    NOTICE = 3
    RAW = 4


class IRCResponse(object):
    def __init__(self, responseType, response, target):
        """
        @type responseType: ResponseType
        @type response: unicode
        @type target: IRCChannel
        """
        self.type = responseType
        if not isinstance(response, unicode):
            self.response = unicode(response, "utf-8")
        else:
            self.response = response
        self.target = target
