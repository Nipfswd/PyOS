import pygame
import time

class Debugger:
    def __init__(self):
        self.lines = []
        self.max_lines = 12
        self.font = pygame.font.SysFont("Consolas", 16)

    def log(self, text):
        timestamp = time.strftime("%H:%M:%S")
        self.lines.append(f"[{timestamp}] {text}")
        if len(self.lines) > self.max_lines:
            self.lines.pop(0)

    def draw(self, surface):
        y = 10
        for line in self.lines:
            txt = self.font.render(line, True, (255, 255, 0))
            surface.blit(txt, (10, y))
            y += 18
