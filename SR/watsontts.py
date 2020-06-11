from __future__ import print_function
import json
from os.path import join, dirname
from watson_developer_cloud import TextToSpeechV1
from watson_developer_cloud.websocket import SynthesizeCallback
import pygame
import time


service = TextToSpeechV1(
   url='https://stream-fra.watsonplatform.net/text-to-speech/api',
    iam_apikey='ksdf8WijvLfzX1__28bFnyeXejDmyynOP0LPAzUj9Ehh')

voices = service.list_voices().get_result()
print(json.dumps(voices, indent=2))

with open(join(dirname(__file__), 'resources/speech.mp3'),
          'wb') as audio_file:
    response = service.synthesize(
        'Hello world!', accept='audio/mp3',
        voice="en-US_AllisonVoice").get_result()
    audio_file.write(response.content)

pygame.init()
pygame.mixer.music.load("resources/speech.mp3")
pygame.mixer.music.play()
time.sleep(10)
