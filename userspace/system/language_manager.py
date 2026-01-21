import os
import json
from userspace.system.settings_manager import SettingsManager

LANG_ROOT = os.path.join("config", "live", "PyOS", "Languages")


class LanguageManager:
    def __init__(self):
        self.settings = SettingsManager()
        self.current_lang = self.settings.get("General", "language")
        self.strings = {}

        self.load_language(self.current_lang)

    def load_language(self, lang_code):
        path = os.path.join(LANG_ROOT, f"{lang_code}.json")

        if not os.path.exists(path):
            print(f"[LanguageManager] Missing language file: {path}")
            return

        with open(path, "r", encoding="utf-8") as f:
            self.strings = json.load(f)

    def get(self, key):
        return self.strings.get(key, f"[{key}]")

    def set_language(self, lang_code):
        self.settings.set("General", "language", lang_code)
        self.load_language(lang_code)
