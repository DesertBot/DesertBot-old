from zope.interface import Attribute, Interface


class IBotModule(Interface):
    name = Attribute("The module's name.")
    canDisable = Attribute("Whether or not this module can be blacklisted on a specific server. True by default. "
                           "Core module override this flag and cannot be blacklisted for any server.")

    def hookBot(bot):
        """
        Called when the module is loaded and is used to hook the bot instance to be used later.
        """

    def actions():
        """
        Returns the list of actions this module hooks into. Actions are defined as a tuple with the following values:
        [ (actionname, priority, function) ]
        actionname (string):  The name of the action.
        priority (int):       Actions are handled in order of priority. Typically you should stick to a priority of 1,
                              unless you're overriding another hook of this action.
        function (reference): A reference to the function in the module that handles this action.
        """

    def load():
        """
        Called when the module is loaded. This is typically where configuration values are being read and stored.
        """

    def unload():
        """
        Called when the module is unloaded. Cleanup should happen here.
        """
    def enable(server):
        """
        Called when the module is enabled for a server. This is where server specific intializing can be done.
        """

    def disable(server):
        """
        Called when the module is disabled for a server. Server specific cleanup should happen here.
        """

class BotModule(object):
    canDisable = True

    def hookBot(self, bot):
        self.bot = bot

    def actions(self):
        return []

    def load(self):
        pass

    def unload(self):
        pass

    def enable(self, server):
        pass

    def disable(self, server):
        pass
