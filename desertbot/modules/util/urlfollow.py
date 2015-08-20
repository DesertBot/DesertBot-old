from twisted.plugin import IPlugin
from desertbot.channel import IRCChannel
from desertbot.moduleinterface import BotModule, IBotModule
from zope.interface import implements
from bs4 import BeautifulSoup
from isodate import parse_duration
from urlparse import urlparse
import re, time


class URLFollow(BotModule):
    implements(IPlugin, IBotModule)

    name = "URLFollow"

    def actions(self):
        return [ ("ctcp-message", 20, self.searchActions),
                 ("message-channel", 20, self.searchChannelMessage),
                 ("message-user", 20, self.searchPrivateMessage) ]

    def searchPrivateMessage(self, server, user, messageBody):
        self._searchURLs(server, user.nick, messageBody)

    def searchChannelMessage(self, server, channel, user, body):
        self._searchURLs(server, channel.name, body)

    def searchActions(self, server, source, user, body):
        if not body.upper().startswith("ACTION"):
            return
        if isinstance(source, IRCChannel):
            self._searchURLs(server, source.name, body)
        else:
            self._searchURLs(server, user.nick, body)

    def load(self):
        self.imgurClientID = None
        self.ytKey = None
        if "api-keys" not in self.bot.storage:
            self.bot.storage["api-keys"] = {}
        if "imgur" in self.bot.storage["api-keys"]:
            self.imgurClientID = self.bot.storage["api-keys"]["imgur"]
        if "google" in self.bot.storage["api-keys"]:
            self.ytKey = self.bot.storage["api-keys"]["google"]

    def _searchURLs(self, server, source, body):
        if not self.bot.moduleHandler.useModuleOnServer(self.name, server):
            return
        regex = re.compile(r"(https?://|www\.)[^\s]+", re.IGNORECASE)
        for url in filter(regex.match, body.split(" ")):
            response = self._handleURL(url)
            if response:
                self.bot.servers[server].outputHandler.cmdPRIVMSG(source, response)

    def _handleURL(self, url):
        ytMatch = re.search(r"(youtube\.com/watch.+v=|youtu\.be/)(?P<videoID>[^&#\?]{11})", url)
        if ytMatch:
            return self._handleYouTube(ytMatch.group("videoID"))
        imgurMatch = re.search(r"(i\.)?imgur\.com/(?P<imgurID>[^\.]+)", url)
        if imgurMatch:
            return self._handleImgur(imgurMatch.group("imgurID"))
        if not re.search("\.(jpe?g|gif|png|bmp)$", url):
            return self._handleGeneric(url)
        return None

    def _handleGeneric(self, url):
        result = self.bot.moduleHandler.runActionUntilValue("fetch-url", url)
        if not result or result.status_code != 200:
            return None
        parsed_uri = urlparse(result.url)
        soup = BeautifulSoup(result.content)
        title = soup.find("title").text.encode("utf-8", "ignore").replace("\r", "").replace("\n", " ")
        if len(title) > 300:
            title = title[:297] + "..."
        return "[URL] {} (at host: {}).".format(title, parsed_uri.hostname)

    def _handleYouTube(self, videoID):
        params = {
            "id": videoID,
            "fields": "items(id,snippet(title,description),contentDetails(duration))",
            "parts": "snippet,contentDetails",
        }
        if self.ytKey:
            params["key"] = self.ytKey
        url = "https://www.googleapis.com/youtube/v3/videos"
        result = self.bot.moduleHandler.runActionUntilValue("fetch-url", url, params)
        if not result:
            return None
        j = result.json()
        if len(j["items"]) < 1:
            return None
        snippet = j["items"][0]["snippet"]
        title = snippet["title"].replace("\r", "").replace("\n", " ").encode("utf-8", "ignore")
        description = snippet["description"].replace("\r", "").replace("\n", " ").encode("utf-8", "ignore")
        durSeconds = parse_duration(j["items"][0]["contentDetails"]["duration"]).total_seconds()
        if len(description) > 149:
            description = description[:147] + "..."
        if durSeconds < 3600:
            duration = time.strftime("%M:%S", time.gmtime(durSeconds))
        else:
            duration = time.strftime("%H:%M:%S", time.gmtime(durSeconds))
        return "[YouTube] {} | {} | {}".format(title, duration, description)

    def _handleImgur(self, imgurID):
        if not self.imgurClientID:
            return
        albumLink = False
        if imgurID.startswith("gallery/"):
            imgurID = imgurID.replace("gallery/", "")
            url = "https://api.imgur.com/3/gallery/{}".format(imgurID)
        elif imgurID.startswith("a/"):
            imgurID = imgurID.replace("a/", "")
            url = "https://api.imgur.com/3/album/{}".format(imgurID)
            albumLink = True
        else:
            url = "https://api.imgur.com/3/image/{}".format(imgurID)
        headers = { "Authorization": "Client-ID {}".format(self.imgurClientID) }
        result = self.bot.moduleHandler.runActionUntilValue("fetch-url", url, None, headers)
        if not result:
            return
        j = result.json()
        if j["status"] != 200:
            return
        j = j["data"]
        data = []
        if j["title"]:
            data.append("{}".format(j["title"]))
        else:
            data.append("No title")
        if j["nsfw"]:
            data.append("NSFW!")
        if albumLink:
            data.append("Album: {} images".format(j["images_count"]))
        elif "is_album" in j and j["is_album"]:
            data.append("Album: {} images".format(len(j["images"])))
        if "animated" in j and j["animated"]:
            data.append("Animated!")
        if "width" in j and "height" in j:
            data.append("{}x{}".format(j["width"], j["height"]))
        if "size" in j:
            data.append("Size: {} kB".format(int(j["size"])/1024))
        data.append("Views: {}".format(j["views"]))
        return "[Imgur] {}".format(" | ".join(data))

urlFollow = URLFollow()
