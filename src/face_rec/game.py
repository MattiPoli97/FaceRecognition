import pygame
import os
import random
import cv2
import sys
from . import face_recognition

class MemoryGame:
    def __init__(self, input, model, images, music):
        pygame.init()

        self.images = images
        self.model = model
        self.input = input
        self.music = music
        
        # Time variables
        self.hide_time = 1000
        self.pic_display_time = 2000
        self.finish_time = 2000
        self.startmusic_time = 30000
        self.playmusic_time = 20000
        self.fading_time = 2000

        # Game variables
        self.gameWidth = 840
        self.gameHeight = 640
        self.picSize = 200
        self.enlarged_size = 500
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
        #self.bgImage = cv2.imread('Background.png')
        #self.bgImage = cv2.resize(self.bgImage, (self.gameWidth, self.gameHeight))
        #self.bgImage = cv2.rotate(self.bgImage, cv2.ROTATE_90_COUNTERCLOCKWISE)
        #self.bgImage = cv2.cvtColor(self.bgImage, cv2.COLOR_BGR2RGB)
        #self.bgImageSurf = pygame.surfarray.make_surface(self.bgImage)
        #self.bgImageRect = self.bgImageSurf.get_rect()

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
            #picture = cv2.imread(item)
            #picture = cv2.resize(picture, (self.picSize, self.picSize))
            #picture = cv2.rotate(picture, cv2.ROTATE_90_COUNTERCLOCKWISE)
            #picture = cv2.cvtColor(picture, cv2.COLOR_BGR2RGB)
            #picture_surf = pygame.surfarray.make_surface(picture)
            #self.memPics.append(picture_surf)

        for i in range(self.gameRows):
            for j in range(self.gameColumns):
                rect_x = self.leftMargin + j * (self.picSize + self.padding)
                rect_y = self.topMargin + i * (self.picSize + self.padding)
                self.memPicsRect.append(pygame.Rect(rect_x, rect_y, self.picSize, self.picSize))
                self.hiddenImages.append(False)

        self.button_rect = pygame.Rect(20, 20, 100, 50)
        self.button_font = pygame.font.SysFont(None, 30)
        self.button_text = self.button_font.render("Resize", True, self.BLACK)
        
    def play(self):
        gameLoop = True
        while gameLoop:
            self.screen.blit(self.bgImage, self.bgImageRect)

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

            for i in range(len(self.memoryPictures)):
                if self.hiddenImages[i]:
                    self.screen.blit(self.memPics[i], self.memPicsRect[i].topleft)
                else:
                    pygame.draw.rect(self.screen, self.WHITE, self.memPicsRect[i])
            pygame.display.flip()

            if self.selection1 is not None and self.selection2 is not None:
                if self.memoryPictures[self.selection1] == self.memoryPictures[self.selection2]:

                    if self.memoryPictures[self.selection1] == "music":
                        random_music_file = random.choice(self.music)
                        pygame.mixer.music.load(random_music_file)
                        pygame.mixer.music.play(start=self.startmusic_time, fade_ms=self.fading_time)
                        pygame.time.wait(self.playmusic_time)
                        pygame.mixer.music.fadeout(self.fading_time)

                    pygame.time.wait(self.hide_time)
                    self.screen.fill(self.WHITE)
                    # Convert Pygame surface to numpy array
                    img_array = pygame.surfarray.array3d(self.memPics[self.selection1])
                    # Convert RGB to BGR (OpenCV uses BGR)
                    img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                    # Resize using OpenCV
                    scaled_img = cv2.resize(img_array, (self.enlarged_size, self.enlarged_size))
                    # Convert back to RGB
                    scaled_img = cv2.cvtColor(scaled_img, cv2.COLOR_BGR2RGB)
                    # Convert numpy array back to Pygame surface
                    scaled_surf = pygame.surfarray.make_surface(scaled_img)
                    img_rect = scaled_surf.get_rect(center=(self.gameWidth // 2, self.gameHeight // 2))
                    self.screen.blit(scaled_surf, img_rect)
                    pygame.display.update()
                    pygame.time.wait(self.pic_display_time)

                else:
                    pygame.time.wait(self.hide_time)
                    self.hiddenImages[self.selection1] = False
                    self.hiddenImages[self.selection2] = False

                self.selection1, self.selection2 = None, None

            win = all(self.hiddenImages)
            if win:
                self.show_win_message()
                gameLoop = False

            pygame.display.update()

        pygame.quit()

    def show_win_message(self):
        self.screen.blit(self.bgImage, self.bgImageRect)
        pygame.display.flip()
        pygame.time.wait(500)
        rect_width = 400
        rect_height = 200
        rect_x = (self.gameWidth - rect_width) // 2
        rect_y = (self.gameHeight - rect_height) // 2
        pygame.draw.rect(self.screen, self.WHITE, (rect_x, rect_y, rect_width, rect_height))
        font = pygame.font.SysFont(None, 40)
        text = font.render("Congrats! You won!", True, self.BLACK)
        text_rect = text.get_rect(center=(self.gameWidth // 2, self.gameHeight // 2))
        self.screen.blit(text, text_rect)
        pygame.display.update()
        pygame.time.wait(self.finish_time)
        face_recognition.main(self.input, self.model, self.images)

def main(input, model, image_folder, music_folder):
    if isinstance(image_folder, str):
        images = [os.path.join(image_folder, file) for file in os.listdir(image_folder) if file.endswith(".jpeg") or file.endswith(".png")]
    else:
        images = image_folder

    if isinstance(music_folder, str):
        music = [os.path.join(music_folder, file) for file in os.listdir(music_folder) if file.endswith(".wav") or file.endswith(".mp3")]
    else:
        music = music_folder

    game = MemoryGame(input, model, images, music)
    game.play()

if __name__ == "__main__":
    main()

