import os
import shutil
import pygame

from userspace.system.language_manager import LanguageManager
from userspace.ui.desktop_icons import DESKTOP_PATH
from userspace.system.file_icon_manager import FileIconManager
from userspace.system.trash_manager import move_to_trash

FONT_PATH = os.path.join("res", "fonts", "msa", "Ac437_TridentEarly_8x14.ttf")

FOLDER_ICON_PATH = os.path.join("res", "images", "main", "imageres", "folder.png")
FILE_ICON_PATH = os.path.join("res", "images", "main", "imageres", "file.png")
DRIVE_ICON_PATH = os.path.join("res", "images", "main", "imageres", "drive.png")

DRIVES_ROOT = os.path.join("config", "live", "PyOS", "Drives")

SPECIAL_FOLDERS = {
    "Desktop": DESKTOP_PATH
}


class FileExplorerApp:
    def __init__(self):
        self.lang = LanguageManager()
        self.icon_manager = FileIconManager()

        # Drives
        self.drives = self.load_virtual_drives()
        self.drive_rects = {}

        # Default view
        self.current_path = "THIS_PC"
        self.current_drive = None

        # Layout
        self.sidebar_width = 160

        # State
        self.icon_positions = {}
        self.selected_item = None
        self.clipboard = None
        self.renaming_item = None
        self.rename_text = ""
        self.last_click = 0

        # Icons
        self.folder_icon = pygame.image.load(FOLDER_ICON_PATH).convert_alpha()
        self.folder_icon = pygame.transform.scale(self.folder_icon, (48, 48))

        self.file_icon = pygame.image.load(FILE_ICON_PATH).convert_alpha()
        self.file_icon = pygame.transform.scale(self.file_icon, (48, 48))

        self.drive_icon = pygame.image.load(DRIVE_ICON_PATH).convert_alpha()
        self.drive_icon = pygame.transform.scale(self.drive_icon, (48, 48))

        self.font = pygame.font.Font(FONT_PATH, 16)

    # ---------------------------------------------------------
    # VIRTUAL DRIVE SYSTEM
    # ---------------------------------------------------------
    def load_virtual_drives(self):
        if not os.path.exists(DRIVES_ROOT):
            os.makedirs(DRIVES_ROOT)

        drives = []
        for name in os.listdir(DRIVES_ROOT):
            full = os.path.join(DRIVES_ROOT, name)
            if os.path.isdir(full):
                drives.append(name)

        if not drives:
            drives = ["C", "D"]
            for d in drives:
                path = os.path.join(DRIVES_ROOT, d)
                os.makedirs(path, exist_ok=True)

            c_path = os.path.join(DRIVES_ROOT, "C")
            for folder in [
                "Windows",
                "Users",
                "Program Files",
                "Program Files (x86)",
                "System32",
                "Temp",
            ]:
                os.makedirs(os.path.join(c_path, folder), exist_ok=True)

            d_path = os.path.join(DRIVES_ROOT, "D")
            for folder in ["Games", "Media", "Projects", "Downloads"]:
                os.makedirs(os.path.join(d_path, folder), exist_ok=True)

        return drives

    # ---------------------------------------------------------
    # MAIN UPDATE / DRAW
    # ---------------------------------------------------------
    def update(self, surface, mouse_pos):
        surface.fill((240, 240, 240))

        # Path bar
        pygame.draw.rect(surface, (220, 220, 220), (0, 0, surface.get_width(), 30))

        if self.current_path == "THIS_PC":
            path_text = self.lang.get("explorer_this_pc")
        else:
            path_text = self.current_path

        txt = self.font.render(path_text, True, (0, 0, 0))
        surface.blit(txt, (10, 7))

        # Sidebar
        pygame.draw.rect(
            surface,
            (230, 230, 230),
            (0, 30, self.sidebar_width, surface.get_height() - 30),
        )

        sidebar_title = self.font.render(self.lang.get("explorer_drives"), True, (0, 0, 0))
        surface.blit(sidebar_title, (10, 35))

        sidebar_items = [
            self.lang.get("explorer_this_pc"),
            "Desktop",
        ] + self.drives

        self.drive_rects = {}
        y_drive = 60

        for item in sidebar_items:
            rect = pygame.Rect(10, y_drive, self.sidebar_width - 20, 24)
            self.drive_rects[item] = rect

            if (
                (item == self.lang.get("explorer_this_pc") and self.current_path == "THIS_PC")
                or (item == self.current_drive)
                or (item == "Desktop" and self.current_path == DESKTOP_PATH)
            ):
                pygame.draw.rect(surface, (200, 220, 255), rect)
            elif rect.collidepoint(mouse_pos):
                pygame.draw.rect(surface, (210, 210, 210), rect)

            label = self.font.render(item, True, (0, 0, 0))
            surface.blit(label, (rect.x + 5, rect.y + 4))

            y_drive += 28

        # THIS PC view
        if self.current_path == "THIS_PC":
            self.draw_this_pc(surface, mouse_pos)
            return

        # Normal folder view
        try:
            items = os.listdir(self.current_path)
        except Exception:
            items = []

        x_start = self.sidebar_width + 20
        x = x_start
        y = 50
        spacing_x = 120
        spacing_y = 100

        self.icon_positions = {}

        if not items:
            empty_text = self.font.render(self.lang.get("explorer_empty"), True, (100, 100, 100))
            surface.blit(empty_text, (x_start, 50))
            return

        for item in items:
            full_path = os.path.join(self.current_path, item)
            icon = self.icon_manager.get_icon(full_path)

            rect = pygame.Rect(x, y, 48, 48)

            if rect.collidepoint(mouse_pos):
                hover = pygame.Surface((48, 48), pygame.SRCALPHA)
                hover.fill((0, 120, 255, 80))
                surface.blit(hover, (x, y))

            if self.selected_item == item:
                sel = pygame.Surface((48, 48), pygame.SRCALPHA)
                sel.fill((0, 120, 255, 120))
                surface.blit(sel, (x, y))

            surface.blit(icon, (x, y))

            if self.renaming_item == item:
                pygame.draw.rect(surface, (255, 255, 255), (x - 2, y + 52, 140, 22))
                pygame.draw.rect(surface, (0, 0, 0), (x - 2, y + 52, 140, 22), 1)
                txt = self.font.render(self.rename_text, True, (0, 0, 0))
                surface.blit(txt, (x, y + 54))
            else:
                label = self.font.render(item, True, (0, 0, 0))
                surface.blit(label, (x, y + 52))

            self.icon_positions[item] = rect

            x += spacing_x
            if x + 100 > surface.get_width():
                x = x_start
                y += spacing_y

    # ---------------------------------------------------------
    # THIS PC VIEW
    # ---------------------------------------------------------
    def draw_this_pc(self, surface, mouse_pos):
        x = self.sidebar_width + 20
        y = 60
        spacing_y = 120

        self.icon_positions = {}

        # Desktop
        rect = pygame.Rect(x, y, 48, 48)
        if rect.collidepoint(mouse_pos):
            hover = pygame.Surface((48, 48), pygame.SRCALPHA)
            hover.fill((0, 120, 255, 80))
            surface.blit(hover, (x, y))

        surface.blit(self.folder_icon, (x, y))
        label = self.font.render("Desktop", True, (0, 0, 0))
        surface.blit(label, (x, y + 52))
        self.icon_positions["Desktop"] = rect

        y += spacing_y

        # Drives
        for drive in self.drives:
            rect = pygame.Rect(x, y, 48, 48)

            if rect.collidepoint(mouse_pos):
                hover = pygame.Surface((48, 48), pygame.SRCALPHA)
                hover.fill((0, 120, 255, 80))
                surface.blit(hover, (x, y))

            surface.blit(self.drive_icon, (x, y))

            label = self.font.render(drive, True, (0, 0, 0))
            surface.blit(label, (x, y + 52))

            pygame.draw.rect(surface, (180, 180, 180), (x, y + 75, 120, 12))
            pygame.draw.rect(surface, (100, 180, 255), (x, y + 75, 80, 12))

            self.icon_positions[drive] = rect

            y += spacing_y

    # ---------------------------------------------------------
    # EVENT HANDLING
    # ---------------------------------------------------------
    def handle_event(self, event, window_rect):
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
            local_x = event.pos[0] - window_rect.x
            local_y = event.pos[1] - (window_rect.y + 30)
        else:
            local_x, local_y = None, None

        # Renaming
        if self.renaming_item:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.finish_rename()
                elif event.key == pygame.K_ESCAPE:
                    self.renaming_item = None
                elif event.key == pygame.K_BACKSPACE:
                    self.rename_text = self.rename_text[:-1]
                else:
                    if event.unicode:
                        self.rename_text += event.unicode
            return None

        # Sidebar click
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for item, rect in self.drive_rects.items():
                if rect.collidepoint((local_x, local_y)):

                    if item == self.lang.get("explorer_this_pc"):
                        self.current_path = "THIS_PC"
                        self.current_drive = None
                        self.selected_item = None
                        self.renaming_item = None
                        return None

                    if item == "Desktop":
                        self.current_path = DESKTOP_PATH
                        self.current_drive = None
                        self.selected_item = None
                        self.renaming_item = None
                        return None

                    self.current_drive = item
                    self.current_path = os.path.join(DRIVES_ROOT, item)
                    self.selected_item = None
                    self.renaming_item = None
                    return None

        # Right-click context menu
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            for name, rect in self.icon_positions.items():
                if rect.collidepoint((local_x, local_y)):

                    if name in SPECIAL_FOLDERS:
                        full_path = SPECIAL_FOLDERS[name]
                    else:
                        full_path = os.path.join(self.current_path, name)

                    return {
                        "type": "context_item",
                        "item": name,
                        "path": full_path,
                        "current_path": self.current_path,   # ⭐ NEW
                        "labels": {
                            "open": self.lang.get("explorer_open"),
                            "edit": "Edit in Notepad",          # ⭐ NEW
                            "delete": self.lang.get("explorer_delete"),
                            "rename": self.lang.get("explorer_rename"),
                            "copy": self.lang.get("explorer_copy"),
                            "cut": self.lang.get("explorer_cut"),
                            "paste": self.lang.get("explorer_paste"),
                        },
                    }

            return {
                "type": "context_empty",
                "path": self.current_path,
                "labels": {
                    "new_folder": self.lang.get("explorer_new_folder"),
                    "paste": self.lang.get("explorer_paste"),
                },
            }

        # Left-click: selection + double-click
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            clicked_item = None
            for name, rect in self.icon_positions.items():
                if rect.collidepoint((local_x, local_y)):
                    clicked_item = name

            now = pygame.time.get_ticks()

            if clicked_item:
                if now - self.last_click < 300:
                    # Double-click

                    if clicked_item == "Desktop":
                        self.current_path = DESKTOP_PATH
                        self.selected_item = None
                        return None

                    if self.current_path == "THIS_PC":
                        self.current_drive = clicked_item
                        self.current_path = os.path.join(DRIVES_ROOT, clicked_item)
                        self.selected_item = None
                        return None

                    full_path = os.path.join(self.current_path, clicked_item)
                    if os.path.isdir(full_path):
                        self.current_path = full_path
                        self.selected_item = None
                else:
                    self.selected_item = clicked_item

                self.last_click = now

        return None

    # ---------------------------------------------------------
    # FILE OPERATIONS
    # ---------------------------------------------------------
    def copy(self, item):
        if self.current_path == "THIS_PC":
            return
        self.clipboard = {
            "path": os.path.join(self.current_path, item),
            "mode": "copy",
        }

    def cut(self, item):
        if self.current_path == "THIS_PC":
            return
        self.clipboard = {
            "path": os.path.join(self.current_path, item),
            "mode": "cut",
        }

    def paste(self):
        if not self.clipboard or self.current_path == "THIS_PC":
            return

        src = self.clipboard["path"]
        dst = os.path.join(self.current_path, os.path.basename(src))

        base = dst
        i = 1
        while os.path.exists(dst):
            dst = f"{base} ({i})"
            i += 1

        if self.clipboard["mode"] == "copy":
            if os.path.isdir(src):
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)

        elif self.clipboard["mode"] == "cut":
            shutil.move(src, dst)
            self.clipboard = None

    def delete(self, item):
        if self.current_path == "THIS_PC":
            return
        full = os.path.join(self.current_path, item)
        move_to_trash(full)
        if self.selected_item == item:
            self.selected_item = None

    def start_rename(self, item):
        if self.current_path == "THIS_PC":
            return
        self.renaming_item = item
        self.rename_text = item

    def finish_rename(self):
        old = os.path.join(self.current_path, self.renaming_item)
        new = os.path.join(self.current_path, self.rename_text)

        if old != new and self.rename_text.strip():
            os.rename(old, new)

        self.renaming_item = None
