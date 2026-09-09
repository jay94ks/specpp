#include "minitest.hpp"
#include "concurrency.hpp"
#include <vector>

TEST(test_atomic_cas_succeeds_when_value_matches) {
    Atomic<int> a(1);
    CHECK(a.compareAndSwap(1, 2));
    CHECK_EQ(a.get(), 2);
}

TEST(test_atomic_cas_fails_when_value_differs) {
    Atomic<int> a(1);
    CHECK(!a.compareAndSwap(999, 2));
    CHECK_EQ(a.get(), 1);
}

TEST(test_mutex_trylock_fails_while_held) {
    Mutex m;
    m.lock();
    CHECK(!m.tryLock());
    m.unlock();
    CHECK(m.tryLock());
    m.unlock();
}

TEST(test_thread_join_waits_for_completion) {
    Atomic<int> result(0);
    Thread t([&result]() { result.set(42); });
    t.start();
    t.join();
    CHECK_EQ(result.get(), 42);
    CHECK(!t.isAlive());
}

TEST(test_concurrent_increment_with_cas_loses_no_updates) {
    // ConcurrentDictionary.getOrAdd 등에서 권장하는 CAS 재시도 패턴을 그대로
    // 검증한다 — 여러 스레드가 동시에 증가시켜도 유실 없이 정확히 누적되는지.
    Atomic<int> counter(0);
    std::vector<Thread*> threads;
    for (int i = 0; i < 8; i++) {
        threads.push_back(new Thread([&counter]() {
            for (int j = 0; j < 1000; j++) {
                int old;
                do {
                    old = counter.get();
                } while (!counter.compareAndSwap(old, old + 1));
            }
        }));
    }
    for (auto* t : threads) t->start();
    for (auto* t : threads) t->join();
    CHECK_EQ(counter.get(), 8000);
    for (auto* t : threads) delete t;
}

TEST_MAIN()
