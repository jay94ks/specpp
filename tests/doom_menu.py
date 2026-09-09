"""examples/doom/menu.md 의 # Domain/# Behavior 참조 구현."""


class MenuItem:
    def __init__(self, label, kind, action=None, submenu=None):
        self.label = label
        self.kind = kind  # "Action" | "Toggle" | "Slider" | "Submenu"
        self.action = action
        self.submenu = submenu
        self.toggleValue = False
        self.sliderValue = 0


class Menu:
    def __init__(self, title, items):
        self.title = title
        self.items = items
        self.selectedIndex = 0


class MenuStack:
    def __init__(self):
        self.stack = []

    @property
    def isOpen(self):
        return len(self.stack) > 0

    # spp-source: examples/doom/menu.md#Feature:_메뉴_열기/닫기
    def open(self, rootMenu):
        self.stack.append(rootMenu)

    def closeOneLevel(self):
        if self.stack:
            self.stack.pop()
        return len(self.stack) == 0  # True면 메뉴가 완전히 닫혔다.

    @property
    def current(self):
        return self.stack[-1] if self.stack else None

    # spp-source: examples/doom/menu.md#Feature:_메뉴_항목_선택
    def moveSelection(self, direction):
        menu = self.current
        if menu is None or not menu.items:
            return
        delta = -1 if direction == "Up" else 1
        menu.selectedIndex = (menu.selectedIndex + delta) % len(menu.items)

    def confirmSelection(self):
        menu = self.current
        if menu is None:
            return None
        item = menu.items[menu.selectedIndex]
        if item.kind == "Action" and item.action is not None:
            item.action()
        elif item.kind == "Submenu" and item.submenu is not None:
            self.stack.append(item.submenu)
        elif item.kind == "Toggle":
            item.toggleValue = not item.toggleValue
        return item
