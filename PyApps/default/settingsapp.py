import pygame

from userspace.system.settings_manager import SettingsManager
from userspace.system.language_manager import LanguageManager

FONT_PATH = "res/fonts/msa/Ac437_TridentEarly_8x14.ttf"


class SettingsApp:
    def __init__(self):
        self.font = pygame.font.Font(FONT_PATH, 18)
        self.small_font = pygame.font.Font(FONT_PATH, 16)

        self.settings = SettingsManager()
        self.lang = LanguageManager()

        # Categories
        self.categories = ["General", "Personalization", "System"]
        self.category_rects = {}
        self.current_category = "General"

        # Language dropdown
        self.available_languages = ["en-US", "sv-SE"]
        self.lang_dropdown_rect = pygame.Rect(350, 50, 160, 25)
        self.dropdown_open = False

        # Animation toggle
        self.anim_toggle_rect = pygame.Rect(350, 100, 80, 25)

        # Volume slider
        self.volume_slider_rect = pygame.Rect(300, 200, 200, 10)
        self.dragging_volume = False

    def update(self, surface, mouse_pos):
        surface.fill((240, 240, 240))

        # Sidebar
        pygame.draw.rect(surface, (220, 220, 220), (0, 0, 200, surface.get_height()))

        y = 20
        self.category_rects = {}
        for cat in self.categories:
            rect = pygame.Rect(10, y, 180, 30)
            self.category_rects[cat] = rect

            if cat == self.current_category:
                pygame.draw.rect(surface, (180, 200, 255), rect)
            elif rect.collidepoint(mouse_pos):
                pygame.draw.rect(surface, (200, 200, 200), rect)

            label_key = {
                "General": "settings_general",
                "Personalization": "settings_personalization",
                "System": "settings_system",
            }.get(cat, "settings_general")

            label = self.font.render(self.lang.get(label_key), True, (0, 0, 0))
            surface.blit(label, (rect.x + 10, rect.y + 5))

            y += 40

        # Category content
        if self.current_category == "General":
            self.draw_general(surface)
        elif self.current_category == "Personalization":
            self.draw_personalization(surface)
        elif self.current_category == "System":
            self.draw_system(surface)

    # -------------------------
    # CATEGORY DRAWING
    # -------------------------

    def draw_general(self, surface):
        # Language label
        label = self.font.render(self.lang.get("settings_language"), True, (0, 0, 0))
        surface.blit(label, (250, 50))

        # Language dropdown box
        pygame.draw.rect(surface, (255, 255, 255), self.lang_dropdown_rect)
        pygame.draw.rect(surface, (0, 0, 0), self.lang_dropdown_rect, 1)

        current = self.settings.get("General", "language")
        txt = self.small_font.render(current, True, (0, 0, 0))
        surface.blit(txt, (self.lang_dropdown_rect.x + 5, self.lang_dropdown_rect.y + 5))

        # Dropdown list
        if self.dropdown_open:
            y = self.lang_dropdown_rect.bottom
            for lang_code in self.available_languages:
                rect = pygame.Rect(self.lang_dropdown_rect.x, y, self.lang_dropdown_rect.width, 25)
                pygame.draw.rect(surface, (255, 255, 255), rect)
                pygame.draw.rect(surface, (0, 0, 0), rect, 1)
                t = self.small_font.render(lang_code, True, (0, 0, 0))
                surface.blit(t, (rect.x + 5, rect.y + 5))
                y += 25

        # Animations toggle
        label = self.font.render(self.lang.get("settings_animations"), True, (0, 0, 0))
        surface.blit(label, (250, 100))

        anim_state = self.settings.get("General", "animations")
        pygame.draw.rect(surface, (255, 255, 255), self.anim_toggle_rect)
        pygame.draw.rect(surface, (0, 0, 0), self.anim_toggle_rect, 1)

        state_label = self.small_font.render(
            self.lang.get("settings_animations_on") if anim_state == "true" else self.lang.get("settings_animations_off"),
            True,
            (0, 0, 0)
        )
        surface.blit(state_label, (self.anim_toggle_rect.x + 5, self.anim_toggle_rect.y + 5))

    def draw_personalization(self, surface):
        theme = self.settings.get("Personalization", "theme")

        label = self.font.render(self.lang.get("settings_theme"), True, (0, 0, 0))
        surface.blit(label, (250, 50))

        theme_label = self.small_font.render(theme, True, (0, 0, 0))
        surface.blit(theme_label, (350, 50))

    def draw_system(self, surface):
        volume = int(self.settings.get("System", "volume"))

        label = self.font.render(self.lang.get("settings_volume"), True, (0, 0, 0))
        surface.blit(label, (250, 150))

        # Slider background
        pygame.draw.rect(surface, (180, 180, 180), self.volume_slider_rect)

        # Slider knob
        knob_x = self.volume_slider_rect.x + (volume / 100) * self.volume_slider_rect.width
        pygame.draw.circle(
            surface,
            (0, 120, 255),
            (int(knob_x), self.volume_slider_rect.y + self.volume_slider_rect.height // 2),
            8,
        )

        vol_label = self.small_font.render(str(volume), True, (0, 0, 0))
        surface.blit(vol_label, (self.volume_slider_rect.x + 210, self.volume_slider_rect.y - 5))

    # -------------------------
    # EVENT HANDLING
    # -------------------------

    def handle_event(self, event, window_rect):
        # Convert to local coords
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
            local_x = event.pos[0] - window_rect.x
            local_y = event.pos[1] - (window_rect.y + 30)
        else:
            local_x, local_y = None, None

        # Category switching
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for cat, rect in self.category_rects.items():
                if rect.collidepoint((local_x, local_y)):
                    self.current_category = cat
                    self.dropdown_open = False
                    return None

        # General: language dropdown
        if self.current_category == "General":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Toggle dropdown
                if self.lang_dropdown_rect.collidepoint((local_x, local_y)):
                    self.dropdown_open = not self.dropdown_open
                    return None

                # Select language
                if self.dropdown_open:
                    y = self.lang_dropdown_rect.bottom
                    for lang_code in self.available_languages:
                        rect = pygame.Rect(self.lang_dropdown_rect.x, y, self.lang_dropdown_rect.width, 25)
                        if rect.collidepoint((local_x, local_y)):
                            self.settings.set("General", "language", lang_code)
                            self.lang.set_language(lang_code)
                            self.dropdown_open = False
                            return None
                        y += 25

                # Animations toggle
                if self.anim_toggle_rect.collidepoint((local_x, local_y)):
                    current = self.settings.get("General", "animations")
                    new_value = "false" if current == "true" else "true"
                    self.settings.set("General", "animations", new_value)
                    return None

        # System: volume slider
        if self.current_category == "System":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.volume_slider_rect.collidepoint((local_x, local_y)):
                    self.dragging_volume = True
                    return None

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.dragging_volume = False

            if event.type == pygame.MOUSEMOTION and self.dragging_volume:
                rel = local_x - self.volume_slider_rect.x
                rel = max(0, min(self.volume_slider_rect.width, rel))
                volume = int((rel / self.volume_slider_rect.width) * 100)
                self.settings.set("System", "volume", volume)

        return None
