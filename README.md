# Day One story sender

I promised my girlfriend to send her a story from our trip every day. During our trip, I wrote a diary everyday on my phone in the [Day One](http://dayoneapp.com/) app. Here I use the desktop app to export the stories.

It uses the Gmail API to send e-mails and sends a message at a random time during the day between 10:00 and 23:00.

## How to use
### Setup stories to send and private variables
Select the Day One entries in the desktop Day One app and right-click `Open in... -> JSON -> TextEdit` and save this in the folder with these scripts.

Edit the `private_variables_example.py` and save as `private_variables.py`.

The random send algorithm is written in a way that on the middle of the day there is a 50% change of the e-mail being sent if the script is run every minute. I do this by adding a `cronjob` at my Raspberry Pi, by using `crontab -e` and then adding (edit full path):
```
*/1 * * * * /usr/bin/python /home/pi/day-one-story-sender/send_story.py >> /home/pi/day-one-story-sender/send.log 2>&1
```

Install Python dependencies
```
pip install https://github.com/ryancox/motionless/archive/master.zip # because of bugged pip version
pip install geopy python-dateutil pytz
```

### Setup Google API
1. Follow [step 1: Turn on the Gmail API](https://developers.google.com/gmail/api/quickstart/python#step_1_turn_on_the_api_name) to create a `client_secret.json` file.
2. Install the Google Client Library with:
```
pip install --upgrade google-api-python-client
```
3. Run (add the `--noauth_local_webserver` flag if you work through `ssh`)
```
python gmailsendapi.py
```
After which, you should receive a test mail.
