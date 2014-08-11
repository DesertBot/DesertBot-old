import os
import yaml


class ConfigHandler(object):
    def loadDefaultConfig(self, defaultConfig):
        if not os.path.exists(os.path.join("config", defaultConfig)):
            raise ConfigException(defaultConfig, "File not found.")

    def loadServerConfig(self):
        pass

    def _validateConfig(self):
        pass


class ConfigException(Exception):
    def __init__(self, configFile, reason):
        self.configFile = configFile
        self.reason = reason

    def __str__(self):
        return "Could not read config file {}, reason: {}".format(self.configFile, self.reason)
