from twisted.logger import formatEvent, formatTime, ILogObserver
from zope.interface import provider


logFormat = lambda event: u"{0} [{1}]: {2}".format(formatTime(event["log_time"]), event["log_level"].name.upper(),
                                                   formatEvent(event))

@provider(ILogObserver)
def consoleLogObserver(event):
    print u"{0} [{1}]: {2}".format(formatTime(event["log_time"]), event["log_level"].name.upper(), formatEvent(event))
