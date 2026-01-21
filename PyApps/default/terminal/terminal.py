import pygame
import os
import time
import importlib
import pkgutil

FONT_PATH = os.path.join("res", "fonts", "msa", "Ac437_TridentEarly_8x14.ttf")


class TerminalApp:
    def __init__(self):
        self.font = pygame.font.Font(FONT_PATH, 18)

        # Virtual filesystem root
        self.VFS_ROOT = os.path.normpath(os.path.join("config", "live", "PyOS"))
        self.cwd = self.VFS_ROOT

        # Terminal state
        self.lines = ["PyOS Terminal v0.3 (VFS mode)", ""]
        self.input_text = ""
        self.cursor_visible = True
        self.cursor_timer = 0

        # Colors (DOS-style)
        self.text_color = (200, 200, 200)
        self.bg_color = (20, 20, 20)

        # Scrolling
        self.scroll = 0
        self.auto_scroll = True
        self.last_surface_height = 0

        # Logging
        self.LOG_PATH = os.path.join(
            self.VFS_ROOT, "System", "Logs", "Apps", "cmd.log"
        )

        # Commands
        self.commands = {}
        self.load_commands()

        self.update_prompt()

    # ---------------------------------------------------------
    # COMMAND LOADER
    # ---------------------------------------------------------
    def load_commands(self):
        self.commands = {}

        pkg_name = __package__ + ".commands" if __package__ else "PyApps.default.terminal.commands"

        try:
            cmdpkg = importlib.import_module(pkg_name)
        except ImportError:
            return

        for info in pkgutil.iter_modules(cmdpkg.__path__):
            mod_name = f"{pkg_name}.{info.name}"
            try:
                mod = importlib.import_module(mod_name)
            except Exception:
                continue

            if hasattr(mod, "run"):
                self.commands[info.name] = mod.run

    # ---------------------------------------------------------
    # PATH HELPERS
    # ---------------------------------------------------------
    def vfs_abs(self, path):
        if not os.path.isabs(path):
            path = os.path.join(self.cwd, path)
        path = os.path.normpath(path)

        if not path.startswith(self.VFS_ROOT):
            return self.VFS_ROOT

        return path

    def update_prompt(self):
        shown = self.cwd.replace(self.VFS_ROOT, "")
        if shown == "":
            shown = "/"
        self.prompt = f"{shown}> "

    # ---------------------------------------------------------
    # DRAW
    # ---------------------------------------------------------
    def update(self, surface, mouse_pos):
        self.last_surface_height = surface.get_height()
        surface.fill(self.bg_color)

        y = 10 - self.scroll
        for line in self.lines:
            txt = self.font.render(line, True, self.text_color)
            surface.blit(txt, (10, y))
            y += 24

        # Input line
        input_line = self.prompt + self.input_text
        txt = self.font.render(input_line, True, self.text_color)
        surface.blit(txt, (10, y))

        # Cursor blink
        self.cursor_timer += 1
        if self.cursor_timer >= 30:
            self.cursor_timer = 0
            self.cursor_visible = not self.cursor_visible

        if self.cursor_visible:
            cx = txt.get_width() + 10
            cy = y
            pygame.draw.rect(surface, self.text_color, (cx, cy + 2, 12, 20))

    # ---------------------------------------------------------
    # EVENTS
    # ---------------------------------------------------------
    def handle_event(self, event, window_rect):
        if event.type == pygame.MOUSEWHEEL:
            old_scroll = self.scroll
            self.scroll -= event.y * 30
            self.scroll = max(0, self.scroll)

            max_scroll = max(0, len(self.lines) * 24 + 40 - self.last_surface_height)

            if self.scroll < old_scroll:
                self.auto_scroll = False

            if self.scroll >= max_scroll - 5:
                self.auto_scroll = True

            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]

            elif event.key == pygame.K_RETURN:
                self.execute_command(self.input_text)
                self.input_text = ""

            else:
                if event.unicode and event.unicode.isprintable():
                    self.input_text += event.unicode

    # ---------------------------------------------------------
    # EXECUTE COMMAND
    # ---------------------------------------------------------
    def execute_command(self, cmd):
        cmd = cmd.strip()
        self.lines.append(self.prompt + cmd)
        self._log_command(cmd)

        if cmd == "":
            self.lines.append("")
            self._scroll_to_bottom()
            return

        parts = cmd.split()
        command = parts[0].lower()
        args = parts[1:]

        # Built-in fallback help
        if command == "help" and "help" not in self.commands:
            self.lines.append("Available commands:")
            for name in sorted(self.commands.keys()):
                self.lines.append(f"  {name}")
            self.lines.append("")
            self._scroll_to_bottom()
            return

        # Modular command
        if command in self.commands:
            try:
                self.commands[command](self, args)
            except Exception as e:
                self.lines.append(f"{command}: error: {e}")
            self.lines.append("")
            self._scroll_to_bottom()
            return

        # Unknown
        self.lines.append(f"Unknown command: {command}")
        self.lines.append("")
        self._scroll_to_bottom()

    # ---------------------------------------------------------
    # SCROLL
    # ---------------------------------------------------------
    def _scroll_to_bottom(self):
        if self.auto_scroll:
            total_height = len(self.lines) * 24 + 40
            self.scroll = max(0, total_height - self.last_surface_height)

    # ---------------------------------------------------------
    # LOGGING
    # ---------------------------------------------------------
    def _log_command(self, cmd):
        try:
            log_dir = os.path.dirname(self.LOG_PATH)
            os.makedirs(log_dir, exist_ok=True)
            with open(self.LOG_PATH, "a", encoding="utf-8") as f:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{timestamp}] {cmd}\n")
        except Exception:
            pass
