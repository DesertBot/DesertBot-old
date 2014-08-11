import os

from yaml import load
from yaml.parser import ParserError
from yaml.scanner import ScannerError


class ConfigHandler(object):
    def __init__(self):
        self.defaultConfigData = {}

    def loadDefaultConfig(self, defaultConfig):
        if os.path.exists(os.path.join("config", defaultConfig)):
            with open(os.path.join("config", defaultConfig), "r") as defaultConfig:
                try:
                    self.defaultConfigData = load(defaultConfig)
                except ScannerError as e:
                    raise ConfigException(defaultConfig, e.problem)
                except ParserError as e:
                    raise ConfigException(defaultConfig, e.problem)
        else:
            raise ConfigException(defaultConfig, "File not found.")

    def loadServerConfig(self, serverConfig):
        serverConfigData = self.defaultConfigData.copy()
        with open(os.path.join("config", serverConfig), "r") as defaultConfig:
            try:
                serverConfigData.update(load(defaultConfig))
            except ScannerError as e:
                raise ConfigException(defaultConfig, e.problem)
            except ParserError as e:
                raise ConfigException(defaultConfig, e.problem)

        missing = self._validateConfig(serverConfigData)
        if len(missing) == 0:
            return serverConfigData
        else:
            raise ConfigException(serverConfig, "Required values {} were not found in {}".
                                  format(", ".join(missing),
                                         serverConfig))

    def _validateConfig(self, serverConfigData):
        required = ["nickname", "username", "realname", "server"]
        missing = []
        for req in required:
            if req not in serverConfigData.keys():
                missing.append(req)
            return missing


class ConfigException(Exception):
    def __init__(self, configFile, reason):
        self.configFile = configFile
        self.reason = reason

    def __str__(self):
        return "Could not read config file {}, reason: {}".format(self.configFile, self.reason)
