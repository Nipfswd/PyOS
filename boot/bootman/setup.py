#!/usr/bin/env python3
import os
import sys
import pygame


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from extra.public.boot.booterr_log import log_error
from boot.bootextr.string import fade_in_text, fade_out_all
from kernel.main.login import login_main
from kernel.utils.fs_init import init_pyfs

FONT_PATH = os.path.join("res", "fonts", "msa", "Ac437_TridentEarly_8x14.ttf")
LOGO_PATH = os.path.join("res", "images", "msa", "boot", "splash_logo_msa.png")

BG_COLOR = (0, 0, 0)
FG_COLOR = (255, 255, 255)


def main():
    init_pyfs()
    try:
        pygame.init()

        screen = pygame.display.set_mode(
            (0, 0),
            pygame.FULLSCREEN | pygame.NOFRAME
        )
        width, height = screen.get_size()
        screen.fill(BG_COLOR)

        # Load logo
        logo = pygame.image.load(LOGO_PATH).convert_alpha()
        scale = (width * 0.3) / logo.get_width()
        logo = pygame.transform.scale(
            logo,
            (int(logo.get_width() * scale), int(logo.get_height() * scale))
        )
        logo_rect = logo.get_rect(center=(width // 2, int(height * 0.30)))

        # Load font
        font = pygame.font.Font(FONT_PATH, int(height * 0.06))

        # Draw logo + welcome
        screen.blit(logo, logo_rect)
        text_surface = font.render("Welcome", True, FG_COLOR)
        text_rect = text_surface.get_rect(center=(width // 2, int(height * 0.60)))
        screen.blit(text_surface, text_rect)
        pygame.display.flip()

        # Fade in "Click to continue"
        fade_in_text(
            screen,
            font,
            "Click to continue",
            FG_COLOR,
            (width // 2, int(height * 0.70)),
            delay=0.9,
            duration=1.0
        )

        # Wait for click
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type in (pygame.QUIT, pygame.MOUSEBUTTONDOWN):
                    waiting = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    waiting = False

        fade_out_all(screen)
        pygame.time.delay(300)

        # → LOGIN
        login_main(screen)

        # SAFETY FREEZE
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return
            pygame.time.delay(50)

    except Exception as e:
        log_error(f"Unhandled exception: {e}")


if __name__ == "__main__":
    main()
