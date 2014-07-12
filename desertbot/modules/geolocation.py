# -*- coding: utf-8 -*-

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

    baseAPIAddress = "http://maps.googleapis.com/maps/api/geocode/json"

    def onTrigger(self, message):
        return

    def getGeoLocationFromLatLon(self, latitude, longitude):
        params = {"latlng": ",".join([latitude, longitude]),
                  "sensor": "false",
                  "language": "english"}
        return self._getLocationFromJSON(self._getJSON(self.baseAPIAddress, params))

    def getGeoLocationFromPlace(self, place):
        params = {"address": place.replace(" ", "+"),
                  "sensor": "false"}
        return self._getLocationFromJSON(self._getJSON(self.baseAPIAddress, params))

    def _getLocationFromJSON(self, jsonString):
        if jsonString["status"] == "OK":
            firstHit = jsonString["results"][0]
            locality = self._siftForCreepy(firstHit["address_components"])
            latitude = float(firstHit["geometry"]["location"]["lat"])
            longitude = float(firstHit["geometry"]["location"]["lng"])
            return [locality, latitude, longitude]
        else:
            return None

    def _getJSON(self, url, params):
        urlutils = self.bot.moduleHandler.getModule(u"urlutils")
        if not urlutils:
            log.err("WARNING: Module \"urlutils\" is required for the \"geolocation\" module to "
                    "work.")
            return {"status": "ERROR"}
        else:
            return urlutils.fetchURL(url, params=params).json()

    def _siftForCreepy(self, addressComponents):
        locationInfo = []
        safeList = ["locality", "administrative_area_level_1", "country", "natural_feature",
                    "colloquial_area"]
        for location in addressComponents:
            if len(set(safeList).intersection(location["types"])) > 0:
                locationInfo.append(location["long_name"])
        return ", ".join(locationInfo)


geolocation = GeoLocation()
