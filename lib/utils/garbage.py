import gc
import threading
import time
from ..logger import logger
import asyncio

@logger.LoggerApplication
class GarbageCollector:
    def __init__(self, collect_time: int, logger: logger.Logger):
        """
        Note: collect_time should be an int representing time beetween collecting in seconds
        """
        self.collect_time = collect_time # time beetween collections
        self.logger = logger
        self.closed = False
        gc.set_threshold(1000,50,30)

        self._start()

    def _start(self):
        self.logger.info(f"GC starting... (monitoring results every {self.collect_time/60:.1f} min)")
        thread = threading.Thread(target=asyncio.run, args=(self.monitor(),))
        thread.start()
        self.logger.info("Thread ready, monitoring enabled")

    def close(self):
        self.closed = True
        self.logger.warn("GC monitor disabled, no further results will be collected.")

    async def monitor(self):
        while True:
            should_break = False
            for _ in range(self.collect_time): 
                if self.closed:
                    should_break = True
                    break
                await asyncio.sleep(1)    
            if should_break: break
            await self.get_results()

    async def get_results(self):
        before = gc.get_count()
        collected = gc.collect()
        buckets = gc.get_count()
        collected_garbage = sum(before) - sum(buckets)
        
        if collected_garbage <= 100:
            self.logger.info(f"Suspiciously small amount of garbage, buckets: {before}, collected {collected_garbage}")
            
        self.logger.debug(f"Collected garbage results: {before} -> {buckets}, collected {collected_garbage} ({collected})")
            