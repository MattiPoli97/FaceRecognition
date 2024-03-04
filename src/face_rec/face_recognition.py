import cv2
from pathlib import Path

def main(input, model):
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(model)   #load trained model
    
    faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    font = cv2.FONT_HERSHEY_SIMPLEX

    id = 1 #two persons 

    names = ['','Mattia',] 

    # Initialize and start realtime video capture
    cam = cv2.VideoCapture(input)

    # Define min window size to be recognized as a face
    minW = 30
    minH = 30

    i = 0

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
        output = Path("./test")
        cv2.imwrite(f'{output}/test_{i}.png', img)
        i += 1
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()