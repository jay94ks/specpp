"""std/system/{exception,math,random,datetime,timespan,guid,convert,environment}.md reference implementation."""
import math as _math
import random as _random
import datetime as _dt
import uuid as _uuid
import os as _os
import sys as _sys


class Exception_(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class Math_:
    PI = _math.pi
    E = _math.e

    @staticmethod
    def abs(x):
        return abs(x)

    @staticmethod
    def sqrt(x):
        if x < 0:
            raise ValueError("sqrt of negative number")
        return _math.sqrt(x)

    @staticmethod
    def pow(base, exponent):
        return _math.pow(base, exponent)

    @staticmethod
    def min(a, b):
        return min(a, b)

    @staticmethod
    def max(a, b):
        return max(a, b)

    @staticmethod
    def floor(x):
        return _math.floor(x)

    @staticmethod
    def ceil(x):
        return _math.ceil(x)

    @staticmethod
    def round(x):
        return round(x)


class Random_:
    def __init__(self, seed=None):
        self._r = _random.Random(seed)

    def nextInt(self, min_, max_):
        return self._r.randrange(min_, max_)

    def nextFloat(self):
        return self._r.random()

    def nextBoolean(self):
        return self._r.random() < 0.5


class TimeSpan:
    def __init__(self, seconds):
        self._seconds = seconds

    @staticmethod
    def fromSeconds(v):
        return TimeSpan(v)

    @staticmethod
    def fromMinutes(v):
        return TimeSpan(v * 60)

    @staticmethod
    def fromHours(v):
        return TimeSpan(v * 3600)

    @staticmethod
    def fromDays(v):
        return TimeSpan(v * 86400)

    def totalSeconds(self):
        return self._seconds

    def add(self, other):
        return TimeSpan(self._seconds + other._seconds)

    def compareTo(self, other):
        return (self._seconds > other._seconds) - (self._seconds < other._seconds)


class DateTime:
    def __init__(self, year, month, day, hour=0, minute=0, second=0):
        self._dt = _dt.datetime(year, month, day, hour, minute, second)

    @classmethod
    def _wrap(cls, raw):
        self = cls.__new__(cls)
        self._dt = raw
        return self

    @staticmethod
    def now():
        return DateTime._wrap(_dt.datetime.now())

    @staticmethod
    def utcNow():
        return DateTime._wrap(_dt.datetime.utcnow())

    def addDays(self, days):
        return DateTime._wrap(self._dt + _dt.timedelta(days=days))

    def add(self, span):
        return DateTime._wrap(self._dt + _dt.timedelta(seconds=span.totalSeconds()))

    def compareTo(self, other):
        return (self._dt > other._dt) - (self._dt < other._dt)

    def toString(self):
        return str(self._dt)


class Guid:
    def __init__(self, value):
        self._value = value

    @staticmethod
    def newGuid():
        return Guid(_uuid.uuid4())

    @staticmethod
    def parse(text):
        return Guid(_uuid.UUID(text))

    def toString(self):
        return str(self._value)

    def equals(self, other):
        return self._value == other._value


class Convert:
    @staticmethod
    def toInt(text):
        return int(text)

    @staticmethod
    def toFloat(text):
        return float(text)

    @staticmethod
    def toBoolean(text):
        t = text.strip().lower()
        if t == "true":
            return True
        if t == "false":
            return False
        raise ValueError("not a boolean: " + text)

    @staticmethod
    def toString(value):
        return str(value)


class Environment:
    @staticmethod
    def args():
        return _sys.argv[1:]

    @staticmethod
    def getVariable(name):
        return _os.environ.get(name)

    @staticmethod
    def setVariable(name, value):
        _os.environ[name] = value

    @staticmethod
    def exit(code):
        _sys.exit(code)
