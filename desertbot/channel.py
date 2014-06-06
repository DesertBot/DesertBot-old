# -*- coding: utf-8 -*-
class IRCChannel(object):
    def __init__(self, name):
        self.name = name
        self.modes = {}
        self.users = {}
        self.ranks = {}
        self.topic = None
        self.topicSetter = None
        self.topicTimestamp = 0
        self.namesListCompete = True
