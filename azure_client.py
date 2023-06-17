from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
from dotenv import load_dotenv
import os

load_dotenv()
key = os.environ['ACCOUNT_KEY']


def create_client():
    credentials = CognitiveServicesCredentials(key)
    client = ComputerVisionClient(
        endpoint="https://test-vision-captioning.cognitiveservices.azure.com/",
        credentials=credentials
    )
    return client
