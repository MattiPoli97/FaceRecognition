import pygame
import random
from . import game
from . import utils

def main(avatar, model, images, music) :
    pygame.init()
    bg_sound = pygame.mixer.Sound('background_music.wav')
    bg_sound.play(loops=-1)
    
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
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_width(), screen.get_height()
    pygame.display.set_caption("MEMORY GAME")
    screen.fill(random_bg_color)
    balls = []
    for _ in range(40):
        x = random.randint(SCREEN_WIDTH // 4, 3 * SCREEN_WIDTH // 4)
        y = random.randint(SCREEN_HEIGHT // 4, 3 * SCREEN_HEIGHT // 4)
        radius = random.randint(SCREEN_WIDTH//40, SCREEN_HEIGHT//6)
        ball = utils.Leaf(x, y, radius, SCREEN_WIDTH, SCREEN_HEIGHT)
        balls.append(ball)

    # Button parameters
    button_width = SCREEN_WIDTH // 2.5
    button_height = SCREEN_HEIGHT // 6
    button_x = (SCREEN_WIDTH - button_width) // 4 - SCREEN_WIDTH // 16
    button_y = SCREEN_HEIGHT // 6
    button_x_1 = 3 * (SCREEN_WIDTH - button_width) // 4 + SCREEN_WIDTH // 16
    button_y_1 = button_y + SCREEN_HEIGHT // 2

    button_l = utils.Button_with_icon(button_x, button_y, button_width, button_height, "Giochiamo!",
                                      icon="./icons/icon_game.png")
    button_r = utils.Button_with_icon(button_x_1, button_y_1, button_width, button_height, "Ricordiamo!",
                                      icon="./icons/icon_remember.png")
    exit_button = utils.Button(SCREEN_WIDTH // 45, SCREEN_WIDTH // 45, SCREEN_WIDTH // 16,
                                         SCREEN_WIDTH // 32, RED, "X")
    home_button = utils.Button_with_icon(SCREEN_WIDTH // 45, SCREEN_WIDTH // 16, SCREEN_WIDTH // 16,
                                         SCREEN_WIDTH // 32, icon="./icons/icon_home.png")

    running = True
    while running:
        screen.fill(random_bg_color)

        for ball in balls:
            ball.move()
            ball.draw(screen)

        pygame.display.update()

        # Gestione degli eventi
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
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
                        background_alpha -= 5

                    for event in pygame.event.get():
                        if event.type == pygame.MOUSEBUTTONDOWN and not game_started:
                            mouse_x, mouse_y = pygame.mouse.get_pos()
                            if button_x <= mouse_x <= button_x + button_width and button_y <= mouse_y <= button_y + button_height:
                                game_started = True
                                giochiamo = True
                            if button_x_1 <= mouse_x <= button_x_1 + button_width and button_y_1 <= mouse_y <= button_y_1 + button_height:
                                game_started = True
                            if exit_button.is_clicked(pygame.mouse.get_pos()):
                                pygame.quit()
                            if home_button.is_clicked(pygame.mouse.get_pos()):
                                running_1 = False
                    
                    button_l.draw(screen)
                    button_r.draw(screen)
                    exit_button.draw(screen, WHITE)
                    home_button.draw(screen)

                    pygame.display.flip()

                    pygame.time.Clock().tick(60)

                    if game_started:
                        while background_alpha < 255:
                            fade_surface.set_alpha(background_alpha)
                            background_alpha += 5
                        
                            screen.blit(fade_surface, (0, 0))
                            pygame.display.flip()

                        bg_sound.set_volume(0.2)
                        avatar = "./frames"
                        utils.play_video_from_images(avatar, "./avatar/intro.mp4", screen, SCREEN_WIDTH // 3, SCREEN_HEIGHT, True)
                        bg_sound.set_volume(1)
                        game.main(input, model, images, music, bg_sound, giochiamo)
                        #cam = cv2.VideoCapture(0)
                        #utils.detect_face(cam, model, bg_sound, images, music, giochiamo)


    pygame.quit()

if __name__ == "__main__" :
    main()