import pygame
import cv2
import random
import datetime
import time
from . import game
import subprocess


class Bubble:
    def __init__(self, screen_width, screen_height):
        self.radius = random.randint(5, 15)  # Random radius
        self.x = random.randint(self.radius, screen_width - self.radius)  # Random x-coordinate
        self.y = random.randint(self.radius, screen_height - self.radius)  # Random y-coordinate
        self.speed_x = random.uniform(-5, 5)  # Random x-speed
        self.speed_y = random.uniform(-5, 5)  # Random y-speed
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))  # Random color
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 600

    def move(self):
        # Move the bubble
        self.x += self.speed_x
        self.y += self.speed_y

        # Bounce off the edges of the screen
        if self.x - self.radius < 0 or self.x + self.radius > self.SCREEN_WIDTH:
            self.speed_x *= -1
        if self.y - self.radius < 0 or self.y + self.radius > self.SCREEN_HEIGHT:
            self.speed_y *= -1

        #Touch video
        if self.x + self.radius > self.SCREEN_WIDTH - 200 and self.y + self.radius > self.SCREEN_HEIGHT - 150:
            self.speed_x *= -1
            self.speed_y *= -1

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

def display_video(video_capture, screen, SCREEN_WIDTH, SCREEN_HEIGHT):
    ret, frame = video_capture.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert frame colors from BGR to RGB
        frame = cv2.resize(frame, (int(SCREEN_WIDTH/4), int(SCREEN_HEIGHT/4)))

        frame = pygame.image.frombuffer(frame.tostring(), frame.shape[1::-1], "RGB")
        screen.blit(frame, (SCREEN_WIDTH - frame.get_width(), SCREEN_HEIGHT - frame.get_height()))

        pygame.display.flip()
        pygame.time.delay(60) 
    else:
        video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Restart video from the beginning

def detect_face(cam, model, bg_sound, image_folder, music_folder):
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(model)
    
    faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    font = cv2.FONT_HERSHEY_SIMPLEX

    names = ['','Mattia','Diana', 'Giulia'] 
    id = len(names) - 1 

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
            game.main(input, model, image_folder, music_folder, bg_sound)
        
        if datetime.datetime.now() >= endTime:
            bg_sound.set_volume(0.2)
            text_to_speak_intro = f"Buongiorno. Benvenuto nel giardino parlante!!"
            speak(text_to_speak_intro)
            cam.release()
            cv2.destroyAllWindows()
            game.main(input, model, image_folder, music_folder, bg_sound)
            
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cam.release()
    cv2.destroyAllWindows()

def speak(text):
    #subprocess.call(['say', '-v', 'Reed', text])
    subprocess.call(['say','-v', 'Alice', text])

def main(avatar) :
    pygame.init()
    bg_sounds = [pygame.mixer.Sound('relaxing-145038.mp3'), pygame.mixer.Sound('motivational.mp3')]
    bg_sound = random.choice(bg_sounds)
    bg_sound.play()
    
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    WHITE = (255, 255, 255)

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("TSINGTAO")
    screen.fill(WHITE)

    running = True

    video_path = avatar 
    video_capture = cv2.VideoCapture(video_path)

    cam = cv2.VideoCapture(0)

    bubbles = [Bubble(SCREEN_WIDTH, SCREEN_HEIGHT) for _ in range(20)]

    # Button parameters
    button_width = 200
    button_height = 50
    button_x = (SCREEN_WIDTH - button_width) // 4
    button_y = (SCREEN_HEIGHT - button_height) // 2

    button_width_1 = 200
    button_height_1 = 50
    button_x_1 = 3*(SCREEN_WIDTH - button_width) // 4

    game_started = False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and not game_started:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if button_x <= mouse_x <= button_x + button_width and button_y <= mouse_y <= button_y + button_height:
                    game_started = True
                if button_x_1 <= mouse_x <= button_x_1 + button_width_1 and button_y <= mouse_y <= button_y + button_height_1:
                    game_started = True
        
        display_video(video_capture, screen, SCREEN_WIDTH, SCREEN_HEIGHT)  
        pygame.draw.rect(screen, WHITE, ((0,0, SCREEN_WIDTH-200, SCREEN_HEIGHT-150)))
        pygame.draw.rect(screen, WHITE, ((SCREEN_WIDTH-200,0, SCREEN_WIDTH, SCREEN_HEIGHT-150)))
        pygame.draw.rect(screen, WHITE, ((0,SCREEN_HEIGHT-150, SCREEN_WIDTH-200, SCREEN_HEIGHT)))
        for bubble in bubbles:
            bubble.move()
            bubble.draw(screen)
        
        pygame.draw.ellipse(screen, (0, 0, 0), (button_x_1, button_y, button_width_1, button_height_1))
        font = pygame.font.Font(None, 36)
        text1 = font.render("Ricordiamo", True, (255, 255, 255))
        text_rect = text1.get_rect(center=(button_x_1 + button_width_1 // 2, button_y + button_height_1 // 2))
        screen.blit(text1, text_rect)

        pygame.draw.ellipse(screen, (0, 0, 0), (button_x, button_y, button_width, button_height))
        font = pygame.font.Font(None, 36)
        text = font.render("Giochiamo", True, (255, 255, 255))
        text_rect = text.get_rect(center=(button_x + button_width // 2, button_y + button_height // 2))
        screen.blit(text, text_rect)

        pygame.display.flip()

        # Control frame rate
        pygame.time.Clock().tick(60)
        if game_started :
            detect_face(cam, './trainer.yml', bg_sound, "./Immagini Proverbi", "./music")


    # Release video capture and quit Pygame
    video_capture.release()
    pygame.quit()

if __name__ == "__main__" :
    main()