import unittest
from spp_std.system_ import Math_, Random_, TimeSpan, DateTime, Guid, Convert, Exception_, Environment, Debug, DebugAssertionError
from spp_std.system_process import Process
import sys


class MathTest(unittest.TestCase):
    def test_sqrt(self):
        self.assertEqual(Math_.sqrt(16), 4)

    def test_max(self):
        self.assertEqual(Math_.max(3, 7), 7)


class RandomTest(unittest.TestCase):
    def test_next_int_in_range(self):
        r = Random_(1)
        v = r.nextInt(1, 7)
        self.assertGreaterEqual(v, 1)
        self.assertLess(v, 7)

    def test_same_seed_reproduces_same_sequence(self):
        # Intent: "같은 seed로 만든 두 Random은 항상 같은 순서의 값을 반환한다."
        r1, r2 = Random_(42), Random_(42)
        seq1 = [r1.nextInt(0, 1000) for _ in range(5)]
        seq2 = [r2.nextInt(0, 1000) for _ in range(5)]
        self.assertEqual(seq1, seq2)


class TimeSpanTest(unittest.TestCase):
    def test_minutes_to_seconds(self):
        self.assertEqual(TimeSpan.fromMinutes(2).totalSeconds(), 120)


class DateTimeTest(unittest.TestCase):
    def test_add_day_is_later(self):
        now = DateTime.now()
        tomorrow = DateTime.now().addDays(1)
        self.assertGreater(tomorrow.compareTo(now), 0)

    def test_construct_specific_date(self):
        self.assertLess(DateTime(2024, 1, 1).compareTo(DateTime(2024, 1, 2)), 0)

    def test_construct_defaults_to_midnight(self):
        self.assertEqual(DateTime(2024, 1, 1).compareTo(DateTime(2024, 1, 1, 0, 0, 0)), 0)


class GuidTest(unittest.TestCase):
    def test_roundtrip(self):
        g = Guid.newGuid()
        parsed = Guid.parse(g.toString())
        self.assertTrue(parsed.equals(g))


class ConvertTest(unittest.TestCase):
    def test_string_to_int(self):
        self.assertEqual(Convert.toInt("42"), 42)

    def test_unparsable_raises(self):
        with self.assertRaises(ValueError):
            Convert.toInt("abc")


class ExceptionTest(unittest.TestCase):
    def test_subclass_carries_message(self):
        class ValidationError(Exception_):
            pass

        try:
            raise ValidationError("title은 필수입니다")
        except ValidationError as e:
            self.assertEqual(e.message, "title은 필수입니다")

    def test_specref_carries_spec_location(self):
        class ValidationError(Exception_):
            pass

        try:
            raise ValidationError(
                "title은 필수입니다", "examples/todo-cli.md#Behavior.할 일 추가"
            )
        except ValidationError as e:
            self.assertEqual(e.specRef, "examples/todo-cli.md#Behavior.할 일 추가")

    def test_specref_defaults_to_none(self):
        try:
            raise Exception_("문제 발생")
        except Exception_ as e:
            self.assertIsNone(e.specRef)


class DebugTest(unittest.TestCase):
    def test_assert_passes_silently(self):
        Debug.assert_(True, "여기 오면 안 됨")  # 예외를 던지지 않아야 한다

    def test_assert_fails_with_message_and_specref(self):
        with self.assertRaises(DebugAssertionError) as ctx:
            Debug.assert_(False, "빈 목록이면 안 됨", "std/collections/queue.md#Interface.ConcurrentQueue")
        self.assertEqual(ctx.exception.message, "빈 목록이면 안 됨")
        self.assertEqual(ctx.exception.specRef, "std/collections/queue.md#Interface.ConcurrentQueue")


class EnvironmentTest(unittest.TestCase):
    def test_missing_variable_returns_none(self):
        self.assertIsNone(Environment.getVariable("SPP_DOES_NOT_EXIST"))

    def test_set_then_get_variable(self):
        Environment.setVariable("SPP_TEST_VAR", "1")
        self.assertEqual(Environment.getVariable("SPP_TEST_VAR"), "1")


class ProcessTest(unittest.TestCase):
    def test_start_and_wait_returns_exit_code(self):
        p = Process(sys.executable, ["-c", "pass"])
        p.start()
        code = p.wait()
        self.assertEqual(code, 0)

    def test_kill_stops_running_process(self):
        p = Process(sys.executable, ["-c", "import time; time.sleep(100)"])
        p.start()
        self.assertTrue(p.isRunning())
        p.kill()
        self.assertFalse(p.isRunning())


if __name__ == "__main__":
    unittest.main()
