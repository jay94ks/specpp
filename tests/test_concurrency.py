import unittest
from spp_std.concurrency_ import (
    Atomic, ConcurrentQueue, ConcurrentStack, ConcurrentDictionary, ConcurrentBag, Thread, Mutex,
)


class AtomicTest(unittest.TestCase):
    def test_cas_succeeds_when_value_matches(self):
        a = Atomic(1)
        self.assertTrue(a.compareAndSwap(1, 2))
        self.assertEqual(a.get(), 2)

    def test_cas_fails_when_value_differs(self):
        a = Atomic(1)
        self.assertFalse(a.compareAndSwap(999, 2))
        self.assertEqual(a.get(), 1)


class ConcurrentQueueTest(unittest.TestCase):
    def test_single_thread_fifo(self):
        q = ConcurrentQueue()
        q.enqueue("a")
        q.enqueue("b")
        self.assertEqual(q.dequeue(), "a")
        self.assertEqual(q.dequeue(), "b")

    def test_concurrent_enqueue_does_not_lose_items(self):
        q = ConcurrentQueue()
        t1 = Thread(lambda: q.enqueue("a"))
        t2 = Thread(lambda: q.enqueue("b"))
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        self.assertEqual(q.size(), 2)


class ConcurrentStackTest(unittest.TestCase):
    def test_single_thread_lifo(self):
        s = ConcurrentStack()
        s.push("a")
        s.push("b")
        self.assertEqual(s.pop(), "b")
        self.assertEqual(s.pop(), "a")

    def test_concurrent_push_does_not_lose_items(self):
        s = ConcurrentStack()
        t1 = Thread(lambda: s.push("a"))
        t2 = Thread(lambda: s.push("b"))
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        self.assertEqual(s.size(), 2)


class ConcurrentDictionaryTest(unittest.TestCase):
    def test_get_or_add_converges_to_one_stored_value(self):
        # std/concurrency/dictionary.md: getOrAdd는 factory가 몇 번 "호출"되는지는
        # 보장하지 않는다 (락 기반이면 보통 한 번, CAS 기반이면 여러 번일 수 있다) —
        # 보장하는 것은 "그 key에 대해 최종적으로 저장되는 값은 하나이고, 모든
        # 호출자가 그 값을 돌려받는다"는 것뿐이다. 이 구현은 락 기반이라 우연히
        # 정확히 한 번만 호출되지만, 테스트는 스펙이 실제로 요구하는 수렴 성질만
        # 검증한다.
        d = ConcurrentDictionary()
        calls = []

        def factory():
            calls.append(1)
            return "value"

        results = []
        threads = [Thread(lambda: results.append(d.getOrAdd("k", factory))) for _ in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertGreaterEqual(len(calls), 1)
        self.assertTrue(all(r == "value" for r in results))
        self.assertEqual(d.get("k"), "value")


class ConcurrentBagTest(unittest.TestCase):
    def test_take_as_many_as_added(self):
        bag = ConcurrentBag()
        bag.add("a")
        bag.add("b")
        bag.add("c")
        taken = {bag.tryTake(), bag.tryTake(), bag.tryTake()}
        self.assertEqual(taken, {"a", "b", "c"})
        self.assertIsNone(bag.tryTake())


class MutexTest(unittest.TestCase):
    def test_trylock_fails_while_held(self):
        m = Mutex()
        m.lock()
        try:
            self.assertFalse(m.tryLock())
        finally:
            m.unlock()
        self.assertTrue(m.tryLock())
        m.unlock()


class ThreadTest(unittest.TestCase):
    def test_join_waits_for_completion(self):
        result = Atomic(0)
        t = Thread(lambda: result.set(42))
        t.start()
        t.join()
        self.assertEqual(result.get(), 42)
        self.assertFalse(t.isAlive())


if __name__ == "__main__":
    unittest.main()
