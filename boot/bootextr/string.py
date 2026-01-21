import pygame
import time

def fade_in_text(screen, font, text, color, center_pos, delay=0.9, duration=1.0):
    # Wait with event pumping so window stays alive
    start_delay = time.time()
    while time.time() - start_delay < delay:
        pygame.event.pump()
        pygame.time.delay(10)

    start_time = time.time()
    alpha = 0

    base_surface = font.render(text, True, color)
    text_surface = base_surface.convert_alpha()
    rect = text_surface.get_rect(center=center_pos)

    while alpha < 255:
        pygame.event.pump()  # prevents freeze

        now = time.time()
        progress = (now - start_time) / duration
        alpha = min(255, int(progress * 255))

        text_surface.set_alpha(alpha)

        screen.blit(text_surface, rect)
        pygame.display.flip()

        pygame.time.delay(10)

    return rect


def fade_out_all(screen, fade_speed=5):
    overlay = pygame.Surface(screen.get_size())
    overlay = overlay.convert()
    overlay.fill((0, 0, 0))

    for alpha in range(0, 256, fade_speed):
        pygame.event.pump()  # prevents freeze

        overlay.set_alpha(alpha)
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        pygame.time.delay(10)
