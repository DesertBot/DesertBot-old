# -*- coding: utf-8 -*-
from zope.interface import implements
from twisted.plugin import IPlugin
from desertbot.postprocessinterface import IPost, Module
from desertbot.response import IRCResponse


class ExamplePost(Module):
    implements(IPlugin, IPost)

    name = u"examplepostprocess"
    helpText = u"Appends responses with sillyness."

    def onTrigger(self, response):
        """
        @type response: IRCResponse
        """
        return IRCResponse(response.responseType,
                           u"{} - Sent from DesertBot".format(response.response), response.user,
                           response.target)


examplepost = ExamplePost()
