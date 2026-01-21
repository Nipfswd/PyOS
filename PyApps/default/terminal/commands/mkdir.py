import os

def run(term, args):
    if not args:
        term.lines.append("Usage: mkdir <foldername>")
        return

    path = term.vfs_abs(args[0])
    try:
        os.makedirs(path, exist_ok=True)
        term.lines.append(f"Created folder: {path}")
    except Exception as e:
        term.lines.append(f"Error: {e}")
