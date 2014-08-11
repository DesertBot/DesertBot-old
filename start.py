import argparse
import logging
import os

from desertbot.bot import DesertBot


parser = argparse.ArgumentParser(description="A modular IRC bot written in Python, using Pydle as "
                                             "its backend.")
parser.add_argument("-f", "--logfile", help="The file the debug log will be written to (default "
                                            "desertbot.log).", type=str, default="desertbot.log")
parser.add_argument("-l", "--loglevel", help="The logging level that will be used while running "
                                             "the bot (default INFO).", type=str, default="INFO")
cmdArgs = parser.parse_args()

if __name__ == "__main__":
    # Create folders
    if not os.path.exists(os.path.join("config")):
        os.makedirs("config")

    # Initialize logging
    logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s] "
                                     " %(message)s")
    logger = logging.getLogger()

    # Determine the logging level
    numeric_level = getattr(logging, cmdArgs.loglevel.upper(), None)
    if isinstance(numeric_level, int):
        logger.setLevel(numeric_level)
    else:
        raise ValueError("Invalid log level {}".format(cmdArgs.loglevel))

    # Set up file logging
    fileHandler = logging.FileHandler(cmdArgs.logfile)
    fileHandler.setFormatter(logFormatter)
    fileHandler.setLevel(numeric_level)
    logger.addHandler(fileHandler)

    # Set up console logging
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    consoleHandler.setLevel(numeric_level)
    logger.addHandler(consoleHandler)

    # Create the bot to get started
    desertbot = DesertBot(cmdArgs)
