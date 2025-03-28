import json
import os
from datetime import datetime, timedelta
from filelock import FileLock, Timeout
from ..memory_mapping import MEMORY_MAPPER

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEMORY_FILE = os.path.join(BASE_DIR, "..", "memory.json")

LOCK_FILE = MEMORY_FILE + ".lock"


def parse_time(ts):
    try:
        return datetime.fromisoformat(ts)
    except:
        return datetime.min  # ensures old/corrupt entries are dropped

def prune_entries(entries, expiry_duration):
    now = datetime.now()
    threshold = now - expiry_duration
    return [entry for entry in entries if parse_time(entry.get("created_at", "")) > threshold]

def prune_memory(memory):
    memory["short_term"] = prune_entries(memory.get(MEMORY_MAPPER["SHORT_TERM"], []), timedelta(hours=24))
    memory["medium_term"] = prune_entries(memory.get(MEMORY_MAPPER["MEDIUM_TERM"], []), timedelta(days=30))
    return memory


def main():
    lock = FileLock(LOCK_FILE, timeout=5)
    try:
        with lock:
            with open(MEMORY_FILE, "r") as f:
                memory = json.load(f)

            cleaned = prune_memory(memory)

            with open(MEMORY_FILE, "w") as f:
                json.dump(cleaned, f, indent=2)

            print("Memory cleaned and saved successfully.")
    except Timeout:
        print("Could not acquire memory file lock. Another process is using it.")


if __name__ == "__main__":
    main()
