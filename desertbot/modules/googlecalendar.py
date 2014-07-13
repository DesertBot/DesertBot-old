# -*- coding: utf-8 -*-
from collections import OrderedDict
import datetime
#import httplib2
#import gflags
from apiclient.discovery import build
#from oauth2client.file import Storage
#from oauth2client.client import OAuth2WebServerFlow
#from oauth2client.tools import run
from dateutil.parser import parse
from dateutil.tz import tzutc

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
        #TODO Commented all this junk because we don't need user authentication
        #TODO at the moment.
        #TODO I'd rather not do it all again though, so I'm gonna commit it anyway.

        # Set up a Flow object to be used if we need to authenticate. This
        # sample uses OAuth 2.0, and we set up the OAuth2WebServerFlow with
        # the information it needs to authenticate. Note that it is called
        # the Web Server Flow, but it can also handle the flow for native
        # applications
        # The client_id and client_secret can be found in Google Developers Console
        #try:
        #    id = self.bot.config["apikeys"]["google"]["id"]
        #    secret = self.bot.config["apikeys"]["google"]["secret"]
        #except KeyError as e:
        #    log.err("Google API id and secret missing")
        #    return

        #FLAGS = gflags.FLAGS

        #FLOW = OAuth2WebServerFlow(
        #    client_id=id,
        #    client_secret=secret,
        #    scope="https://www.googleapis.com/auth/calendar.readonly",
        #    user_agent="{}/{}".format(self.bot.versionName, self.bot.versionNum))

        # If the Credentials don't exist or are invalid, run through the native client
        # flow. The Storage object will ensure that if successful the good
        # Credentials will get written back to a file.
        #storage = Storage("googlecalendar_credentials.dat")
        #credentials = storage.get()
        #if credentials is None or credentials.invalid:
        #    credentials = run(FLOW, storage)

        # Create an httplib2.Http object to handle our HTTP requests and authorize it
        # with our good Credentials.
        #http = httplib2.Http()
        #http = credentials.authorize(http)

        # Build a service object for interacting with the API. Visit
        # the Google Developers Console
        # to get a developerKey for your own application.
        try:
            devkey = self.bot.config["apikeys"]["google"]["devkey"]
        except KeyError as e:
            log.err("Google API devkey missing")
            return

        self._service = build(serviceName="calendar", version="v3", developerKey=devkey)

    def getNextEvent(self, calendarID):
        now = datetime.datetime.now(tzutc())
        query = self._service.events().list(calendarId=calendarID,
                                            maxResults=2,  # we fetch 2 in case there's one running
                                            orderBy="startTime",
                                            singleEvents=True,
                                            timeMin=now.isoformat())
        events = query.execute()
        if len(events["items"]) == 0:
            return None

        for event in events["items"]:
            event["start"] = parse(event["start"]["dateTime"])
            event["end"] = parse(event["end"]["dateTime"])

            cutoffDelay = (event["end"] - event["start"]) / 2
            if cutoffDelay > datetime.timedelta(hours=1):
                cutoffDelay = datetime.timedelta(hours=1)
            eventCutoff = event["start"] + cutoffDelay
            if now < eventCutoff:
                event["till"] = self._deltaTimeToString(event["start"] - now)
                return event

        return None

    # mostly taken from dave_random's UnsafeBot (whose source is not generally accessible)
    def _deltaTimeToString(self, timeDelta, resolution='m'):
        """
        returns a string version of the given timedelta,
        with a resolution of minutes ('m') or seconds ('s')
        @type timeDelta: timedelta
        @type resolution: str
        """
        d = OrderedDict()
        d['days'] = timeDelta.days
        d['hours'], rem = divmod(timeDelta.seconds, 3600)
        if resolution == 'm' or resolution == 's':
            d['minutes'], seconds = divmod(rem, 60)
            if resolution == 's':
                d['seconds'] = seconds

        def lex(durationWord, duration):
            if duration == 1:
                return '{0} {1}'.format(duration, durationWord[:-1])
            else:
                return '{0} {1}'.format(duration, durationWord)

        deltaString = ' '.join([lex(word, number) for word, number in d.iteritems() if number > 0])
        return deltaString if len(deltaString) > 0 else 'seconds'

googlecalendar = GoogleCalendar()