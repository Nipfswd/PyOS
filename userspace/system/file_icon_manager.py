import os
import pygame

ICON_DIR = "res/images/main/fileicons"

DEFAULT_FILE_ICON = os.path.join(ICON_DIR, "file.png")
DEFAULT_FOLDER_ICON = os.path.join(ICON_DIR, "folder.png")

class FileIconManager:
    def __init__(self):
        self.cache = {}
        self.ext_map = {
            ".txt": "txt.png",
            ".py": "python.png",
            ".jpg": "image.png",
            ".jpeg": "image.png",
            ".png": "image.png",
            ".gif": "image.png",
            ".mp3": "audio.png",
            ".wav": "audio.png",
            ".mp4": "video.png",
            ".mov": "video.png",
            ".zip": "zip.png",
            ".rar": "zip.png",
            ".pdf": "pdf.png",
            ".json": "json.png",
            ".ini": "config.png",
        }

    def load_icon(self, filename):
        if filename in self.cache:
            return self.cache[filename]

        path = os.path.join(ICON_DIR, filename)
        if not os.path.exists(path):
            path = DEFAULT_FILE_ICON

        img = pygame.image.load(path).convert_alpha()
        img = pygame.transform.scale(img, (48, 48))
        self.cache[filename] = img
        return img

    def get_icon(self, path):
        if os.path.isdir(path):
            return self.load_icon(os.path.basename(DEFAULT_FOLDER_ICON))

        ext = os.path.splitext(path)[1].lower()
        if ext in self.ext_map:
            return self.load_icon(self.ext_map[ext])

        return self.load_icon(os.path.basename(DEFAULT_FILE_ICON))
