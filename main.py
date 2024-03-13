from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
import os

load_dotenv()
app = FastAPI()

YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
DEVELOPER_KEY = os.environ.get('YOUTUBE_DATA_API_KEY')

def get_captions(video_id):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)
    
    try:
        # 자막 목록을 가져옵니다.
        caption_result = youtube.captions().list(part="snippet", videoId=video_id).execute()
        captions = caption_result.get("items", [])
        
        # 원하는 언어의 자막을 필터링합니다. 여기서는 'en'으로 설정되어 있습니다.
        english_captions = [caption for caption in captions if caption["snippet"]["language"] == "en"]
        
        if english_captions:
            # 첫 번째 영어 자막을 선택합니다.
            caption_id = english_captions[0]["id"]
            # 자막의 실제 내용을 가져오는 API 호출은 변경 사항이 필요할 수 있으며, 
            # API 문서를 확인해 적절한 요청을 구성해야 합니다.
            # 예제에서는 단순히 ID를 반환하고 있습니다.
            return caption_id
        else:
            return None
    except HttpError as e:
        print(f"An HTTP error {e.resp.status} occurred:\n{e.content}")
        return None


@app.get("/", response_class=HTMLResponse)
async def get_video():
    video_id = "CKZvWhCqx1s"  # YouTube 비디오 ID
    captions = get_captions(video_id)
    if captions:
        captions_content = captions
    else:
        captions_content = "자막을 불러올 수 없습니다."
    
    html_content = f"""
    <html>
        <head>
            <title>YouTube Video with Lyrics</title>
        </head>
        <body>
            <div>
                <iframe width="560" height="315" src="https://www.youtube.com/embed/{video_id}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
            </div>
            <div id="lyrics" style="margin-top: 20px;">
                <p>{captions_content}</p>
            </div>
        </body>
    </html>
    """
    return html_content

