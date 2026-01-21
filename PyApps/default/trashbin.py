import pygame
import os
import time

from userspace.system.trash_manager import (
    list_trash,
    restore,
    delete_permanently,
    empty_trash,
)

FONT_PATH = os.path.join("res", "fonts", "msa", "Ac437_TridentEarly_8x14.ttf")


class TrashBinApp:
    def __init__(self):
        self.font = pygame.font.Font(FONT_PATH, 18)
        self.small = pygame.font.Font(FONT_PATH, 14)

        self.items = list_trash()
        self.selected = None
        self.last_click = 0
        self.scroll = 0

        self.row_height = 32
        self.header_height = 40

        self.context_menu = None
        self.context_pos = (0, 0)

    # ---------------------------------------------------------
    # UPDATE / DRAW
    # ---------------------------------------------------------
    def update(self, surface, mouse_pos):
        surface.fill((240, 240, 240))

        # Header
        pygame.draw.rect(surface, (200, 200, 200), (0, 0, surface.get_width(), self.header_height))
        title = self.font.render("Recycle Bin", True, (0, 0, 0))
        surface.blit(title, (10, 8))

        # Empty Trash button
        btn_rect = pygame.Rect(surface.get_width() - 150, 5, 140, 30)
        pygame.draw.rect(surface, (180, 60, 60), btn_rect)
        txt = self.font.render("Empty Trash", True, (255, 255, 255))
        surface.blit(txt, (btn_rect.x + 10, btn_rect.y + 5))
        self.empty_btn_rect = btn_rect

        # Column headers
        y = self.header_height
        pygame.draw.rect(surface, (220, 220, 220), (0, y, surface.get_width(), 30))
        surface.blit(self.small.render("Name", True, (0, 0, 0)), (10, y + 7))
        surface.blit(self.small.render("Original Path", True, (0, 0, 0)), (200, y + 7))
        surface.blit(self.small.render("Deleted", True, (0, 0, 0)), (surface.get_width() - 150, y + 7))

        # Items
        y += 30
        start_y = y - self.scroll

        for item in self.items:
            row_rect = pygame.Rect(0, start_y, surface.get_width(), self.row_height)

            # Hover / selected
            if row_rect.collidepoint(mouse_pos):
                pygame.draw.rect(surface, (210, 210, 255), row_rect)
            if self.selected == item["id"]:
                pygame.draw.rect(surface, (180, 200, 255), row_rect)

            # Draw text
            surface.blit(self.small.render(item["name"], True, (0, 0, 0)), (10, start_y + 7))
            surface.blit(self.small.render(item["original_path"], True, (0, 0, 0)), (200, start_y + 7))

            ts = time.strftime("%Y-%m-%d %H:%M", time.localtime(item["deleted_at"]))
            surface.blit(self.small.render(ts, True, (0, 0, 0)), (surface.get_width() - 150, start_y + 7))

            # Save row rect for click detection
            item["rect"] = row_rect

            start_y += self.row_height

        # Context menu
        if self.context_menu:
            self.draw_context_menu(surface)

    # ---------------------------------------------------------
    # CONTEXT MENU
    # ---------------------------------------------------------
    def draw_context_menu(self, surface):
        x, y = self.context_pos
        w, h = 180, len(self.context_menu) * 28

        pygame.draw.rect(surface, (255, 255, 255), (x, y, w, h))
        pygame.draw.rect(surface, (0, 0, 0), (x, y, w, h), 2)

        for i, (label, cmd) in enumerate(self.context_menu):
            item_rect = pygame.Rect(x, y + i * 28, w, 28)
            pygame.draw.rect(surface, (230, 230, 230), item_rect)
            surface.blit(self.small.render(label, True, (0, 0, 0)), (item_rect.x + 5, item_rect.y + 5))

            self.context_menu[i] = (label, cmd, item_rect)

    # ---------------------------------------------------------
    # EVENT HANDLING
    # ---------------------------------------------------------
    def handle_event(self, event, window_rect):
        # Convert to local coords
        if hasattr(event, "pos"):
            lx = event.pos[0] - window_rect.x
            ly = event.pos[1] - (window_rect.y + 30)
        else:
            lx, ly = None, None

        # Scroll
        if event.type == pygame.MOUSEWHEEL:
            self.scroll -= event.y * 30
            self.scroll = max(0, self.scroll)
            return

        # Context menu click
        if self.context_menu:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for label, cmd, rect in self.context_menu:
                    if rect.collidepoint((lx, ly)):
                        self.run_context_command(cmd)
                        self.context_menu = None
                        return
                self.context_menu = None
            return

        # Empty trash button
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.empty_btn_rect.collidepoint((lx, ly)):
                empty_trash()
                self.items = list_trash()
                return

        # Click on items
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            clicked = None
            for item in self.items:
                if item["rect"].collidepoint((lx, ly)):
                    clicked = item
                    break

            now = pygame.time.get_ticks()

            if clicked:
                if now - self.last_click < 300:
                    restore(clicked["id"])
                    self.items = list_trash()
                else:
                    self.selected = clicked["id"]

                self.last_click = now
                return

        # Right-click context menu
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            for item in self.items:
                if item["rect"].collidepoint((lx, ly)):
                    self.selected = item["id"]
                    self.context_menu = [
                        ("Restore", f"restore::{item['id']}"),
                        ("Delete Permanently", f"delete::{item['id']}"),
                    ]
                    self.context_pos = (lx, ly)
                    return

    # ---------------------------------------------------------
    # CONTEXT COMMANDS
    # ---------------------------------------------------------
    def run_context_command(self, cmd):
        if cmd.startswith("restore::"):
            tid = cmd.split("::")[1]
            restore(tid)
            self.items = list_trash()

        elif cmd.startswith("delete::"):
            tid = cmd.split("::")[1]
            delete_permanently(tid)
            self.items = list_trash()
