from fastapi import *
import os
import youtube_dl

app = FastAPI()

VIDEO_DOWNLOAD_PATH = './yt_temp/'  # 다운로드 경로

@app.get("/")
async def root():
    return {"message": "Hello World"}



@app.get("/yt/{code}")
async def dl(code: str):
    download_mp3(VIDEO_DOWNLOAD_PATH, ['https://www.youtube.com/watch?v=' + code])
    print('Complete download!')

        
    return {"message": code}



def download_mp3(output_dir, youtube_video_list):

    download_path = os.path.join(output_dir, '%(id)s-%(title)s.%(ext)s')

    for video_url in youtube_video_list:

        # youtube_dl options
        ydl_opts = {
            'format': 'bestaudio/best',  # 가장 좋은 화질로 선택(화질을 선택하여 다운로드 가능)
            'outtmpl': download_path, # 다운로드 경로 설정
            # 'writesubtitles': 'best', # 자막 다운로드(자막이 없는 경우 다운로드 X)
            # 'writethumbnail': 'best',  # 영상 thumbnail 다운로드
            # 'writeautomaticsub': True, # 자동 생성된 자막 다운로드
            # 'subtitleslangs': 'en',  # 자막 언어가 영어인 경우(다른 언어로 변경 가능)
            'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
            }]
        }

        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
        except Exception as e:
            print('error', e)
