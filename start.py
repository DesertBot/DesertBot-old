from desertbot.bot import DesertBot

if __name__ == "__main__":
    client = DesertBot('DesertBotPydle', realname='My Bot')
    client.connect('irc.desertbus.org', 6697, tls=True, tls_verify=False)
    client.handle_forever()
