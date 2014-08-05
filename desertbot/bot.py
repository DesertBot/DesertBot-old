import pydle

from botconnection import DesertBotConnection


class DesertBot(object):
    def __init__(self, cmdArgs):
        self.connections = {}
        self.configs = {}
        self.cmdArgs = cmdArgs
        self.pool = pydle.ClientPool()

        self._loadConfigs()

        self.pool.handle_forever()

    def _loadConfigs(self):
        pass

    def startConnection(self, server):
        config = self.configs[server]
        connection = DesertBotConnection(config["nicknames"][0], config["nicknames"][1:], username = config["username"], realname = config["realname"])

        connection.connect(config["server"], config["port"], tls=False, tls_verify=False)
        self.connections[config["server"]] = connection
        self.pool.add(connection)

    def stopConnection(self, server):
        pass

    def quit(self, restart = False):
        pass
