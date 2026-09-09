import io
import unittest
from spp_std.io_streams import Stdout, Stderr, Stdin


class StdoutTest(unittest.TestCase):
    def test_println_adds_newline(self):
        buf = io.StringIO()
        Stdout(buf).println("Hello World")
        self.assertEqual(buf.getvalue(), "Hello World\n")

    def test_print_has_no_newline_and_is_contiguous(self):
        buf = io.StringIO()
        out = Stdout(buf)
        out.print("A")
        out.print("B")
        self.assertEqual(buf.getvalue(), "AB")


class StderrTest(unittest.TestCase):
    def test_error_message_goes_to_stderr_only(self):
        out_buf, err_buf = io.StringIO(), io.StringIO()
        Stderr(err_buf).println("✘ title은 필수입니다")
        self.assertEqual(err_buf.getvalue(), "✘ title은 필수입니다\n")
        self.assertEqual(out_buf.getvalue(), "")


class StdinTest(unittest.TestCase):
    def test_read_line(self):
        stdin = Stdin(io.StringIO("우유 사기\n"))
        self.assertEqual(stdin.readLine(), "우유 사기")

    def test_read_line_at_eof_returns_none(self):
        stdin = Stdin(io.StringIO(""))
        self.assertIsNone(stdin.readLine())


if __name__ == "__main__":
    unittest.main()
