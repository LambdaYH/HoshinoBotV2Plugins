import sqlite3
import random


class ImageData:
    def __init__(self, db_path):
        self.db_path = db_path
        self.imageCache = {}
        self._cache_ImageLinks()

    def _connect(self):
        return sqlite3.connect(self.db_path).cursor()

    def _get_categories(self):
        r = (
            self._connect()
            .execute("SELECT name FROM sqlite_master WHERE type='table' order by name")
            .fetchall()
        )
        return r

    def _cache_ImageLinks(self):
        categories = self._get_categories()
        for category in categories:
            cat = category[0].replace("IMAGELINK", "", 1)
            self.imageCache[cat] = []
            r = self._connect().execute(f"SELECT LINK FROM {cat}IMAGELINK").fetchall()
            for img in r:
                self.imageCache[cat].append(img[0])
            random.shuffle(self.imageCache[cat])

    async def _get_random_image(self, table):
        return random.choice(self.imageCache[table])
