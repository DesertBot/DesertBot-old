from twisted.plugin import IPlugin
from desertbot.moduleinterface import BotModule, IBotModule
from zope.interface import implements
from fnmatch import fnmatch


class Admin(BotModule):
    implements(IPlugin, IBotModule)

    name = "Admin"

    def actions(self):
        return [ ("checkadminpermission", 1, self.checkPermission) ]

    def checkPermission(self, server, source, user, permission):
        # TODO: Implement admin permission system
        if not self.bot.moduleHandler.useModuleOnServer(self.name, server):
            return False

        adminList = self.bot.config.serverItemWithDefault(server, "bot_admins", [])
        for adminHost in adminList:
            if fnmatch(user.fullUserPrefix(), adminHost):
                return True
        self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "You do not have the \"{}\" permission!"
                                                          .format(permission))
        return False

admin = Admin()
