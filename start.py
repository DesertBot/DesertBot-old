import argparse
import logging
import os

from desertbot.bot import DesertBot


parser = argparse.ArgumentParser(description="A modular IRC bot written in Python, using Pydle as "
                                             "its backend.")
cmdArgs = parser.parse_args()

if __name__ == "__main__":
    # Create folders
    if not os.path.exists(os.path.join("config")):
        os.makedirs("config")

    # Initialize logging
    logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s] "
                                     " %(message)s")
    logger = logging.getLogger("")
    logger.setLevel(logging.INFO)

    # Set up file logging
    fileHandler = logging.FileHandler("desertbot.log")
    fileHandler.setFormatter(logFormatter)
    fileHandler.setLevel(logging.INFO)
    logger.addHandler(fileHandler)

    # Set up console logging
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    consoleHandler.setLevel(logging.INFO)
    logger.addHandler(consoleHandler)

    # Create the bot to get started
    desertbot = DesertBot(cmdArgs)
