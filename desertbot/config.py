import os
import yaml


class Config(object):
    def __init__(self, server):
        self.configData = {}
        yaml.load(os.path.join("configs", "{}.yaml".format(server)))

    def __iter__(self):
        return iter(self.configData)

    def __getitem__(self, key):
        return self.configData[key]

    def checkRequiredValues(self):
        required = ["nickname", "username", "realname"]
        return True if required in self.configData else False
