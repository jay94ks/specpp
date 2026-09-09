"""std/collections/*.md reference implementation."""


class Collection:
    def size(self):
        raise NotImplementedError

    def isEmpty(self):
        return self.size() == 0


class Set(Collection):
    def __init__(self, items=None):
        self._items = []
        for item in items or []:
            self.add(item)

    @staticmethod
    def of(items):
        return Set(items)

    def add(self, item):
        if item not in self._items:
            self._items.append(item)

    def remove(self, item):
        if item in self._items:
            self._items.remove(item)

    def has(self, item):
        return item in self._items

    def size(self):
        return len(self._items)

    def toList(self):
        return list(self._items)


class Queue(Collection):
    def __init__(self, items=None):
        self._items = list(items or [])

    @staticmethod
    def of(items):
        return Queue(items)

    def enqueue(self, item):
        self._items.append(item)

    def dequeue(self):
        return self._items.pop(0) if self._items else None

    def peek(self):
        return self._items[0] if self._items else None

    def size(self):
        return len(self._items)


class Stack(Collection):
    def __init__(self, items=None):
        self._items = list(items or [])

    @staticmethod
    def of(items):
        return Stack(items)

    def push(self, item):
        self._items.append(item)

    def pop(self):
        return self._items.pop() if self._items else None

    def peek(self):
        return self._items[-1] if self._items else None

    def size(self):
        return len(self._items)


class Dictionary(Collection):
    def __init__(self):
        self._map = {}

    @staticmethod
    def of(entries):
        d = Dictionary()
        for k, v in entries.items():
            d.set(k, v)
        return d

    def set(self, key, value):
        self._map[key] = value

    def get(self, key):
        return self._map.get(key)

    def has(self, key):
        return key in self._map

    def remove(self, key):
        self._map.pop(key, None)

    def keys(self):
        return list(self._map.keys())

    def values(self):
        return list(self._map.values())

    def size(self):
        return len(self._map)


class List:
    @staticmethod
    def map(items, fn):
        return [fn(x) for x in items]

    @staticmethod
    def filter(items, predicate):
        return [x for x in items if predicate(x)]

    @staticmethod
    def reduce(items, initial, fn):
        acc = initial
        for x in items:
            acc = fn(acc, x)
        return acc

    @staticmethod
    def sort(items, compare):
        import functools
        return sorted(items, key=functools.cmp_to_key(compare))

    @staticmethod
    def indexOf(items, item):
        try:
            return items.index(item)
        except ValueError:
            return -1

    @staticmethod
    def contains(items, item):
        return item in items

    @staticmethod
    def slice(items, start, end):
        return items[start:end]

    @staticmethod
    def reverse(items):
        return list(reversed(items))
