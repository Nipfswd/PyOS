import pygame

from userspace.system.language_manager import LanguageManager

FONT_PATH = "res/fonts/msa/Ac437_TridentEarly_8x14.ttf"


class StartMenu:
    def __init__(self, screen_width, screen_height, font=None):
        self.width = 320
        self.height = 420
        self.x = 0
        self.y = screen_height - self.height - 70  # above taskbar
        self.visible = False

        self.bg_color = (32, 32, 32)
        self.hover_color = (60, 60, 60)
        self.text_color = (255, 255, 255)

        self.font = font or pygame.font.Font(FONT_PATH, 18)

        self.lang = LanguageManager()

        # (label_key, command)
        self.items = [
            ("start_menu_file_explorer", "fileexplorer"),
            ("start_menu_trash_bin", "trashbin"),
            ("start_menu_settings", "settingsapp"),
            ("start_menu_notepad", "notepad"),
        ]

        self.item_rects = []

    def toggle(self):
        self.visible = not self.visible

    def hide(self):
        self.visible = False

    def draw(self, surface):
        if not self.visible:
            return

        menu_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, self.bg_color, menu_rect)

        self.item_rects = []
        y = self.y + 20
        mx, my = pygame.mouse.get_pos()

        for key, cmd in self.items:
            rect = pygame.Rect(self.x + 10, y, self.width - 20, 32)
            self.item_rects.append((rect, cmd))

            if rect.collidepoint((mx, my)):
                pygame.draw.rect(surface, self.hover_color, rect)

            label = self.lang.get(key)
            text = self.font.render(label, True, self.text_color)
            surface.blit(text, (rect.x + 10, rect.y + 5))

            y += 40

    def handle_event(self, event):
        if not self.visible:
            return None

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for rect, cmd in self.item_rects:
                if rect.collidepoint((mx, my)):
                    self.hide()
                    return cmd

            # Click outside closes menu
            menu_rect = pygame.Rect(self.x, self.y, self.width, self.height)
            if not menu_rect.collidepoint((mx, my)):
                self.hide()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.hide()

        return None
