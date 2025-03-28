import os
import json
import datetime
from filelock import FileLock, Timeout
from ..memory_mapping import MEMORY_MAPPER,CREATED_AT

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEMORY_FILE = os.path.join(BASE_DIR, "..", "memory.json")

LOCK_FILE = MEMORY_FILE + ".lock"



def load_file():
    lock = FileLock(LOCK_FILE, timeout=5)
    try:
        with lock:
            try:
                with open(MEMORY_FILE, "r") as f:
                    memory = json.load(f)
                    return memory

            except:
                return {
                    MEMORY_MAPPER["SHORT_TERM"] : [],
                    MEMORY_MAPPER["MEDIUM_TERM"] : [],
                    MEMORY_MAPPER["LONG_TERM"] : {}
                }
    except Timeout:
        print("Could not acquire memory file lock. Another process is using it.")


def save_memory(memory):
    lock = FileLock(LOCK_FILE, timeout=5)
    try:
        with lock:
            with open(MEMORY_FILE, "w") as f:
                json.dump(memory, f, indent=2)

    except Timeout:
        print("Could not acquire memory file lock. Another process is using it.")


def update_memory(new_memories):
    """We use this function to update
    memories of exsiting memories"""

    memory = load_file()

    if memory is None:
        return

    for item in new_memories.get(MEMORY_MAPPER["SHORT_TERM"],[]):
        if CREATED_AT not in item:
            item[CREATED_AT] = datetime.datetime.now().isoformat()
        memory[MEMORY_MAPPER["SHORT_TERM"]].append(item)
    
    for item in new_memories.get(MEMORY_MAPPER["MEDIUM_TERM"],[]):
        if CREATED_AT not in item:
            item[CREATED_AT] = datetime.datetime.now().isoformat()
        memory[MEMORY_MAPPER["MEDIUM_TERM"]].append(item)
    
    for key, value in new_memories.get(MEMORY_MAPPER["LONG_TERM"], {}).items():
        memory[MEMORY_MAPPER["LONG_TERM"]][key] = value


    save_memory(memory)






    

