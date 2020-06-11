from __future__ import print_function
import gauridecoder_arecord
import sys
import signal
import speech_recognition as sr
import os
import redis
import json
from os.path import join, dirname
from watson_developer_cloud import TextToSpeechV1
from watson_developer_cloud.websocket import SynthesizeCallback
from rasa_core.agent import Agent
from rasa_core.interpreter import RasaNLUInterpreter
import pygame
import time
import requests
import json
"""
This demo file shows you how to use the new_message_callback to interact with
the recorded audio after a keyword is spoken. It uses the speech recognition
library in order to convert the recorded audio into text.

Information on installing the speech recognition library can be found at:
https://pypi.python.org/pypi/SpeechRecognition/
"""
redis_host = "localhost"
redis_port = 6379
redis_password = "uimmxx"
interpreter = RasaNLUInterpreter('resources/models/current/nlu')
agent = Agent.load('resources/models/dialogue', interpreter=interpreter)

r = redis.StrictRedis(host='localhost', port=6379, db=0)
msg = r.get("msg:SRName")
print(msg) 

interrupted = False

service = TextToSpeechV1(
   url='https://stream-fra.watsonplatform.net/text-to-speech/api',
    iam_apikey='ksdf8WijvLfzX1__28bFnyeXejDmyynOP0LPAzUj9Ehh')

voices = service.list_voices().get_result()
print(json.dumps(voices, indent=2))

def playSpeech():
    pygame.init()
    pygame.mixer.music.load("resources/speech.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        continue
    pygame.quit()

def getFuelStatus():
    print("checking fuel level")
    url = "https://api.mercedes-benz.com/experimental/connectedvehicle/v1/vehicles/08748497FBE9AAADE2/fuel"
    headers = { 'accept' : 'application/json', 'authorization' : 'Bearer 5f12a859-a500-46a1-bdd2-2ddb822c6799' }    
    mbResponse = requests.get(url,headers=headers)
    if(mbResponse.ok):
        jData = mbResponse.json()
        print("The response contains {0} properties".format(len(jData)))
        print("\n")
        fuel = jData['fuellevelpercent']['value'] * 100
        playMessage("Fuel level is "+str('{0:g}'.format(fuel))+"%")        
    else:  
        mbResponse.raise_for_status()       

def getLockStatus():
    print("checking lockStatus")
    url = "https://api.mercedes-benz.com/experimental/connectedvehicle/v1/vehicles/08748497FBE9AAADE2/doors"
    headers = { 'accept' : 'application/json', 'authorization' : 'Bearer 5f12a859-a500-46a1-bdd2-2ddb822c6799' }    
    mbResponse = requests.get(url,headers=headers)
    if(mbResponse.ok):
        jData = mbResponse.json()
        print("The response contains {0} properties".format(len(jData)))
        print("\n")
        status = str(jData['doorlockstatusvehicle']['value'])
        playMessage("All doors are "+ status)        
    else:  
        mbResponse.raise_for_status()


def setLockStatus(lockStatus):
    print("setting lockStatus to ", lockStatus)
    url = "https://api.mercedes-benz.com/experimental/connectedvehicle/v1/vehicles/08748497FBE9AAADE2/doors"
    headersItem = { 'content-type' : 'application/json', 'authorization' : 'Bearer 5f12a859-a500-46a1-bdd2-2ddb822c6799' }    
    dataItem = { 'command': 'LOCK'}
    if lockStatus == 'UNLOCK':
        dataItem = { 'command': 'UNLOCK'}
    mbResponse = requests.post(url,data=json.dumps(dataItem),headers=headersItem)
    jData = mbResponse.json()
    print("The response contains {0} properties".format(len(jData)))
    print("\n")        
    playMessage("All doors are "+ lockStatus+"ed")        
    

def doAction(rasaAction):
    print("Action is", rasaAction)
    if rasaAction == "checkFuelStatus":
        getFuelStatus()
    elif rasaAction == "checkLockStatus":
        getLockStatus()
    elif rasaAction == "lockMyCar":        
        setLockStatus('LOCK')
    elif rasaAction == "unlockMyCar":        
        setLockStatus('UNLOCK')
    elif rasaAction == "unlockAndSetHeater":
        print("Setting car Heaters")
    else:
        print("No valid Action")

def audioRecorderCallback(fname):
    print("Processing...")
    r = sr.Recognizer()
    with sr.AudioFile(fname) as source:
        audio = r.record(source)  # read the entire audio file
    # recognize speech using Google Speech Recognition
    try:       
        googlemsg = r.recognize_google(audio)
        rasaMessage=""
        rasaAction=""
        print(googlemsg)
        responses = agent.handle_text(googlemsg)        
        time.sleep(0)
        if len(responses) > 0:
            splitMessage = responses[0].get('text').split(':')            
            rasaMessage = splitMessage[0]
            if len(splitMessage) == 2:
                print(splitMessage[1])
                rasaAction  = splitMessage[1]
        else:
            rasaMessage ="I can not process this"                                      
            
        with open(join(dirname(__file__), 'resources/speech.mp3'),
              'wb') as audio_file:
            response = service.synthesize(
                rasaMessage, accept='audio/mp3',
                voice="en-US_AllisonVoice").get_result()
            audio_file.write(response.content)

        playSpeech()    

        print("rasaAction ", rasaAction)
        if rasaAction != "":
            doAction(rasaAction)
        
    except sr.UnknownValueError:
        print("Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Speech Recognition service; {0}".format(e))

    os.remove(fname)
    time.sleep(0.03)
    detector.callBackRecord(detected_callback=detectedCallback,
                            audio_recorder_callback=audioRecorderCallback,
                            interrupt_check=interrupt_callback, sleep_time=0.01)



def detectedCallback():    
    print('recording audio...', end='', flush=True)

def playMessage(message):                         
            
    with open(join(dirname(__file__), 'resources/speech.mp3'),
          'wb') as audio_file:
        response = service.synthesize(
            message, accept='audio/mp3',
            voice="en-US_AllisonVoice").get_result()
        audio_file.write(response.content)

    playSpeech()

def detectedCallbackFirstTime():    
    playMessage("Hey there")            

def signal_handler(signal, frame):
    global interrupted
    interrupted = True

def interrupt_callback():
    global interrupted
    return interrupted

if len(sys.argv) == 1:
    print("Error: need to specify model name")
    print("Usage: python demo.py your.model")
    sys.exit(-1)

model = sys.argv[1]

# capture SIGINT signal, e.g., Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

detector = gauridecoder_arecord.HotwordDetector(model, sensitivity=0.38)
print('Listening... Press Ctrl+C to exit')


# main loop
detector.start(detected_callback=detectedCallbackFirstTime,
               audio_recorder_callback=audioRecorderCallback,
               interrupt_check=interrupt_callback,
               sleep_time=0.01)

detector.terminate()




