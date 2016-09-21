#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Standard lib imports
from __future__ import print_function
from collections import namedtuple
import datetime
import json
import os
from random import randint
import re
import sys

# Third party imports
import dateutil.parser
from geopy.geocoders import Nominatim
import geopy.distance
from gmailsendapi import send_message, create_message
from motionless import CenterMap
from pytz import timezone, utc

# Local imports
from private_variables import my_mail, her_mail, day_one_text_file  # all strings
from private_variables import start_date  # datetime.date object

python_version = sys.version_info.major

location = namedtuple('location', ['latitude', 'longitude'])
file_path = os.path.dirname(os.path.abspath(__file__))


def remove_entry_tag(text):
    '''Replaces strings like ![](....).'''
    return re.sub(r'!\[\]\(.*?\)', '', text)


def day_header(text):
    return re.sub(r'Day [0-9]*', '<h1>\g<0></h1>', text)


def map_html(entry):
    lat, lon = get_lat_lon(entry)
    cmap = CenterMap(lat=lat, lon=lon, maptype='terrain', zoom=10)
    return "<img src='{}'>".format(cmap.generate_url())


def parse_date(entry):
    fmt = '%Y-%m-%d %H:%M:%S %Z%z'
    date = dateutil.parser.parse(entry['creationDate'], ignoretz=True)
    tz = timezone(entry['timeZone'])
    loc_dt = utc.localize(date).astimezone(tz)
    return loc_dt.strftime(fmt)


def todays_index(base, num_days):
    date_list = [base + datetime.timedelta(days=i) for i in range(num_days)]
    date_deltas = [(d - datetime.date.today()).days for d in date_list]
    return date_deltas.index(0)


def weather(entry):
    temperature = entry['weather']['temperatureCelsius']
    description = entry['weather']['conditionsDescription']
    if python_version == 2:
        sep = ' degree Celsius, '
    else:
        sep = ' °C, '
    return str(temperature) + sep + description


def get_lat_lon(entry):
    return location(entry['location']['latitude'],
                    entry['location']['longitude'])


def adress(entry):
    geolocator = Nominatim()
    loc = get_lat_lon(entry)
    location = geolocator.reverse(loc)
    return location.address


def distance(entries, index):
    geolocator = Nominatim()
    today = get_lat_lon(entries[index])
    yesterday = get_lat_lon(entries[index - 1])
    return geopy.distance.vincenty(today, yesterday).kilometers


def distance_text(entries, index):
    km = distance(entries, index)
    return "The distance since yesterday is {:.2} kilometers.".format(km)


def send_todays_story(sender, to, day_one_text_file,
                      base=start_date):
    if python_version == 2:
        with open(day_one_text_file) as f:
            data = json.load(f)
    else:
        with open(day_one_text_file, encoding='utf-8') as f:
            data = json.load(f)

    entries = [entry for entry in data['entries']]
    index = todays_index(base, len(entries))
    entry = entries[index]

    subject = "Love in India: #{}".format(index + 1)

    message_text = day_header(remove_entry_tag(entry['text']))
    message_text += "<p><em>{}</em></p>".format(parse_date(entry))
    message_text += "<p><em>{}</em></p>".format(weather(entry))
    message_text += "<p><strong>{}</strong></p>".format(adress(entry))
    if index > 0:
        message_text += "<p><strong>{}</strong></p>".format(
            distance_text(entries, index))
    message_text += map_html(entry)
    message = create_message(sender, to, subject, message_text, 'html')
    send_message(message)


if __name__ == "__main__":
    # execute only if run as a script
    send_file = os.path.join(file_path, 'send.txt')
    if not os.path.exists(send_file):
        # Create send.txt if it doesn't exist
        open(send_file, 'w').close()

    with open(send_file, 'r') as f:
        # Read the date when the last story was sent.
        send_file_date = f.read()

    now = datetime.datetime.now()
    if send_file_date == str(now.date()):
        # Don't send if story is already sent.
        print("Already sent")
    else:
        # Send with 0.3% probability if time is in between 10:00 and 23:00.
        if now.time() > datetime.time(10, 0):
            if now.time() < datetime.time(23, 0):
                send_now = randint(0, 1000) < 3
                if send_now:
                    print("Random number is smaller than 3")
                else:
                    print("Number between 3 and 1000")
            else:
                # If not sent before 23:00, send it now.
                send_now = True
                print("It's later than 23 o'clock, so sending now")

            if send_now:
                send_todays_story(my_mail, my_mail, day_one_text_file)
                send_todays_story(my_mail, her_mail, day_one_text_file)
                print("Send time is {}".format(str(now.time())))
                with open(send_file, 'w') as f:
                    f.write(str(now.date()))
