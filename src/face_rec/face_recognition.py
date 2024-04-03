import cv2
from pathlib import Path
from . import game
import time
import subprocess
import random
import pygame
import datetime

def main(input, model, image_folder):
    # Play backgroung music
    pygame.init()
    bg_sounds = [pygame.mixer.Sound('relaxing-145038.mp3'), pygame.mixer.Sound('motivational.mp3')]
    bg_sound = random.choice(bg_sounds)
    bg_sound.play()
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(model)   #load trained model
    
    faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    font = cv2.FONT_HERSHEY_SIMPLEX

    names = ['','Mattia','Diana', 'Giulia'] 
    id = len(names) - 1 

    # Initialize and start realtime video capture
    cam = cv2.VideoCapture(input)

    # Define min window size to be recognized as a face
    minW = 30
    minH = 30

    endTime = datetime.datetime.now() + datetime.timedelta(seconds=10)

    while True:
        
        ret, img = cam.read()
        if not ret:
            break
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = faceCascade.detectMultiScale( 
            gray,
            scaleFactor = 1.2,
            minNeighbors = 5,
            minSize = (int(minW), int(minH)),
        )

        for(x,y,w,h) in faces:

            cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)

            id, confidence = recognizer.predict(gray[y:y+h,x:x+w])

            # Check if confidence is less them 100 ==> "0" is perfect match 
            if (confidence < 100):
                id = names[id]
                confidence = "  {0}%".format(round(100 - confidence))
            else:
                id = "unknown"
                confidence = "  {0}%".format(round(100 - confidence))
            
            cv2.putText(img, str(id), (x+5,y-5), font, 1, (255,255,255), 2)
            cv2.putText(img, str(confidence), (x+5,y+h-5), font, 1, (255,255,0), 1)  
        
        cv2.imshow('camera',img) 
        
        if id in names:
            #text_to_speak = "Good morning {id}!! It's time to wake up. Today will be a beatiful day and it's time to shyne!"
            bg_sound.set_volume(0.2)
            text_to_speak_intro = f"Buongiorno {id}. Benvenuto nel giardino parlante!!"
            text_to_speak = f"Proprio una bella giornata oggi!"
            speak(text_to_speak_intro)
            time.sleep(1)
            speak(text_to_speak)
            pygame.mixer.music.set_volume(1)
            time.sleep(2)
            cam.release()
            cv2.destroyAllWindows()
            game.main(input, model, image_folder)
        
        if datetime.datetime.now() >= endTime:
            bg_sound.set_volume(0.2)
            text_to_speak_intro = f"Buongiorno. Benvenuto nel giardino parlante!!"
            speak(text_to_speak_intro)
            cam.release()
            cv2.destroyAllWindows()
            game.main(input, model, image_folder)
            
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cam.release()
    cv2.destroyAllWindows()

def speak(text):
    #subprocess.call(['say', '-v', 'Reed', text])
    subprocess.call(['say','-v', 'Alice', text])

if __name__ == "__main__":
    main()