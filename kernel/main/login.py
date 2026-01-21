import os
import pygame
from kernel.utils.config import config_main

LOGIN_BG_PATH = os.path.join("res", "images", "msa", "boot", "img100.jpg")
FONT_PATH     = os.path.join("res", "fonts", "msa", "Ac437_TridentEarly_8x14.ttf")

FG_COLOR      = (255, 255, 255)
BOX_COLOR     = (255, 255, 255)
BOX_ACTIVE    = (0, 200, 255)
TEXT_COLOR    = (200, 200, 200)
ERROR_COLOR   = (255, 80, 80)


def login_main(screen):
    width, height = screen.get_size()

    login_bg = pygame.image.load(LOGIN_BG_PATH).convert()
    login_bg = pygame.transform.scale(login_bg, (width, height))

    font_big = pygame.font.Font(FONT_PATH, int(height * 0.07))
    font_small = pygame.font.Font(FONT_PATH, int(height * 0.045))

    username = ""
    password = ""
    active_box = 0
    error_msg = ""

    user_box = pygame.Rect(width * 0.30, height * 0.45, width * 0.40, height * 0.06)
    pass_box = pygame.Rect(width * 0.30, height * 0.60, width * 0.40, height * 0.06)

    running = True
    while running:
        screen.blit(login_bg, (0, 0))

        title = font_big.render("Login", True, FG_COLOR)
        screen.blit(title, title.get_rect(center=(width // 2, height * 0.25)))

        user_label = font_small.render("Username:", True, FG_COLOR)
        pass_label = font_small.render("Password:", True, FG_COLOR)
        screen.blit(user_label, (user_box.x, user_box.y - height * 0.05))
        screen.blit(pass_label, (pass_box.x, pass_box.y - height * 0.05))

        pygame.draw.rect(screen, BOX_ACTIVE if active_box == 0 else BOX_COLOR, user_box, 3)
        pygame.draw.rect(screen, BOX_ACTIVE if active_box == 1 else BOX_COLOR, pass_box, 3)

        user_text = font_small.render(username, True, TEXT_COLOR)
        pass_text = font_small.render("*" * len(password), True, TEXT_COLOR)
        screen.blit(user_text, (user_box.x + 10, user_box.y + 5))
        screen.blit(pass_text, (pass_box.x + 10, pass_box.y + 5))

        if error_msg:
            err = font_small.render(error_msg, True, ERROR_COLOR)
            screen.blit(err, err.get_rect(center=(width // 2, height * 0.75)))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if user_box.collidepoint(event.pos):
                    active_box = 0
                elif pass_box.collidepoint(event.pos):
                    active_box = 1

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    active_box = 1 - active_box

                elif event.key == pygame.K_RETURN:
                    if username == config_main.user and password == config_main.password:
                        from userspace.desktop.desktop_init import desktop_main
                        desktop_main(screen)

                        # Freeze if desktop returns
                        while True:
                            for e in pygame.event.get():
                                if e.type == pygame.QUIT:
                                    pygame.quit()
                                    return
                                if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                                    pygame.quit()
                                    return
                            pygame.time.delay(50)
                    else:
                        error_msg = "Invalid username or password"
                        password = ""

                elif event.key == pygame.K_BACKSPACE:
                    if active_box == 0:
                        username = username[:-1]
                    else:
                        password = password[:-1]

                else:
                    ch = event.unicode
                    if ch.isprintable():
                        if active_box == 0:
                            username += ch
                        else:
                            password += ch
