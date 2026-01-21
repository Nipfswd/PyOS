import os
import pygame
import datetime
import traceback

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "full_log.txt")


class LogAll:
    def __init__(self):
        os.makedirs(LOG_DIR, exist_ok=True)
        self.file = open(LOG_FILE, "a", encoding="utf-8")
        self.start_time = datetime.datetime.now()

        self.log("========== LOGGER STARTED ==========")
        self.log(f"Start time: {self.start_time}")
        self.log("====================================")

    # ---------------------------------------------------------
    # CORE LOGGING
    # ---------------------------------------------------------
    def log(self, text):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        line = f"[{timestamp}] {text}"

        print(line)
        self.file.write(line + "\n")
        self.file.flush()

    # ---------------------------------------------------------
    # EVENT LOGGING
    # ---------------------------------------------------------
    def log_event(self, event):
        """Logs every pygame event."""
        if hasattr(event, "pos"):
            self.log(f"EVENT: type={event.type} btn={getattr(event, 'button', None)} pos={event.pos} rel={getattr(event, 'rel', None)}")
        else:
            self.log(f"EVENT: type={event.type}")

    def log_desktop_event(self, desktop_event):
        """Logs desktop icon actions."""
        self.log(f"DESKTOP_ACTION: {desktop_event}")

    def log_window_event(self, win, event):
        """Logs window-level events."""
        self.log(f"WINDOW_EVENT: {win['app'].__class__.__name__} type={event.type} pos={getattr(event, 'pos', None)}")

    def log_app_event(self, app, event):
        """Logs events forwarded to apps."""
        if hasattr(event, "pos"):
            self.log(f"APP_EVENT: {app.__class__.__name__} type={event.type} btn={getattr(event, 'button', None)} pos={event.pos}")
        else:
            self.log(f"APP_EVENT: {app.__class__.__name__} type={event.type}")

    # ---------------------------------------------------------
    # WINDOW MANAGEMENT LOGGING
    # ---------------------------------------------------------
    def log_window_created(self, win):
        self.log(f"WINDOW_CREATED: {win['app'].__class__.__name__} at {win['rect']}")

    def log_window_closed(self, win):
        self.log(f"WINDOW_CLOSED: {win['app'].__class__.__name__}")

    def log_window_focus(self, win):
        self.log(f"WINDOW_FOCUS: {win['app'].__class__.__name__}")

    def log_window_drag(self, win, pos):
        self.log(f"WINDOW_DRAG: {win['app'].__class__.__name__} pos={pos}")

    def log_window_resize(self, win, rect):
        self.log(f"WINDOW_RESIZE: {win['app'].__class__.__name__} rect={rect}")

    # ---------------------------------------------------------
    # UI ELEMENT LOGGING
    # ---------------------------------------------------------
    def log_taskbar(self, action):
        self.log(f"TASKBAR_ACTION: {action}")

    def log_startmenu(self, action):
        self.log(f"STARTMENU_ACTION: {action}")

    def log_contextmenu(self, action):
        self.log(f"CONTEXTMENU_ACTION: {action}")

    # ---------------------------------------------------------
    # PERFORMANCE LOGGING
    # ---------------------------------------------------------
    def log_fps(self, fps):
        self.log(f"FPS: {fps}")

    # ---------------------------------------------------------
    # ERROR LOGGING
    # ---------------------------------------------------------
    def log_exception(self, e):
        self.log("EXCEPTION:")
        self.log(str(e))
        tb = traceback.format_exc()
        for line in tb.split("\n"):
            self.log(line)

    # ---------------------------------------------------------
    # CLEANUP
    # ---------------------------------------------------------
    def close(self):
        self.log("========== LOGGER STOPPED ==========")
        self.file.close()
