import os
import shutil

def run(term, args):
    if len(args) < 2:
        term.lines.append("Usage: copy <src> <dst>")
        return

    src_arg, dst_arg = args[0], args[1]
    src = term.vfs_abs(src_arg)
    dst = term.vfs_abs(dst_arg)

    if not os.path.exists(src):
        term.lines.append(f"copy: cannot stat '{src_arg}': No such file or directory")
        return

    if os.path.isdir(src):
        term.lines.append(f"copy: '{src_arg}' is a directory (use xcopy)")
        return

    if os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(src))

    try:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        term.lines.append(f"Copied file: {src_arg} -> {dst_arg}")
    except Exception as e:
        term.lines.append(f"copy error: {e}")
