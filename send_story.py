#!/usr/bin/env python

from __future__ import print_function
import os
from gmailsendapi import send_message, create_message
import datetime
import re
from random import randint
from private_variables import my_mail, her_mail, day_one_text_file  # all strings
from private_variables import start_date  # datetime.date object

file_path = os.path.dirname(os.path.abspath(__file__))

def remove_photo_tag(text):
    '''Replaces strings like ![](.... "").'''
    return re.sub(r'!\[\]\(.*?\"\"\)', '', text)


def send_todays_story(sender, to, day_one_text_file=day_one_text_file,
                      base=start_date):
    with open(os.path.join(file_path, day_one_text_file)) as f:
        text = ''.join([remove_photo_tag(line) for line in f])

    dagen = ['\tDate:' + dag for dag in text.split('\tDate:') if dag is not '']
    date_list = [base + datetime.timedelta(days=i) for i, _ in enumerate(dagen)]
    date_deltas = [(d - datetime.date.today()).days for d in date_list]
    today_index = date_deltas.index(0)
    message_text = dagen[today_index]
    subject = "Love in India: #{}".format(today_index + 1)
    message = create_message(sender, to, subject, message_text, 'plain')
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
                send_todays_story(my_mail, her_mail)
                print("Send time is {}".format(str(now.time())))
                with open(send_file, 'w') as f:
                    f.write(str(now.date()))
