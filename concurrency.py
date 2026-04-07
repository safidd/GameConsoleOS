import threading
import time

class SaveGameBuffer:
    def __init__(self, capacity=5):
        self.buffer = []
        self.capacity = capacity
        
        self.mutex = threading.Lock()
        
        self.not_full = threading.Condition(self.mutex)
        self.not_empty = threading.Condition(self.mutex)

    def produce(self, data):
        with self.not_full:
            while len(self.buffer) == self.capacity:
                print("[Concurrency] Buffer FULL. Render Thread BLOCKED.")
                self.not_full.wait()
            
            self.buffer.append(data)
            print(f"[Concurrency] Render Thread produced: '{data}'. Buffer size: {len(self.buffer)}")
            
            self.not_empty.notify()

    def consume(self):
        with self.not_empty:
            while len(self.buffer) == 0:
                print("[Concurrency] Buffer EMPTY. Save Thread BLOCKED.")
                self.not_empty.wait()
            
            data = self.buffer.pop(0)
            print(f"[Concurrency] Save Thread consumed: '{data}'. Buffer size: {len(self.buffer)}")
            
            self.not_full.notify()
            
            return data