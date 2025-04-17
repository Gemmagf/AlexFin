import json
import os

class Translator:
    def __init__(self, lang_code='en', translations_dir='translations'):
        self.lang_code = lang_code
        self.translations = {}
        self.translations_dir = translations_dir
        self.load_language(lang_code)

    def load_language(self, lang_code):
        path = os.path.join(self.translations_dir, f"{lang_code}.json")
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
        except FileNotFoundError:
            print(f"[WARN] Translation file not found: {path}. Falling back to empty.")
            self.translations = {}

    def gettext(self, key, default=None, **kwargs):
        value = self.translations.get(key, default or key)
        if kwargs:
            try:
                return value.format(**kwargs)
            except KeyError:
                return value  # fallback in case of bad format keys
        return value
