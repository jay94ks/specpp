import unittest

from doom_menu import Menu, MenuItem, MenuStack


class MenuOpenCloseTest(unittest.TestCase):
    """menu.md의 '## Feature: 메뉴 열기/닫기' 검증."""

    def test_open_pushes_root_menu(self):
        stack = MenuStack()
        root = Menu("Main", [MenuItem("New Game", "Action")])
        stack.open(root)
        self.assertTrue(stack.isOpen)
        self.assertIs(stack.current, root)

    def test_cancel_pops_and_closes_when_stack_empties(self):
        stack = MenuStack()
        stack.open(Menu("Main", []))
        fullyClosed = stack.closeOneLevel()
        self.assertTrue(fullyClosed)
        self.assertFalse(stack.isOpen)

    def test_cancel_from_submenu_returns_to_parent(self):
        stack = MenuStack()
        parent = Menu("Main", [])
        child = Menu("Options", [])
        stack.open(parent)
        stack.stack.append(child)
        fullyClosed = stack.closeOneLevel()
        self.assertFalse(fullyClosed)
        self.assertIs(stack.current, parent)


class MenuSelectionTest(unittest.TestCase):
    """menu.md의 '## Feature: 메뉴 항목 선택' 검증."""

    def setUp(self):
        self.actions = []
        self.items = [
            MenuItem("New Game", "Action", action=lambda: self.actions.append("new")),
            MenuItem("Options", "Submenu", submenu=Menu("Options", [MenuItem("Sound", "Action")])),
            MenuItem("Fullscreen", "Toggle"),
        ]
        self.menu = Menu("Main", self.items)
        self.stack = MenuStack()
        self.stack.open(self.menu)

    def test_down_wraps_to_first_item(self):
        self.menu.selectedIndex = len(self.items) - 1
        self.stack.moveSelection("Down")
        self.assertEqual(self.menu.selectedIndex, 0)

    def test_up_wraps_to_last_item(self):
        self.menu.selectedIndex = 0
        self.stack.moveSelection("Up")
        self.assertEqual(self.menu.selectedIndex, len(self.items) - 1)

    def test_confirm_action_runs_it(self):
        self.menu.selectedIndex = 0
        self.stack.confirmSelection()
        self.assertEqual(self.actions, ["new"])

    def test_confirm_submenu_pushes_it(self):
        self.menu.selectedIndex = 1
        self.stack.confirmSelection()
        self.assertEqual(self.stack.current.title, "Options")

    def test_confirm_toggle_flips_value(self):
        self.menu.selectedIndex = 2
        item = self.stack.confirmSelection()
        self.assertTrue(item.toggleValue)
        self.stack.confirmSelection()
        self.assertFalse(item.toggleValue)


if __name__ == "__main__":
    unittest.main()
