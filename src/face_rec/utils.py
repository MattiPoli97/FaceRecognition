import pygame
import pygame.gfxdraw
import cv2
import random
import datetime
import time
import os
import pyttsx3
from typing import Optional
import math

# colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
WHITE_4D = (255, 255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GREY = (230, 230, 230)
BEIGE = (205,203, 192)
Soft_Blue = (191, 219, 255)
Soft_Pink = (255, 204, 229)
Soft_Green = (204, 255, 204)
Soft_Yellow = (255, 255, 204)
Soft_Lavender = (230, 230, 255)
Soft_red = (255, 139, 130)
Lava_red = (206, 16, 33)
Sky_blue = (99, 197, 218)
Emerald_green = (2, 192, 43)

class Leaf:
    def __init__(self, x, y, size, SCREEN_WIDTH, SCREEN_HEIGHT):
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.size = size
        self.leaf = pygame.transform.scale(pygame.image.load("leaf.png"), (self.size, self.size))
        self.x = x
        self.y = y
        self.speed_x = random.randint(-SCREEN_WIDTH//250, SCREEN_WIDTH//250)
        self.speed_y = random.randint(-SCREEN_WIDTH//250, SCREEN_WIDTH//250)
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
    def __init__(self, x, y, width, height, text=None, icon=None, font='./Comfortaa/Comfortaa-Bold.ttf', font_size=60,
                 color=None, text_color=BLACK, moving=False):
        self.base_rect = pygame.Rect(x, y, width, height)
        self.rect = self.base_rect.copy()
        self.text = text
        self.icon = icon
        self.font = pygame.font.Font(font, font_size) if font else pygame.font.SysFont(None, font_size)
        self.color = color if color else (229, 193, 66, 128)
        self.text_color = text_color
        self.start_time = time.time()
        self.moving = moving

    def draw(self, surface):
        if self.moving:
            elapsed_time = time.time() - self.start_time
            scale_factor = 1 + 0.05 *math.sin(elapsed_time * 2* math.pi)
            
            new_width = int(self.base_rect.width * scale_factor)
            new_height = int(self.base_rect.height * scale_factor)
            self.rect.width = new_width
            self.rect.height = new_height
            self.rect.center = self.base_rect.center
        # Draw the rectangle with anti-aliasing
        pygame.draw.rect(surface, self.color, self.rect, border_radius=20)

        if self.icon:
            icon_surface = pygame.image.load(self.icon).convert_alpha()
            icon_surface = pygame.transform.scale(icon_surface, (self.rect.height, self.rect.height))
            icon_rect = icon_surface.get_rect(topleft=(self.rect.x, self.rect.y)) if self.text is not None else icon_surface.get_rect(center=self.rect.center)
            surface.blit(icon_surface, icon_rect)

            if self.text is not None:
                text_surface = self.font.render(self.text, True, self.text_color)
                text_rect = text_surface.get_rect(center=(self.rect.centerx + icon_surface.get_width()//2, self.rect.centery))
                surface.blit(text_surface, text_rect)
        else:
            if self.text is not None:
                text_surface = self.font.render(self.text, True, self.text_color)
                text_rect = text_surface.get_rect(center=self.rect.center)
                surface.blit(text_surface, text_rect)

    def remove(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect, border_radius=20)

    def is_correct(self, position, index):
        return True if index == position else False

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


def play_video_from_images(folder, music_file, screen, display_text, text=None, goon_button: Optional[Button] = None,
                           solution_button: Optional[Button] = None, solution1: Optional[Button] = None, solution2: Optional[Button] = None):
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
            
        font = pygame.font.Font('./Comfortaa/Comfortaa-Regular.ttf', 100)
        text_surface = font.render(text, True, WHITE)
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
                if (solution_button is not None and solution1 is not None 
                        and solution2 is not None
                        and solution_button.is_clicked(pygame.mouse.get_pos())):
                    solution_button.remove(screen)
                    solution1.draw(screen)
                    solution2.draw(screen)
                    pygame.display.update()
                if goon_button is not None and goon_button.is_clicked(pygame.mouse.get_pos()):
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
            screen.blit(frames[frame_index], (SCREEN_WIDTH * 3//4 - frame_w//2, SCREEN_HEIGHT//7 + 30))
        else:
            screen.blit(frames[frame_index], (SCREEN_WIDTH//2 - frame_w//2, SCREEN_HEIGHT - frame_h - 10))
        pygame.display.flip()
        clock.tick(30)

        frame_index += 1
        if frame_index >= len(frames):
            if folder == "./frames_dancing_avatar":
                    frame_index = 0
            else:
                running = False


def read(text):
    # Initialize the TTS engine
    
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')

    for voice in voices:
        if "italian" == voice.name:
            idx = voice.id
            print(idx)
        
    engine.setProperty('voice', idx)
    engine.setProperty('rate', 150)  # Set the speech rate (words per minute), default is 200
    #engine.setProperty('pitch', 0.5)
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


def mask_roundedcorner(picture, radius):
    # Create mask for rounded corners
    width, height = picture.get_size()
    mask_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    mask_surface.fill((0, 0, 0, 0))

    pygame.gfxdraw.filled_circle(mask_surface, radius, radius, radius, WHITE_4D)
    pygame.gfxdraw.filled_circle(mask_surface, width - radius - 1, radius, radius, WHITE_4D)
    pygame.gfxdraw.filled_circle(mask_surface, radius, height - radius - 1, radius, WHITE_4D)
    pygame.gfxdraw.filled_circle(mask_surface, width - radius - 1, height - radius - 1, radius, WHITE_4D)

    mask_surface.fill(WHITE_4D, rect=(radius, 0, width - 2 * radius, height))
    mask_surface.fill(WHITE_4D, rect=(0, radius, width, height - 2 * radius))

    result = pygame.Surface((width, height), pygame.SRCALPHA)
    result.blit(picture, (0, 0))
    result.blit(mask_surface, (0, 0), None, pygame.BLEND_RGBA_MIN)
    return result


def detect_face(cam):

    faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    minW = 30
    minH = 30

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
        print(faces)
        print(len(faces))
        return True if len(faces) != 0 else False

