# -*- coding: utf-8 -*-
from urllib import urlencode
from urllib2 import build_opener, Request, urlopen, URLError
from urlparse import urlparse

from zope.interface import implements
from twisted.plugin import IPlugin
from twisted.python import log
from desertbot.moduleinterface import IModule, Module, ModuleType
import re


class URLResponse(object):
    def __init__(self, body, domain, responseHeaders):
        self.body = body
        self.domain = domain
        self.responseHeaders = responseHeaders


class URLUtils(Module):
    implements(IPlugin, IModule)

    name = u"urlutils"
    triggers = []
    moduleType = ModuleType.UTILITY
    helpText = u"Provides utility functions for loading and posting URLs."

    def onTrigger(self, message):
        return


def fetchURL(url, extraHeaders=None):
    headers = [( "User-agent", "Mozilla/5.0" )]
    if extraHeaders:
        for header in extraHeaders:
            # For whatever reason headers are defined in different way in opener than they are in
            # a normal urlopen
            headers.append((header, extraHeaders[header]))
    try:
        opener = build_opener()
        opener.addheaders = headers
        response = opener.open(url)
        responseHeaders = response.info().dict
        pageType = responseHeaders["content-type"]

        # Make sure we don't download any unwanted things
        if re.match(
                "^(text/.*|application/((rss|atom|rdf)\+)?xml(;.*)?|application/(.*)json(;.*)?)$",
                pageType):
            urlResponse = URLResponse(response.read(), urlparse(response.geturl()).hostname,
                                      responseHeaders)
            response.close()
            return urlResponse
        else:
            response.close()

    except URLError as e:
        reason = None
        if hasattr(e, "reason"):
            reason = "We failed to reach the server, reason: {}".format(e.reason)
        elif hasattr(e, "code"):
            reason = "The server couldn't fulfill the request, code: {}".format(e.code)
        log.err("ERROR: Fetch from \"{}\" failed: {}".format(url, reason))


def postURL(url, values, extraHeaders=None):
    headers = {"User-agent": "Mozilla/5.0"}
    if extraHeaders:
        for header in extraHeaders:
            headers[header] = extraHeaders[header]

    data = urlencode(values)

    try:
        request = Request(url, data, headers)
        response = urlopen(request)
        responseHeaders = response.info().dict
        pageType = responseHeaders["content-type"]

        # Make sure we don't download any unwanted things
        if re.match(
                '^(text/.*|application/((rss|atom|rdf)\+)?xml(;.*)?|application/(.*)json(;.*)?)$',
                pageType):
            urlResponse = URLResponse(response.read(), urlparse(response.geturl()).hostname,
                                      responseHeaders)
            response.close()
            return urlResponse
        else:
            response.close()

    except URLError as e:
        reason = None
        if hasattr(e, "reason"):
            reason = "We failed to reach the server, reason: {}".format(e.reason)
        elif hasattr(e, "code"):
            reason = "The server couldn't fulfill the request, code: {}".format(e.code)
        log.err("ERROR: Post to \"{}\" failed: {}".format(url, reason))


urlutils = URLUtils()
