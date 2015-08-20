# Taken from txircd:
# https://github.com/ElementalAlchemist/txircd/blob/8832098149b7c5f9b0708efe5c836c8160b0c7e6/txircd/utils.py#L9
def _enum(**enums):
    return type('Enum', (), enums)

ModeType = _enum(LIST=0, PARAM_SET=1, PARAM_UNSET=2, NO_PARAM=3)
ModuleLoadType = _enum(LOAD=0, UNLOAD=1, ENABLE=2, DISABLE=3)

def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def parseUserPrefix(prefix):
    if "!" in prefix:
        nick = prefix[:prefix.find("!")]
        ident = prefix[prefix.find("!") + 1:prefix.find("@")]
        host = prefix[prefix.find("@") + 1:]
        return nick, ident, host

    # Not all "users" have idents and hostnames
    nick = prefix
    return nick, None, None

def networkName(bot, server):
    return bot.servers[server].supportHelper.network
