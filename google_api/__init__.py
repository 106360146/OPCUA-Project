
# Ref: https://learndataanalysis.org/google-drive-api-in-python-getting-started-lesson-1/

import pickle
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

def Create_Service(client_alias, api_name, api_version, *scopes):
    '''
        @client_alias: 用來產生唯一的 pickle 名稱用，因為別的服務也可能使用此服務。
        @api_name: 用來告訴 Google 是哪一個 api
        @api_version: 用來告訴 Google api 版本
        @scopes: Google API 的權限設定
    '''
    CLIENT_SECRET_FILE = 'credentials.json'
    API_SERVICE_NAME = api_name
    API_VERSION = api_version
    SCOPES = [scope for scope in scopes[0]]

    cred = None
    pickle_file = f'config/token_{client_alias}.pickle'

    if os.path.exists(pickle_file):
        with open(pickle_file, 'rb') as token:
            cred = pickle.load(token)

    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            cred = flow.run_local_server()

        with open(pickle_file, 'wb') as token:
            pickle.dump(cred, token)
    try:
        service = build(API_SERVICE_NAME, API_VERSION, credentials=cred)
        return service
    except Exception as e:
        print(f"{e}: Unable to connect.")
        return None

