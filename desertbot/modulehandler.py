from twisted.plugin import getPlugins
from twisted.python.rebuild import rebuild
from desertbot.moduleinterface import IBotModule
from desertbot.utils import ModuleLoadType
import desertbot.modules, importlib


class ModuleHandler(object):
    def __init__(self, bot):
        self.bot = bot
        self.loadedModules = {}
        self.enabledModules = {}
        self.actions = {}

    def loadModule(self, name):
        for module in getPlugins(IBotModule, desertbot.modules):
            if not module.name:
                raise ModuleLoaderError("???", "Module did not provide a name.", ModuleLoadType.LOAD)
            if module.name.lower() == name.lower():
                rebuild(importlib.import_module(module.__module__))
                self._loadModuleData(module)
                return module.name
        raise ModuleLoaderError(name, "The module could not be found.", ModuleLoadType.LOAD)

    def _loadModuleData(self, module):
        # Make sure the module meets the requirements and is not already loaded
        if not IBotModule.providedBy(module):
            raise ModuleLoaderError("???", "Module doesn't implement the module interface.", ModuleLoadType.LOAD)
        if module.name in self.loadedModules:
            raise ModuleLoaderError(module.name, "Module is already loaded.", ModuleLoadType.LOAD)

        # We're good at this point so we can start initializing the module now
        module.hookBot(self.bot)
        actions = {}
        for action in module.actions():
            if action[0] not in actions:
                actions[action[0]] = [ (action[2], action[1]) ]
            else:
                actions[action[0]].append((action[2], action[1]))

        # Add the actions implemented by the module and sort them by priority
        for action, actionList in actions.iteritems():
            if action not in self.actions:
                self.actions[action] = []
            for actionData in actionList:
                for index, handlerData in enumerate(self.actions[action]):
                    if handlerData[1] < actionData[1]:
                        self.actions[action].insert(index, actionData)
                        break
                else:
                    self.actions[action].append(actionData)

        # Add the module to the list of loaded modules and call its load hooks
        self.loadedModules[module.name] = module
        module.load()

        # Enable the module for the appropriate servers
        for server in self.bot.servers.iterkeys():
            if "disabled_modules" not in self.bot.config["servers"][server]:
                self.enableModule(module.name, server)
            elif module not in self.bot.config["servers"][server]["disabled_modules"]:
                self.enableModule(module.name, server)

        self.runGenericAction("moduleload", module.name)

    def unloadModule(self, name):
        lowercaseMapping = dict((k.lower(), v) for k, v in self.loadedModules.iteritems())
        if name.lower() not in lowercaseMapping:
            raise ModuleLoaderError(name, "The module is not loaded.", ModuleLoadType.UNLOAD)
        module = lowercaseMapping[name.lower()]
        module.unload()
        self.runGenericAction("moduleunload", module.name)
        for action in module.actions():
            self.actions[action[0]].remove((action[2], action[1]))
        for server, moduleList in self.enabledModules.iteritems():
            if module.name in moduleList:
                self.disableModule(module.name, server, True)
        del self.loadedModules[module.name]
        return module.name

    def reloadModule(self, name):
        self.unloadModule(name)
        return self.loadModule(name)

    def enableModule(self, module, server):
        lowercaseLoaded = dict((k.lower(), v) for k, v in self.loadedModules.iteritems())
        if module.lower() not in lowercaseLoaded:
            raise ModuleLoaderError(module, "The module is not loaded.", ModuleLoadType.ENABLE)
        if server not in self.enabledModules:
            self.enabledModules[server] = []
        properCaseName = lowercaseLoaded[module.lower()].name
        if properCaseName in self.enabledModules[server]:
            raise ModuleLoaderError(properCaseName, "The module is already enabled.", ModuleLoadType.ENABLE)
        self.enabledModules[server].append(properCaseName)
        lowercaseLoaded[module.lower()].enable(server)
        return properCaseName

    def disableModule(self, module, server, forUnload = False):
        lowercaseLoaded = dict((k.lower(), v) for k, v in self.loadedModules.iteritems())
        if module.lower() not in lowercaseLoaded:
            raise ModuleLoaderError(module, "The module is not loaded.", ModuleLoadType.DISABLE)
        if server not in self.enabledModules:
            self.enabledModules[server] = []
        properCaseName = lowercaseLoaded[module.lower()].name
        if properCaseName not in self.enabledModules[server]:
            raise ModuleLoaderError(properCaseName, "The module is not enabled.", ModuleLoadType.DISABLE)
        if not self.loadedModules[properCaseName].canDisable and not forUnload:
            raise ModuleLoaderError(properCaseName, "The module can never be disabled.", ModuleLoadType.DISABLE)
        self.enabledModules[server].remove(properCaseName)
        lowercaseLoaded[module.lower()].disable(server)
        return properCaseName

    def loadAllModules(self):
        requestedModules = self.bot.config.itemWithDefault("modules", [])
        for module in requestedModules:
            try:
                self.loadModule(module)
            except ModuleLoaderError as e:
                self.bot.log.error("Module {module} failed to load: {error.message}", module=module, error=e)

    def unloadAllModules(self):
        modules = self.loadedModules.keys()
        for module in modules:
            self.unloadModule(module)

    def enableModulesForServer(self, server):
        if server not in self.enabledModules:
            self.enabledModules[server] = []
        for module in self.loadedModules.iterkeys():
            if "disabled_modules" not in self.bot.config["servers"][server]:
                self.enableModule(module, server)
            elif module not in self.bot.config["servers"][server]["disabled_modules"]:
                self.enableModule(module, server)

    def useModuleOnServer(self, module, server):
        if module not in self.loadedModules or server not in self.enabledModules:
            # A module gave us a bogus name or the server has no enabled modules. Reject it to prevent weird things.
            return False
        if not self.loadedModules[module].canDisable:
            # Modules that can't be disabled are always allowed.
            return True
        if module in self.enabledModules[server]:
            return True
        return False

    def runGenericAction(self, actionName, *params, **kw):
        actionList = []
        if actionName in self.actions:
            actionList = self.actions[actionName]
        for action in actionList:
            action[0](*params, **kw)

    def runProcessingAction(self, actionName, data, *params, **kw):
        actionList = []
        if actionName in self.actions:
            actionList = self.actions[actionName]
        for action in actionList:
            action[0](data, *params, **kw)
            if not data:
                return

    def runActionUntilTrue(self, actionName, *params, **kw):
        actionList = []
        if actionName in self.actions:
            actionList = self.actions[actionName]
        for action in actionList:
            if action[0](*params, **kw):
                return True
        return False

    def runActionUntilFalse(self, actionName, *params, **kw):
        actionList = []
        if actionName in self.actions:
            actionList = self.actions[actionName]
        for action in actionList:
            if not action[0](*params, **kw):
                return True
        return False

    def runActionUntilValue(self, actionName, *params, **kw):
        actionList = []
        if actionName in self.actions:
            actionList = self.actions[actionName]
        for action in actionList:
            value = action[0](*params, **kw)
            if value:
                return value
        return None

class ModuleLoaderError(Exception):
    def __init__(self, module, message, loadType):
        self.module = module
        self.message = message
        self.loadType = loadType

    def __str__(self):
        if self.loadType == ModuleLoadType.LOAD:
            return "Module {} could not be loaded: {}".format(self.module, self.message)
        elif self.loadType == ModuleLoadType.UNLOAD:
            return "Module {} could not be unloaded: {}".format(self.module, self.message)
        elif self.loadType == ModuleLoadType.ENABLE:
            return "Module {} could not be enabled: {}".format(self.module, self.message)
        elif self.loadType == ModuleLoadType.DISABLE:
            return "Module {} could not be disabled: {}".format(self.module, self.message)
        return "Error: {}".format(self.message)
