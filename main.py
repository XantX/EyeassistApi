import cv2
import os
import base64
import requests
from fastapi import FastAPI
from pytube import YouTube

app = FastAPI()


@app.get("/")
async def root():
    processVideo()
    return {"message": "Hellow World"}


def processVideo():
    yt = YouTube('https://www.youtube.com/watch?v=eNFAJbWCSww')
    stream = yt.streams.get_highest_resolution()

    stream.download(filename='video_descargado.mp4')

    cap = cv2.VideoCapture('video_descargado.mp4')

    ret, frame = cap.read()
    if ret:
        _, buffer = cv2.imencode('.jpg', frame)
        encoded_frame = base64.b64encode(buffer)
        with open('frame_encoded.txt', 'w') as f:
            f.write(encoded_frame.decode('utf-8'))

    cap.release()

    if os.path.exists('video_descargado.mp4'):
        os.remove('video_descargado.mp4')
    else:
        print('No hay video')
