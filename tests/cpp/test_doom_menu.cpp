// examples/doom/menu.md 검증 (C++17).
#include "doom_menu.hpp"
#include "minitest.hpp"

using namespace Doom;

TEST(menu_open_pushes_root) {
    MenuStack stack;
    auto root = std::make_shared<Menu>("Main", std::vector<MenuItem>{{"New Game", "Action", nullptr, nullptr}});
    stack.open(root);
    CHECK(stack.isOpen());
    CHECK(stack.current() == root.get());
}

TEST(menu_cancel_closes_when_stack_empties) {
    MenuStack stack;
    stack.open(std::make_shared<Menu>("Main", std::vector<MenuItem>{}));
    CHECK(stack.closeOneLevel());
    CHECK(!stack.isOpen());
}

TEST(menu_cancel_from_submenu_returns_to_parent) {
    MenuStack stack;
    auto parent = std::make_shared<Menu>("Main", std::vector<MenuItem>{});
    auto child = std::make_shared<Menu>("Options", std::vector<MenuItem>{});
    stack.open(parent);
    stack.stack.push_back(child);
    CHECK(!stack.closeOneLevel());
    CHECK(stack.current() == parent.get());
}

TEST(menu_selection_wraps_and_confirms) {
    bool actionRan = false;
    auto submenu = std::make_shared<Menu>("Options", std::vector<MenuItem>{{"Sound", "Action", nullptr, nullptr}});
    std::vector<MenuItem> items = {
        {"New Game", "Action", [&] { actionRan = true; }, nullptr},
        {"Options", "Submenu", nullptr, submenu},
        {"Fullscreen", "Toggle", nullptr, nullptr},
    };
    auto menu = std::make_shared<Menu>("Main", items);
    MenuStack stack;
    stack.open(menu);

    menu->selectedIndex = items.size() - 1;
    stack.moveSelection("Down");
    CHECK_EQ(menu->selectedIndex, 0u);

    stack.confirmSelection();
    CHECK(actionRan);

    menu->selectedIndex = 1;
    stack.confirmSelection();
    CHECK_EQ(stack.current()->title, std::string("Options"));

    // 새 스택에서 토글 확인.
    MenuStack stack2;
    auto menu2 = std::make_shared<Menu>("Main", items);
    stack2.open(menu2);
    menu2->selectedIndex = 2;
    auto* item = stack2.confirmSelection();
    CHECK(item->toggleValue);
}

TEST_MAIN()
