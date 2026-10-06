import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, "src")

from config import parse_args  # noqa: E402
from script_runner import run_script  # noqa: E402


class TestParseArgs(unittest.TestCase):

    def test_vfs_path_only(self) -> None:
        config = parse_args(["--vfs-path", "/tmp/vfs"])
        self.assertEqual(config.vfs_path, Path("/tmp/vfs"))
        self.assertIsNone(config.script_path)

    def test_both_args(self) -> None:
        config = parse_args([
            "--vfs-path", "/tmp/vfs",
            "--script-path", "/tmp/script.sh",
        ])
        self.assertEqual(config.vfs_path, Path("/tmp/vfs"))
        self.assertEqual(config.script_path, Path("/tmp/script.sh"))

    def test_missing_vfs_path(self) -> None:
        with self.assertRaises(SystemExit):
            with mock.patch("sys.stderr", mock.Mock()):
                parse_args([])


class TestScriptRunner(unittest.TestCase):

    def test_script_not_found(self) -> None:

        def dummy_execute(cmd, args):
            return 0

        def dummy_parse(line):
            return line.split()[0] if line else "", []

        def dummy_expand(text):
            return text

        result = run_script(
            script_path=Path("/nonexistent/script.sh"),
            execute_command=dummy_execute,
            parse_command=dummy_parse,
            expand_env_vars=dummy_expand,
        )
        self.assertEqual(result, 1)


if __name__ == "__main__":
    unittest.main()
