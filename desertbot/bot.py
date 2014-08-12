import logging
import pydle
import sys

from desertbot.botconnection import DesertBotConnection
from desertbot.config import ConfigHandler, ConfigException


class DesertBot(object):
    """
    The main class that will keep track of all open connections and configs.
    """
    def __init__(self, cmdArgs):
        """
        Creates a bot.
        :param cmdArgs: The arguments parsed from the command line
        :return:
        """
        self.connections = {}
        self.configs = {}
        self.cmdArgs = cmdArgs

        self.pool = pydle.ClientPool()
        self.configHandler = ConfigHandler()

        self._loadConfigs()
        self._intializeConnections()

        self.pool.handle_forever()

    def _loadConfigs(self):
        """
        Tells the config handler to load the default config file and all server config files it
        can find.
        :return:
        """
        logging.info("Loading configs...")
        try:
            self.configHandler.loadDefaultConfig(self.cmdArgs.configfile)
            logging.info("Loaded default config file {}".format(self.cmdArgs.configfile))
        except ConfigException as e:
            logging.error("Could not read config file {}, reason: {}".format(e.configFile,
                                                                             e.reason))
            # No need to continue without a default config file
            sys.exit(-1)

        for serverConfig in self.configHandler.getConfigList(self.cmdArgs.configfile):
            try:
                config = self.configHandler.loadServerConfig(serverConfig)
                self.configs[config["server"]] = config
                logging.info("Loaded server config file {}".format(serverConfig))
            except ConfigException as e:
                logging.error("Could not read config file {}, reason: {}. Skipping this file...".
                              format(e.configFile,
                                     e.reason))

    def _intializeConnections(self):
        """
        Starts up connections for all servers that have valid config files loaded in. This could
        be changed later to only make certain servers connect or an "autoconnect" field could be
        added to the config.
        :return:
        """
        for config in self.configs.keys():
            self.startConnection(config)

    def startConnection(self, server):
        """
        Creates a new server connection. The address has to be specified. All other settings will
        then be read from the config.
        :param server: The address of the server to connect to.
        :return:
        """
        config = self.configs[server]
        nicknames = config["nicknames"]
        # Check for fallback nicknames should the initial one be taken
        if len(nicknames) > 1:
            fallback = nicknames[1:]
        else:
            fallback = []

        # Intialize the connection
        connection = DesertBotConnection(nicknames[0], fallback, username=config["username"],
                                         realname=config["realname"])
        logging.info("Connecting to {}...".format(server))

        # Connect and add the connection to the client pool and the connections dictionary
        connection.connect(config["server"], config["port"], tls=config["tls"], tls_verify=False)
        self.connections[config["server"]] = connection
        self.pool.add(connection)

    def stopConnection(self, server):
        """
        Closes a server connection.
        :param server: The address of the server to disconnect from.
        :return:
        """
        # Disconnect and remove the connection from the dictionary and client pool
        connection = self.connections[server]
        connection.disconnect()
        self.pool.remove(connection)
        del self.connections[server]

    def quit(self, restart = False):
        pass
