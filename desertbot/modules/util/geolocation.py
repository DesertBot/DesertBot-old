from twisted.plugin import IPlugin
from desertbot.moduleinterface import BotModule, IBotModule
from zope.interface import implements


class GeoLocation(BotModule):
    implements(IPlugin, IBotModule)

    name = "GeoLocation"
    canDisable = False
    baseURL = "https://maps.googleapis.com/maps/api/geocode/json?"

    def actions(self):
        return [ ("geolocation-latlon", 1, self.geolocationForLatLon),
                 ("geolocation-place", 1, self.geolocationForPlace) ]

    def load(self):
        self.googleKey = None
        if "api-keys" not in self.bot.storage:
            self.bot.storage["api-keys"] = {}
        if "google" in self.bot.storage["api-keys"]:
            self.googleKey = self.bot.storage["api-keys"]["google"]

    def geolocationForLatLon(self, lat, lon):
        params = {
            "latlng": "{},{}".format(lat, lon),
        }
        return self._sendLocationRequest(params)

    def geolocationForPlace(self, place):
        params = {
            "address": place.replace(" ", "+")
        }
        return self._sendLocationRequest(params)

    def _sendLocationRequest(self, params):
        params["sensor"] = "false"
        params["language"] = "english"
        if self.googleKey:
            params["key"] = self.googleKey
        result = self.bot.moduleHandler.runActionUntilValue("fetch-url", self.baseURL, params)
        if not result:
            return None

        return self._geolocationFromJSON(result.json())

    def _geolocationFromJSON(self, json):
        data = {
            "success": json["status"] == "OK"
        }
        if not data["success"]:
            return data

        firstHit = json["results"][0]
        data["latitude"] = float(firstHit["geometry"]["location"]["lat"])
        data["longitude"] = float(firstHit["geometry"]["location"]["lng"])
        data["locality"] = self._siftForCreepy(firstHit)
        return data

    def _siftForCreepy(self, locality):
        safeTypes = ["administrative_area_level_1", "colloquial_area", "country", "locality", "natural_feature"]
        locationInfo = []
        for addressComponent in locality["address_components"]:
            if len(set(addressComponent["types"]).intersection(safeTypes)) > 0:
                locationInfo.append(addressComponent["long_name"])
        if len(locationInfo) == 0:
            return "Unknown"
        # We need to handle the unicode before we send it back to the caller
        return ", ".join(locationInfo).encode("utf-8", "ignore")

geoLocation = GeoLocation()
