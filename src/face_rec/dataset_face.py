import cv2
import time

def main(input, width, height, face_id) :
    cap = cv2.VideoCapture(input)
    #cap.set(3, width)
    #cap.set(4, height)
    face_id = face_id

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    print("\n Initializing face capture ...")

    count = 0
    time.sleep(10)
    while(True):
        
        ret, img = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x,y,w,h) in faces:
            time.sleep(2)
            cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)     
            count += 1
            print(f"\n Captured Image : {count}/30 ...")
            # Saving
            cv2.imwrite("./dataset/User." + str(face_id) + '.' + str(count) + ".png", gray[y:y+h,x:x+w])

            cv2.imshow('image', img)
            

        k = cv2.waitKey(100) & 0xff 
        if k == 27:
            break
        elif count >= 30: #30 face samples and stop video
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
