import os

from yaml import load
from yaml.parser import ParserError
from yaml.scanner import ScannerError


class ConfigHandler(object):
    """
    A class that serves to load, validate and list config files.
    """
    def __init__(self):
        """
        Creates a config handler and initialize it with a dictionary in which the default data
        will be stored.
        :return:
        """
        self.defaultConfigData = {}

    def loadDefaultConfig(self, defaultConfig):
        """
        Loads the default config file and initializes the defaultConfigData dictionary with the
        values read from it.
        :param defaultConfig: The name of the default config file.
        :return:
        """
        if os.path.exists(os.path.join("config", defaultConfig)):
            with open(os.path.join("config", defaultConfig), "r") as defaultConfig:
                try:
                    self.defaultConfigData = load(defaultConfig)
                except ScannerError as e:
                    # We got a garbled YAML file
                    raise ConfigException(defaultConfig, e.problem)
                except ParserError as e:
                    raise ConfigException(defaultConfig, e.problem)
        else:
            raise ConfigException(defaultConfig, "File not found.")

    def loadServerConfig(self, serverConfig):
        """
        Loads the config for the given server, creates a copy of the default config values and
        updates these.
        :param serverConfig: The name of the server config file.
        :return serverConfigFata: The dictionary with the config values that will be used for the
        specified server.
        """
        serverConfigData = self.defaultConfigData.copy()
        with open(os.path.join("config", serverConfig), "r") as defaultConfig:
            try:
                serverConfigData.update(load(defaultConfig))
            except ScannerError as e:
                # We got a garbled YAML file
                raise ConfigException(defaultConfig, e.problem)
            except ParserError as e:
                raise ConfigException(defaultConfig, e.problem)

        missing = self._validateConfig(serverConfigData)
        if len(missing) == 0:
            return serverConfigData
        else:
            raise ConfigException(serverConfig, "Required values \"{}\" were not found".
                                  format("\", \"".join(missing)))

    def _validateConfig(self, serverConfigData):
        """
        Makes sure all required values are present in the config.
        :param serverConfigData: The dictionary that will be checked.
        :return missing: The list of missing values. This list will be empty if the config has
        all required values.
        """
        required = ["nicknames", "username", "realname", "server"]
        missing = []
        for req in required:
            if req not in serverConfigData.keys():
                missing.append(req)
        return missing

    def getConfigList(self, defaultConfig):
        """
        Scans the config folder for all .yaml files.
        :param defaultConfig: The name of the default config file (to exclude it in searching).
        :return configs: A list of all config files found in the config folder.
        """
        root = os.path.join("config")
        configs = []
        for item in os.listdir(root):
            if not os.path.isfile(os.path.join(root, item)):
                continue
            if not item.endswith(".yaml"):
                continue
            if item == defaultConfig:
                continue
            configs.append(item)
        return configs


class ConfigException(Exception):
    """
    A custom exception class to inform the user of errors in the config files.
    """
    def __init__(self, configFile, reason):
        """
        Creates a config exception.
        :param configFile: The file that caused the exception.
        :param reason: The reason why the exception occurred.
        :return:
        """
        self.configFile = configFile
        self.reason = reason

    def __str__(self):
        """
        A string representation of the exception.
        :return:
        """
        return "Could not read config file {}, reason: {}".format(self.configFile, self.reason)
