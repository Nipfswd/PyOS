import os

def run(term, args):
    if not args:
        term.lines.append("Usage: cd <path>")
        return

    target = term.vfs_abs(args[0])
    if os.path.isdir(target):
        term.cwd = target
        term.update_prompt()
        term.lines.append(f"Changed directory to {term.cwd}")
    else:
        term.lines.append(f"Directory not found: {args[0]}")
