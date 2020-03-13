#!/usr/bin/python2
# Copyright (c) 2015 Gris Ge
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
#     The above copyright notice and this permission notice shall be included
#     in all copies or substantial portions of the Software.
#
#     THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
#     OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#     MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#     IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
#     CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
#     TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
#     SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
#
# Author: Gris Ge <cnfourt@gmail.com>

# Code was edit based on
# https://github.com/mpetroff/kindle-weather-display.git
# Which is also MIT license.
#
# Kindle Weather Display
# Matthew Petroff (http://mpetroff.net/)
# September 2012

import codecs
import datetime
import os
import sys

from weather_api_caiyun import WeatherAPI
from argparse import ArgumentParser
from aqi import aqi_get
from sci import sci_get


def _exec(cmd):
    rc = os.system(cmd)
    if (rc != 0):
        print("`%s` failed with error %d" % (cmd, rc))
        exit(rc)

CODE_FOLDER = os.path.dirname(os.path.realpath(__file__))

OUTPUT = os.environ.get("KW_OUTPUT", "/var/www/html/weather/weather.png")

TMP_OUTPUT = "%s/weather.png" % CODE_FOLDER
SVG_PORTRAIT_FILE = "%s/weather-script-preprocess.svg" % CODE_FOLDER
SVG_LANSCAPE_LEFT = "%s/weather-script-preprocess-landscape.svg" % CODE_FOLDER
SVG_LANSCAPE_RIGHT = "%s/weather-script-preprocess-landscape-right.svg" % \
    CODE_FOLDER
SVG_FILE = SVG_PORTRAIT_FILE
SVG_OUTPUT = "%s/weather-script-output.svg" % CODE_FOLDER
MAX_WEATHER_DAY_COUNT = 3
INCLUDE_SCI = False

if len(sys.argv) >= 5 and sys.argv[4] != '0':
    SVG_FILE = SVG_LANSCAPE_FILE

if os.environ.get("KW_LANSCAPE_RIGHT") is not None:
    SVG_FILE = SVG_LANSCAPE_RIGHT
elif os.environ.get("KW_LANSCAPE_LEFT") is not None:
    SVG_FILE = SVG_LANSCAPE_LEFT
else:
    SVG_FILE = SVG_PORTRAIT_FILE


AQI_CITY = os.environ.get("KW_AQI_CITY", None)

if os.environ.get("KW_INCLUDE_SCI") is not None:
    INCLUDE_SCI = True

WEATHER_KEY = os.environ.get("KW_WEATHER_KEY")
LATITUDE = os.environ.get("KW_LATITUDE")
LONGTITUDE = os.environ.get("KW_LONGTITUDE")
WEATHER_AIRPORT = os.environ.get("KW_AIRPORT")

if WEATHER_KEY is None:
    print("Need KW_WEATHER_KEY environment variables")
    exit(1)

weather_obj = WeatherAPI(WEATHER_KEY)

if WEATHER_AIRPORT:
    weather_obj.set_airport_code(WEATHER_AIRPORT)
else:
    weather_obj.set_lat_lon(LATITUDE, LONGTITUDE)

# Open SVG to process
output = codecs.open(SVG_FILE, "r", encoding="utf-8").read()

_MAP = {
    "$I": WeatherAPI.condition,
    "$H": WeatherAPI.temp_max,
    "$L": WeatherAPI.temp_min,
}

for x in _MAP.keys():
    for i in range(MAX_WEATHER_DAY_COUNT + 1):
        output = output.replace("%s%d" % (x, i),
                                "%s" % _MAP[x](weather_obj, i))

# Replace refresh time
output = output.replace("$TIME",
                        datetime.datetime.now().strftime("%b %d %a %H:%M"))

# Updaet AQI. TODO(Gris Ge): still place holder yet.
if AQI_CITY is not None:
    output = output.replace("$AQI", str(aqi_get(AQI_CITY)))

if INCLUDE_SCI:
    (sci, sci_change) = sci_get()
    output = output.replace("$SCI", str(sci))
    output = output.replace("$SCHG", str(sci_change))
else:
    output = output.replace("SCI: $SCI $SCHG", "")

day_one = weather_obj.today

# Insert days of week
one_day = datetime.timedelta(days=1)
days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

for i in range(MAX_WEATHER_DAY_COUNT + 1):
    output = output.replace("$D%s" % i,
                            days_of_week[(day_one + i * one_day).weekday()])

# Write output
codecs.open(SVG_OUTPUT, "w", encoding="utf-8").write(output)

_exec("rsvg-convert --background-color=white -o %s %s" %
      (TMP_OUTPUT, SVG_OUTPUT))
_exec("pngcrush -c 0 -ow %s 1>/dev/null 2>&1" % TMP_OUTPUT)
_exec("mv -f '%s' '%s'" % (TMP_OUTPUT, OUTPUT))
