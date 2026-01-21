import os

def run(term, args):
    path = term.cwd if not args else term.vfs_abs(args[0])

    if not os.path.exists(path):
        if args:
            term.lines.append(f"tree: path not found: {args[0]}")
        else:
            term.lines.append("tree: path not found")
        return

    def walk(p, prefix=""):
        try:
            items = sorted(os.listdir(p))
        except Exception:
            return

        for i, name in enumerate(items):
            full = os.path.join(p, name)
            is_last = (i == len(items) - 1)

            branch = "└── " if is_last else "├── "
            term.lines.append(prefix + branch + name)

            if os.path.isdir(full):
                extension = "    " if is_last else "│   "
                walk(full, prefix + extension)

    term.lines.append(path.replace(term.VFS_ROOT, "/"))
    walk(path)
