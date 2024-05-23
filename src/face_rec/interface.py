import pygame
import random
from . import game, utils

class Interface:
    def __init__(self, avatar, model, images, music):
        pygame.init()

        self.avatar = avatar
        self.model = model
        self.images = images
        self.music = music

        self.bg_sound = pygame.mixer.Sound('background_music.wav')
        self.bg_sound.play(loops=-1)
    
        # Color definition
        Soft_Blue = (191, 219, 255)
        Soft_Pink = (255, 204, 229)
        Soft_Green = (204, 255, 204)
        Soft_Yellow = (255, 255, 204)
        Soft_Lavender = (230, 230, 255)
        bg_color_list = [Soft_Blue, Soft_Yellow, Soft_Green, Soft_Lavender, Soft_Pink]
        self.random_bg_color = random.choice(bg_color_list)

        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = self.screen.get_width(), self.screen.get_height()
        pygame.display.set_caption("MEMORY GAME")

        self.leaves = []
        for _ in range(20):
            x = random.randint(self.SCREEN_WIDTH // 4, 3 * self.SCREEN_WIDTH // 4)
            y = random.randint(self.SCREEN_HEIGHT // 4, 3 * self.SCREEN_HEIGHT // 4)
            radius = random.randint(self.SCREEN_WIDTH//15, self.SCREEN_WIDTH//6)
            ball = utils.Leaf(x, y, radius, self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
            self.leaves.append(ball)

        # Button parameters
        self.top_width = self.SCREEN_WIDTH // 16
        self.top_height = self.SCREEN_WIDTH // 16
        self.y_top = self.SCREEN_WIDTH // 45
        self.x_home = self.SCREEN_WIDTH // 45
        self.x_exit = self.SCREEN_WIDTH - self.SCREEN_WIDTH // 45 - self.top_width

        self.button_width = self.SCREEN_WIDTH // 2.5
        self.button_height = self.SCREEN_HEIGHT // 6
        self.button_x_l = self.SCREEN_WIDTH//4 - self.button_width//2
        self.button_x_r = self.SCREEN_WIDTH * 3//4 - self.button_width//2
        self.button_y = self.SCREEN_HEIGHT // 2

        title = "Cosa vuoi fare oggi?"
        self.title_width = self.SCREEN_WIDTH//2
        self.x_title = self.SCREEN_WIDTH//2 - self.title_width//2

        self.button_l = utils.Button(self.button_x_l, self.button_y, self.button_width, self.button_height,
                                     text="Giochiamo!", icon="./icons/icon_game.png", font_size=70)
        self.button_r = utils.Button(self.button_x_r, self.button_y, self.button_width, self.button_height,
                                     text="Ricordiamo!", icon="./icons/icon_remember.png", font_size=70)

        self.exit_button = utils.Button(self.x_exit, self.y_top, self.top_width, self.top_height,
                                        color=utils.RED, text="X", text_color=utils.WHITE)
        self.home_button = utils.Button(self.x_home, self.y_top, self.top_width, self.top_height,
                                        icon="./icons/icon_home.png")

        self.button_title = utils.Button(self.x_title, self.y_top, self.title_width, self.button_height,
                                         color=utils.WHITE, text=title)

    def run(self):
        running = True

        while running:
            self.screen.fill(self.random_bg_color)

            for ball in self.leaves:
                ball.move()
                ball.draw(self.screen)

            pygame.display.update()

            # Gestione degli eventi
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    image = pygame.image.load('Background.png').convert_alpha()
                    SCALED_WIDTH, SCALED_HEIGTH = utils.mantain_aspectratio(image, self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
                    image_scaled = pygame.transform.scale(image,(SCALED_WIDTH, SCALED_HEIGTH))
                    rotated_scaled_image = pygame.transform.flip(image_scaled, True, False)
                    background_images = [image_scaled, rotated_scaled_image, image_scaled, rotated_scaled_image]
                    background_index = 0
                    background_alpha = 255  # Initial alpha value for fading
                    background_scroll_x = 0
                    background_scroll_speed = 2.5

                    running_1 = True
                    scrolling_enabled = True
                    game_started = False
                    giochiamo = False

                    while running_1:

                        self.screen.blit(background_images[background_index], (background_scroll_x, 0))
                        self.screen.blit(background_images[1 - background_index], (background_scroll_x + SCALED_WIDTH, 0))

                        fade_surface = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
                        fade_surface.fill((0, 0, 0))
                        fade_surface.set_alpha(background_alpha)
                        self.screen.blit(fade_surface, (0, 0))

                        if scrolling_enabled:
                            background_scroll_x -= background_scroll_speed
                            if background_scroll_x <= -SCALED_WIDTH:
                                background_scroll_x = 0

                        if background_alpha > 0:
                            background_alpha -= 5

                        for event in pygame.event.get():
                            if event.type == pygame.MOUSEBUTTONDOWN and not game_started:
                                mouse_x, mouse_y = pygame.mouse.get_pos()
                                if (self.button_x_l <= mouse_x <= self.button_x_l + self.button_width
                                        and self.button_y <= mouse_y <= self.button_y + self.button_height):
                                    game_started = True
                                    giochiamo = True
                                if (self.button_x_r <= mouse_x <= self.button_x_r + self.button_width
                                        and self.button_y <= mouse_y <= self.button_y + self.button_height):
                                    game_started = True
                                if self.exit_button.is_clicked(pygame.mouse.get_pos()):
                                    pygame.quit()
                                if self.home_button.is_clicked(pygame.mouse.get_pos()):
                                    running_1 = False

                        self.button_l.draw(self.screen)
                        self.button_r.draw(self.screen)
                        self.exit_button.draw(self.screen)
                        self.home_button.draw(self.screen)
                        self.button_title.draw(self.screen)

                        pygame.display.flip()
                        #utils.text_sound("start_text.mp3")

                        pygame.time.Clock().tick(60)

                        if game_started:
                            while background_alpha < 255:
                                fade_surface.set_alpha(background_alpha)
                                background_alpha += 5

                                self.screen.blit(fade_surface, (0, 0))
                                pygame.display.flip()

                            self.bg_sound.set_volume(0.2)

                            utils.play_video_from_images(self.avatar, "./avatar/intro.mp4", self.screen,
                                                         True, "Il giardino parlante ti dà il benvenuto!")
                            self.bg_sound.set_volume(1)
                            game.main(input, self.model, self.images, self.music, self.bg_sound, giochiamo)
                            #cam = cv2.VideoCapture(0)
                            #utils.detect_face(cam, model, bg_sound, images, music, giochiamo)


        pygame.quit()

def main(avatar, model, images, music):
    interface = Interface(avatar, model, images, music)
    interface.run()


if __name__ == "__main__" :
    main()