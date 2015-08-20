from twisted.logger import FileLogObserver, FilteringLogObserver, globalLogPublisher, InvalidLogLevelError, \
    Logger, LogLevel, LogLevelFilterPredicate
from twisted.python.logfile import DailyLogFile
from desertbot.bot import DesertBot
from desertbot.utils.logutils import consoleLogObserver, logFormat
from signal import signal, SIGINT
import argparse


if __name__ == "__main__":
    # Parse the command line arguments
    parser = argparse.ArgumentParser(description="A modular Twisted IRC bot.")
    parser.add_argument("-c", "--config", help="The configuration file to use", type=str, default="desertbot.yaml")
    parser.add_argument("-f", "--logfile", help="The file the log will be written to", type=str, default="desertbot.log")
    parser.add_argument("-l", "--loglevel", help="The logging level the bot will use", type=str, default="INFO")
    options = parser.parse_args()

    # Start the bot
    desertbot = DesertBot(options.config)

    # Determine the logging level
    logFilter = LogLevelFilterPredicate()
    try:
        logFilter.setLogLevelForNamespace("desertbot", LogLevel.levelWithName(options.loglevel.lower()))
        invalidLogLevel = False
    except InvalidLogLevelError:
        logFilter.setLogLevelForNamespace("desertbot", LogLevel.info)
        invalidLogLevel = True

    # Set up logging
    logFile = DailyLogFile("desertbot.log", "")
    fileObserver = FileLogObserver(logFile, logFormat)
    fileFilterObserver = FilteringLogObserver(fileObserver, (logFilter,))
    consoleFilterObserver = FilteringLogObserver(consoleLogObserver, (logFilter,))
    desertbot.log = Logger("desertbot")
    globalLogPublisher.addObserver(fileFilterObserver)
    globalLogPublisher.addObserver(consoleFilterObserver)

    desertbot.log.info("Starting bot...")

    # Yell at the user if they specified an invalid log level
    if invalidLogLevel:
        desertbot.log.warn("Picked up invalid log level {invalidLevel}, level has been set to INFO instead.",
                           invalidLevel=options.loglevel.lower())

    signal(SIGINT, lambda signal, stack: desertbot.shutdown())
    desertbot.startup()
