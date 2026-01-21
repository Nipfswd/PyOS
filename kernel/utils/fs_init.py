import os
import json

PYOS_ROOT = os.path.join("config", "live", "PyOS")

DIRS = {
    "system": [
        "System",
        "System/Kernel",
        "System/Drivers",
        "System/Config",
    ],
    "users": [
        "Users",
        "Users/admin",
        "Users/admin/Desktop",
        "Users/admin/Documents",
        "Users/admin/Downloads",
        "Users/admin/Trash",
    ],
    "apps": [
        "Apps",
        "Apps/Installed",
        "Apps/Shortcuts",
    ],
    "temp": [
        "Temp"
    ],
    "meta": [
        "Meta"
    ]
}

DEFAULT_FILES = {
    "Meta/users.json": {
        "users": [
            {
                "name": "admin",
                "home": "Users/admin",
                "desktop": "Users/admin/Desktop",
                "trash": "Users/admin/Trash"
            }
        ],
        "default": "admin"
    },

    "Meta/fs_index.json": {
        "version": 1,
        "root": "PyOS",
        "paths": {
            "system": "System",
            "users": "Users",
            "apps": "Apps",
            "temp": "Temp",
            "meta": "Meta"
        }
    },

    # Desktop shortcuts
    "Users/admin/Desktop/Trash.lnk": {
        "type": "shortcut",
        "target": "Users/admin/Trash",
        "icon": "trashbin.png",
        "app": "trashbin"
    },
    "Users/admin/Desktop/FileExplorer.lnk": {
        "type": "shortcut",
        "target": "Users/admin",
        "icon": "fileexplorer.png",
        "app": "fileexplorer"
    },

    # App registry
    "Apps/Installed/trashbin.json": {
        "name": "Trash Bin",
        "exec": "PyApps/default/trashbin.py",
        "icon": "trashbin.png",
        "type": "system"
    },
    "Apps/Installed/fileexplorer.json": {
        "name": "File Explorer",
        "exec": "PyApps/default/fileexplorer.py",
        "icon": "fileexplorer.png",
        "type": "system"
    }
}


def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def init_pyfs():
    os.makedirs(PYOS_ROOT, exist_ok=True)

    # Create directories
    for group in DIRS.values():
        for d in group:
            os.makedirs(os.path.join(PYOS_ROOT, d), exist_ok=True)

    # Create default files
    for rel_path, content in DEFAULT_FILES.items():
        abs_path = os.path.join(PYOS_ROOT, rel_path)
        if not os.path.exists(abs_path):
            write_json(abs_path, content)

    # System README
    readme_path = os.path.join(PYOS_ROOT, "System", "README.txt")
    if not os.path.exists(readme_path):
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(
                "PyOS System Directory\n"
                "----------------------\n"
                "This directory contains core OS components.\n"
            )

    # Desktop metadata
    desktop_info = os.path.join(PYOS_ROOT, "Users/admin/Desktop/desktop.json")
    if not os.path.exists(desktop_info):
        write_json(desktop_info, {
            "desktop_version": 1,
            "icons": [
                {
                    "name": "Trash",
                    "file": "Trash.lnk",
                    "icon": "trashbin.png",
                    "type": "shortcut"
                },
                {
                    "name": "File Explorer",
                    "file": "FileExplorer.lnk",
                    "icon": "fileexplorer.png",
                    "type": "shortcut"
                }
            ]
        })
