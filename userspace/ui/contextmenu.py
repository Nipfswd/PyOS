import pygame


class ContextMenu:
    def __init__(self, items, font):
        """
        items = [("Label", "command"), ...]
        """
        self.items = items
        self.font = font
        self.visible = False
        self.x = 0
        self.y = 0
        self.width = 180
        self.item_height = 26
        self.bg_color = (40, 40, 40)
        self.hover_color = (70, 70, 90)
        self.text_color = (230, 230, 230)
        self.border_color = (20, 20, 20)

    def open(self, x, y):
        self.visible = True
        self.x = x
        self.y = y

    def close(self):
        self.visible = False

    def draw(self, screen):
        if not self.visible:
            return

        height = len(self.items) * self.item_height
        rect = pygame.Rect(self.x, self.y, self.width, height)

        pygame.draw.rect(screen, self.bg_color, rect)
        pygame.draw.rect(screen, self.border_color, rect, 2)

        mouse_x, mouse_y = pygame.mouse.get_pos()

        for i, (label, cmd) in enumerate(self.items):
            item_rect = pygame.Rect(self.x, self.y + i * self.item_height, self.width, self.item_height)

            if item_rect.collidepoint(mouse_x, mouse_y):
                pygame.draw.rect(screen, self.hover_color, item_rect)

            text = self.font.render(label, True, self.text_color)
            screen.blit(text, (self.x + 8, self.y + i * self.item_height + 4))

    def handle_event(self, event):
        if not self.visible:
            return None

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = event.pos

            for i, (label, cmd) in enumerate(self.items):
                item_rect = pygame.Rect(self.x, self.y + i * self.item_height, self.width, self.item_height)
                if item_rect.collidepoint(mouse_x, mouse_y):
                    self.close()
                    return cmd

            # Click outside closes menu
            self.close()

        return None
