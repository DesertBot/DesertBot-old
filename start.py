import argparse
import os

from desertbot.bot import DesertBot
from desertbot.botconnection import DesertBotConnection


parser = argparse.ArgumentParser(description="A modular IRC bot written in Python, using Pydle as its backend.")
cmdArgs = parser.parse_args()

if __name__ == "__main__":
    # Create folders
    if not os.path.exists(os.path.join("config")):
        os.makedirs("config")

    # TODO: Start logging here

    # Create the bot to get started
    desertbot = DesertBot(cmdArgs)
