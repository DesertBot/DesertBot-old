# -*- coding: utf-8 -*-
import operator

from twisted.plugin import getPlugins
from twisted.python import log
from twisted.internet import threads
from desertbot.moduleinterface import IModule, ModuleType, AccessLevel
from desertbot.postprocessinterface import IPost
from desertbot.response import IRCResponse, ResponseType
from desertbot.message import IRCMessage
from desertbot.user import IRCUser
from desertbot import modules, postprocesses
import re


class ModuleHandler(object):
    def __init__(self, bot):
        """
        @type bot: desertbot.DesertBot
        """
        self.bot = bot
        self.loadedModules = {}
        self.loadedPostProcesses = {}
    
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
    
    def postProcess(self, response):
        """
        @type response: IRCResponse
        """
        newResponse = response
        for post in sorted(self.loadedPostProcesses.values(), key=operator.attrgetter("modulePriority")):
            try:
                if post.shouldExecute(newResponse):
                    if not post.runInThread:
                        newResponse = post.onTrigger(newResponse)
                        self.sendResponse(newResponse)
                    else:
                        d = threads.deferToThread(post.onTrigger, newResponse)
                        d.addCallback(self.sendResponse)
            except Exception as e:
                errorMsg = "An error occured while postprocessing: \"{}\" ({})".format(response.response, e)
                log.err(errorMsg)
                self.sendResponse(newResponse)

    def handleMessage(self, message):
        """
        @type message: IRCMessage
        """
        for module in sorted(self.loadedModules.values(), key=operator.attrgetter("modulePriority")):
            try:
                if self._shouldTrigger(module, message):
                    if not module.runInThread:
                        response = module.onTrigger(message)
                        self.postProcess(response)
                    else:
                        d = threads.deferToThread(module.onTrigger, message)
                        d.addCallback(self.postProcess)
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
                if message.command in module.triggers and _allowedToUse(module, message.user):
                    return True
                else:
                    return False
            elif module.moduleType == ModuleType.UTILITY:
                return module.shouldTrigger(message)

    def _allowedToUse(self, module, user):
        """
        @type user: IRCUser
        """
        if user is None:
            return False
        
        if module.accessLevel == AccessLevel.ANYONE:
            return True

        if module.accessLevel == AccessLevel.ADMINS:
            for adminRegex in self.bot.admins:
                if re.match(adminRegex, user.getUserString()):
                    return True
            return False

    def loadModule(self, name):
        """
        @type name: unicode
        """
        return self._load(name, u"IModule")
        
    def loadPostProcess(self, name):
        """
        @type name: unicode
        """
        return self._load(name, u"IPost")

    def unloadModule(self, name):
        """
        @type name: unicode
        """
        return self._unload(name, u"IModule")
        
    def unloadPostProcess(self, name):
        """
        @type name: unicode
        """
        return self._unload(name, u"IPost")
        
    def loadAllModules(self):
        for module in getPlugins(IModule, modules):
            if module.name is not None and module.name != "" and module.name != u"":
                self.loadModule(module.name)
    
    def loadPostProcesses(self):
        for module in getPlugins(IPost, postprocesses):
            if module.name is not None and module.name != "" and module.name != u"":
                self.loadPostProcess(module.name)
                
    def _load(self, name, interfaceName):
        """
        @type name: unicode
        @type interfaceName: unicode
        """
        if name is None or name == "" or name == u"":
            errorMsg = "Module name not specified!"
            log.err(errorMsg)
            return False, errorMsg
        if interfaceName == u"IModule":
            if name.lower() not in self.loadedModules:
                moduleReload = False
            else:
                moduleReload = True
            for module in getPlugins(IModule, modules):
                if module.name == name.lower():
                    self.loadedModules[module.name] = module
                    try:
                        self.loadedModules[module.name].onModuleLoaded()
                    except Exception as e:
                        errorMsg = "An error occurred while loading module \"{}\" ({})".format(module.name, e)
                        log.err(errorMsg)
                        return False, errorMsg
                    if moduleReload:
                        loadMsg = "Module \"{}\" was successfully reloaded!".format(module.name)
                        log.msg(loadMsg)
                        return True, loadMsg
                    else:
                        loadMsg = "Module \"{}\" was successfully loaded!".format(module.name)
                        log.msg(loadMsg)
                        return True, loadMsg
        elif interfaceName == u"IPost":
            if name.lower() not in self.loadedPostProcesses:
                moduleReload = False
            else:
                moduleReload = True
            for module in getPlugins(IPost, postprocesses):
                if module.name == name.lower():
                    self.loadedPostProcesses[module.name] = module
                    try:
                        self.loadedPostProcesses[module.name].onModuleLoaded()
                    except Exception as e:
                        errorMsg = "An error occurred while loading module \"{}\" ({})".format(module.name, e)
                        log.err(errorMsg)
                        return False, errorMsg
                    if moduleReload:
                        loadMsg = "Module \"{}\" was successfully reloaded!".format(module.name)
                        log.msg(loadMsg)
                        return True, loadMsg
                    else:
                        loadMsg = "Module \"{}\" was successfully loaded!".format(module.name)
                        log.msg(loadMsg)
                        return True, loadMsg
            return False, "No module named \"{}\" could be found!".format(name)
            
    def _unload(self, name, interfaceName):
        """
        @type name: unicode
        @type interfaceName: unicode
        """
        if name is None or name == "" or name == u"":
            errorMsg = "Module name not specified!"
            log.err(errorMsg)
            return False, errorMsg
        if interfaceName == u"IModule":
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
                return True, loadMsg
            else:
                errorMsg = "No module named \"{}\" is loaded!".format(name)
                log.err(errorMsg)
                return False, errorMsg
        if interfaceName == u"IPost":
            if name.lower() in self.loadedPostProcesses:
                try:
                    self.loadedPostProcesses[name.lower()].onModuleUnloaded()
                except Exception as e:
                    errorMsg = "An error occurred while unloading module \"{}\" ({})".format(module.name, e)
                    log.err(errorMsg)
                # Unload module so it doesn't get stuck, but emit the error still.
                del self.loadedPostProcesses[name.lower()]
                loadMsg = "Module \"{}\" was successfully unloaded!".format(module.name)
                log.msg(loadMsg)
                return True, loadMsg
            else:
                errorMsg = "No module named \"{}\" is loaded!".format(name)
                log.err(errorMsg)
                return False, errorMsg
        
