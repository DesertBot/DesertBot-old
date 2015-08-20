from twisted.plugin import IPlugin
from desertbot.moduleinterface import BotModule, IBotModule
from zope.interface import implements


class NickServIdentify(BotModule):
    implements(IPlugin, IBotModule)

    name = "NickServIdentify"

    def actions(self):
        return [ ("welcome", 1, self.identify) ]

    def identify(self, serverName):
        if not self.bot.moduleHandler.useModuleOnServer(self.name, serverName):
            return

        if "nickserv_nick" not in self.bot.config and "nickserv_nick" not in self.bot.config["servers"][serverName]:
            nick = "NickServ"
            self.bot.log.warn("[{connection}] No valid NickServ nickname was found; defaulting to NickServ...",
                              connection=serverName)
        else:
            nick = self.bot.config.serverItemWithDefault(serverName, "nickserv_nick", "NickServ")
        if "nickserv_pass" not in self.bot.config and "nickserv_pass" not in self.bot.config["servers"][serverName]:
            self.bot.log.warn("[{connection}] No NickServ password found. Aborting authentication...",
                              connection=serverName)
            return
        password = self.bot.config.serverItemWithDefault(serverName, "nickserv_pass", None)
        self.bot.servers[serverName].outputHandler.cmdPRIVMSG(nick, "IDENTIFY {}".format(password))

nickServID = NickServIdentify()
