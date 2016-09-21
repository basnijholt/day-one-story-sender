# Day One story sender

I promissed my girlfriend to send her a story from our trip every day in a random time slot. I wrote everything on my phone in the [Day One](http://dayoneapp.com/) app and use the desktop app to export the stories.

It uses the GMail API to send e-mails and sends a message on a random time during the day between 10:00 and 23:00.

## How to use
### Setup stories to send and private variables
Select the Day One entries in the desktop Day One app and right-click `Open in... -> Plain Text -> TextEdit` and save this in the folder with these scripts.

Edit the `private-file-example.py` and save as `private-file.py`.

The random send algorithm is written in a way that on the middle of the day there is a 50% change of the e-mail being sent if the script is run every minute. I do this by adding a `cronjob` at my Raspberry Pi, by using `crontab -e` and then adding:
```
*/1 * * * * /usr/bin/python /full/path/to/send_story.py
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
