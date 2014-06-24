#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
import argparse, os, sys
from desertbot.bothandler import BotHandler
from twisted.python import log

parser = argparse.ArgumentParser(description="An IRC bot written in Python.")
parser.add_argument("-s", "--servers", help="the IRC servers to connect to (required)", type=str, nargs="+", required=True)
parser.add_argument("-l", "--logfile", help="the file the debug log will be written to (default desertbot.log)", type=str, default="desertbot.log")
parser.add_argument("-v", "--verbose", help="log to console (default False)", type=bool, default=False)
cmdArgs = parser.parse_args()

if __name__ == "__main__":
    # Create folders
    if not os.path.exists(os.path.join("config")):
        os.makedirs("config")
    
    # Open log file
    open(cmdArgs.logfile, "a").close()
    log.startLogging(open(cmdArgs.logfile, "a"), setStdout=False)
    if cmdArgs.verbose:
        log.startLogging(sys.stdout)

    botHandler = BotHandler(cmdArgs)
