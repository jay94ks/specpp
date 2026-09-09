import unittest
from spp_std.collections_ import Set, Queue, Stack, Dictionary, List


class SetTest(unittest.TestCase):
    def test_duplicate_add_is_ignored(self):
        s = Set()
        s.add("a")
        s.add("a")
        self.assertEqual(s.size(), 1)

    def test_has(self):
        s = Set()
        s.add("a")
        self.assertTrue(s.has("a"))
        self.assertFalse(s.has("b"))

    def test_isEmpty_inherited_default(self):
        self.assertTrue(Set().isEmpty())
        self.assertFalse(Set.of(["a"]).isEmpty())


class QueueTest(unittest.TestCase):
    def test_fifo_order(self):
        q = Queue()
        q.enqueue("a")
        q.enqueue("b")
        self.assertEqual(q.dequeue(), "a")
        self.assertEqual(q.dequeue(), "b")

    def test_dequeue_empty_returns_none(self):
        self.assertIsNone(Queue().dequeue())


class StackTest(unittest.TestCase):
    def test_lifo_order(self):
        s = Stack()
        s.push("a")
        s.push("b")
        self.assertEqual(s.pop(), "b")
        self.assertEqual(s.pop(), "a")

    def test_pop_empty_returns_none(self):
        self.assertIsNone(Stack().pop())


class DictionaryTest(unittest.TestCase):
    def test_set_and_get(self):
        d = Dictionary()
        d.set("a", 1)
        self.assertEqual(d.get("a"), 1)
        self.assertIsNone(d.get("b"))


class ListTest(unittest.TestCase):
    def test_filter_then_map(self):
        result = List.map(List.filter([1, 2, 3, 4], lambda x: x % 2 == 0), lambda x: x * 10)
        self.assertEqual(result, [20, 40])

    def test_reduce_sum(self):
        self.assertEqual(List.reduce([1, 2, 3], 0, lambda acc, x: acc + x), 6)

    def test_original_not_mutated(self):
        original = [3, 1, 2]
        List.sort(original, lambda a, b: a - b)
        self.assertEqual(original, [3, 1, 2])


if __name__ == "__main__":
    unittest.main()
