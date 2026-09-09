"""std/concurrency/*.md reference implementation."""
import threading


class Atomic:
    def __init__(self, initial):
        self._value = initial
        self._lock = threading.Lock()

    def get(self):
        with self._lock:
            return self._value

    def set(self, value):
        with self._lock:
            self._value = value

    def exchange(self, newValue):
        with self._lock:
            old = self._value
            self._value = newValue
            return old

    def compareAndSwap(self, expected, newValue):
        with self._lock:
            if self._value == expected:
                self._value = newValue
                return True
            return False


class ConcurrentQueue:
    def __init__(self):
        self._items = []
        self._lock = threading.Lock()

    def enqueue(self, item):
        with self._lock:
            self._items.append(item)

    def dequeue(self):
        with self._lock:
            return self._items.pop(0) if self._items else None

    def size(self):
        with self._lock:
            return len(self._items)

    def isEmpty(self):
        return self.size() == 0


class ConcurrentStack:
    def __init__(self):
        self._items = []
        self._lock = threading.Lock()

    def push(self, item):
        with self._lock:
            self._items.append(item)

    def pop(self):
        with self._lock:
            return self._items.pop() if self._items else None

    def size(self):
        with self._lock:
            return len(self._items)

    def isEmpty(self):
        return self.size() == 0


class ConcurrentDictionary:
    def __init__(self):
        self._map = {}
        self._lock = threading.Lock()

    def set(self, key, value):
        with self._lock:
            self._map[key] = value

    def get(self, key):
        with self._lock:
            return self._map.get(key)

    def has(self, key):
        with self._lock:
            return key in self._map

    def remove(self, key):
        with self._lock:
            self._map.pop(key, None)

    def getOrAdd(self, key, factory):
        with self._lock:
            if key in self._map:
                return self._map[key]
            value = factory()
            self._map[key] = value
            return value

    def size(self):
        with self._lock:
            return len(self._map)

    def isEmpty(self):
        return self.size() == 0


class ConcurrentBag:
    def __init__(self):
        self._items = []
        self._lock = threading.Lock()

    def add(self, item):
        with self._lock:
            self._items.append(item)

    def tryTake(self):
        with self._lock:
            return self._items.pop() if self._items else None

    def size(self):
        with self._lock:
            return len(self._items)

    def isEmpty(self):
        return self.size() == 0


class Mutex:
    def __init__(self):
        self._lock = threading.Lock()

    def lock(self):
        self._lock.acquire()

    def unlock(self):
        self._lock.release()

    def tryLock(self):
        return self._lock.acquire(blocking=False)


class Thread:
    def __init__(self, fn):
        self._thread = threading.Thread(target=fn)

    def start(self):
        self._thread.start()

    def join(self):
        self._thread.join()

    def isAlive(self):
        return self._thread.is_alive()
