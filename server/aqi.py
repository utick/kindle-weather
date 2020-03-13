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
import urllib2
import re

_AQI_URL = 'http://aqicn.org/city/<CITY>/m'
_AQI_DIV_NAME = 'aqi'
_AQI_REGEX = re.compile('summary.+\+([0-9]+)\+')
_HTTP_HEADER = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:42.0) "
                  "Gecko/20100101 Firefox/42.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;"
              "q=0.9,*/*;q=0.8",
}


def _fetch_html(url):
    request = urllib2.Request(url, headers=_HTTP_HEADER)
    return urllib2.urlopen(request).read()


def aqi_get(city_name):
    '''
    Return integer for AQI of given city and raise error if failure.
    Data is from parsed from aqicn.org webpage.
    '''
    url = _AQI_URL.replace('<CITY>', city_name)
    html_content = _fetch_html(url)
    for line in html_content.split("\n"):
        match = _AQI_REGEX.search(line)
        if match:
            return int(match.group(1))
    return -1
