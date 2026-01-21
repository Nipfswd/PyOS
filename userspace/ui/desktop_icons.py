import os
import pygame

from userspace.system.file_icon_manager import FileIconManager

# Adjust if your OS uses a different path
DESKTOP_PATH = "Desktop"


class DesktopIcons:
    def __init__(self):
        self.icon_manager = FileIconManager()

        # Layout
        self.icon_size = 48
        self.spacing_x = 120
        self.spacing_y = 100
        self.start_x = 20
        self.start_y = 20

        # State
        self.icon_positions = {}   # name -> rect
        self.selected = None
        self.last_click = 0

        # Fonts
        self.font = pygame.font.SysFont("Arial", 14)

    # ---------------------------------------------------------
    # DRAW DESKTOP ICONS
    # ---------------------------------------------------------
    def draw(self, surface, mouse_pos):
        try:
            items = os.listdir(DESKTOP_PATH)
        except Exception:
            items = []

        x = self.start_x
        y = self.start_y

        self.icon_positions = {}

        for item in items:
            full_path = os.path.join(DESKTOP_PATH, item)

            rect = pygame.Rect(x, y, self.icon_size, self.icon_size)
            self.icon_positions[item] = rect

            # Hover highlight
            if rect.collidepoint(mouse_pos):
                hover = pygame.Surface((self.icon_size, self.icon_size), pygame.SRCALPHA)
                hover.fill((0, 120, 255, 80))
                surface.blit(hover, (x, y))

            # Selected highlight
            if self.selected == item:
                sel = pygame.Surface((self.icon_size, self.icon_size), pygame.SRCALPHA)
                sel.fill((0, 120, 255, 120))
                surface.blit(sel, (x, y))

            # Icon
            icon = self.icon_manager.get_icon(full_path)
            surface.blit(icon, (x, y))

            # Label
            label = self.font.render(item, True, (255, 255, 255))
            label_rect = label.get_rect(center=(x + self.icon_size // 2,
                                                y + self.icon_size + 12))
            surface.blit(label, label_rect)

            # Move to next grid position
            y += self.spacing_y
            if y + self.icon_size > surface.get_height() - 100:
                y = self.start_y
                x += self.spacing_x

    # ---------------------------------------------------------
    # EVENT HANDLING
    # ---------------------------------------------------------
    def handle_event(self, event):
        # We only care about mouse button events
        if event.type not in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            return None

        mouse_pos = event.pos

        # -------------------------
        # LEFT CLICK
        # -------------------------
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            clicked = None

            for name, rect in self.icon_positions.items():
                if rect.collidepoint(mouse_pos):
                    clicked = name
                    break

            now = pygame.time.get_ticks()

            if clicked:
                # Double-click
                if now - self.last_click < 300:
                    self.last_click = 0
                    return {
                        "type": "open",
                        "name": clicked,
                        "path": os.path.join(DESKTOP_PATH, clicked)
                    }

                # Single click → select
                self.selected = clicked
                self.last_click = now
                return {
                    "type": "select",
                    "name": clicked
                }

            # Left-click empty desktop → clear selection
            self.selected = None
            self.last_click = now
            return {
                "type": "clear_selection"
            }

        # -------------------------
        # RIGHT CLICK
        # -------------------------
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            for name, rect in self.icon_positions.items():
                if rect.collidepoint(mouse_pos):
                    return {
                        "type": "context_item",
                        "name": name,
                        "path": os.path.join(DESKTOP_PATH, name)
                    }

            # Right-click empty desktop
            return {
                "type": "context_empty"
            }

        return None
