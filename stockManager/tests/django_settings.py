"""Django 测试配置：与业务 settings 隔离，强制内存缓存与测试密钥。"""
# pyright: reportWildcardImportFromLibrary=false
import os

os.environ["DJANGO_SECRET_KEY"] = "test-secret-not-for-production"
os.environ.setdefault("DJANGO_DEBUG", "true")
os.environ.setdefault("REDIS_URL", "redis://127.0.0.1:6379/15")

from stockManager.settings import *  # noqa: E402, F403

SECRET_KEY = "test-secret-not-for-production"
DEBUG = True
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "stockmanager-tests",
    }
}
