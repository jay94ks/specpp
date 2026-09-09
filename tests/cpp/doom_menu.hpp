// examples/doom/menu.md 의 # Domain/# Behavior 참조 구현 (C++17).
#pragma once
#include <functional>
#include <memory>
#include <string>
#include <vector>

namespace Doom {

struct Menu;

struct MenuItem {
    std::string label;
    std::string kind;  // "Action" | "Toggle" | "Slider" | "Submenu"
    std::function<void()> action;
    std::shared_ptr<Menu> submenu;
    bool toggleValue = false;
    int sliderValue = 0;
};

struct Menu {
    std::string title;
    std::vector<MenuItem> items;
    size_t selectedIndex = 0;

    Menu(std::string t, std::vector<MenuItem> i) : title(std::move(t)), items(std::move(i)) {}
};

class MenuStack {
public:
    std::vector<std::shared_ptr<Menu>> stack;

    bool isOpen() const { return !stack.empty(); }

    // spp-source: examples/doom/menu.md#Feature:_메뉴_열기/닫기
    void open(std::shared_ptr<Menu> root) { stack.push_back(std::move(root)); }

    bool closeOneLevel() {
        if (!stack.empty()) stack.pop_back();
        return stack.empty();
    }

    Menu* current() { return stack.empty() ? nullptr : stack.back().get(); }

    // spp-source: examples/doom/menu.md#Feature:_메뉴_항목_선택
    void moveSelection(const std::string& direction) {
        Menu* menu = current();
        if (!menu || menu->items.empty()) return;
        if (direction == "Up") {
            menu->selectedIndex = (menu->selectedIndex == 0) ? menu->items.size() - 1 : menu->selectedIndex - 1;
        } else {
            menu->selectedIndex = (menu->selectedIndex + 1) % menu->items.size();
        }
    }

    MenuItem* confirmSelection() {
        Menu* menu = current();
        if (!menu) return nullptr;
        MenuItem* item = &menu->items[menu->selectedIndex];
        if (item->kind == "Action" && item->action) {
            item->action();
        } else if (item->kind == "Submenu" && item->submenu) {
            stack.push_back(item->submenu);
        } else if (item->kind == "Toggle") {
            item->toggleValue = !item->toggleValue;
        }
        return item;
    }
};

}  // namespace Doom
