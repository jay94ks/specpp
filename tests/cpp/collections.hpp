// std/collections/{collection,set,queue,stack,dictionary}.md reference implementation (C++17).
#pragma once
#include <deque>
#include <optional>
#include <stack>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

template <typename T>
class Collection {
public:
    virtual int size() const = 0;
    virtual bool isEmpty() const { return size() == 0; }
    virtual ~Collection() = default;
};

template <typename T>
class Set : public Collection<T> {
    std::unordered_set<T> items_;

public:
    Set() = default;
    explicit Set(const std::vector<T>& items) { for (auto& i : items) add(i); }
    static Set<T> of(const std::vector<T>& items) { return Set<T>(items); }

    void add(const T& item) { items_.insert(item); }
    void remove(const T& item) { items_.erase(item); }
    bool has(const T& item) const { return items_.count(item) > 0; }
    int size() const override { return static_cast<int>(items_.size()); }
    std::vector<T> toList() const { return std::vector<T>(items_.begin(), items_.end()); }
};

template <typename T>
class Queue : public Collection<T> {
    std::deque<T> items_;

public:
    void enqueue(const T& item) { items_.push_back(item); }
    std::optional<T> dequeue() {
        if (items_.empty()) return std::nullopt;
        T front = items_.front();
        items_.pop_front();
        return front;
    }
    std::optional<T> peek() const {
        if (items_.empty()) return std::nullopt;
        return items_.front();
    }
    int size() const override { return static_cast<int>(items_.size()); }
};

template <typename T>
class Stack : public Collection<T> {
    std::vector<T> items_;

public:
    void push(const T& item) { items_.push_back(item); }
    std::optional<T> pop() {
        if (items_.empty()) return std::nullopt;
        T top = items_.back();
        items_.pop_back();
        return top;
    }
    std::optional<T> peek() const {
        if (items_.empty()) return std::nullopt;
        return items_.back();
    }
    int size() const override { return static_cast<int>(items_.size()); }
};

template <typename K, typename V>
class Dictionary : public Collection<K> {
    std::unordered_map<K, V> map_;

public:
    void set(const K& key, const V& value) { map_[key] = value; }
    std::optional<V> get(const K& key) const {
        auto it = map_.find(key);
        if (it == map_.end()) return std::nullopt;
        return it->second;
    }
    bool has(const K& key) const { return map_.count(key) > 0; }
    void remove(const K& key) { map_.erase(key); }
    int size() const override { return static_cast<int>(map_.size()); }
};
