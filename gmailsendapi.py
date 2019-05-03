#!/usr/bin/env python

import base64
from email.mime.text import MIMEText
import os
import pickle
import sys

from googleapiclient.discovery import build
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from private_variables import my_mail

python_version = sys.version_info.major

SCOPES = 'https://mail.google.com/'

file_path = os.path.dirname(os.path.abspath(__file__))
CLIENT_SECRET_FILE = os.path.join(file_path, 'credentials.json')
TOKEN_FILE = os.path.join(file_path, 'token.pickle')

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    return creds


def get_service():
    credentials = get_credentials()
    service = build('gmail', 'v1', credentials=credentials)
    return service


def create_message(sender, to, subject, message_text, style='html'):
    """Create a message for an email.

    Args:
      sender: Email address of the sender.
      to: Email address of the receiver.
      subject: The subject of the email message.
      message_text: The text of the email message.

    Returns:
      An object containing a base64url encoded email object.
    """
    if python_version == 2:
        message_text = unicode(message_text).encode('utf-8')
    message = MIMEText(message_text, _subtype=style)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    message = message.as_string()
    if python_version == 2:
        message = base64.urlsafe_b64encode(message)
    else:
        message = base64.urlsafe_b64encode(
            message.encode('utf-8')).decode('utf-8')
    return {'raw': message}


def send_message(message):
    """Send an email message.

    Args:
      can be used to indicate the authenticated user.
      message: Message to be sent.

    Returns:
      Sent Message.
    """
    service = get_service()
    message = service.users().messages().send(userId='me', body=message).execute()
    print('Message Id: %s' % message['id'])
    return message


if __name__ == '__main__':
    message = create_message(sender='',
                             to=my_mail,
                             subject='Test message succeeded',
                             message_text='Test message')

    send_message(message)
    print("You should have received a test message now.")
