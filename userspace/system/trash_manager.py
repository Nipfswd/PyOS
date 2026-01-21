import os
import shutil
import json
import time

TRASH_ROOT = os.path.join("config", "live", "PyOS", "$Trash.Bin")
FILES_DIR = os.path.join(TRASH_ROOT, "files")
META_FILE = os.path.join(TRASH_ROOT, "index.json")


def _ensure_trash_dirs():
    os.makedirs(FILES_DIR, exist_ok=True)
    if not os.path.exists(META_FILE):
        with open(META_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)


def _load_index():
    _ensure_trash_dirs()
    try:
        with open(META_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_index(index):
    os.makedirs(TRASH_ROOT, exist_ok=True)
    with open(META_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)


def move_to_trash(path):
    """
    Move a file or folder to $Trash.Bin and record metadata.
    Returns trash_id or None on failure.
    """
    _ensure_trash_dirs()

    if not os.path.exists(path):
        return None

    index = _load_index()

    trash_id = str(int(time.time() * 1000))
    base_name = os.path.basename(path)
    trash_name = f"{trash_id}_{base_name}"
    trash_path = os.path.join(FILES_DIR, trash_name)

    try:
        if os.path.isdir(path):
            shutil.move(path, trash_path)
        else:
            shutil.move(path, trash_path)
    except Exception:
        return None

    index[trash_id] = {
        "original_path": os.path.abspath(path),
        "trash_path": trash_path,
        "name": base_name,
        "is_dir": os.path.isdir(trash_path),
        "deleted_at": time.time(),
    }

    _save_index(index)
    return trash_id


def list_trash():
    """
    Returns a list of entries:
    { 'id', 'name', 'original_path', 'is_dir', 'deleted_at' }
    """
    index = _load_index()
    items = []
    for tid, data in index.items():
        items.append({
            "id": tid,
            "name": data.get("name"),
            "original_path": data.get("original_path"),
            "is_dir": data.get("is_dir", False),
            "deleted_at": data.get("deleted_at", 0),
        })
    return items


def restore(trash_id):
    """
    Restore an item from trash to its original path.
    Returns True on success, False otherwise.
    """
    index = _load_index()
    if trash_id not in index:
        return False

    entry = index[trash_id]
    trash_path = entry["trash_path"]
    original_path = entry["original_path"]

    # Ensure parent exists
    parent = os.path.dirname(original_path)
    os.makedirs(parent, exist_ok=True)

    # If something already exists there, append (restored)
    target = original_path
    if os.path.exists(target):
        base = os.path.basename(original_path)
        parent = os.path.dirname(original_path)
        name, ext = os.path.splitext(base)
        i = 1
        while True:
            candidate = os.path.join(parent, f"{name} (restored {i}){ext}")
            if not os.path.exists(candidate):
                target = candidate
                break
            i += 1

    try:
        shutil.move(trash_path, target)
    except Exception:
        return False

    # Remove from index
    del index[trash_id]
    _save_index(index)
    return True


def delete_permanently(trash_id):
    """
    Permanently delete a single item from trash.
    """
    index = _load_index()
    if trash_id not in index:
        return False

    entry = index[trash_id]
    trash_path = entry["trash_path"]

    try:
        if os.path.isdir(trash_path):
            shutil.rmtree(trash_path)
        elif os.path.exists(trash_path):
            os.remove(trash_path)
    except Exception:
        return False

    del index[trash_id]
    _save_index(index)
    return True


def empty_trash():
    """
    Permanently delete everything in $Trash.Bin.
    """
    index = _load_index()
    for tid, entry in list(index.items()):
        trash_path = entry["trash_path"]
        try:
            if os.path.isdir(trash_path):
                shutil.rmtree(trash_path)
            elif os.path.exists(trash_path):
                os.remove(trash_path)
        except Exception:
            pass
        if tid in index:
            del index[tid]
    _save_index(index)
