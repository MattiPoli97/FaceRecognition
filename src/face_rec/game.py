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

def display_video(video_capture, screen, SCREEN_WIDTH, SCREEN_HEIGHT, pos_x, pos_y):
    # Inizializza il video capture
    video_capture = cv2.VideoCapture(video_capture)

    while True:
        # Leggi il frame successivo
        ret, frame = video_capture.read()

        # Verifica se il frame è stato letto correttamente
        if ret:
            # Converte i colori del frame da BGR a RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            frame = cv2.resize(frame, (int(SCREEN_WIDTH / 2), int(SCREEN_HEIGHT / 2)))
            
            frame = pygame.image.frombuffer(frame.tostring(), frame.shape[1::-1], "RGB")
            screen.blit(frame, (pos_x, pos_y))

            pygame.display.flip()
            pygame.time.delay(int(1000 / 30))  # 30 FPS (tempo in millisecondi)

        else:
            video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
            break

def play_video(folder, music_file, screen, width, height, resize, display_text, goon_button):
   
    clock = pygame.time.Clock()
    SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_width(), screen.get_height()
    frames = []
    for filename in sorted(os.listdir(folder)):
        if filename.endswith(".png"):
            frame = pygame.image.load(os.path.join(folder, filename)).convert_alpha()  # Load image with alpha channel
            if resize:
                frame = pygame.transform.scale(frame, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            frames.append(frame)
   
    frame_index = 0
    running = True

    if music_file:
        pygame.mixer.music.load(music_file)
        pygame.mixer.music.play(start=25, fade_ms=5000)

    #Load the text if needed
    if display_text :
        font = pygame.font.SysFont(None, 100) 
        text = "Eccoci nel GIARDINO PARLANTE!"
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
        
        screen.blit(frames[frame_index], (width, height - frame.get_rect().size[1]))
        pygame.display.flip()
        clock.tick(60)

        frame_index += 1
        if frame_index >= len(frames):
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
        self.pic_display_time = 2000
        self.finish_time = 2000
        self.startmusic_time = 30000
        self.playmusic_time = 20000
        self.fading_time = 5000
        self.max_time = 120

        # Game variables
        self.gameWidth = 840
        self.gameHeight = 640
        self.picSize = 200
        self.enlarged_size = self.gameWidth // 2
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
        #for item in images:
        #    self.memoryPictures.append(item.split('.')[0])
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

    def multiple_choice(self, stempath):

        rect_width = 300
        rect_height = 100
        question_x = (self.gameWidth - rect_width) * 3 // 4 + 100
        question_y = (self.gameHeight - rect_height) // 8
        question = Button(question_x, question_y, rect_width, rect_height, (255, 255, 255), "Che cosa vedi?")
        question.draw(self.screen, (0, 0, 0))

        # list of the names of plants for options
        file_path = "plant_names.xlsx"

        df = pd.read_excel(file_path)
        plants_column = df['Plants']
        plant_names = [plant.capitalize() for plant in plants_column.tolist()]  # Convert the excel file to a list, first letter uppercase
        stemcapitalized = stempath.capitalize()  # Make sure that stem is uppercase
        # extract the right name from this list and 2 other random names
        plant_names.remove(stemcapitalized)
        random_names = random.sample(plant_names, 2)
        plant_names.append(stemcapitalized)
        # randomly arrange the 3 names extracted
        options = [stemcapitalized] + random_names
        random.shuffle(options)

        option_buttons = []
        for i, option_text in enumerate(options):
            option_y = (self.gameHeight - rect_height) * (2*i + 3) // 8
            option_button = Button(question_x, option_y, rect_width, rect_height, (230, 230, 230), option_text)
            option_buttons.append(option_button)
            option_button.draw(self.screen, (0, 0, 0))

        right_index = options.index(stemcapitalized)
        correct_answer_given = False

        pygame.display.update()

        # handle right/wrong answers
        while not correct_answer_given:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for i, option_button in enumerate(option_buttons):
                        if option_button.is_clicked(pygame.mouse.get_pos()):
                            if option_button.is_correct(i, right_index):
                                option_button.color = (0, 255, 0)
                                correct_answer_given = True
                            else:
                                option_button.color = (255, 0, 0)
                            option_button.draw(self.screen, (0, 0, 0))
                            pygame.display.update()

    def play(self):
        gameLoop = True
        button = Button(20, 20, 50, 25, (255, 0, 0), "X")
        goon_button = Button(50, 540, 100, 50, (0, 255, 0), "Avanti")
       
        while gameLoop:
            self.screen.blit(self.bgImage, self.bgImageRect)
            button.draw(self.screen, (255, 255, 255))

            enlarged_image = True

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
                    goon_button.draw(self.screen, (255, 255, 255))
                    pygame.display.update()

                    start_time = time.time()

                    image_path = Path(self.memoryPictures[self.selection1]).stem
                    print(image_path)

                    # 3 options: music, proverb or multiple choice question
                    if image_path == "music":
                        # play the music
                        self.bg_sound.stop()
                        random_music_file = random.choice(self.music)
                        
                        # lateral message
                        rect_width = 300
                        rect_height = 100
                        proverb_x = (self.gameWidth - rect_width) * 3 // 4 + 100
                        complete_y = (self.gameHeight - rect_height) // 3
                        complete = Button(proverb_x, complete_y, rect_width, rect_height, (255, 255, 255),
                                          "Riconosci questa canzone?")
                        complete.draw(self.screen, (0, 0, 0))

                        pygame.display.update()
                        # display video of avatar
                        dancing_avatar = "/Users/mattiamagro/Desktop/FaceRecognition/frames_dancing_avatar"
                        while enlarged_image and (time.time() < start_time + self.max_time):
                            play_video(dancing_avatar, random_music_file, self.screen, self.gameWidth/2, self.gameHeight, True, False, goon_button)
                            enlarged_image = False      
                            self.bg_sound.play()

                        pygame.mixer.music.fadeout(self.fading_time)
                        self.bg_sound.play()

                    elif len(image_path.split()) > 1:  # se il path ha più di una parola

                        # lateral message
                        rect_width = 300
                        rect_height = 100
                        proverb_x = (self.gameWidth - rect_width) * 3 // 4 + 100
                        complete_y = (self.gameHeight - rect_height) // 3
                        complete = Button(proverb_x, complete_y, rect_width, rect_height, (255, 255, 255),
                                          "Completa il proverbio")
                        complete.draw(self.screen, (0, 0, 0))
                        # proverbio
                        rect_width = 300
                        rect_height = 100
                        proverb_y = (self.gameHeight - rect_height) * 2 // 3
                        words = image_path.split()[:len(image_path.split()) // 2 + 1]  # select half of the words of the proverb
                        first_part = ' '.join(words) + ' ...'  # concatenate the words followed by ...
                        question = Button(proverb_x, proverb_y, rect_width, rect_height, (230, 230, 230), first_part)
                        question.draw(self.screen, (0, 0, 0))

                        pygame.display.update()

                    else:
                        self.multiple_choice(image_path)

                    while enlarged_image and (time.time() < start_time + self.max_time):
                        for event in pygame.event.get():
                            if event.type == pygame.MOUSEBUTTONDOWN:
                                if goon_button.is_clicked(pygame.mouse.get_pos()):
                                    enlarged_image = False


                else:
                    pygame.time.wait(self.hide_time)
                    self.hiddenImages[self.selection1] = False
                    self.hiddenImages[self.selection2] = False

                self.selection1, self.selection2 = None, None

            win = all(self.hiddenImages)
            if win:
                self.screen.fill((205,203, 192))
                video_clip = "./avatar/winning_avatar.mp4"
                display_video(video_clip, self.screen, self.gameWidth, self.gameHeight, self.gameWidth / 4, self.gameHeight / 4) 
                self.show_win_message()
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
        interface.main("./frames", self.model, self.images, self.music)

def main(input, model, image_folder, music_folder, bg_sound):
    
    images = [os.path.join(image_folder, file) for file in os.listdir(image_folder) if file.endswith(".jpeg") or file.endswith(".png")] if isinstance(image_folder, str) else image_folder

    if isinstance(music_folder, str):
        music = [os.path.join(music_folder, file) for file in os.listdir(music_folder) if file.endswith(".wav") or file.endswith(".mp3")]
    else:
        music = music_folder

    game = MemoryGame(input, model, images, music, bg_sound)
    game.play()


if __name__ == "__main__":
    main()

