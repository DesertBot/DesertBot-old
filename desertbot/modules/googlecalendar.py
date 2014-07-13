# -*- coding: utf-8 -*-
from collections import OrderedDict
import datetime
from apiclient.discovery import build
from dateutil.parser import parse
from dateutil.tz import gettz

from zope.interface import implements
from twisted.plugin import IPlugin
from twisted.python import log
from desertbot.moduleinterface import IModule, Module, ModuleType


class GoogleCalendar(Module):
    implements(IPlugin, IModule)
    name = u"googlecalendar"
    triggers = []
    moduleType = ModuleType.UTILITY
    helpText = u"Provides utility functions for reading data from google calendars."

    def onModuleLoaded(self):
        # Build a service object for interacting with the API. Visit
        # the Google Developers Console
        # to get a developerKey for your own application.
        try:
            devkey = self.bot.config["apikeys"]["google"]["devkey"]
        except KeyError as e:
            log.err("Google API devkey missing")
            return

        self._service = build(serviceName="calendar", version="v3", developerKey=devkey)

    def getNextEvent(self, calendarID, timezone="America/Vancouver"):
        if calendarID is None:
            return None

        tz = gettz(timezone)
        now = datetime.datetime.now(tz)
        query = self._service.events().list(calendarId=calendarID,
                                            maxResults=2,  # we fetch 2 in case there's one running
                                            orderBy="startTime",
                                            singleEvents=True,
                                            timeMin=now.isoformat())
        events = query.execute()
        if len(events["items"]) == 0:
            return None

        for event in events["items"]:
            event["start"] = parse(event["start"]["dateTime"]).astimezone(tz)
            event["end"] = parse(event["end"]["dateTime"]).astimezone(tz)

            cutoffDelay = (event["end"] - event["start"]) / 2
            if cutoffDelay > datetime.timedelta(hours=1):
                cutoffDelay = datetime.timedelta(hours=1)
            eventCutoff = event["start"] + cutoffDelay
            if now < eventCutoff:
                timeTill = event["start"] - now
                if timeTill < datetime.timedelta(0):
                    event["till"] = u"{} ago".format(self._deltaTimeToString(-timeTill))
                else:
                    event["till"] = u"{} from now".format(self._deltaTimeToString(timeTill))
                return event

        return None

    # mostly taken from dave_random's UnsafeBot (whose source is not generally accessible)
    def _deltaTimeToString(self, timeDelta, resolution="m"):
        """
        returns a string version of the given timedelta,
        with a resolution of minutes ("m") or seconds ("s")
        @type timeDelta: timedelta
        @type resolution: str
        """
        d = OrderedDict()
        d["days"] = timeDelta.days
        d["hours"], rem = divmod(timeDelta.seconds, 3600)
        if resolution == "m" or resolution == "s":
            d["minutes"], seconds = divmod(rem, 60)
            if resolution == "s":
                d["seconds"] = seconds

        def lex(durationWord, duration):
            if duration == 1:
                return u"{} {}".format(duration, durationWord[:-1])
            else:
                return u"{} {}".format(duration, durationWord)

        deltaString = u" ".join([lex(word, number) for word, number in d.iteritems() if number > 0])
        return deltaString if len(deltaString) > 0 else "seconds"

googlecalendar = GoogleCalendar()