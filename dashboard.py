#!/usr/bin/python

import json
import time
import google.oauth2.credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from secretmanager import Secrets
from pubsub import Publish


#declare global variables
projectId = ''
youtubeClientSecretName = ''
youtubeCredentialsName = ''
topicId = ''
scope = ["https://www.googleapis.com/auth/youtube.readonly"]
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

rawClientSecret = None
rawYoutubeCreds = None

try:
  rawClientSecret = Secrets.access_secret_version(projectId, youtubeClientSecretName , 'latest')
except:
  print('error loading youtube-client-secret from secret manager')

try:
  rawYoutubeCreds = Secrets.access_secret_version(projectId, youtubeCredentialsName, 'latest')
except:
  print('error loading youtube-credential from secret manager')

# Authorize the request and store authorization credentials.
def get_authenticated_service(clientSecret):
  flow = InstalledAppFlow.from_client_config(json.loads(clientSecret), scope)
  #flow = InstalledAppFlow.from_client_secrets_file(clientSecret, SCOPES)
  flow.run_local_server(port=8080, prompt='consent')
  credentials = flow.credentials
  #print(credentials.to_json())
  return credentials

# main method
if __name__ == '__main__':
  # - If there is no secret, the user has not authorised oAuth to call the API on behalf of the user
  # - Refresh the token using the client credentials downloaded and saved in the secrets manager
  # - Save the new token in the Google Cloud Secret Manager
  if(rawYoutubeCreds == None):
    print('Not authenticated, launching user authentication workflow')
    clientSecret = get_authenticated_service(rawClientSecret)
    print('saving client secret to secret manager')
    resp = Secrets.add_secret_version(projectId, youtubeCredentialsName, clientSecret.to_json())
    rawYoutubeCreds = clientSecret.to_json()

  # Convert the content of the secret to Google oauth credentials object
  print('convert youtube credentials from secrets manager to Credentials object')
  youtubeCredentials = google.oauth2.credentials.Credentials.from_authorized_user_info(json.loads(rawYoutubeCreds), scopes=scope)  

  # init the pubsub class
  publishClient = Publish(projectId, topicId)

  # Now that we have a key to authenticate build the youtube api endpoint to access the data based on the defined scope
  youtube = build(API_SERVICE_NAME, API_VERSION, credentials = youtubeCredentials)

  # Repeatedly call the same api for monitoring purposes, sleep for 10 seconds.
  while(1):
    # if the token has been expired, refresh it and update the Google Cloud Secrets Manager
    if(youtubeCredentials.expired):
      print('refreshing youtube token')
      youtubeCredentials.refresh(Request())
      print('saving refresh token to secret manager')
      Secrets.add_secret_version(projectId, youtubeCredentialsName, youtubeCredentials.to_json())
      # Regenerate the youtube endpoint with the new credentials
      youtube = build(API_SERVICE_NAME, API_VERSION, credentials = youtubeCredentials)

    # Call a test api to ensure it is working
    channels_response = youtube.channels().list(
      mine=True,
      part='contentDetails'
    ).execute()

    # Print out the API response
    for channel in channels_response['items']:
      #print(channel)
      try:
        publishClient.publish(channel)
      except:
        print('error publishing to pubsub')

    # call the same api every 10 seconds for monitoring channel status  
    time.sleep(10)

