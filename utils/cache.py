import asyncio
import os
import json
import aiofiles
import time
from .errors import (
   CacheExpired,
   CacheNotFound
)

CACHE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/.cache"))

class JSONCacheManager:
    """
    CacheManager lets you easily enable and create cache/temporary files and get them with ease
    
    Under the hood, cache files are JSON files that just store data and have an expiration time (then they are deleted)
    """
    def __init__(
        self,
        cache_file: str,
        expiration_time: int = 60 * 60 * 24 * 30 # a month, in seconds
    ) -> None:
        self.cache_file = os.path.abspath(os.path.join(CACHE_DIR, cache_file))
        try:
            os.mkdir(CACHE_DIR)
        except:
            pass
        
        self.expiration_time = expiration_time
        self.create_file()
    
    def create_file(self) -> None:
        try:
            with open(self.cache_file, mode="r") as _: pass
        except:
            print("Creating cache file...")
            with open(self.cache_file, mode="w") as f: 
                f.write("{}")

    
    async def save(self, key: str, data: dict) -> None:
        async with aiofiles.open(self.cache_file, mode="r") as f:
            content = json.loads(await f.read())
        
        content[key] = data
        content[key]["expiration"] = round(time.time()) + self.expiration_time
        
        async with aiofiles.open(self.cache_file, mode="w") as f:
            saved = json.dumps(content)
            await f.write(saved)    
        
    
    async def get_cache_file(self) -> dict:
        async with aiofiles.open(self.cache_file, mode="r") as f:
            return json.loads(await f.read())

    async def get(self, key: str) -> dict:
        filecontents = await self.get_cache_file()
        
        try:
            if filecontents[key]["expiration"] < round(time.time()): 
                del filecontents[key]
                # set without setting expiration
                async with aiofiles.open(self.cache_file, mode="w") as f:
                    await f.write(json.dumps(filecontents))
                
                raise CacheExpired
                # return None
            
            return filecontents[key]
        except KeyError:
            raise CacheNotFound
            # return None
