import yaml

_required = ["servers"]

class Config(object):

    def __init__(self, configFile):
        self.configFile = configFile
        self._configData = {}

    def loadConfig(self):
        configData = self._readConfig(self.configFile)
        self._validateConfigData(configData)
        self._configData = configData

    # From txircd:
    # https://github.com/ElementalAlchemist/txircd/blob/762e5ae6fa740f52e6b18fd6d2f9d2ee2507d263/txircd/config.py#L50
    def _readConfig(self, fileName):
        try:
            with open(fileName, "r") as config:
                configData = yaml.safe_load(config)
                if not configData:
                    configData = {}
        except Exception as e:
            raise ConfigError(fileName, e)

        if "include" in configData:
            for fileName in configData["include"]:
                includeConfig = self._readConfig(fileName)
                for key, val in includeConfig.iteritems():
                    if key not in configData:
                        configData[key] = val
                    elif not isinstance(configData[key], basestring): # Let's try to merge them if they're collections
                        if isinstance(val, basestring):
                            raise ConfigError(fileName, "The included configuration file tried to merge a non-string "
                                                        "with a string.")
                        try: # Make sure both things we're merging are still iterable types (not numbers or whatever)
                            iter(configData[key])
                            iter(val)
                        except TypeError:
                            pass # Just don't merge them if they're not
                        else:
                            try:
                                configData[key] += val # Merge with the + operator
                            except TypeError: # Except that some collections (dicts) can't
                                try:
                                    for subkey, subval in val.iteritems(): # So merge them manually
                                        if subkey not in configData[key]:
                                            configData[key][subkey] = subval
                                except (AttributeError, TypeError):
                                    # If either of these, they weren't both dicts (but were still iterable);
                                    # requires user to resolve
                                    raise ConfigError(fileName, "The variable {} could not be successfully merged "
                                                                "across files.".format(key))
            del configData["include"]
        return configData


    def _validateConfigData(self, configData):
        for item in _required:
            if item not in configData:
                raise ConfigError(self.configFile, "Required item \"{}\" was not found in the config.".format(item))

    def __len__(self):
        return len(self._configData)

    def __iter__(self):
        return iter(self._configData)

    def __getitem__(self, item):
        return self._configData[item]

    def itemWithDefault(self, item, default):
        if item in self._configData:
            return self._configData[item]
        return default

    def serverItemWithDefault(self, server, item, default):
        if item in self._configData["servers"][server]:
            return self._configData["servers"][server][item]
        if item in self._configData:
            return self._configData[item]
        return default

class ConfigError(Exception):
    def __init__(self, configFile, message):
        self.configFile = configFile
        self.message = message

    def __str__(self):
        return "An error occurred while reading config file {}: {}".format(self.configFile, self.message)
