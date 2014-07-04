# -*- coding: utf-8 -*-
import json

from zope.interface import implements
from twisted.plugin import IPlugin
from twisted.python import log
from desertbot.moduleinterface import IModule, Module, ModuleType


class GeoLocation(Module):
    implements(IPlugin, IModule)

    name = u"geolocation"
    triggers = []
    moduleType = ModuleType.UTILITY
    helpText = u"Provides utility functions for looking up geographical locations using the " \
               u"Google Maps geocoding API."

    baseAPIAddress = "http://maps.googleapis.com/maps/api/geocode/json?"

    def onTrigger(self, message):
        return

    def getGeoLocationFromLatLon(self, latitude, longitude):
        url = "{}latlng={},{}&sensor=false&language=english".format(self.baseAPIAddress, latitude,
                                                                    longitude)
        return self._getLocationFromJSON(self._getJSON(url))

    def getGeoLocationFromPlace(self, place):
        place = place.replace(" ", "+")
        url = "{}address={}&sensor=false".format(self.baseAPIAddress, place)
        return self._getLocationFromJSON(self._getJSON(url))

    def _getLocationFromJSON(self, jsonString):
        if jsonString["status"] == "OK":
            firstHit = jsonString["results"][0]
            locality = self._siftForCreepy(firstHit["address_components"])
            latitude = float(firstHit["geometry"]["location"]["lat"])
            longitude = float(firstHit["geometry"]["location"]["lng"])
            return [locality, latitude, longitude]
        else:
            return None

    def _getJSON(self, url):
        if "urlutils" in self.bot.moduleInterface.modules:
            urlutils = self.bot.moduleInterface.modules["urlutils"]
            return json.loads(urlutils.fetchURL(url).body)
        else:
            log.err("WARNING: Module \"urlutils\" is required for the \"geolocation\" module to "
                    "work.")
            return {"status": "ERROR"}

    def _siftForCreepy(self, addressComponents):
        locationInfo = []
        safeList = ["locality", "administrative_area_level_1", "country", "natural_feature",
                    "colloquial_area"]
        for location in addressComponents:
            if len(set(safeList).intersection(location["types"])) > 0:
                locationInfo.append(location["long_name"])
        return ", ".join(locationInfo)


geolocation = GeoLocation()
