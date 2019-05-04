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
import geopy.distance
from geopy.geocoders import Nominatim
from motionless import CenterMap
from pytz import timezone, utc

# Local imports
from gmailsendapi import create_message, send_message
from private_variables import day_one_file, her_mail, my_mail, title  # all strings
from private_variables import start_date  # datetime.date object

python_version = sys.version_info.major
location = namedtuple("location", ["latitude", "longitude"])
file_path = os.path.dirname(os.path.abspath(__file__))


def remove_entry_tag(text):
    """Replaces strings like ![](....)."""
    return re.sub(r"!\[\]\(.*?\)", "", text)


def day_header(text):
    return re.sub(r"Day [0-9]*", "<h1>\g<0></h1>", text)


def map_html(entry):
    lat, lon = get_lat_lon(entry)
    with open(os.path.join(file_path, "api_key.txt")) as f:
        key = f.read()
    cmap = CenterMap(lat=lat, lon=lon, maptype="terrain", zoom=10, key=key)
    return "<img src='{}'>".format(cmap.generate_url())


def parse_date(entry):
    fmt = "%Y-%m-%d %H:%M:%S %Z%z"
    date = dateutil.parser.parse(entry["creationDate"], ignoretz=True)
    tz = timezone(entry["timeZone"])
    loc_dt = utc.localize(date).astimezone(tz)
    return loc_dt.strftime(fmt)


def todays_index(base, num_days):
    date_list = [base + datetime.timedelta(days=i) for i in range(num_days)]
    date_deltas = [(d - datetime.date.today()).days for d in date_list]
    return date_deltas.index(0)


def weather(entry):
    temperature = entry["weather"]["temperatureCelsius"]
    description = entry["weather"]["conditionsDescription"]
    if python_version == 2:
        sep = " degree Celsius, "
    else:
        sep = " °C, "
    return str(temperature) + sep + description


def get_lat_lon(entry):
    return location(entry["location"]["latitude"], entry["location"]["longitude"])


def adress(entry):
    geolocator = Nominatim(user_agent="day-one-story-sender")
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
    return "The distance since yesterday is {0:.1f} kilometers.".format(km)


def load_entries_from_json(day_one_file):
    if python_version == 2:
        with open(day_one_file) as f:
            data = json.load(f)
    else:
        with open(day_one_file, encoding="utf-8") as f:
            data = json.load(f)

    return [entry for entry in data["entries"]]


def create_todays_message(day_one_file, base):
    entries = load_entries_from_json(day_one_file)
    index = todays_index(base, len(entries))
    entry = entries[index]

    subject = "{}: #{}".format(title, index + 1)
    print(subject)
    message_text = day_header(remove_entry_tag(entry["text"]))
    message_text += "<p><em>{}</em></p>".format(parse_date(entry))
    message_text += "<p><em>{}</em></p>".format(weather(entry))
    message_text += "<p><strong>{}</strong></p>".format(adress(entry))
    if index > 0:  # Because a distance with the previous day doesn't exist.
        message_text += "<p><strong>{}</strong></p>".format(
            distance_text(entries, index)
        )
    message_text += map_html(entry)
    return (
        subject,
        message_text.replace(r"\.", ".").replace(r"\(", "(").replace(r"\)", ")"),
    )


if __name__ == "__main__":
    # execute only if run as a script
    send_file = os.path.join(file_path, "send.txt")
    day_one_file = os.path.join(file_path, day_one_file)
    if not os.path.exists(send_file):
        # Create send.txt if it doesn't exist
        open(send_file, "w").close()

    with open(send_file, "r") as f:
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
                subject, msg_text = create_todays_message(day_one_file, start_date)
                args = dict(sender=my_mail, subject=subject, message_text=msg_text)
                send_message(create_message(to=my_mail, **args))
                send_message(create_message(to=her_mail, **args))
                print("Send time is {}".format(str(now.time())))
                with open(send_file, "w") as f:
                    f.write(str(now.date()))
