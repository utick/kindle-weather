#!/usr/bin/python2
# Copyright (C) 2015 Gris Ge
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; If not, see <http://www.gnu.org/licenses/>.
#
# Author: Gris Ge <cnfourt@gmail.com>
import datetime
import json
from urllib2 import urlopen


def _fetch_json(url):
    print url
    json_str = urlopen(url).read()
    return json.loads(json_str)


def _parse_forecast(data_json):
    """
    return [WeatherData]
    """
    tmp_list = []
    for i in range(5):
        temperature = data_json["result"]["daily"]["temperature"]
        skycon = data_json["result"]["daily"]["skycon"]
        tmp_list.append(WeatherData(skycon[i]["value"], temperature[i]["max"],
                                    temperature[i]["min"]))
    return tmp_list


class WeatherData(object):
    def __init__(self, condition, temp_max, temp_min):
        self.condition = condition
        self.temp_max = temp_max
        self.temp_min = temp_min


class WeatherAPI(object):

    _BASE_API_URL = "https://api.caiyunapp.com/v2.5/%s/%s,%s/weather.json"

    def __init__(self, api_key):
        self._api_key = api_key
        self._today = datetime.date.today()

    def set_lat_lon(self, lat, lon):
        forecast_json = _fetch_json(
            WeatherAPI._BASE_API_URL %
            (self._api_key, lon, lat))

        self._data = _parse_forecast(forecast_json)

    def set_airport_code(self, airport_code):
        forecast_json = _fetch_json(
            WeatherAPI._BASE_API_URL %
            (self._api_key, airport_code))

        self._data = _parse_forecast(forecast_json)


    def temp_max(self, day):
        """
        Input day as integer, 0 means today, 1 means tomorrow, max is 3.
        """
        if day > 3:
            raise Exception("Invalid day, should less or equal to 3")

        return self._data[day].temp_max

    def temp_min(self, day):
        if day > 3:
            raise Exception("Invalid day, should less or equal to 3")
        return self._data[day].temp_min

    def condition(self, day):
        if day > 3:
            raise Exception("Invalid day, should less or equal to 3")
        return self._data[day].condition

    @property
    def today(self):
        """
        Return a object of datetime.date
        """
        return self._today
