import os
import yaml


class Config(object):
    def __init__(self, server):
        self.configData = {}
        yaml.load(os.path.join("configs", "{}.yaml".format(server)))
        # TODO: Check whether or not all required config options are preesent

    def __iter__(self):
        return iter(self.configData)

    def __getitem__(self, key):
        return self.configData[key]