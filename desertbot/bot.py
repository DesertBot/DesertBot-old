import pydle
import logging
import sys

from desertbot.botconnection import DesertBotConnection
from desertbot.config import ConfigHandler, ConfigException


class DesertBot(object):
    # Static variable for the default config. Could make this a command line arg in the future.
    DEFAULT_CONFIG = "default.yaml"

    def __init__(self, cmdArgs):
        self.connections = {}
        self.configs = {}
        self.cmdArgs = cmdArgs

        self.pool = pydle.ClientPool()
        self.configHandler = ConfigHandler()

        self._loadConfigs()
        self._intializeConnections()

        self.pool.handle_forever()

    def _loadConfigs(self):
        logging.info("Loading configs...")
        try:
            self.configHandler.loadDefaultConfig(self.DEFAULT_CONFIG)
            logging.info("Loaded default config file {}".format(self.DEFAULT_CONFIG))
        except ConfigException as e:
            logging.error("Could not read config file {}, reason: {}".format(e.configFile,
                                                                             e.reason))
            # No need to continue without a default config file
            sys.exit(-1)

        for serverConfig in self.configHandler.getConfigList(self.DEFAULT_CONFIG):
            try:
                config = self.configHandler.loadServerConfig(serverConfig)
                self.configs[config["server"]] = config
                logging.info("Loaded server config file {}".format(serverConfig))
            except ConfigException as e:
                logging.error("Could not read config file {}, reason: {}. Skipping this file...".
                              format(e.configFile,
                                     e.reason))

    def _intializeConnections(self):
        for config in self.configs.keys():
            self.startConnection(config)

    def startConnection(self, server):
        config = self.configs[server]
        nicknames = config["nicknames"]
        if len(nicknames) > 1:
            fallback = nicknames[1:]
        else:
            fallback = []
        connection = DesertBotConnection(nicknames[0], fallback, username=config["username"],
                                         realname=config["realname"])

        logging.info("Connecting to {}...".format(server))
        connection.connect(config["server"], config["port"], tls=config["tls"], tls_verify=False)
        self.connections[config["server"]] = connection
        self.pool.add(connection)

    def stopConnection(self, server):
        connection = self.connections[server]
        connection.disconnect()
        self.pool.remove(connection)
        del self.connections[server]

    def quit(self, restart = False):
        pass
