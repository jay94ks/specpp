// std/concurrency/{atomic,mutex,thread}.md reference implementation (C++17).
#pragma once
#include <atomic>
#include <functional>
#include <mutex>
#include <thread>

template <typename T>
class Atomic {
    std::atomic<T> value_;

public:
    explicit Atomic(T initial) : value_(initial) {}
    T get() const { return value_.load(); }
    void set(T value) { value_.store(value); }
    T exchange(T newValue) { return value_.exchange(newValue); }
    bool compareAndSwap(T expected, T newValue) {
        return value_.compare_exchange_strong(expected, newValue);
    }
};

class Mutex {
    std::mutex m_;

public:
    void lock() { m_.lock(); }
    void unlock() { m_.unlock(); }
    bool tryLock() { return m_.try_lock(); }
};

// SPEC.md의 Thread는 "생성 시 함수를 받고, start()가 호출되어야 실제로 실행을
// 시작한다"는 계약이다. std::thread는 생성과 동시에 실행을 시작하므로, 이
// 계약을 그대로 지키려면 실제 std::thread 생성을 start() 호출 시점까지
// 미뤄야 한다.
class Thread {
    std::function<void()> fn_;
    std::thread t_;

public:
    explicit Thread(std::function<void()> fn) : fn_(std::move(fn)) {}
    void start() { t_ = std::thread(fn_); }
    void join() { if (t_.joinable()) t_.join(); }
    bool isAlive() const { return t_.joinable(); }
};
