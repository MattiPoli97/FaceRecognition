import pygame
import os
import random

pygame.init()

# Time variables
hide_time = 1000
pic_display_time = 2000
finish_time = 2000

#  Variables for Game
gameWidth = 840
gameHeight = 640
picSize = 200
gameColumns = 3
gameRows = 2
padding = 20
leftMargin = (gameWidth - ((picSize + padding) * gameColumns)) // 2
rightMargin = leftMargin
topMargin = (gameHeight - ((picSize + padding) * gameRows)) // 2
bottomMargin = topMargin
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
selection1 = None
selection2 = None

# Loading the pygame screen.
screen = pygame.display.set_mode((gameWidth, gameHeight))
pygame.display.set_caption('Memory Game')
gameIcon = pygame.image.load('images/Apple.png')
pygame.display.set_icon(gameIcon)

# Load the BackGround image into Python
bgImage = pygame.image.load('Background.png')
bgImage = pygame.transform.scale(bgImage, (gameWidth, gameHeight))
bgImageRect = bgImage.get_rect()

# Create list of Memory Pictures
memoryPictures = []
for item in os.listdir('images/'):
    memoryPictures.append(item.split('.')[0])
selected_images = random.sample(memoryPictures, 3)  # Randomly select 3 unique images
memoryPictures = selected_images * 2  # Duplicate selected images to create pairs
random.shuffle(memoryPictures)  # Shuffle the list of images

# Load each of the images into the python memory
memPics = []
memPicsRect = []
hiddenImages = []
for item in memoryPictures:
    picture = pygame.image.load(f'images/{item}.png')
    picture = pygame.transform.scale(picture, (picSize, picSize))
    memPics.append(picture)

for i in range(gameRows):
    for j in range(gameColumns):
        rect_x = leftMargin + j * (picSize + padding)
        rect_y = topMargin + i * (picSize + padding)
        memPicsRect.append(pygame.Rect(rect_x, rect_y, picSize, picSize))
        hiddenImages.append(False)

gameLoop = True
while gameLoop:
    # Load background image
    screen.blit(bgImage, bgImageRect)

    # Input events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            gameLoop = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for rect in memPicsRect:
                if rect.collidepoint(event.pos):
                    index = memPicsRect.index(rect)
                    if not hiddenImages[index]:
                        if selection1 is not None:
                            selection2 = index
                            hiddenImages[selection2] = True
                        else:
                            selection1 = index
                            hiddenImages[selection1] = True

    for i in range(len(memoryPictures)):
        if hiddenImages[i]:
            screen.blit(memPics[i], memPicsRect[i].topleft)
        else:
            pygame.draw.rect(screen, WHITE, memPicsRect[i])
    pygame.display.flip()

    # When a correct pair is matched
    if selection1 is not None and selection2 is not None:
        if memoryPictures[selection1] == memoryPictures[selection2]:
            # Display the matched image full-screen
            pygame.time.wait(hide_time)
            screen.fill(WHITE)
            pic_rect = memPics[selection1].get_rect(center=(gameWidth // 2, gameHeight // 2))
            screen.blit(memPics[selection1], pic_rect)  # Display the image
            pygame.display.update()
            pygame.time.wait(pic_display_time)

        else:
            # If the pair doesn't match, hide the images after a brief delay
            pygame.time.wait(hide_time)
            hiddenImages[selection1] = False
            hiddenImages[selection2] = False

        # Reset the selection indices
        selection1, selection2 = None, None

    # Win condition
    win = all(hiddenImages)
    if win:
        # Display the congratulations message
        screen.blit(bgImage, bgImageRect)
        pygame.display.flip()
        pygame.time.wait(500)
        rect_width = 400
        rect_height = 200
        rect_x = (gameWidth - rect_width) // 2
        rect_y = (gameHeight - rect_height) // 2
        pygame.draw.rect(screen, WHITE, (rect_x, rect_y, rect_width, rect_height))
        font = pygame.font.SysFont(None, 40)
        text = font.render("Message", True, BLACK)
        text_rect = text.get_rect(center=(gameWidth // 2, gameHeight // 2))
        screen.blit(text, text_rect)
        pygame.display.update()
        pygame.time.wait(finish_time)
        gameLoop = False

    pygame.display.update()

pygame.quit()

