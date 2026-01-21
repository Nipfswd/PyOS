def run(term, args):
    if not args:
        term.lines.append("Usage: start <appname>")
        term.lines.append("Apps: notepad, fileexplorer, terminal, settings, trashbin")
        return

    app = args[0].lower()

    valid = ["notepad", "fileexplorer", "terminal", "settings", "trashbin"]

    if app not in valid:
        term.lines.append(f"start: unknown app '{app}'")
        return

    # Signal to desktop_init.py
    term.last_command_result = ("start_app", app)

    term.lines.append(f"Starting {app}...")
