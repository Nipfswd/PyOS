import os

def run(term, args):
    path = term.cwd if not args else term.vfs_abs(args[0])

    try:
        items = os.listdir(path)
    except Exception as e:
        term.lines.append(f"Error: {e}")
        return

    if not items:
        term.lines.append("Directory is empty")
        return

    items.sort()
    for name in items:
        full = os.path.join(path, name)
        if os.path.isdir(full):
            term.lines.append(f"<DIR>     {name}")
        else:
            size = os.path.getsize(full)
            term.lines.append(f"{size:8d}  {name}")
