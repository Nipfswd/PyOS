import os
from datetime import datetime

def log_error(message: str):
    """
    Write errors to $PWD/logs/boot/booterr/log<date><month><year>.log
    Creates directories automatically.
    """
    base = os.getcwd()
    log_dir = os.path.join(base, "logs", "boot", "booterr")

    # Ensure directory structure exists
    os.makedirs(log_dir, exist_ok=True)

    # Build filename
    now = datetime.now()
    filename = f"log{now.day}{now.month}{now.year}.log"
    log_path = os.path.join(log_dir, filename)

    # Append error entry
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{now}] {message}\n")
