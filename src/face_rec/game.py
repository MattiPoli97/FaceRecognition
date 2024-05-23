import pygame
import os
import random
import sys
import time
from pathlib import Path
import pandas as pd
from . import interface
from . import utils

class GameBase:
    def __init__(self, input, model, images, music, bg_sound):
        pygame.init()

        self.input = input
        self.model = model
        self.images = images
        self.music = music
        self.bg_sound = bg_sound

        self.setup_screen()

        # Time variables
        self.hide_time = 1000
        self.finish_time = 2000
        self.startmusic_time = 30000
        self.playmusic_time = 20000
        self.fading_time = 2000
        self.max_time = 120

        # Size variables
        self.enlarged_size = self.gameWidth * 3 // 7
        self.map_sizex = self.gameWidth // 2
        self.map_sizey = self.gameHeight // 2

        # Buttons
        self.bottom_width = self.gameWidth // 5.5
        self.bottom_height = self.gameHeight // 11
        self.y_bottom = self.gameHeight * 11//12 - 10
        self.x_goon = self.gameWidth//4 - self.bottom_width - 10
        self.x_repeat = self.gameWidth//4 + 10
        self.top_width = self.gameWidth // 16
        self.top_height = self.gameWidth // 16
        self.y_top = self.gameWidth // 45
        self.x_home = self.gameWidth // 45
        self.x_exit = self.gameWidth - self.gameWidth // 45 - self.top_width
        self.sol_width = self.gameWidth // 4
        self.sol_height = self.gameHeight // 11

        self.goon_button = utils.Button(self.x_goon, self.y_bottom,
                                        self.bottom_width, self.bottom_height,
                                        color=utils.Emerald_green, text="Avanti", icon="./icons/icon_avanti.png")
        self.repeat = utils.Button(self.x_repeat, self.y_bottom,
                                   self.bottom_width, self.bottom_height,
                                   color=utils.Sky_blue, text="Ripeti", icon="./icons/icon_repeat.png")
        self.exit_button = utils.Button(self.x_exit, self.y_top, self.top_width, self.top_height,
                                        color=utils.RED, text="X", text_color=utils.WHITE)
        self.home_button = utils.Button(self.x_home, self.y_top, self.top_width, self.top_height,
                                        icon="./icons/icon_home.png")

    def setup_screen(self):
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            pygame.display.set_caption('Memory Game' if isinstance(self, MemoryGame) else 'Foto Flow')
            self.gameWidth, self.gameHeight = self.screen.get_width(), self.screen.get_height()

    def enlarge_image(self, picture_path, size):
        self.screen.fill(utils.WHITE)
        enlarged_picture = pygame.image.load(picture_path).convert_alpha()
        enlarged_picture = pygame.transform.scale(enlarged_picture, size)
        enlarged_picture = utils.mask_roundedcorner(enlarged_picture, radius=20)
        img_rect = enlarged_picture.get_rect(center=(self.gameWidth // 4, self.gameHeight // 2))
        self.screen.blit(enlarged_picture, img_rect)
        self.goon_button.draw(self.screen)
        self.repeat.draw(self.screen)

    def music_scene(self, start_time):
        # play the music
        # self.bg_sound.stop()
        utils.fade_out_sound(self.bg_sound, self.fading_time)
        random_music_file = random.choice(self.music)

        self.repeat.remove(self.screen)

        rect_width = self.gameWidth // 3
        rect_height = self.gameHeight // 6
        music_x = self.gameWidth * 3//4 - rect_width//2
        music_y = self.gameHeight // 7 - rect_height//2
        y_solb = self.gameHeight - self.sol_height - 10
        y_sol = self.gameHeight - rect_height

        text_music = "Riconosci la canzone?"
        music_path = Path(random_music_file).stem

        complete = utils.Button(music_x, music_y, rect_width, rect_height, text=text_music,
                                color=utils.WHITE, hover_color=utils.WHITE)
        solution_b = utils.Button(music_x, y_solb, self.sol_width, self.sol_height,
                                  color=utils.YELLOW, text="Soluzione", icon="./icons/icon_help.png")
        solution = utils.Button(music_x, y_sol, rect_width, rect_height, text=music_path,
                                color=utils.WHITE, hover_color=utils.WHITE, font_size=50)

        complete.draw(self.screen)
        solution_b.draw(self.screen)

        pygame.display.update()
        utils.text_sound("music_text.mp3")

        while self.enlarged_image and (time.time() < start_time + self.max_time):

            utils.play_video_from_images("./frames_dancing_avatar", random_music_file, self.screen,
                                         False, goon_button=self.goon_button, solution_button=solution_b, solution=solution)
            self.enlarged_image = False
            pygame.mixer.music.fadeout(self.fading_time)

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.goon_button.is_clicked(pygame.mouse.get_pos()):
                        self.enlarged_image = False

        self.bg_sound.set_volume(1)
        # fade_in_sound(self.bg_sound, self.fading_time)
        self.bg_sound.play()

    def proverb_scene(self, image_path, start_time):

        utils.fade_out_sound(self.bg_sound, self.fading_time)

        rect_width = self.gameWidth // 2.2
        rect_height = self.gameHeight // 6
        x_right = self.gameWidth * 3//4 - rect_width//2
        y_1 = (self.gameHeight - rect_height) // 3
        y_2 = (self.gameHeight - rect_height) * 2//3
        y_3 = self.gameHeight - rect_height
        y_4 = self.gameHeight - rect_height -20

        text_complete = "Completa il proverbio"
        first_words = image_path.split()[:len(image_path.split()) // 2 + 1]  # select half of the words of the proverb
        first_part = ' '.join(first_words) + ' ...'  # concatenate the words followed by ...
        last_words = image_path.split()[len(image_path.split()) // 2 + 1:]
        last_part = ' '.join(last_words)

        complete = utils.Button(x_right, y_1, rect_width, rect_height, text=text_complete,
                                color=utils.WHITE, hover_color=utils.WHITE)
        proverb = utils.Button(x_right, y_2, rect_width, rect_height, text=first_part,
                                    color=utils.GREY, hover_color=utils.GREY)
        solution_b = utils.Button(x_right, y_3, self.sol_width, self.sol_height,
                                  color=utils.YELLOW, text="Soluzione", icon="./icons/icon_help.png")
        solution = utils.Button(x_right, y_4, rect_width, rect_height,
                                color=utils.GREY, text=last_part, hover_color=utils.GREY)


        complete.draw(self.screen)
        proverb.draw(self.screen)
        solution_b.draw(self.screen)

        pygame.display.update()
        utils.text_sound("complete_proverb.mp3")
        utils.read(first_part)

        while self.enlarged_image and (time.time() < start_time + self.max_time):

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.repeat.is_clicked(pygame.mouse.get_pos()):
                        utils.text_sound("complete_proverb.mp3")
                        utils.read(first_part)
                    if solution_b.is_clicked(pygame.mouse.get_pos()):
                        solution_b.remove(self.screen)
                        solution.draw(self.screen)
                        pygame.display.update()
                    if self.goon_button.is_clicked(pygame.mouse.get_pos()):
                        self.enlarged_image = False

        self.bg_sound.set_volume(1)
        self.bg_sound.play()

    def multiple_choice(self, image_path, start_time):

        self.goon_button.remove(self.screen)
        utils.fade_out_sound(self.bg_sound, self.fading_time)
        rect_width = self.gameWidth // 3
        rect_height = self.gameHeight // 6
        question_x = (self.gameWidth - rect_width) * 3 // 4 + self.gameHeight // 6
        question_y = (self.gameHeight - rect_height) // 8
        text_question = "Che cosa vedi?"
        self.question = utils.Button(question_x, question_y, rect_width, rect_height,
                                     color=utils.WHITE, text=text_question, hover_color=utils.WHITE)
        self.question.draw(self.screen)

        # list of the names of plants for options
        file_path = "plant_names.xlsx"

        df = pd.read_excel(file_path)
        plants_column = df['Plants']
        plant_names = [plant.capitalize() for plant in plants_column.tolist()]  # Convert the excel file to a list
        stemcapitalized = image_path.capitalize()  # Make sure that stem is uppercase
        # extract the right name from this list and 2 other random names
        plant_names.remove(stemcapitalized)
        random_names = random.sample(plant_names, 2)
        plant_names.append(stemcapitalized)
        # randomly arrange the 3 names extracted
        options = [stemcapitalized] + random_names
        random.shuffle(options)

        self.option_buttons = []
        for i, option_text in enumerate(options):
            option_y = (self.gameHeight - rect_height) * (2*i + 3) // 8
            option_button = utils.Button(question_x, option_y, rect_width, rect_height,
                                         color=utils.GREY, text=option_text)
            self.option_buttons.append(option_button)
            option_button.draw(self.screen)

        right_index = options.index(stemcapitalized)
        correct_answer_given = False

        pygame.display.update()
        utils.text_sound("question_text.mp3")
        utils.read(options)

        # handle right/wrong answers
        while not correct_answer_given and (time.time() < start_time + self.max_time):

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.repeat.is_clicked(pygame.mouse.get_pos()):
                        utils.text_sound("question_text.mp3")
                        utils.read(options)
                    for i, option_button in enumerate(self.option_buttons):
                        if option_button.is_clicked(pygame.mouse.get_pos()):
                            if option_button.is_correct(i, right_index):
                                option_button.color = utils.Emerald_green
                                correct_answer_given = True
                            else:
                                option_button.color = utils.Soft_red
                            option_button.draw(self.screen)
                            pygame.display.update()

    def task_managing(self, image_path, start_time, size):

        self.screen.fill(utils.WHITE)
        # redraw buttons
        self.goon_button.draw(self.screen)
        self.repeat.draw(self.screen)
        # draw the map picture
        map_pictures = os.listdir("image_tasks")
        for item in map_pictures:
            path = os.path.join("image_tasks", item)
            if os.path.isfile(path):
                picture = pygame.image.load(path)
                picture = pygame.transform.scale(picture, size)
                pic_rect = picture.get_rect(center=(self.gameWidth // 2, self.gameHeight // 2))
                stempath = Path(path).stem
                words_path = stempath.split('_')
                for word in words_path:
                    if word == image_path:
                        self.screen.blit(picture, pic_rect)
        # explanation of task
        x = 0
        y1 = self.gameHeight // 6
        y2 = self.gameHeight * 3 // 4
        text1 = "Andate qui:"
        text2 = "Tocca, annusa e assaggia ... che cosa provi?"
        explanation1 = utils.Button(x, y1, self.gameWidth, 50, color=utils.WHITE, text=text1)
        explanation2 = utils.Button(x, y2, self.gameWidth, 50, color=utils.WHITE, text=text2)
        explanation1.draw(self.screen)
        explanation2.draw(self.screen)
        pygame.display.update()
        utils.text_sound("task_1.mp3")
        utils.text_sound("task_2.mp3")
        utils.text_sound("task_3.mp3")

        while self.enlarged_image and (time.time() < start_time + self.max_time):

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.repeat.is_clicked(pygame.mouse.get_pos()):
                        utils.text_sound("task_1.mp3")
                        utils.text_sound("task_2.mp3")
                        utils.text_sound("task_3.mp3")
                    if self.goon_button.is_clicked(pygame.mouse.get_pos()):
                        self.enlarged_image = False

class MemoryGame(GameBase):

    def __init__(self, input, model, images, music, bg_sound):
        super().__init__(input, model, images, music, bg_sound)

        # Game variables
        self.picSize = self.gameWidth // 4
        self.gameColumns = 3
        self.gameRows = 2
        padding = self.gameWidth // 40
        self.leftMargin = (self.gameWidth - (self.picSize * self.gameColumns + padding * (self.gameColumns - 1))) // 2
        self.topMargin = (self.gameHeight - (self.picSize * self.gameRows + padding * (self.gameRows - 1))) // 2

        self.selection1 = None
        self.selection2 = None
        
        # Load the background image
        self.bgImage = pygame.image.load('Background.png')
        scaled_bgW, scaled_gbH = utils.mantain_aspectratio(self.bgImage, self.gameWidth, self.gameHeight)
        self.bgImage = pygame.transform.scale(self.bgImage, (scaled_bgW, scaled_gbH))
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
            picture = pygame.image.load(item).convert_alpha()
            picture = pygame.transform.scale(picture, (self.picSize, self.picSize))
            picture = utils.mask_roundedcorner(picture, radius=20)
            self.memPics.append(picture)

        for i in range(self.gameRows):
            for j in range(self.gameColumns):
                rect_x = self.leftMargin + j * (self.picSize + padding)
                rect_y = self.topMargin + i * (self.picSize + padding)
                self.memPicsRect.append(pygame.Rect(rect_x, rect_y, self.picSize, self.picSize))
                self.hiddenImages.append(False)

        self.button_rect = pygame.Rect(20, 20, 100, 50)
        self.button_font = pygame.font.SysFont(None, 30)
        self.button_text = self.button_font.render("Resize", True, utils.BLACK)

    def play(self):
        gameLoop = True

        while gameLoop:
            self.screen.fill(utils.Soft_Green)
            self.exit_button.draw(self.screen)
            self.home_button.draw(self.screen)

            self.enlarged_image = True

            for event in pygame.event.get():
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
                    if self.exit_button.is_clicked(pygame.mouse.get_pos()):
                        gameLoop = False
                    if self.home_button.is_clicked(pygame.mouse.get_pos()):
                        self.bg_sound.set_volume(0)
                        self.bg_sound.stop()
                        interface.main("./frames", self.model, self.images, self.music)

            for i in range(len(self.memoryPictures)):
                if self.hiddenImages[i]:
                    self.screen.blit(self.memPics[i], self.memPicsRect[i].topleft)
                else:
                    pygame.draw.rect(self.screen, utils.WHITE, self.memPicsRect[i], border_radius=20)
            pygame.display.flip()

            if self.selection1 is not None and self.selection2 is not None:
                if self.memoryPictures[self.selection1] == self.memoryPictures[self.selection2]:

                    pygame.time.wait(self.hide_time)
                    super().enlarge_image(self.memoryPictures[self.selection1], (self.enlarged_size, self.enlarged_size))

                    start_time = time.time()

                    image_path = Path(self.memoryPictures[self.selection1]).stem
                    print(image_path)

                    # 3 options: music, proverb or multiple choice question
                    if image_path.split('_')[0] == "music":
                        super().music_scene(start_time)

                    elif len(image_path.split()) > 1:  # se il path ha più di una parola
                        super().proverb_scene(image_path, start_time)

                    else:
                        super().multiple_choice(image_path, start_time)
                        pygame.time.wait(self.hide_time)
                        super().task_managing(image_path, start_time, (self.map_sizex, self.map_sizey))

                else:
                    pygame.time.wait(self.hide_time)
                    self.hiddenImages[self.selection1] = False
                    self.hiddenImages[self.selection2] = False

                self.selection1, self.selection2 = None, None

            win = all(self.hiddenImages)
            if win:
                self.screen.fill(utils.BLACK)
                utils.play_video_from_images("./frames_winning_avatar", "./avatar/win.mp4", self.screen,
                                             True, "Complimenti! Alla prossima!")
                self.finish_and_restart()
                self.bg_sound.set_volume(0.2)
                gameLoop = False

            pygame.display.update()

        pygame.quit()
        sys.exit()

    def finish_and_restart(self):

        pygame.time.wait(self.finish_time)
        self.bg_sound.set_volume(0)
        interface.main("./frames", self.model, self.images, self.music)

class FotoFlow(GameBase):
    def __init__(self, input, model, images, music, bg_sound):
        super().__init__(input, model, images, music, bg_sound)

        self.flowing_images = random.sample(images, 5)
        self.flowPics = []
        for item in self.flowing_images:
            picture = pygame.image.load(item)
            self.scaled_width, self.scaled_height = utils.mantain_aspectratio(picture, self.gameWidth, self.gameHeight)
            picture = pygame.transform.scale(picture, (self.scaled_width, self.scaled_height))

            self.flowPics.append(picture)

    def play(self):
        flow_alpha = 255  # Initial alpha value for fading
        flow_scroll_x = 0
        flow_scroll_speed = self.gameWidth//250

        running = True
        scrolling_enabled = True
        while running:
            self.screen.fill(utils.WHITE)
            total_width = len(self.flowPics) * self.scaled_width
            for i, image in enumerate(self.flowPics):
                x_pos = (flow_scroll_x + i * self.scaled_width) % total_width
                self.screen.blit(image, (x_pos, 0))
                if x_pos > self.gameWidth - self.scaled_width:
                    self.screen.blit(image, (x_pos - total_width, 0))

            self.exit_button.draw(self.screen)
            self.home_button.draw(self.screen)

            fade_surface = pygame.Surface((self.gameWidth, self.gameHeight))
            fade_surface.fill(utils.BLACK)
            fade_surface.set_alpha(flow_alpha)
            self.screen.blit(fade_surface, (0, 0))

            for event in pygame.event.get():

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()

                    if self.exit_button.is_clicked(pygame.mouse.get_pos()):
                        running = False
                        break
                    if self.home_button.is_clicked(pygame.mouse.get_pos()):
                        interface.main("./frames", self.model, self.images, self.music)
                        break

                    for i, image in enumerate(self.flowPics):
                        image_path = Path(self.flowing_images[i]).stem
                        image_x = flow_scroll_x + i * self.scaled_width
                        if image_x <= mouse_x <= image_x + image.get_width() and 0 <= mouse_y <= image.get_height():
                            start_time = time.time()
                            self.enlarged_image = True
                            super().enlarge_image(self.flowing_images[i], (self.enlarged_size, self.enlarged_size))

                            if image_path.split('_')[0] == "music":
                                super().music_scene(start_time)

                            elif len(image_path.split()) > 1:  # se il path ha più di una parola
                                super().proverb_scene(image_path, start_time)

                            else:
                                super().multiple_choice(image_path, start_time)
                                pygame.time.wait(self.hide_time)
                                super().task_managing(image_path, start_time, (self.map_sizex, self.map_sizey))

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

