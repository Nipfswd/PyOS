import os
import pygame
import urllib.request
import urllib.parse
from html.parser import HTMLParser

FONT_PATH = os.path.join("res", "fonts", "msa", "Ac437_TridentEarly_8x14.ttf")


# ---------------------------------------------------------
# SIMPLE HTML MODEL
# ---------------------------------------------------------
class Node:
    def __init__(self, tag, attrs=None, parent=None):
        self.tag = tag
        self.attrs = attrs or {}
        self.children = []
        self.text = ""
        self.parent = parent

    def append_child(self, node):
        self.children.append(node)

    def add_text(self, text):
        self.text += text


class DOMBuilder(HTMLParser):
    def __init__(self):
        super().__init__()
        self.root = Node("document")
        self.current = self.root

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        node = Node(tag.lower(), attrs_dict, parent=self.current)
        self.current.append_child(node)
        self.current = node

    def handle_endtag(self, tag):
        tag = tag.lower()
        while self.current is not None and self.current.tag != tag:
            self.current = self.current.parent
        if self.current is not None:
            self.current = self.current.parent or self.root

    def handle_data(self, data):
        if data.strip():
            self.current.add_text(data)

    def parse(self, html):
        self.root = Node("document")
        self.current = self.root
        self.feed(html)
        return self.root


# ---------------------------------------------------------
# STYLE HELPERS
# ---------------------------------------------------------
def parse_style(style_str):
    styles = {}
    for part in style_str.split(";"):
        if ":" in part:
            k, v = part.split(":", 1)
            styles[k.strip().lower()] = v.strip()
    return styles


def color_from_css(value):
    value = value.strip().lower()
    if value.startswith("#") and len(value) in (4, 7):
        try:
            if len(value) == 4:
                r = int(value[1] * 2, 16)
                g = int(value[2] * 2, 16)
                b = int(value[3] * 2, 16)
            else:
                r = int(value[1:3], 16)
                g = int(value[3:5], 16)
                b = int(value[5:7], 16)
            return (r, g, b)
        except Exception:
            return (0, 0, 0)
    named = {
        "black": (0, 0, 0),
        "white": (255, 255, 255),
        "red": (220, 0, 0),
        "green": (0, 160, 0),
        "blue": (0, 0, 220),
        "gray": (120, 120, 120),
        "grey": (120, 120, 120),
    }
    return named.get(value, (0, 0, 0))


# ---------------------------------------------------------
# LAYOUT ENGINE (VERY SIMPLE)
# ---------------------------------------------------------
class LayoutBox:
    def __init__(self, kind, rect, surf=None, href=None):
        self.kind = kind      # "text" or "image"
        self.rect = rect      # pygame.Rect
        self.surf = surf      # pygame.Surface
        self.href = href      # for links


class PyBrowApp:
    def __init__(self):
        self.font_base = pygame.font.Font(FONT_PATH, 18)
        self.VFS_ROOT = os.path.normpath(os.path.join("config", "live", "PyOS"))

        # Address bar
        self.address = "http://example.com"
        self.address_active = False
        self.address_cursor = len(self.address)

        # History
        self.history = []
        self.history_index = -1

        # Page
        self.html = ""
        self.dom = None
        self.layout_boxes = []
        self.scroll = 0
        self.last_surface_height = 0

        # Link hitboxes
        self.link_boxes = []  # list of (rect, href)

        # Load initial page
        self.load_url(self.address, add_history=True)

    # ---------------------------------------------------------
    # VFS + NETWORK
    # ---------------------------------------------------------
    def vfs_abs(self, path):
        if not path.startswith("/"):
            path = "/" + path
        full = os.path.normpath(os.path.join(self.VFS_ROOT, path.lstrip("/")))
        if not full.startswith(self.VFS_ROOT):
            return self.VFS_ROOT
        return full

    def fetch_url(self, url):
        url = url.strip()
        if url.startswith("file://"):
            path = url[len("file://") :]
            path = self.vfs_abs(path)
            if not os.path.exists(path):
                return f"<h1>404 Not Found</h1><p>{url}</p>"
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                return f"<h1>Error</h1><p>{e}</p>"

        if url.startswith("/") and not url.startswith("//"):
            path = self.vfs_abs(url)
            if not os.path.exists(path):
                return f"<h1>404 Not Found</h1><p>{url}</p>"
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                return f"<h1>Error</h1><p>{e}</p>"

        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url

        try:
            with urllib.request.urlopen(url, timeout=5) as resp:
                content_type = resp.headers.get("Content-Type", "")
                charset = "utf-8"
                if "charset=" in content_type:
                    charset = content_type.split("charset=")[-1].split(";")[0].strip()
                data = resp.read()
                return data.decode(charset, errors="replace")
        except Exception as e:
            return f"<h1>Network Error</h1><p>{e}</p>"

    # ---------------------------------------------------------
    # LOAD URL
    # ---------------------------------------------------------
    def load_url(self, url, add_history=True):
        self.address = url
        self.address_cursor = len(self.address)

        if add_history:
            if self.history_index < len(self.history) - 1:
                self.history = self.history[: self.history_index + 1]
            self.history.append(url)
            self.history_index = len(self.history) - 1

        self.html = self.fetch_url(url)

        parser = DOMBuilder()
        self.dom = parser.parse(self.html)

        self._layout_page()

    # ---------------------------------------------------------
    # LAYOUT PAGE
    # ---------------------------------------------------------
    def _layout_page(self):
        self.layout_boxes = []
        self.link_boxes = []
        self.scroll = 0

        x_margin = 20
        y = 50  # below address bar
        max_width = 800  # will be clamped in update

        def walk(node, current_style, current_href):
            nonlocal y

            tag = node.tag
            style = dict(current_style)
            href = current_href

            if "style" in node.attrs:
                inline = parse_style(node.attrs["style"])
                if "color" in inline:
                    style["color"] = color_from_css(inline["color"])
                if "font-size" in inline:
                    try:
                        style["size"] = int(inline["font-size"].replace("px", "").strip())
                    except Exception:
                        pass

            if tag in ("b", "strong"):
                style["bold"] = True
            if tag in ("i", "em"):
                style["italic"] = True
            if tag == "u":
                style["underline"] = True
            if tag in ("h1", "h2", "h3", "h4"):
                style["bold"] = True
                style["size"] = {"h1": 28, "h2": 24, "h3": 20, "h4": 18}[tag]
                y += 10
            if tag in ("p", "div"):
                y += 6
            if tag in ("ul", "ol"):
                y += 4
            if tag == "br":
                y += style["size"] + 4
            if tag == "a":
                href = node.attrs.get("href", href)
                style["color"] = (0, 0, 220)
                style["underline"] = True

            if tag == "img":
                src = node.attrs.get("src", "")
                img_surf = self._load_image(src)
                if img_surf:
                    rect = img_surf.get_rect()
                    rect.x = x_margin
                    rect.y = y
                    self.layout_boxes.append(LayoutBox("image", rect, img_surf, href=None))
                    y += rect.height + 8

            if node.text.strip():
                text = node.text.strip()
                font = pygame.font.Font(FONT_PATH, style["size"])
                font.set_bold(style.get("bold", False))
                font.set_italic(style.get("italic", False))

                color = style.get("color", (0, 0, 0))

                words = text.split(" ")
                line = ""
                x = x_margin

                for w in words:
                    test = (line + " " + w).strip()
                    surf = font.render(test, True, color)
                    if surf.get_width() > max_width and line:
                        line_surf = font.render(line, True, color)
                        rect = line_surf.get_rect()
                        rect.x = x
                        rect.y = y
                        box = LayoutBox("text", rect, line_surf, href=href)
                        self.layout_boxes.append(box)
                        if href:
                            self.link_boxes.append((rect, href))
                        y += style["size"] + 4
                        line = w
                    else:
                        line = test

                if line:
                    line_surf = font.render(line, True, color)
                    rect = line_surf.get_rect()
                    rect.x = x
                    rect.y = y
                    box = LayoutBox("text", rect, line_surf, href=href)
                    self.layout_boxes.append(box)
                    if href:
                        self.link_boxes.append((rect, href))
                    y += style["size"] + 6

            for child in node.children:
                walk(child, style, href)

            if tag in ("h1", "h2", "h3", "h4", "p", "div", "ul", "ol"):
                y += 4

        base_style = {
            "size": 18,
            "bold": False,
            "italic": False,
            "underline": False,
            "color": (0, 0, 0),
        }
        for child in self.dom.children:
            walk(child, base_style, None)

    def _load_image(self, src):
        src = src.strip()
        if not src:
            return None

        if src.startswith("http://") or src.startswith("https://"):
            try:
                with urllib.request.urlopen(src, timeout=5) as resp:
                    data = resp.read()
                import io

                img_file = io.BytesIO(data)
                return pygame.image.load(img_file).convert_alpha()
            except Exception:
                return None

        if src.startswith("file://"):
            path = src[len("file://") :]
            path = self.vfs_abs(path)
        elif src.startswith("/"):
            path = self.vfs_abs(src)
        else:
            path = self.vfs_abs(src)

        if not os.path.exists(path):
            return None

        try:
            return pygame.image.load(path).convert_alpha()
        except Exception:
            return None

    # ---------------------------------------------------------
    # UPDATE / DRAW
    # ---------------------------------------------------------
    def update(self, surface, mouse_pos):
        self.last_surface_height = surface.get_height()
        surface.fill((255, 255, 255))

        width = surface.get_width()

        pygame.draw.rect(surface, (230, 230, 230), (0, 0, width, 30))
        pygame.draw.rect(surface, (200, 200, 200), (10, 5, width - 20, 20), 1)

        addr_font = pygame.font.Font(FONT_PATH, 16)
        addr_text = addr_font.render(self.address, True, (0, 0, 0))
        surface.blit(addr_text, (14, 7))

        if self.address_active:
            cursor_x = 14 + addr_font.size(self.address[: self.address_cursor])[0]
            pygame.draw.line(
                surface, (0, 0, 0), (cursor_x, 7), (cursor_x, 7 + 18), 1
            )

        pygame.draw.rect(
            surface,
            (245, 245, 245),
            (0, 30, width, surface.get_height() - 30),
        )

        y_offset = 30 - self.scroll
        for box in self.layout_boxes:
            surface.blit(box.surf, (box.rect.x, box.rect.y + y_offset))

    # ---------------------------------------------------------
    # EVENTS
    # ---------------------------------------------------------
    def handle_event(self, event, window_rect):
        if event.type == pygame.MOUSEBUTTONDOWN:
            local_x = event.pos[0] - window_rect.x
            local_y = event.pos[1] - (window_rect.y + 30)

            if 5 <= local_y <= 25:
                self.address_active = True
            else:
                self.address_active = False

                if local_y >= 30:
                    click_y = local_y + self.scroll
                    click_pos = (local_x, click_y)
                    for rect, href in self.link_boxes:
                        if rect.collidepoint(click_pos) and href:
                            new_url = urllib.parse.urljoin(self.address, href)
                            self.load_url(new_url, add_history=True)
                            break

        if event.type == pygame.MOUSEWHEEL:
            self.scroll -= event.y * 40
            self.scroll = max(0, self.scroll)
            return

        if event.type == pygame.KEYDOWN:
            if self.address_active:
                if event.key == pygame.K_BACKSPACE:
                    if self.address_cursor > 0:
                        self.address = (
                            self.address[: self.address_cursor - 1]
                            + self.address[self.address_cursor :]
                        )
                        self.address_cursor -= 1

                elif event.key == pygame.K_LEFT:
                    if self.address_cursor > 0:
                        self.address_cursor -= 1

                elif event.key == pygame.K_RIGHT:
                    if self.address_cursor < len(self.address):
                        self.address_cursor += 1

                elif event.key == pygame.K_RETURN:
                    self.load_url(self.address, add_history=True)

                else:
                    if event.unicode and event.unicode.isprintable():
                        self.address = (
                            self.address[: self.address_cursor]
                            + event.unicode
                            + self.address[self.address_cursor :]
                        )
                        self.address_cursor += 1

            else:
                if event.key == pygame.K_BACKSPACE:
                    pass

                elif event.key == pygame.K_LEFT:
                    if self.history_index > 0:
                        self.history_index -= 1
                        self.load_url(self.history[self.history_index], add_history=False)

                elif event.key == pygame.K_RIGHT:
                    if self.history_index < len(self.history) - 1:
                        self.history_index += 1
                        self.load_url(self.history[self.history_index], add_history=False)
