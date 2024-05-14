import pygame
import cv2
import random
import datetime
import time
from face_rec import game
import os
import pyttsx3

# colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GREY = (230, 230, 230)
BEIGE = (205,203, 192)

class Leaf:
    def __init__(self, x, y, size, SCREEN_WIDTH, SCREEN_HEIGHT):
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
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

        # Generate a random color mask
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y

        if self.x <= self.size or self.x >= self.SCREEN_WIDTH - self.size:
            self.speed_x *= -1
        if self.y <= self.size or self.y >= self.SCREEN_HEIGHT - self.size:
            self.speed_y *= -1

        self.rotation += self.speed_x

    def draw(self, screen):
        # Apply color mask
        colored_leaf = self.leaf.copy()
        colored_leaf.fill(self.color + (255,), special_flags=pygame.BLEND_RGBA_MULT)  # Set alpha to 255

        # Rotate around the center of the leaf
        rotated_leaf = pygame.transform.rotate(colored_leaf, self.rotation)
        rect = rotated_leaf.get_rect(center=(self.x, self.y))

        screen.blit(rotated_leaf, rect.topleft)
class Button:
    def __init__(self, x, y, width, height, color, text=''):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.text = text
        self.font = pygame.font.Font(None, 70)

    def draw(self, surface, writing_color):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=20)
        text_surface = self.font.render(self.text, True, writing_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

        #if self.rect.collidepoint(pygame.mouse.get_pos()):
            #pygame.draw.rect(surface, (200, 200, 200, 50), self.rect, border_radius=20)

    def remove(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect, border_radius=20)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def is_correct(self, position, index):
        return True if index == position else False
class Button_with_icon:
    def __init__(self, x, y, width, height, text=None, icon=None, font=None, font_size=70, color=(229, 193, 66, 128),
                 hover_color=(200, 200, 200, 128)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.icon = icon
        self.font = pygame.font.Font(font, font_size) if font else pygame.font.SysFont(None, font_size)
        self.color = color
        self.hover_color = hover_color

    def draw(self, surface):
        # Draw the rectangle with anti-aliasing
        pygame.draw.rect(surface, self.color, self.rect, border_radius=20)

        if self.rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(surface, self.hover_color, self.rect, border_radius=20)

        if self.icon:
            icon_surface = pygame.image.load(self.icon).convert_alpha()
            icon_surface = pygame.transform.scale(icon_surface, (self.rect.height, self.rect.height))
            icon_rect = icon_surface.get_rect(topleft=(self.rect.x, self.rect.y)) if self.text is not None else icon_surface.get_rect(center=self.rect.center)
            surface.blit(icon_surface, icon_rect)

        if self.text is not None:
            text_surface = self.font.render(self.text, True, (0, 0, 0))
            text_rect = text_surface.get_rect(midleft=(self.rect.centerx, self.rect.centery))
            surface.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

def play_video_from_images(folder, music_file, screen, display_text, goon_button: Button | None, text=None):
    clock = pygame.time.Clock()

    SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_width(), screen.get_height()
    frames = []
    for i, filename in enumerate(sorted(os.listdir(folder))):
        if filename.endswith(".png") and filename.startswith("f") and i % 2 == 0:
            frame = pygame.image.load(os.path.join(folder, filename))
            frames.append(frame)

    frame_index = 0
    running = True

    # Load the text if needed
    if display_text:

        font = pygame.font.SysFont(None, 100)
        text_surface = font.render(text, True, (255, 255, 255))
        text_width, text_height = text_surface.get_rect().size
        text_x = (SCREEN_WIDTH - text_width) // 2

        if text_width > SCREEN_WIDTH:
            words = text.split()
            half_index = len(words) // 2
            first_line = ' '.join(words[:half_index])
            second_line = ' '.join(words[half_index:])
            text_surface1 = font.render(first_line, True, (255, 255, 255))
            text_surface2 = font.render(second_line, True, (255, 255, 255))
            text_height = text_surface1.get_rect().height * 2

    if music_file:
        pygame.mixer.music.load(music_file)
        sound = pygame.mixer.Sound(music_file)
        sound.set_volume(2)
        pygame.mixer.music.play()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if goon_button.is_clicked(pygame.mouse.get_pos()):
                    pygame.mixer.music.fadeout(5000)
                    return

        if display_text:
            if text_width > SCREEN_WIDTH:
                screen.blit(text_surface1,
                            ((SCREEN_WIDTH - text_surface1.get_width()) // 2, text_surface1.get_height() - 50))
                screen.blit(text_surface2, ((SCREEN_WIDTH - text_surface2.get_width()) // 2, text_height - 30))
            else:
                screen.blit(text_surface, (text_x, text_height))

        frame_w, frame_h = frames[0].get_width(), frames[0].get_height()

        if folder == "./frames_dancing_avatar":
            screen.blit(frames[frame_index], (SCREEN_WIDTH * 3//4 - frame_w//2, SCREEN_HEIGHT* 3//4 - frame_h//2))
        else:
            screen.blit(frames[frame_index], (SCREEN_WIDTH//2 - frame_w//2, SCREEN_HEIGHT//2 - frame_h//2 + text_height))
        pygame.display.flip()
        clock.tick(30)

        frame_index += 1
        if frame_index >= len(frames):
            if folder == "./frames_dancing_avatar":
                    frame_index = 0
            else:
                running = False


def detect_face(cam, model, bg_sound, image_folder, music_folder, giochiamo):
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(model)

    faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    font = cv2.FONT_HERSHEY_SIMPLEX

    names = ['', 'Mattia', 'Diana', 'Giulia']
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
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(int(minW), int(minH)),
        )

        for (x, y, w, h) in faces:

            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

            id, confidence = recognizer.predict(gray[y:y + h, x:x + w])

            # Check if confidence is less them 100 ==> "0" is perfect match
            if (confidence < 100):
                id = names[id]
                confidence = "  {0}%".format(round(100 - confidence))
            else:
                id = "unknown"
                confidence = "  {0}%".format(round(100 - confidence))

            cv2.putText(img, str(id), (x + 5, y - 5), font, 1, (255, 255, 255), 2)
            cv2.putText(img, str(confidence), (x + 5, y + h - 5), font, 1, (255, 255, 0), 1)

        if id in names:
            # pygame.mixer.music.set_volume(1)
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

def read(text):
    # Initialize the TTS engine
    engine = pyttsx3.init()
    # Set the speech rate (words per minute), default is 200
    engine.setProperty('rate', 100)
    engine.setProperty('pitch', 0.5)
    # Use the TTS engine to read the provided text
    engine.say(text)
    engine.runAndWait()

def text_sound(mp3_path):
    audio = pygame.mixer.Sound(mp3_path)
    audio.play()
    pygame.time.wait(int(audio.get_length() * 1000))  # Wait for the audio to finish playing

def fade_out_sound(sound, duration):
    original_volume = sound.get_volume()
    step = original_volume / (duration / 100)
    for i in range(duration // 100):
        new_volume = original_volume - step * (i + 1)
        sound.set_volume(new_volume)
        pygame.time.delay(100)  # Adjust delay to control fade-out speed
    sound.stop()

def fade_in_sound(sound, duration):
    original_volume = sound.get_volume()
    target_volume = 1.0  #
    steps = int(duration / 1000 * pygame.mixer.get_init()[0])
    step = (target_volume - original_volume) / steps
    for i in range(steps):
        new_volume = original_volume + step * (i + 1)
        sound.set_volume(new_volume)
        pygame.time.delay(int(duration / steps))

def mantain_aspectratio(picture, windowWidth, windowHeight):
    original_width, original_height = picture.get_rect().size
    width_ratio = windowWidth / original_width
    height_ratio = windowHeight / original_height
    scaling_factor = min(width_ratio, height_ratio)
    scaled_width = int(original_width * scaling_factor)
    scaled_height = int(original_height * scaling_factor)
    return scaled_width, scaled_height