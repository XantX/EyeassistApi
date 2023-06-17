import cv2
import os
import math
import base64
import requests
from requests import Response
from fastapi import FastAPI
from pytube import YouTube
from dotenv import load_dotenv
from azure_client import create_client
import io

load_dotenv()
app = FastAPI()
client = create_client()

API_KEY = os.environ['API_KEY']


@app.get("/videos")
async def videos():
    current_minute, current_second, resultado = await processVideo()
    print("Azure resultado", resultado)
    return {"minutes": current_minute, "seconds": current_second, "captions": resultado.captions}


@app.post("/imagenes")
async def imagenes():
    current_minute, current_second, resultado = await processVideo()
    return {"minutes": current_minute, "seconds": current_second}


def get_frame_time(frame_number, fps):
    total_seconds = frame_number / fps
    minutes = math.floor(total_seconds / 60)
    seconds = math.floor(total_seconds % 60)
    return minutes, seconds


async def processVideo():
    if ~os.path.exists('video_descargado.mp4'):
        yt = YouTube('https://www.youtube.com/watch?v=dghbPSTeNjU&ab_channel=agungzoga')
        stream = yt.streams.get_lowest_resolution()
        stream.download(filename='video_descargado.mp4')

    cap = cv2.VideoCapture('video_descargado.mp4')
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)

    print("FPS del video:", fps)
    frame_deseado = 130
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    for frame_actual in range(total_frames):
        ret, frame = cap.read()

        current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
        current_minute, current_second = get_frame_time(current_frame, fps)

        print(f"Frame: {current_frame} - Time: {current_minute:02d}:{current_second:02d}")

        if frame_actual == frame_deseado:
            if ret:
                cv2.imwrite('frame.png', frame)
                _, buffer = cv2.imencode('.jpg', frame)
                encoded_frame = base64.b64encode(buffer)
                base64_string = encoded_frame.decode("utf-8")
                with open('frame_encoded.txt', 'w') as f:
                    f.write(encoded_frame.decode('utf-8'))

                image_bytes = io.BytesIO(base64.b64decode(base64_string))
                resultado = await request_descrition_azure(image_bytes)
                print(resultado)
            break

    cap.release()
    return current_minute, current_second, resultado


async def makeRequest(data):
    headers = {
            "X-API-Key": API_KEY,
            "Content-Type": "application/json",
            }
    result: Response = requests.post('https://alttext.ai/api/v1/images', json=data, headers=headers)
    return result


async def request_descrition_azure(image):
    print("Llamada a azure")
    return client.describe_image_in_stream(image, language='es', max_candidates=3)
