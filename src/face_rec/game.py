import pygame
import os
import random
import cv2
import sys
import time
from pathlib import Path
import pandas as pd
from . import interface
import numpy as np
import pyttsx3

# Initialize the TTS engine
engine = pyttsx3.init()

def read(text):
    # Set the speech rate (words per minute), default is 200
    engine.setProperty('rate', 100)
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

def play_video(folder, music_file, screen, width, height, resize, display_text, goon_button):
   
    clock = pygame.time.Clock()

    SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_width(), screen.get_height()
    aspect_ratio = SCREEN_WIDTH // SCREEN_HEIGHT
    frames = []
    for filename in sorted(os.listdir(folder)):
        if filename.endswith(".png"):
            frame = pygame.image.load(os.path.join(folder, filename))
            if resize:
                frame = pygame.transform.scale(frame, (SCREEN_WIDTH // 3, (SCREEN_WIDTH // 3) // aspect_ratio))
            frames.append(frame)
   
    frame_index = 0
    running = True

    #Load the text if needed
    if display_text :
        font = pygame.font.SysFont(None, 100) 
        text = "Complimenti! Hai finito il Gioco!"
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
        sound.set_volume(4)
        pygame.mixer.music.play()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if goon_button.is_clicked(pygame.mouse.get_pos()):
                    pygame.mixer.music.fadeout(5000)
                    return
        if display_text:
            if text_width > SCREEN_WIDTH:
                screen.blit(text_surface1, ((SCREEN_WIDTH - text_surface1.get_width()) // 2, text_surface1.get_height()))
                screen.blit(text_surface2, ((SCREEN_WIDTH - text_surface2.get_width()) // 2, text_height + 20))
            else:
                screen.blit(text_surface, ((SCREEN_WIDTH - text_width) // 2, (SCREEN_HEIGHT // 2 - text_height)))
        
        if folder != "./frames_winning_avatar" :
            screen.blit(frames[frame_index], (width - frame.get_width(), height - frame.get_height()))
        else:
            screen.blit(frames[frame_index], (width, height))
        pygame.display.flip()
        clock.tick(60)

        frame_index += 1
        if frame_index >= len(frames):
            if folder == "./frames_winning_avatar" :
                break
            else:
                frame_index = 0
            
class Button:
    def __init__(self, x, y, width, height, color, text=''):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.text = text
        self.font = pygame.font.Font(None, 32)

    def draw(self, surface, writing_color):
        pygame.draw.rect(surface, self.color, self.rect)
        text_surface = self.font.render(self.text, True, writing_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def is_correct(self, position, index):
        return True if index == position else False
    
class MemoryGame:
    def __init__(self, input, model, images, music, bg_sound):
        pygame.init()

        self.images = images
        self.model = model
        self.input = input
        self.music = music
        self.bg_sound = bg_sound
        
        # Time variables
        self.hide_time = 1000
        self.finish_time = 2000
        self.startmusic_time = 30000
        self.playmusic_time = 20000
        self.fading_time = 2000
        self.max_time = 120

        # Game variables
        self.gameWidth = 840
        self.gameHeight = 640
        self.picSize = 200
        self.enlarged_size = self.gameWidth // 2
        self.map_sizex = 500
        self.map_sizey = 300
        self.gameColumns = 3
        self.gameRows = 2
        self.padding = 20
        self.leftMargin = (self.gameWidth - ((self.picSize + self.padding) * self.gameColumns)) // 2
        self.rightMargin = self.leftMargin
        self.topMargin = (self.gameHeight - ((self.picSize + self.padding) * self.gameRows)) // 2
        self.bottomMargin = self.topMargin
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.selection1 = None
        self.selection2 = None

        # Initialize the screen
        self.screen = pygame.display.set_mode((self.gameWidth, self.gameHeight))
        pygame.display.set_caption('Memory Game')
        
        # Load the background image
        self.bgImage = pygame.image.load('Background.png')
        self.bgImage = pygame.transform.scale(self.bgImage, (self.gameWidth, self.gameHeight))
        self.bgImageRect = self.bgImage.get_rect()

        # Create list of Memory Pictures
        self.memoryPictures = images
        selected_images = random.sample(self.memoryPictures, 3)  # Randomly select 3 unique images
        self.memoryPictures = selected_images * 2  # Duplicate selected images to create pairs
        random.shuffle(self.memoryPictures)  # Shuffle the list of images

        # Load each of the images into the python memory
        self.memPics = []
        self.memPicsRect = []
        self.hiddenImages = []
        for item in self.memoryPictures:
            picture = pygame.image.load(item)
            picture = pygame.transform.scale(picture, (self.picSize, self.picSize))
            self.memPics.append(picture)

        for i in range(self.gameRows):
            for j in range(self.gameColumns):
                rect_x = self.leftMargin + j * (self.picSize + self.padding)
                rect_y = self.topMargin + i * (self.picSize + self.padding)
                self.memPicsRect.append(pygame.Rect(rect_x, rect_y, self.picSize, self.picSize))
                self.hiddenImages.append(False)

        self.button_rect = pygame.Rect(20, 20, 100, 50)
        self.button_font = pygame.font.SysFont(None, 30)
        self.button_text = self.button_font.render("Resize", True, self.BLACK)

        self.repeat = Button(690, 540, 100, 50, (0, 0, 255), "Ripeti")

    def music_scene(self):
        # play the music
        # self.bg_sound.stop()
        fade_out_sound(self.bg_sound, self.fading_time)
        random_music_file = random.choice(self.music)

        # lateral message
        rect_width = 300
        rect_height = 100
        music_x = (self.gameWidth - rect_width) * 3 // 4 + 100
        music_y = (self.gameHeight - rect_height) // 3
        text_music = "Riconosci questa canzone?"
        complete = Button(music_x, music_y, rect_width, rect_height, (255, 255, 255), text_music)
        complete.draw(self.screen, (0, 0, 0))

        pygame.display.update()
        text_sound("music_text.mp3")

        # display video of avatar
        dancing_avatar = "frames_dancing_avatar"
        while self.enlarged_image and (time.time() < self.start_time + self.max_time):
            play_video(dancing_avatar, random_music_file, self.screen, self.gameWidth / 2, self.gameHeight, True, False,
                       self.goon_button)
            self.enlarged_image = False
            pygame.mixer.music.fadeout(self.fading_time)

        self.bg_sound.set_volume(1)
        # fade_in_sound(self.bg_sound, self.fading_time)
        self.bg_sound.play()

    def proverb_scene(self):
        # lateral message
        rect_width = 300
        rect_height = 100
        proverb_x = (self.gameWidth - rect_width) * 3 // 4 + 100
        complete_y = (self.gameHeight - rect_height) // 3
        text_complete = "Completa il proverbio"
        complete = Button(proverb_x, complete_y, rect_width, rect_height, (255, 255, 255), text_complete)
        complete.draw(self.screen, (0, 0, 0))
        # proverbio
        rect_width = 300
        rect_height = 100
        proverb_y = (self.gameHeight - rect_height) * 2 // 3
        words = self.image_path.split()[
                :len(self.image_path.split()) // 2 + 1]  # select half of the words of the proverb
        first_part = ' '.join(words) + ' ...'  # concatenate the words followed by ...
        self.proverb = Button(proverb_x, proverb_y, rect_width, rect_height, (230, 230, 230), first_part)
        self.proverb.draw(self.screen, (0, 0, 0))
        self.repeat.draw(self.screen, (255, 255, 255))

        pygame.display.update()
        text_sound("complete_proverb.mp3")
        read(first_part)

        speak = True
        while speak:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.repeat.is_clicked(pygame.mouse.get_pos()):
                        text_sound("complete_proverb.mp3")
                        read(first_part)
                        speak = False

    def multiple_choice(self):

        rect_width = 300
        rect_height = 100
        question_x = (self.gameWidth - rect_width) * 3 // 4 + 100
        question_y = (self.gameHeight - rect_height) // 8
        text_question = "Che cosa vedi?"
        self.question = Button(question_x, question_y, rect_width, rect_height, (255, 255, 255), text_question)
        self.question.draw(self.screen, (0, 0, 0))

        # list of the names of plants for options
        file_path = "plant_names.xlsx"

        df = pd.read_excel(file_path)
        plants_column = df['Plants']
        plant_names = [plant.capitalize() for plant in plants_column.tolist()]  # Convert the excel file to a list, first letter uppercase
        stemcapitalized = self.image_path.capitalize()  # Make sure that stem is uppercase
        # extract the right name from this list and 2 other random names
        plant_names.remove(stemcapitalized)
        random_names = random.sample(plant_names, 2)
        plant_names.append(stemcapitalized)
        # randomly arrange the 3 names extracted
        options = [stemcapitalized] + random_names
        random.shuffle(options)

        self.repeat.draw(self.screen, (255, 255, 255))

        self.option_buttons = []
        for i, option_text in enumerate(options):
            option_y = (self.gameHeight - rect_height) * (2*i + 3) // 8
            option_button = Button(question_x, option_y, rect_width, rect_height, (230, 230, 230), option_text)
            self.option_buttons.append(option_button)
            option_button.draw(self.screen, (0, 0, 0))

        right_index = options.index(stemcapitalized)
        correct_answer_given = False

        pygame.display.update()
        text_sound("question_text.mp3")
        read(options)

        speak = True
        while speak:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.repeat.is_clicked(pygame.mouse.get_pos()):
                        text_sound("question_text.mp3")
                        read(options)
                        speak = False

        # handle right/wrong answers
        while not correct_answer_given:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for i, option_button in enumerate(self.option_buttons):
                        if option_button.is_clicked(pygame.mouse.get_pos()):
                            if option_button.is_correct(i, right_index):
                                option_button.color = (0, 255, 0)
                                correct_answer_given = True
                            else:
                                option_button.color = (255, 0, 0)
                            option_button.draw(self.screen, (0, 0, 0))
                            pygame.display.update()


    def task_managing(self):

        self.screen.fill((255, 255, 255))
        # redraw "Avanti" button
        self.goon_button.draw(self.screen, (255, 255, 255))
        # draw the map picture
        map_pictures = os.listdir("image_tasks")
        for item in map_pictures:
            path = os.path.join("image_tasks", item)
            if os.path.isfile(path):
                picture = pygame.image.load(path)
                picture = pygame.transform.scale(picture, (self.map_sizex, self.map_sizey))
                pic_rect = picture.get_rect(center=(self.gameWidth // 2, self.gameHeight // 2))
                stempath = Path(path).stem
                words_path = stempath.split('_')
                for word in words_path:
                    if word == self.image_path:
                        self.screen.blit(picture, pic_rect)
        # explanation of task
        x = 0
        y1 = self.gameHeight // 6
        y2 = self.gameHeight * 3 // 4
        text1 = "Andate qui:"
        text2 = "Tocca, annusa e assaggia ... che cosa provi?"
        explanation1 = Button(x, y1, self.gameWidth, 50, (255, 255, 255), text1)
        explanation2 = Button(x, y2, self.gameWidth, 50, (255, 255, 255), text2)
        explanation1.draw(self.screen, (0, 0, 0))
        explanation2.draw(self.screen, (0, 0, 0))
        self.repeat.draw(self.screen, (255, 255, 255))
        pygame.display.update()
        text_sound("task_1")
        text_sound("task_2")
        text_sound("task_3")

        speak = True
        while speak:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.repeat.is_clicked(pygame.mouse.get_pos()):
                        text_sound("task_1")
                        text_sound("task_2")
                        text_sound("task_3")
                        speak = False


    def play(self):
        gameLoop = True
        button = Button(20, 20, 50, 25, (255, 0, 0), "X")
        self.goon_button = Button(50, 540, 100, 50, (0, 255, 0), "Avanti")
       
        while gameLoop:
            self.screen.blit(self.bgImage, self.bgImageRect)
            button.draw(self.screen, (255, 255, 255))

            self.enlarged_image = True

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    gameLoop = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for rect in self.memPicsRect:
                        if rect.collidepoint(event.pos):
                            index = self.memPicsRect.index(rect)
                            if not self.hiddenImages[index]:
                                if self.selection1 is not None:
                                    self.selection2 = index
                                    self.hiddenImages[self.selection2] = True
                                else:
                                    self.selection1 = index
                                    self.hiddenImages[self.selection1] = True
                    if button.is_clicked(pygame.mouse.get_pos()):
                        gameLoop = False

            for i in range(len(self.memoryPictures)):
                if self.hiddenImages[i]:
                    self.screen.blit(self.memPics[i], self.memPicsRect[i].topleft)
                else:
                    pygame.draw.rect(self.screen, self.WHITE, self.memPicsRect[i])
            pygame.display.flip()

            if self.selection1 is not None and self.selection2 is not None:
                if self.memoryPictures[self.selection1] == self.memoryPictures[self.selection2]:

                    pygame.time.wait(self.hide_time)
                    self.screen.fill(self.WHITE)
                    enlarged_picture = pygame.image.load(self.memoryPictures[self.selection1])
                    enlarged_picture = pygame.transform.scale(enlarged_picture, (self.enlarged_size, self.enlarged_size))
                    img_rect = enlarged_picture.get_rect(center=(self.gameWidth // 4 + 50, self.gameHeight // 2))
                    self.screen.blit(enlarged_picture, img_rect)
                    self.goon_button.draw(self.screen, (255, 255, 255))

                    self.start_time = time.time()

                    self.image_path = Path(self.memoryPictures[self.selection1]).stem
                    print(self.image_path)

                    # 3 options: music, proverb or multiple choice question
                    if self.image_path.split('_')[0] == "music":
                        self.music_scene()

                    elif len(self.image_path.split()) > 1:  # se il path ha più di una parola
                        self.proverb_scene()

                    else:
                        self.multiple_choice()
                        pygame.time.wait(self.hide_time)
                        self.task_managing()

                    while self.enlarged_image and (time.time() < self.start_time + self.max_time):
                        for event in pygame.event.get():
                            if event.type == pygame.MOUSEBUTTONDOWN:
                                if self.goon_button.is_clicked(pygame.mouse.get_pos()):
                                    self.enlarged_image = False


                else:
                    pygame.time.wait(self.hide_time)
                    self.hiddenImages[self.selection1] = False
                    self.hiddenImages[self.selection2] = False

                self.selection1, self.selection2 = None, None

            win = all(self.hiddenImages)
            if win:
                self.screen.fill((205,203, 192))
                winning_avatar = "./frames_winning_avatar"
                play_video(winning_avatar, "./avatar/win.mp4", self.screen, self.gameWidth // 4, self.gameHeight // 2, True, False, self.goon_button)
                self.show_win_message()
                self.bg_sound.set_volume(0.2)
                gameLoop = False

            pygame.display.update()

        pygame.quit()
        sys.exit()

    def show_win_message(self):
        #self.screen.blit(self.bgImage, self.bgImageRect)
        #pygame.display.flip()
        #pygame.time.wait(500)
        #rect_width = 500
        #rect_height = 150
        #rect_x = (self.gameWidth - rect_width) // 2
        #rect_y = (self.gameHeight - rect_height) // 2
        #pygame.draw.rect(self.screen, self.WHITE, (rect_x, rect_y, rect_width, rect_height))
        #font = pygame.font.SysFont(None, 40)
        #text = font.render("Ottimo! Hai completato il gioco!", True, self.BLACK)
        #text_rect = text.get_rect(center=(self.gameWidth // 2, self.gameHeight // 2))
        #self.screen.blit(text, text_rect)
        #pygame.display.update()
        pygame.time.wait(self.finish_time)
        self.bg_sound.set_volume(0)
        interface.main("./frames", self.model, self.images, self.music)

class FotoFlow:
    def __init__(self, input, model, images, music, bg_sound):
        pygame.init()

        self.images = images
        self.model = model
        self.input = input
        self.music = music
        self.bg_sound = bg_sound

        self.gameWidth = 840
        self.gameHeight = 640
        self.enlarged_size = self.gameWidth // 2
        # Initialize the screen
        self.screen = pygame.display.set_mode((self.gameWidth, self.gameHeight))
        pygame.display.set_caption('Foto Flow')
        self.screen.fill((255, 255, 255))

        self.flowing_images = random.sample(images, 5)
        self.flowPics = []
        for item in self.flowing_images:
            picture = pygame.image.load(item)
            picture = pygame.transform.scale(picture, (self.gameWidth, self.gameHeight))
            self.flowPics.append(picture)

    def play(self):
        flow_alpha = 255  # Initial alpha value for fading
        flow_scroll_x = 0
        flow_scroll_speed = 0.5

        running = True
        scrolling_enabled = True
        while running:
            self.screen.fill((255, 255, 255))
            for i, image in enumerate(self.flowPics):
                self.screen.blit(image, (flow_scroll_x + i*self.gameWidth, 0))

            fade_surface = pygame.Surface((self.gameWidth, self.gameHeight))
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(flow_alpha)
            self.screen.blit(fade_surface, (0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    for i, image in enumerate(self.flowPics):
                        image_x = flow_scroll_x + i * self.gameWidth
                        if image_x <= mouse_x <= image_x + image.get_width() and 0 <= mouse_y <= image.get_height():
                            self.screen.fill((255, 255, 255))
                            pygame.display.update()

            if scrolling_enabled:
                flow_scroll_x -= flow_scroll_speed
                if flow_scroll_x <= - (len(self.flowPics)-1) * self.gameWidth:
                    flow_scroll_x = 0

            if flow_alpha > 0:
                flow_alpha -= 2

            pygame.display.flip()

        pygame.quit()
        sys.exit()


def main(input, model, image_folder, music_folder, bg_sound, giochiamo):
    
    images = [os.path.join(image_folder, file) for file in os.listdir(image_folder) if file.endswith(".jpeg") or file.endswith(".png")] if isinstance(image_folder, str) else image_folder

    if isinstance(music_folder, str):
        music = [os.path.join(music_folder, file) for file in os.listdir(music_folder) if file.endswith(".wav") or file.endswith(".mp3")]
    else:
        music = music_folder

    if giochiamo:
        game = MemoryGame(input, model, images, music, bg_sound)
        game.play()
    else:
        game = FotoFlow(input, model, images, music, bg_sound)
        game.play()


if __name__ == "__main__":
    main()

