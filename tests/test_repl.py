import os
import unittest
from unittest import mock

import sys
sys.path.insert(0, "src")

from main import (  # noqa: E402
    Context,
    expand_env_vars,
    execute_command,
    parse_command,
)
from vfs import create_default_vfs  # noqa: E402


class TestExpandEnvVars(unittest.TestCase):
    def test_simple_var(self) -> None:
        with mock.patch.dict(os.environ, {"HOME": "/home/user"}):
            self.assertEqual(expand_env_vars("$HOME"), "/home/user")

    def test_braced_var(self) -> None:
        with mock.patch.dict(os.environ, {"USER": "alice"}):
            self.assertEqual(expand_env_vars("${USER}"), "alice")

    def test_missing_var(self) -> None:
        os.environ.pop("NONEXISTENT", None)
        self.assertEqual(expand_env_vars("$NONEXISTENT"), "")


class TestParseCommand(unittest.TestCase):
    def test_simple(self) -> None:
        self.assertEqual(parse_command("ls"), ("ls", []))

    def test_with_args(self) -> None:
        self.assertEqual(
            parse_command("cd /tmp foo"),
            ("cd", ["/tmp", "foo"]),
        )

    def test_empty(self) -> None:
        self.assertEqual(parse_command(""), ("", []))


class TestExecuteCommand(unittest.TestCase):
    def setUp(self) -> None:
        vfs = create_default_vfs()
        self.ctx = Context(vfs)

    def test_unknown_command(self) -> None:
        self.assertEqual(execute_command("foobar", [], self.ctx), 127)

    def test_known_command(self) -> None:
        result = execute_command("ls", [], self.ctx)
        self.assertEqual(result, 0)


if __name__ == "__main__":
    unittest.main()
