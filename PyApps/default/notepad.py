import pygame
import os

from userspace.system.language_manager import LanguageManager
from userspace.system.settings_manager import SettingsManager

FONT_PATH = "res/fonts/msa/Ac437_TridentEarly_8x14.ttf"


class NotepadApp:
    def __init__(self):
        self.lang = LanguageManager()
        self.settings = SettingsManager()

        self.font = pygame.font.Font(FONT_PATH, 18)
        self.small_font = pygame.font.Font(FONT_PATH, 16)

        self.text_lines = [""]
        self.cursor_pos = [0, 0]  # line, column
        self.scroll_offset = 0

        self.file_path = None
        self.saved = True

        # Toolbar buttons
        self.btn_new = pygame.Rect(10, 5, 60, 20)
        self.btn_open = pygame.Rect(80, 5, 60, 20)
        self.btn_save = pygame.Rect(150, 5, 60, 20)

        # Status bar
        self.status_message = ""
        self.status_color = (0, 0, 0)
        self.status_timer = 0

        # Blinking cursor
        self.cursor_visible = True
        self.cursor_blink_timer = 0  # ms

    # -------------------------
    # STATUS MESSAGE
    # -------------------------

    def show_status(self, text, color):
        self.status_message = text
        self.status_color = color
        self.status_timer = 180  # ~3 seconds at 60 FPS

    # -------------------------
    # DRAW
    # -------------------------

    def update(self, surface, mouse_pos):
        surface.fill((255, 255, 255))

        # Toolbar
        pygame.draw.rect(surface, (230, 230, 230), (0, 0, surface.get_width(), 30))

        pygame.draw.rect(surface, (200, 200, 200), self.btn_new)
        pygame.draw.rect(surface, (200, 200, 200), self.btn_open)
        pygame.draw.rect(surface, (200, 200, 200), self.btn_save)

        surface.blit(self.small_font.render(self.lang.get("notepad_new"), True, (0, 0, 0)), (self.btn_new.x + 5, 7))
        surface.blit(self.small_font.render(self.lang.get("notepad_open"), True, (0, 0, 0)), (self.btn_open.x + 5, 7))
        surface.blit(self.small_font.render(self.lang.get("notepad_save"), True, (0, 0, 0)), (self.btn_save.x + 5, 7))

        # Text area
        y = 40 - self.scroll_offset
        for i, line in enumerate(self.text_lines):
            txt = self.font.render(line, True, (0, 0, 0))
            surface.blit(txt, (10, y))
            y += 24

        # Cursor blink logic
        self.cursor_blink_timer += 1
        if self.cursor_blink_timer >= 30:  # ~0.5 seconds at 60 FPS
            self.cursor_visible = not self.cursor_visible
            self.cursor_blink_timer = 0

        # Draw cursor
        if self.cursor_visible:
            cur_line, cur_col = self.cursor_pos
            if 0 <= cur_line < len(self.text_lines):
                cursor_x = 10 + self.font.size(self.text_lines[cur_line][:cur_col])[0]
                cursor_y = 40 + cur_line * 24 - self.scroll_offset
                pygame.draw.line(surface, (0, 0, 0), (cursor_x, cursor_y), (cursor_x, cursor_y + 20), 2)

        # Status bar
        pygame.draw.rect(surface, (230, 230, 230), (0, surface.get_height() - 24, surface.get_width(), 24))

        if self.status_timer > 0:
            self.status_timer -= 1

        if self.status_message:
            txt = self.small_font.render(self.status_message, True, self.status_color)
            surface.blit(txt, (10, surface.get_height() - 20))

    # -------------------------
    # EVENT HANDLING
    # -------------------------

    def handle_event(self, event, window_rect):
        # Convert to local coords
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
            lx = event.pos[0] - window_rect.x
            ly = event.pos[1] - (window_rect.y + 30)
        else:
            lx, ly = None, None

        # Toolbar buttons
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_new.collidepoint((lx, ly)):
                self.new_file()
                return
            if self.btn_open.collidepoint((lx, ly)):
                self.open_file_dialog()
                return
            if self.btn_save.collidepoint((lx, ly)):
                self.save_file()
                return

        # Typing
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.backspace()
            elif event.key == pygame.K_RETURN:
                self.newline()
            elif event.key == pygame.K_UP:
                self.cursor_up()
            elif event.key == pygame.K_DOWN:
                self.cursor_down()
            elif event.key == pygame.K_LEFT:
                self.cursor_left()
            elif event.key == pygame.K_RIGHT:
                self.cursor_right()
            else:
                if event.unicode and event.unicode.isprintable():
                    self.insert_char(event.unicode)

        # Scroll wheel
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_offset -= event.y * 30
            self.scroll_offset = max(0, self.scroll_offset)

    # -------------------------
    # TEXT EDITING
    # -------------------------

    def insert_char(self, ch):
        line, col = self.cursor_pos
        self.text_lines[line] = self.text_lines[line][:col] + ch + self.text_lines[line][col:]
        self.cursor_pos[1] += 1
        self.saved = False
        self.show_status(self.lang.get("notepad_unsaved"), (180, 120, 0))

    def backspace(self):
        line, col = self.cursor_pos
        if col > 0:
            self.text_lines[line] = self.text_lines[line][:col - 1] + self.text_lines[line][col:]
            self.cursor_pos[1] -= 1
        elif line > 0:
            prev_len = len(self.text_lines[line - 1])
            self.text_lines[line - 1] += self.text_lines[line]
            del self.text_lines[line]
            self.cursor_pos = [line - 1, prev_len]
        self.saved = False
        self.show_status(self.lang.get("notepad_unsaved"), (180, 120, 0))

    def newline(self):
        line, col = self.cursor_pos
        new_line = self.text_lines[line][col:]
        self.text_lines[line] = self.text_lines[line][:col]
        self.text_lines.insert(line + 1, new_line)
        self.cursor_pos = [line + 1, 0]
        self.saved = False
        self.show_status(self.lang.get("notepad_unsaved"), (180, 120, 0))

    def cursor_left(self):
        line, col = self.cursor_pos
        if col > 0:
            self.cursor_pos[1] -= 1
        elif line > 0:
            self.cursor_pos = [line - 1, len(self.text_lines[line - 1])]

    def cursor_right(self):
        line, col = self.cursor_pos
        if col < len(self.text_lines[line]):
            self.cursor_pos[1] += 1
        elif line < len(self.text_lines) - 1:
            self.cursor_pos = [line + 1, 0]

    def cursor_up(self):
        line, col = self.cursor_pos
        if line > 0:
            self.cursor_pos = [line - 1, min(col, len(self.text_lines[line - 1]))]

    def cursor_down(self):
        line, col = self.cursor_pos
        if line < len(self.text_lines) - 1:
            self.cursor_pos = [line + 1, min(col, len(self.text_lines[line + 1]))]

    # -------------------------
    # FILE OPERATIONS
    # -------------------------

    def new_file(self):
        self.text_lines = [""]
        self.cursor_pos = [0, 0]
        self.file_path = None
        self.saved = True
        self.show_status(self.lang.get("notepad_saved"), (0, 150, 0))

    def open_file_dialog(self):
        # Simple: open a fixed file for now
        path = "notepad.txt"
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                self.text_lines = f.read().split("\n")
            self.cursor_pos = [0, 0]
            self.file_path = path
            self.saved = True
            self.show_status(self.lang.get("notepad_saved"), (0, 150, 0))

    def save_file(self):
        path = self.file_path or "notepad.txt"
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(self.text_lines))
        self.file_path = path
        self.saved = True
        self.show_status(self.lang.get("notepad_saved"), (0, 150, 0))
