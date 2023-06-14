import cv2
import os
import base64
import requests
from requests import Response
from fastapi import FastAPI
from pytube import YouTube
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

API_KEY = os.environ['API_KEY']


@app.get("/videos")
async def videos():
    await processVideo()
    return {"message": "Hellow World"}


@app.post("/imagenes")
async def imagenes():
    await processVideo()
    return {"message": "Hellow World"}


async def processVideo():
    if ~os.path.exists('video_descargado.mp4'):
        yt = YouTube('https://www.youtube.com/watch?v=dghbPSTeNjU&ab_channel=agungzoga')
        stream = yt.streams.get_lowest_resolution()
        stream.download(filename='video_descargado.mp4')

    cap = cv2.VideoCapture('video_descargado.mp4')
    fps = cap.get(cv2.CAP_PROP_FPS)
    print("FPS del video:", fps)
    frame_deseado = 630
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    for frame_actual in range(total_frames):
        ret, frame = cap.read()
        if frame_actual == frame_deseado:
            if ret:
                cv2.imwrite('frame.png', frame)
                _, buffer = cv2.imencode('.jpg', frame)
                encoded_frame = base64.b64encode(buffer)
                with open('frame_encoded.txt', 'w') as f:
                    f.write(encoded_frame.decode('utf-8'))

                data = {
                  "image": {
                    "raw": str(encoded_frame.decode('utf-8'))
                   }
                }
                print("Peticion a la api")
                resultado = await makeRequest(data)
                print(resultado)

    cap.release()


async def makeRequest(data):
    headers = {
            "X-API-Key": API_KEY,
            "Content-Type": "application/json",
            }
    result: Response = requests.post('https://alttext.ai/api/v1/images', json=data, headers=headers)
    print(result.content)
    return result
