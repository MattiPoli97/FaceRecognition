import pygame
import cv2
import random
import datetime
import time
from . import game
import os
import math

WIDTH, HEIGHT = 800, 600

class Ball:
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.speed_x = random.randint(-3, 3)
        self.speed_y = random.randint(-3, 3)

    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y

        if self.x <= self.radius or self.x >= WIDTH - self.radius:
            self.speed_x *= -1
        if self.y <= self.radius or self.y >= HEIGHT - self.radius:
            self.speed_y *= -1

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
class Leaf:
    def __init__(self, x, y, size):
        self.size = size
        self.leaf = pygame.transform.scale(pygame.image.load("leaf.png"), (self.size, self.size))
        self.x = x
        self.y = y
        self.speed_x = random.randint(-3, 3)
        self.speed_y = random.randint(-3, 3)
        if self.speed_x == 0 and self.speed_y == 0:
            self.speed_y = 1
            self.speed_x = 1
        self.rotation = random.randint(-180, 180)

    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y

        if self.x <= self.size or self.x >= WIDTH - self.size:
            self.speed_x *= -1
        if self.y <= self.size or self.y >= HEIGHT - self.size:
            self.speed_y *= -1

    def draw(self, screen):
        leaf = pygame.transform.rotate(self.leaf, self.rotation)
        screen.blit(leaf, (self.x - self.size, self.y - self.size))

class Button_with_icon:
    def __init__(self, x, y, width, height, text, icon=None, font=None, font_size=30, color=(229,193,66, 128), hover_color=(200, 200, 200, 128)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.icon = icon
        self.font = pygame.font.Font(font, font_size) if font else pygame.font.SysFont(None, font_size)
        self.color = color
        self.hover_color = hover_color

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(surface, self.hover_color, self.rect)
        
        if self.icon:
            icon_surface = pygame.image.load(self.icon).convert_alpha()
            icon_surface = pygame.transform.scale(icon_surface, (self.rect.height, self.rect.height))
            icon_rect = icon_surface.get_rect(topleft=(self.rect.x, self.rect.y))
            surface.blit(icon_surface, icon_rect)
        
        if self.text:
            text_surface = self.font.render(self.text, True, (0, 0, 0))
            text_rect = text_surface.get_rect(midleft=(self.rect.centerx, self.rect.centery))
            
            surface.blit(text_surface, text_rect)

    def is_clicked(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    return True
        return False

def play_video_from_images(folder, music_file, screen, width, height, resize, display_text):
   
    clock = pygame.time.Clock()

    SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_width(), screen.get_height()
    aspect_ratio = SCREEN_WIDTH // SCREEN_HEIGHT
    frames = []
    for i, filename in enumerate(sorted(os.listdir(folder))):
        if filename.endswith(".png") and i % 2 == 0:
            frame = pygame.image.load(os.path.join(folder, filename))
            if resize:
                frame = pygame.transform.scale(frame, (SCREEN_WIDTH // 2, (SCREEN_WIDTH // 2) // aspect_ratio))
            frames.append(frame)
   
    frame_index = 0
    running = True
   
    #Load the text if needed
    if display_text :
        font = pygame.font.SysFont(None, 100) 
        text = "Il GIARDINO PARLANTE ti da il benvenuto!"
        text_surface = font.render(text, True, (255,255,255)) 
        text_width, text_height = text_surface.get_rect().size
    
        if text_width > SCREEN_WIDTH:
            words = text.split()
            half_index = len(words) // 2
            first_line = ' '.join(words[:half_index])
            second_line = ' '.join(words[half_index:])
            text_surface1 = font.render(first_line, True, (255,255,255))
            text_surface2 = font.render(second_line, True,(255,255,255))
            text_height = text_surface1.get_rect().height * 2  

    if music_file:
        pygame.mixer.music.load(music_file)
        sound = pygame.mixer.Sound(music_file)
        sound.set_volume(2)
        pygame.mixer.music.play()
        pygame.display.flip()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        if display_text:
            if text_width > SCREEN_WIDTH:
                screen.blit(text_surface1, ((SCREEN_WIDTH - text_surface1.get_width()) // 2, text_surface1.get_height() -50))
                screen.blit(text_surface2, ((SCREEN_WIDTH - text_surface2.get_width()) // 2, text_height - 30))
            else:
                screen.blit(text_surface, ((SCREEN_WIDTH - text_width) // 2, (SCREEN_HEIGHT // 2 - text_height)))
        
        screen.blit(frames[frame_index], (width, height - frame.get_rect().size[1]))
        pygame.display.flip()
        clock.tick(30)

        frame_index += 1
        if frame_index >= len(frames):
            frame_index = 0
            running = False
        
def detect_face(cam, model, bg_sound, image_folder, music_folder, giochiamo):
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
            #pygame.mixer.music.set_volume(1)
            time.sleep(2)
            cam.release()
            cv2.destroyAllWindows()
            game.main(input, model, image_folder, music_folder, bg_sound, giochiamo)
        
        if datetime.datetime.now() >= endTime:
            pygame.mixer.music.set_volume(1)
            cam.release()
            cv2.destroyAllWindows()
            game.main(input, model, image_folder, music_folder, bg_sound, giochiamo)
            
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cam.release()
    cv2.destroyAllWindows()

def main(avatar, model, images, music) :
    pygame.init()
    bg_sound = pygame.mixer.Sound('background_music.wav')
    bg_sound.play()
    
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    
    # Color definition
    
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (200, 200, 200)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)

    Soft_Blue = (191, 219, 255)
    Soft_Pink = (255, 204, 229)
    Soft_Green = (204, 255, 204)
    Soft_Yellow = (255, 255, 204)
    Soft_Lavender = (230, 230, 255)
    bg_color_list = [Soft_Blue, Soft_Yellow, Soft_Green, Soft_Lavender, Soft_Pink]
    random_bg_color = random.choice(bg_color_list)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("MEMORY GAME")
    screen.fill(random_bg_color)
    balls = []
    for _ in range(30):
        x = random.randint(SCREEN_WIDTH // 4, 3 * SCREEN_WIDTH // 4)
        y = random.randint(SCREEN_HEIGHT // 4, 3 * SCREEN_HEIGHT // 4)
        radius = random.randint(20, 70)
        ball = Leaf(x, y, radius)
        balls.append(ball)
    
    running = True
    while running:
        # Gestione degli eventi
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                image_reverse = pygame.transform.scale(pygame.image.load('Background.png').convert_alpha(),(SCREEN_WIDTH, SCREEN_HEIGHT))
                rotated_scaled_image = pygame.transform.flip(image_reverse, True, False)
                background_images = [pygame.transform.scale(pygame.image.load('Background.png').convert_alpha(), (SCREEN_WIDTH, SCREEN_HEIGHT)),
                                rotated_scaled_image, pygame.transform.scale(pygame.image.load('Background.png').convert_alpha(), (SCREEN_WIDTH, SCREEN_HEIGHT)), rotated_scaled_image]
                background_index = 0
                background_alpha = 255  # Initial alpha value for fading
                background_scroll_x = 0
                background_scroll_speed = 2

                running_1 = True
            
                scrolling_enabled = True

                # Button parameters
                button_width = 250
                button_height = 100
                button_x = (SCREEN_WIDTH - button_width) // 4 -50
                button_y = 100
                button_x_1 = 3*(SCREEN_WIDTH - button_width) // 4 + 50
                button_y_1 = button_y + SCREEN_HEIGHT//2

                button_l = Button_with_icon(button_x, button_y,button_width, button_height, "Giochiamo!", icon="./icons/icon_game.png") 
                button_r = Button_with_icon(button_x_1, button_y_1 , button_width , button_height, "Ricordiamo!", icon="./icons/icon_remember.png") 

                game_started = False
                giochiamo = False
            
                while running_1:
                    screen.fill(random_bg_color)
                    screen.blit(background_images[background_index], (background_scroll_x, 0))
                    screen.blit(background_images[1 - background_index], (background_scroll_x + SCREEN_WIDTH, 0))
                    
                    fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                    fade_surface.fill((0, 0, 0))
                    fade_surface.set_alpha(background_alpha)
                    screen.blit(fade_surface, (0, 0))

                    if scrolling_enabled:
                        background_scroll_x -= background_scroll_speed
                        if background_scroll_x <= -SCREEN_WIDTH:
                            background_scroll_x = 0

                    if background_alpha > 0:
                        background_alpha -= 2 
                    
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running_1 = False
                        elif event.type == pygame.MOUSEBUTTONDOWN and not game_started:
                            mouse_x, mouse_y = pygame.mouse.get_pos()
                            if button_x <= mouse_x <= button_x + button_width and button_y <= mouse_y <= button_y + button_height:
                                game_started = True
                                giochiamo = True
                            if button_x_1 <= mouse_x <= button_x_1 + button_width and button_y_1 <= mouse_y <= button_y_1 + button_height:
                                game_started = True
                    
                    button_l.draw(screen)
                    button_r.draw(screen)

                    pygame.display.flip()

                    pygame.time.Clock().tick(60)

                    if game_started :
                        while background_alpha < 50:
                            fade_surface.set_alpha(background_alpha)
                            background_alpha += 2 
                        
                            screen.blit(fade_surface, (0, 0))
                            pygame.time.Clock().tick(15)
                            pygame.display.flip()

                        bg_sound.set_volume(0.2)
                        avatar = "./frames"
                        play_video_from_images(avatar, "./avatar/intro.mp4", screen, SCREEN_WIDTH // 4, SCREEN_HEIGHT, True, True)
                        bg_sound.set_volume(1)
                        cam = cv2.VideoCapture(0)
                        detect_face(cam, model, bg_sound, images, music, giochiamo)
        
        screen.fill(random_bg_color)

        for ball in balls:
            ball.move()
            ball.draw(screen)

        pygame.display.update()

        pygame.time.delay(30)

    pygame.quit()

if __name__ == "__main__" :
    main()