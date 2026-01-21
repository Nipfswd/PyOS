def run(term, args):
    if not args or len(args[0]) != 2:
        term.lines.append("Usage: color XY")
        term.lines.append("X = background, Y = foreground")
        term.lines.append("Hex digits 0-F")
        return

    code = args[0].upper()
    bg = code[0]
    fg = code[1]

    colors = {
        "0": (0, 0, 0),
        "1": (0, 0, 170),
        "2": (0, 170, 0),
        "3": (0, 170, 170),
        "4": (170, 0, 0),
        "5": (170, 0, 170),
        "6": (170, 85, 0),
        "7": (170, 170, 170),
        "8": (85, 85, 85),
        "9": (85, 85, 255),
        "A": (85, 255, 85),
        "B": (85, 255, 255),
        "C": (255, 85, 85),
        "D": (255, 85, 255),
        "E": (255, 255, 85),
        "F": (255, 255, 255),
    }

    if bg not in colors or fg not in colors:
        term.lines.append("color: invalid code (must be 0-F)")
        return

    term.bg_color = colors[bg]
    term.text_color = colors[fg]

    term.lines.append(f"Color set: background={bg}, foreground={fg}")
