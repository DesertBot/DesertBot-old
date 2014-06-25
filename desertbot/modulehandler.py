# -*- coding: utf-8 -*-
from twisted.plugin import getPlugins
from twisted.python import log
from twisted.internet import threads
from moduleinterface import IModule, ModuleType, ModulePriority, AccessLevel
from response import IRCResponse, ResponseType
from message import IRCMessage
import modules
import re, operator

class ModuleHandler(object):
    def __init__(self, bot):
        """
        @type bot: desertbot.DesertBot
        """
        self.bot = bot
        self.loadedModules = {}
    
    def sendResponse(self, response):
        """
        @type response: IRCResponse
        """
        responses = []
        
        if hasattr(response, "__iter__"):
            for r in response:
                if r is None or r.response is None or r.response == "":
                    continue
                responses.append(r)
        elif response is not None and response.response is not None and response.response != "":
            responses.append(response)
            
        for response in responses:
            try:
                if response.responseType == ResponseType.PRIVMSG:
                    self.bot.msg(response.target, response.response) #response should be unicode here
                elif response.responseType == ResponseType.ACTION:
                    self.bot.describe(response.target, response.response)
                elif response.responseType == ResponseType.NOTICE:
                    self.bot.notice(response.target, response.response)
                elif response.responseType == ResponseType.RAW:
                    self.bot.sendLine(response.response)
            except Exception as e:
                errorMsg = "An error occurred while sending response: \"{}\" ({})".format(response.response, e)
                log.err(errorMsg)
                    

    def handleMessage(self, message):
        """
        @type message: IRCMessage
        """
        for module in sorted(self.loadedModules.values(), key=operator.attrgetter("modulePriority")):
            try:
                if self._shouldTrigger(module, message):
                    if not module.runInThread:
                        response = module.onTrigger(message)
                        self.sendResponse(response)
                    else:
                        d = threads.deferToThread(module.onTrigger, message)
                        d.addCallback(self.sendResponse)
            except Exception as e:
                errorMsg = "An error occured while handling message: \"{}\" ({})".format(message.messageText, e)
                log.err(errorMsg)
                
    def _shouldTrigger(self, module, message):
        """
        @type message: IRCMessage
        """
        if message.messageType in module.messageTypes:
            if module.moduleType == ModuleType.PASSIVE:
                return True
            elif message.user.nickname == self.bot.nickname:
                return False
            elif module.moduleType == ModuleType.ACTIVE:
                for trigger in module.triggers:
                    match = re.search(".*{}.*".format(trigger), message.messageText, re.IGNORECASE)
                    if match:
                        return True
                return False
            elif module.moduleType == ModuleType.COMMAND:
                if message.command in module.triggers:
                    return True
                return False
            elif module.moduleType == ModuleType.POSTPROCESS:
                return module.shouldTrigger(message)
            elif module.moduleType == ModuleType.UTILITY:
                return module.shouldTrigger(message)

    def _checkCommandAuthorization(self, module, message):
        """
        @type message: IRCMessage
        """
        if module.accessLevel == AccessLevel.ANYONE:
            return True

        if module.accessLevel == AccessLevel.ADMINS:
            for adminRegex in self.bot.admins:
                if re.match(adminRegex, message.user.getUserString()):
                    return True
            return False

    def loadModule(self, name):
        """
        @type name: unicode
        """
        if name is None or name == "" or name == u"":
            errorMsg = "Module name not specified!"
            log.err(errorMsg)
            return (False, errorMsg)
        if name.lower() not in self.loadedModules:
            moduleReload = False
        else:
            moduleReload = True
        for module in getPlugins(IModule, modules):
            if module.name == name.lower():
                if not IModule.providedBy(module):
                    errorMsg = "Module \"{}\" can't be loaded; module does not implement module interface.".format(module.name)
                    log.err(errorMsg)
                    return (False, errorMsg)
                self.loadedModules[module.name] = module
                try:
                    self.loadedModules[module.name].onModuleLoaded()
                except Exception as e:
                    errorMsg = "An error occurred while loading module \"{}\" ({})".format(module.name, e)
                    log.err(errorMsg)
                    return (False, errorMsg)

                if moduleReload:
                    loadMsg = "Module \"{}\" was successfully reloaded!".format(module.name)
                    log.msg(loadMsg)
                    return (True, loadMsg)
                else:
                    loadMsg = "Module \"{}\" was successfully loaded!".format(module.name)
                    log.msg(loadMsg)
                    return (True, loadMsg)
        return (False, "No module named \"{}\" could be found!".format(name))

    def unloadModule(self, name):
        """
        @type name: unicode
        """
        if name is None or name == "" or name == u"":
            errorMsg = "Module name not specified!"
            log.err(errorMsg)
            return (False, errorMsg)
        if name.lower() in self.loadedModules:
            try:
                self.loadedModules[name.lower()].onModuleUnloaded()
            except Exception as e:
                errorMsg = "An error occurred while unloading module \"{}\" ({})".format(module.name, e)
                log.err(errorMsg)
            # Unload module so it doesn't get stuck, but emit the error still.
            del self.loadedModules[name.lower()]
            loadMsg = "Module \"{}\" was successfully unloaded!".format(module.name)
            log.msg(loadMsg)
            return (True, loadMsg)
        else:
            errorMsg = "No module named \"{}\" is loaded!".format(name)
            log.err(errorMsg)
            return (False, errorMsg)
    
    def loadAllModules(self):
        for module in getPlugins(IModule, modules):
            if module.name is not None and module.name != "" and module.name != u"":
                self.loadModule(module.name)
