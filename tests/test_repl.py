import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, "src")

from main import (
    Context,
    execute_command,
    expand_env_vars,
    parse_command,
)
from vfs import create_default_vfs


def make_context() -> Context:
    vfs = create_default_vfs()
    return Context(vfs)


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
    def test_unknown_command(self) -> None:
        result = execute_command("foobar", [], make_context())
        self.assertEqual(result, 127)

    def test_known_command(self) -> None:
        result = execute_command("ls", [], make_context())
        self.assertEqual(result, 0)


if __name__ == "__main__":
    unittest.main()
