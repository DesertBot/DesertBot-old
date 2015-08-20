from twisted.plugin import IPlugin
from desertbot.moduleinterface import BotModule, IBotModule
from zope.interface import implements


class UserLocationChatmap(BotModule):
    implements(IPlugin, IBotModule)

    name = "UserLocationChatmap"
    baseURL = "http://tsukiakariusagi.net/chatmaplookup.php?"

    def actions(self):
        return [ ("userlocation", 1, self.userLocationFromDBChatmap) ]

    def userLocationFromDBChatmap(self, server, source, user, displayErrors):
        if not self.bot.moduleHandler.useModuleOnServer(self.name, server):
            return

        params = {
            "nick": user
        }
        result = self.bot.moduleHandler.runActionUntilValue("fetch-url", self.baseURL, params)
        if not result:
            if displayErrors:
                self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "Chatmap is currently unavailable. Try again "
                                                                          "later.")
            return None
        if result.text == ",":
            if displayErrors:
                self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "You are not on the chatmap.")
            return {
                "success": False
            }
        else:
            coords = result.text.split(",")
            return {
                "success": True,
                "lat": float(coords[0]),
                "lon": float(coords[1])
            }

userLocDB = UserLocationChatmap()
