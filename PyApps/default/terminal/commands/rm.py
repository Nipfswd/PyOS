import os
from userspace.system.trash_manager import move_to_trash

def run(term, args):
    if not args:
        term.lines.append("Usage: rm <file>")
        term.lines.append("       rm -r <folder>")
        return

    recursive = False
    target_arg = args[0]

    if target_arg == "-r":
        if len(args) < 2:
            term.lines.append("Usage: rm -r <folder>")
            return
        recursive = True
        target_arg = args[1]

    target = term.vfs_abs(target_arg)

    if not os.path.exists(target):
        term.lines.append(f"rm: cannot remove '{target_arg}': No such file or directory")
        return

    if os.path.isdir(target) and not recursive:
        term.lines.append(f"rm: cannot remove '{target_arg}': Is a directory")
        term.lines.append("Use rm -r <folder> to remove directories")
        return

    try:
        move_to_trash(target)
        term.lines.append(f"Moved to trash: {target_arg}")
    except Exception as e:
        term.lines.append(f"rm error: {e}")
