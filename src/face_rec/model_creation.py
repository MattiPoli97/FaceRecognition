import cv2
import numpy as np
from PIL import Image #pillow package
import os

# function to get the images and label data
def getImagesAndLabels(path):

    imagePaths = [os.path.join(path,f) for f in os.listdir(path)]     
    faceSamples=[]
    ids = []
    detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    for imagePath in imagePaths:

        PIL_img = Image.open(imagePath).convert('L') # convert it to grayscale
        img_numpy = np.array(PIL_img,'uint8')

        id = int(os.path.split(imagePath)[-1].split(".")[1])
        faces = detector.detectMultiScale(img_numpy)

        for (x,y,w,h) in faces:
            faceSamples.append(img_numpy[y:y+h,x:x+w])
            ids.append(id)

    return faceSamples,ids

def main(path, model):

    path = path

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    
    faces,ids = getImagesAndLabels(path)
    
    recognizer.train(faces, np.array(ids))

    # Saving
    recognizer.write(model)

    # Print the numer of faces trained and end program
    print("\n [INFO] {0} faces trained. Exiting Program".format(len(np.unique(ids))))

if __name__ == "__main__":
    main()