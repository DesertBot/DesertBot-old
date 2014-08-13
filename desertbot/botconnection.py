import pydle


class DesertBotConnection(pydle.Client):
    def on_connect(self):
        pass

    def on_join(self, channel, by):
        pass

    def on_kill(self, target, by, reason):
        pass

    def on_kick(self, channel, target, by, reason):
        pass

    def on_mode_change(self, channel, modes, by):
        pass

    def on_user_mode_change(self, modes):
        pass

    def on_message(self, target, by, message):
        # We might not need this one since it's generic
        pass

    def on_channel_message(self, target, by, message):
        pass

    def on_private_message(self, by, message):
        pass

    def on_nick_change(self, old, new):
        pass

    def on_notice(self, target, by, message):
        # We might not need this one since it's generic
        pass

    def on_channel_notice(self, target, by, message):
        pass

    def on_private_notice(self, by, message):
        pass

    def on_part(self, channel, user, message):
        pass

    def on_topic_change(self, channel, message, by):
        pass

    def on_quit(self, user, message):
        pass
