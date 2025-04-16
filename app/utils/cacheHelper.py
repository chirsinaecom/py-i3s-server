from fastapi_cache.decorator import cache
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
# from main import home
FastAPICache.init(InMemoryBackend(), prefix="slpk-cache")

cache = cache
