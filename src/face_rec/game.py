import pygame
import os
import random
import sys
from . import face_recognition

class MemoryGame:
    def __init__(self, input, model, images):
        pygame.init()

        self.images = images
        self.model = model
        self.input = input
        
        # Time variables
        self.hide_time = 1000
        self.pic_display_time = 2000
        self.finish_time = 2000

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
                    pygame.time.wait(self.hide_time)
                    self.screen.fill(self.WHITE)
                    scaled_img = pygame.transform.scale(self.memPics[self.selection1], (self.enlarged_size, self.enlarged_size))
                    img_rect = scaled_img.get_rect(center=(self.gameWidth // 2, self.gameHeight // 2))
                    self.screen.blit(scaled_img, img_rect)
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

def main(input, model, image_folder) :
    if isinstance(image_folder, str)  :
        images = [os.path.join(image_folder, file) for file in os.listdir(image_folder) if file.endswith(".jpeg") or file.endswith(".png")]
    else :
        images =image_folder
    game = MemoryGame(input, model, images)
    game.play()

if __name__ == "__main__":
    main()
   

    
