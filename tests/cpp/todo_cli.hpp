// examples/todo-cli.md reference implementation (C++17).
#pragma once
#include <algorithm>
#include <chrono>
#include <stdexcept>
#include <string>
#include <vector>

class ValidationError : public std::runtime_error {
public:
    std::string message;
    explicit ValidationError(const std::string& msg) : std::runtime_error(msg), message(msg) {}
};

class NotFoundError : public std::runtime_error {
public:
    std::string message;
    explicit NotFoundError(const std::string& msg) : std::runtime_error(msg), message(msg) {}
};

class Task {
public:
    int id;
    std::string title;
    bool done;
    std::chrono::system_clock::time_point createdAt;

    Task(int id_, std::string title_, bool done_)
        : id(id_), title(std::move(title_)), done(done_), createdAt(std::chrono::system_clock::now()) {}

    // markDone() -> void: done을 true로 바꾼다. 이미 true이면 아무 일도 하지 않는다 (멱등).
    void markDone() { done = true; }
};

inline std::string trim(const std::string& s) {
    size_t start = s.find_first_not_of(" \t\n\r");
    if (start == std::string::npos) return "";
    size_t end = s.find_last_not_of(" \t\n\r");
    return s.substr(start, end - start + 1);
}

class TodoApp {
    std::vector<Task> tasks_;

public:
    Task& add(const std::string& rawTitle) {
        std::string title = trim(rawTitle);
        if (title.empty()) {
            throw ValidationError("title은 필수입니다");
        }
        int maxId = 0;
        for (auto& t : tasks_) maxId = std::max(maxId, t.id);
        tasks_.emplace_back(maxId + 1, title, false);
        return tasks_.back();
    }

    Task& done(int id) {
        for (auto& t : tasks_) {
            if (t.id == id) {
                t.markDone();  // Todo.Task.markDone() 호출 (멱등)
                return t;
            }
        }
        throw NotFoundError("Task #" + std::to_string(id) + "를 찾을 수 없습니다");
    }

    std::vector<Task> list(bool all) const {
        std::vector<Task> result;
        for (auto& t : tasks_) {
            if (all || !t.done) result.push_back(t);
        }
        std::sort(result.begin(), result.end(), [](const Task& a, const Task& b) { return a.id < b.id; });
        return result;
    }
};

inline std::string formatAdd(const Task& t) {
    return "✔ 추가됨: " + t.title + " (#" + std::to_string(t.id) + ")";
}

inline std::string formatListLine(const Task& t) {
    return std::string("[") + (t.done ? "x" : " ") + "] #" + std::to_string(t.id) + " " + t.title;
}
