# -*- coding: utf-8 -*-
from urlparse import urlparse
import requests

from zope.interface import implements
from twisted.plugin import IPlugin
from twisted.python import log
from desertbot.moduleinterface import IModule, Module, ModuleType
import re

class URLUtils(Module):
    implements(IPlugin, IModule)

    name = u"urlutils"
    triggers = []
    moduleType = ModuleType.UTILITY
    helpText = u"Provides utility functions for loading and posting URLs."

    def onTrigger(self, message):
        return


    def fetchURL(self, url, params=None, extraHeaders=None):
        """
        @type url: str
        @type params: dict[str, str]
        @type extraHeaders: dict[str, str]
        @rtype: requests.Response
        """
        headers = {"user-agent": "Mozilla/5.0"}
        if extraHeaders:
            headers.update(extraHeaders)
        try:
            r = requests.get(url, params=params, headers=extraHeaders, stream=True)

            # Only allow certain kinds of data to be read
            if re.match("^("
                        "text/.*|"              # any kind of text
                        "application/(.*)xml|"  # any kind of xml
                        "application/(.*)json"  # any kind of json
                        ")(;.*)?$",
                        r.headers["content-type"]):
                # Force data to be read so the response object will close when we're done with it
                content = r.content
                r.close()
                return r
            else:
                r.close()

        except requests.RequestException as e:
            reason = None
            log.err("ERROR: Fetch from \"{}\" failed: {}".format(url, reason))


    def postURL(self, url, data, extraHeaders=None):
        """
        @type url: str
        @type data: T
        @type extraHeaders: dict[str, str]
        @rtype: requests.Response
        """
        headers = {"user-agent": "Mozilla/5.0"}
        if extraHeaders:
            headers.update(extraHeaders)

        try:
            r = requests.post(url, data=data, headers=headers, stream=True)

            # Only allow certain kinds of data to be read
            if re.match("^("
                        "text/.*|"              # any kind of text
                        "application/(.*)xml|"  # any kind of xml
                        "application/(.*)json"  # any kind of json
                        ")(;.*)?$",
                        r.headers["content-type"]):
                content = r.content
                r.close()
                return r
            else:
                r.close()

        except requests.RequestException as e:
            reason = None
            log.err("ERROR: Post to \"{}\" failed: {}".format(url, reason))


urlutils = URLUtils()
