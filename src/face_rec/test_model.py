import cv2
from PIL import Image
from pathlib import Path
from random import randint
import numpy as np

def main(input, model):
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(model)   #load trained model
    
    faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    font = cv2.FONT_HERSHEY_SIMPLEX

    minW = 30
    minH = 30

    names = ['','1','2', '3', '4', '5', '6', '7','8', '9', '10', '11', '12', '13', '14', '15'] 
    id = len(names) - 1 
    
    im1 = Image.open(input)
    im2 = Image.open("Background.png")
    im2.paste(im1, (randint(0, 1000), randint(0, 1000)))
    #im2.save('test.png', quality=95)
  
    gray = np.array(im2)
    gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)


    faces = faceCascade.detectMultiScale( 
        gray,
        scaleFactor = 1.2,
        minNeighbors = 5,
        minSize = (int(minW), int(minH)),
    )

    for(x,y,w,h) in faces:

        cv2.rectangle(gray, (x,y), (x+w,y+h), (0,255,0), 2)

        id, confidence = recognizer.predict(gray[y:y+h,x:x+w])

        # Check if confidence is less them 100 ==> "0" is perfect match 
        if (confidence < 100):
            id = names[id]
            confidence = "  {0}%".format(round(100 - confidence))
        else:
            id = "unknown"
            confidence = "  {0}%".format(round(100 - confidence))
        
        cv2.putText(gray, str(id), (x+5,y-5), font, 1, (255,255,255), 2)
        cv2.putText(gray, str(confidence), (x+5,y+h-5), font, 1, (255,255,0), 1)  

        cv2.imshow("Result", gray)
        k = cv2.waitKey(5000) & 0xff 
      
        cv2.imwrite(f'test_{Path(input).stem}.png',gray) 

if __name__ == "__main__": 
    main()