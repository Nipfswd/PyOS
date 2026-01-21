import os
import configparser

SETTINGS_PATH = os.path.join("config", "live", "PyOS", "settings.ini")

DEFAULT_SETTINGS = {
    "General": {
        "language": "en-US",
        "animations": "true"
    },
    "Personalization": {
        "wallpaper": "res/images/main/img0_3840x2160.jpg",
        "theme": "light"
    },
    "System": {
        "volume": "70"
    }
}


class SettingsManager:
    def __init__(self):
        self.config = configparser.ConfigParser()

        if not os.path.exists(SETTINGS_PATH):
            self.create_default_settings()
        else:
            self.config.read(SETTINGS_PATH)

    def create_default_settings(self):
        for section, values in DEFAULT_SETTINGS.items():
            self.config[section] = values

        os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
        with open(SETTINGS_PATH, "w") as f:
            self.config.write(f)

    def save(self):
        with open(SETTINGS_PATH, "w") as f:
            self.config.write(f)

    def get(self, section, key):
        return self.config.get(section, key)

    def set(self, section, key, value):
        self.config.set(section, key, str(value))
        self.save()
