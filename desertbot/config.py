# -*- coding: utf-8 -*-
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
            with open(os.path.join("config", "globals.yaml"), "r") as globalConfigFile:
                configData = yaml.load(globalConfigFile)
            with open(os.path.join("config", self.configFileName), 'r') as configFile:
                configData.update(yaml.load(configFile))
            if "port" not in configData:
                configData["port"] = 6667
            self.configData = configData

            return self.checkRequiredValues()

        except yaml.ParserError as e:
            log.err("An error occurred while reading file \"{}\": {}".format(self.configFileName, e))
            return False

    def __iter__(self):
        return iter(self.configData)

    def __getitem__(self, key):
        return self.configData[key]

    def checkRequiredValues(self):
        required = ["nickname", "username", "realname", "server"]
        if required in self.configData:
            return True
        else:
            missing = [data for data in required if data not in self.configData]
            log.err("Required config data \"{}\" not found in \"{}\"!".format(", ".join(missing), self.configFileName))
            return False
