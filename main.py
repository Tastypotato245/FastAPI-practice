from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from dotenv import load_dotenv
import os
import io
import base64

load_dotenv()
app = FastAPI()

CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def get_authenticated_service():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_local_server(port=8080)
    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, credentials=credentials)

def get_captions(video_id):
    youtube = get_authenticated_service()
    
    try:
        caption_result = youtube.captions().list(part="snippet", videoId=video_id).execute()
        captions = caption_result.get("items", [])
        
        english_captions = [caption for caption in captions if caption["snippet"]["language"] == "en"]
        
        if english_captions:
            caption_id = english_captions[0]["id"]
            
            request = youtube.captions().download(id=caption_id, tfmt='vtt')
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            fh.seek(0)
            caption_content = fh.read().decode('UTF-8')
            return caption_content
        else:
            return "Available English captions not found."
    except HttpError as e:
        print(f"An HTTP error {e.resp.status} occurred:\n{e.content}")
        return "An error occurred while fetching captions."

@app.get("/", response_class=HTMLResponse)
async def get_video():
    video_id = "CKZvWhCqx1s"  # YouTube 비디오 ID
    captions_content = get_captions(video_id)
    
    html_content = f"""
    <html>
        <head>
            <title>YouTube Video with Captions</title>
        </head>
        <body>
            <div>
                <iframe width="560" height="315" src="https://www.youtube.com/embed/{video_id}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
            </div>
            <div id="captions" style="margin-top: 20px;">
                <p>{captions_content}</p>
            </div>
        </body>
    </html>
    """
    return html_content
