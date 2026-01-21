def run(term, args):
    term.lines.append("Available commands:")
    for name in sorted(term.commands.keys()):
        term.lines.append(f"  {name}")
