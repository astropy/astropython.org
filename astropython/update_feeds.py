import os
import feedparser

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "astropython.settings")
    from main.utilities import update_feeds
    update_feeds()
