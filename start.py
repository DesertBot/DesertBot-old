from desertbot.bot import DesertBot
import pydle

if __name__ == "__main__":
    pool = pydle.client.ClientPool()

    client = DesertBot('DesertBotPydle', realname='My Bot')
    client.connect('irc.desertbus.org', 6697, tls=True, tls_verify=False)
    client2 = DesertBot('DesertBotPydle', realname='My Bot')
    client2.connect('heufneutje.net', 6697, tls=True, tls_verify=False)
    pool.add(client)
    pool.add(client2)
    pool.handle_forever()
