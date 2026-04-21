import threading
import time
from concurrency import SaveGameBuffer

def render_thread(buffer):
    print("[System] Render Thread started...")
    for i in range(1, 8): # Simulate generating 7 game frames
        frame_data = f"Frame_{i}"
        buffer.produce(frame_data)
        time.sleep(0.5) # Renders fast (0.5 seconds)

def save_thread(buffer):
    print("[System] Save Thread started...")
    for i in range(1, 8): # Simulate saving 7 game frames
        time.sleep(1.5) # Saves slowly (1.5 seconds)
        data = buffer.consume()

if __name__ == "__main__":
    print("--- Starting Game Console OS Concurrency Test ---")
    
    # We set a small capacity of 3 to easily force a buffer overflow scenario
    game_buffer = SaveGameBuffer(capacity=3)

    # Initialize the two independent threads
    t1 = threading.Thread(target=render_thread, args=(game_buffer,))
    t2 = threading.Thread(target=save_thread, args=(game_buffer,))

    # Start them simultaneously
    t1.start()
    t2.start()

    # Wait for both to finish before closing the program
    t1.join()
    t2.join()
    
    print("--- Concurrency Test Complete ---")