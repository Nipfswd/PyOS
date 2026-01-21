import os
import shutil

def run(term, args):
    if len(args) < 2:
        term.lines.append("Usage: xcopy <src> <dst>")
        return

    src_arg, dst_arg = args[0], args[1]
    src = term.vfs_abs(src_arg)
    dst = term.vfs_abs(dst_arg)

    if not os.path.exists(src):
        term.lines.append(f"xcopy: cannot stat '{src_arg}': No such file or directory")
        return

    if os.path.isfile(src):
        try:
            if os.path.isdir(dst):
                dst = os.path.join(dst, os.path.basename(src))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            term.lines.append(f"xcopy (file): {src_arg} -> {dst_arg}")
        except Exception as e:
            term.lines.append(f"xcopy error: {e}")
        return

    if os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(src))

    try:
        if os.path.exists(dst):
            term.lines.append(f"xcopy: destination '{dst_arg}' already exists")
        else:
            shutil.copytree(src, dst)
            term.lines.append(f"Copied directory: {src_arg} -> {dst_arg}")
    except Exception as e:
        term.lines.append(f"xcopy error: {e}")
