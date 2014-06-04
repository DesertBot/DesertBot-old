import os
import yaml
from twisted.python import log


class Config(object):
    def __init__(self, configFileName):
        self.configData = {}
        self.configFileName = configFileName

    def loadConfig(self):
        if not os.path.exists(os.path.join("config", self.configFileName)):
            log.err("Config file \"{}\" was not found!".format(self.configFileName))
            return False

        try:
            with open(os.path.join("config", self.configFileName), 'r') as configFile:
                configData = yaml.load(configFile)
            self.configData = configData
            return True

        except yaml.parser.ParserError as e:
            log.err("An error occurred while reading file \"{}\": {}".format(self.configFileName, e))
            return False

    def __iter__(self):
        return iter(self.configData)

    def __getitem__(self, key):
        return self.configData[key]

    def checkRequiredValues(self):
        required = ["nickname", "username", "realname"]
        return True if required in self.configData else False
