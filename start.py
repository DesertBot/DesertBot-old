import argparse
import logging
import os

from desertbot.bot import DesertBot


parser = argparse.ArgumentParser(description="A modular IRC bot written in Python, using Pydle as "
                                             "its backend.")
parser.add_argument("-c", "--configfile",
                    help="The default config file that will be used for all config files (default "
                         "default.yaml.",
                    type=str,
                    default="default.yaml")
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
    invalidLogLevel = False
    if not isinstance(numeric_level, int):
        numeric_level = logging.INFO
        invalidLogLevel = True
    logger.setLevel(numeric_level)

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

    # Yell at the user if they specified an invalid log level
    if invalidLogLevel:
        logger.warning("Found invalid log level {}; defaulting to INFO.".format(cmdArgs.loglevel))

    # Create the bot to get started
    desertbot = DesertBot(cmdArgs)
