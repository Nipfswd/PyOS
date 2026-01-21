import os
import pygame

TRASH_ICON_PATH = os.path.join("res", "images", "main", "imageres", "trashbin.png")
EXPLORER_ICON_PATH = os.path.join("res", "images", "main", "imageres", "fileexplorer.png")
START_ICON_PATH = os.path.join("res", "images", "main", "imageres", "start.png")


class Taskbar:
    def __init__(self, screen_width, screen_height, taskbar_height, font_path):
        self.width = screen_width
        self.height = screen_height
        self.taskbar_height = taskbar_height

        # Load icons
        self.start_icon = pygame.image.load(START_ICON_PATH).convert_alpha()
        self.start_icon = pygame.transform.scale(self.start_icon, (40, 40))

        self.trash_icon = pygame.image.load(TRASH_ICON_PATH).convert_alpha()
        self.trash_icon = pygame.transform.scale(self.trash_icon, (40, 40))

        self.explorer_icon = pygame.image.load(EXPLORER_ICON_PATH).convert_alpha()
        self.explorer_icon = pygame.transform.scale(self.explorer_icon, (40, 40))

        # Positions
        self.start_pos = (10, self.height - self.taskbar_height + (self.taskbar_height - 40) // 2)
        self.trash_pos = (60, self.height - self.taskbar_height + (self.taskbar_height - 40) // 2)
        self.explorer_pos = (110, self.height - self.taskbar_height + (self.taskbar_height - 40) // 2)

        # Rects
        self.start_rect = pygame.Rect(self.start_pos[0], self.start_pos[1], 40, 40)
        self.trash_rect = pygame.Rect(self.trash_pos[0], self.trash_pos[1], 40, 40)
        self.explorer_rect = pygame.Rect(self.explorer_pos[0], self.explorer_pos[1], 40, 40)

        self.hover_color = (0, 120, 255, 120)
        self.font = pygame.font.Font(font_path, int(self.taskbar_height * 0.45))

    def draw(self, screen):
        pygame.draw.rect(screen, (20, 20, 20), (0, self.height - self.taskbar_height, self.width, self.taskbar_height))

        mouse_pos = pygame.mouse.get_pos()

        # Hover highlight
        for rect, pos in [
            (self.start_rect, self.start_pos),
            (self.trash_rect, self.trash_pos),
            (self.explorer_rect, self.explorer_pos),
        ]:
            if rect.collidepoint(mouse_pos):
                hover = pygame.Surface((40, 40), pygame.SRCALPHA)
                hover.fill(self.hover_color)
                screen.blit(hover, pos)

        # Draw icons
        screen.blit(self.start_icon, self.start_pos)
        screen.blit(self.trash_icon, self.trash_pos)
        screen.blit(self.explorer_icon, self.explorer_pos)

        # Clock
        import time
        current_time = time.strftime("%H:%M:%S")
        clock_surface = self.font.render(current_time, True, (255, 255, 255))
        clock_rect = clock_surface.get_rect(
            right=self.width - 20,
            centery=self.height - self.taskbar_height // 2
        )
        screen.blit(clock_surface, clock_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.start_rect.collidepoint(event.pos):
                return "start_clicked"
            if self.trash_rect.collidepoint(event.pos):
                return "trash_clicked"
            if self.explorer_rect.collidepoint(event.pos):
                return "explorer_clicked"
        return None
