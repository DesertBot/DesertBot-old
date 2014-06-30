# -*- coding: utf-8 -*-
import operator
import re

from twisted.plugin import getPlugins
from twisted.python import log
from twisted.internet import threads

from desertbot.moduleinterface import IModule, ModuleType, AccessLevel
from desertbot.postprocessinterface import IPost
from desertbot.response import IRCResponse, ResponseType
from desertbot.message import IRCMessage
from desertbot.user import IRCUser
from desertbot import modules, postprocesses


class ModuleHandler(object):
    def __init__(self, bot):
        """
        @type bot: desertbot.DesertBot
        """
        self.bot = bot
        self.loadedModules = {}
        self.loadedPostProcesses = {}

    def handleMessage(self, message):
        """
        @type message: IRCMessage
        """
        for module in sorted(self.loadedModules.values(),
                             key=operator.attrgetter("modulePriority")):
            try:
                if self._shouldTrigger(module, message):
                    if not module.runInThread:
                        response = module.onTrigger(message)
                        self.postProcess(response)
                    else:
                        d = threads.deferToThread(module.onTrigger, message)
                        d.addCallback(self.postProcess)
            except Exception as e:
                errorMsg = "An error occured while handling message: \"{}\" ({})".format(
                    message.text, e)
                log.err(errorMsg)

    def postProcess(self, response):
        """
        @type response: IRCResponse
        """
        newResponse = response
        processed = False
        for post in sorted(self.loadedPostProcesses.values(),
                           key=operator.attrgetter("modulePriority")):
            try:
                if post.shouldTrigger(newResponse):
                    processed = True
                    if not post.runInThread:
                        newResponse = post.onTrigger(newResponse)
                        self.sendResponse(newResponse)
                    else:
                        d = threads.deferToThread(post.onTrigger, newResponse)
                        d.addCallback(self.sendResponse)
            except Exception as e:
                errorMsg = "An error occured while postprocessing: \"{}\" ({})".format(
                    response.response, e)
                log.err(errorMsg)
                self.sendResponse(newResponse)
        if not processed:
            self.sendResponse(newResponse)

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
                # the response needs to be encoded from unicode to a
                # utf-8 string before we send it out
                responseText = response.response.encode('utf-8')
                responseTarget = response.target.encode('utf-8')
                if response.type == ResponseType.PRIVMSG:
                    self.bot.msg(responseTarget, responseText)
                elif response.type == ResponseType.ACTION:
                    self.bot.describe(responseTarget, responseText)
                elif response.type == ResponseType.NOTICE:
                    self.bot.notice(responseTarget, responseText)
                elif response.type == ResponseType.RAW:
                    self.bot.sendLine(responseText)
            except Exception as e:
                errorMsg = "An error occurred while sending response: \"{}\" ({})".format(
                    response.response, e)
                log.err(errorMsg)

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

    def _shouldTrigger(self, module, message):
        """
        @type message: IRCMessage
        """
        if message.type in module.messageTypes:
            if module.moduleType == ModuleType.PASSIVE:
                return True
            elif message.user.nickname == self.bot.nickname:
                return False
            elif module.moduleType == ModuleType.ACTIVE:
                for trigger in module.triggers:
                    match = re.search(".*{}.*".format(trigger), message.text,
                                      re.IGNORECASE)
                    if match:
                        return True
                return False
            elif module.moduleType == ModuleType.COMMAND:
                if message.command in module.triggers and self._allowedToUse(module, message):
                    return True
                else:
                    return False
            elif module.moduleType == ModuleType.UTILITY:
                return module.shouldTrigger(message)

    def _allowedToUse(self, module, message):
        """
        @type message: IRCMessage
        """
        if module.accessLevel == AccessLevel.ANYONE:
            return True
            
        if message.user is None:
            return True  # message is probably server stuff
            
        if module.accessLevel == AccessLevel.ADMINS:
            for adminRegex in self.bot.admins:
                if re.match(adminRegex, message.user.getUserString()):
                    return True
                    
            response = IRCResponse(ResponseType.PRIVMSG,
                                   u"Only my admins can use \"{}\"!".format(message.command),
                                   message.user, message.replyTo)
            self.postProcess(response)
            return False

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
                        self.loadedModules[module.name].hookBot(self.bot)
                        self.loadedModules[module.name].onModuleLoaded()
                    except Exception as e:
                        errorMsg = "An error occurred while loading module \"{}\" ({})".format(
                            module.name, e)
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
            errorMsg = "No module named \"{}\" could be found!".format(name)
            log.err(errorMsg)
            return False, errorMsg
        elif interfaceName == u"IPost":
            if name.lower() not in self.loadedPostProcesses:
                moduleReload = False
            else:
                moduleReload = True
            for module in getPlugins(IPost, postprocesses):
                if module.name == name.lower():
                    self.loadedPostProcesses[module.name] = module
                    try:
                        self.loadedPostProcesses[module.name].hookBot(self.bot)
                        self.loadedPostProcesses[module.name].onModuleLoaded()
                    except Exception as e:
                        errorMsg = "An error occurred while loading module \"{}\" ({})".format(
                            module.name, e)
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
            errorMsg = "No module named \"{}\" could be found!".format(name)
            log.err(errorMsg)
            return False, errorMsg

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
                    errorMsg = "An error occurred while unloading module \"{}\" ({})".format(name,
                                                                                             e)
                    log.err(errorMsg)
                # Unload module so it doesn't get stuck, but emit the error still.
                del self.loadedModules[name.lower()]
                loadMsg = "Module \"{}\" was successfully unloaded!".format(name)
                log.msg(loadMsg)
                return True, loadMsg
            else:
                errorMsg = "No module named \"{}\" is loaded!".format(name)
                log.err(errorMsg)
                return False, errorMsg
        elif interfaceName == u"IPost":
            if name.lower() in self.loadedPostProcesses:
                try:
                    self.loadedPostProcesses[name.lower()].onModuleUnloaded()
                except Exception as e:
                    errorMsg = "An error occurred while unloading module \"{}\" ({})".format(name,
                                                                                             e)
                    log.err(errorMsg)
                # Unload module so it doesn't get stuck, but emit the error still.
                del self.loadedPostProcesses[name.lower()]
                loadMsg = "Module \"{}\" was successfully unloaded!".format(name)
                log.msg(loadMsg)
                return True, loadMsg
            else:
                errorMsg = "No module named \"{}\" is loaded!".format(name)
                log.err(errorMsg)
                return False, errorMsg
