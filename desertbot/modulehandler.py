# -*- coding: utf-8 -*-
from desertbot.desertbot import DesertBot
from desertbot.response import IRCResponse
from desertbot.message import IRCMessage
from twisted.plugin import getPlugins

class ModuleHandler(object):
    def __init__(self, bot):
        """
        @type bot: DesertBot
        """
        self.bot = bot
        self.loadedModules = {}
    
    def sendResponse(self, response):
        """
        @type response: IRCResponse
        """
        pass

    def handleMessage(self, message):
        """
        @type message: IRCMessage
        """
        pass
  
    def loadModule(self, name):
        """
        @type name: unicode
        """
        pass
    
    def unloadModule(self, name):
        """
        @type name: unicode
        """
        pass
    
    def loadAllModules(self):
        pass
