import sys
import unittest
from pathlib import Path

sys.path.insert(0, "src")

from vfs import (
    VFSDirectory,
    VFSFile,
    create_default_vfs,
    load_vfs_from_directory,
    resolve_path,
)


class TestLoadVFS(unittest.TestCase):
    def test_minimal(self) -> None:
        vfs = load_vfs_from_directory(Path("test_vfs/minimal"))
        self.assertIn("file.txt", vfs.root.children)
        self.assertIsInstance(vfs.root.children["file.txt"], VFSFile)

    def test_several_files(self) -> None:
        vfs = load_vfs_from_directory(Path("test_vfs/several_files"))
        self.assertIn("a.txt", vfs.root.children)
        self.assertIn("b.txt", vfs.root.children)
        self.assertIn("c.txt", vfs.root.children)

    def test_deep_structure(self) -> None:
        vfs = load_vfs_from_directory(Path("test_vfs/deep"))
        self.assertIn("level1", vfs.root.children)
        level1 = vfs.root.children["level1"]
        self.assertIsInstance(level1, VFSDirectory)
        assert isinstance(level1, VFSDirectory)
        self.assertIn("level2", level1.children)

    def test_nonexistent(self) -> None:
        with self.assertRaises(FileNotFoundError):
            load_vfs_from_directory(Path("/nonexistent_path_xyz"))


class TestDefaultVFS(unittest.TestCase):
    def test_has_home(self) -> None:
        vfs = create_default_vfs()
        self.assertIn("home", vfs.root.children)

    def test_has_readme(self) -> None:
        vfs = create_default_vfs()
        home = vfs.root.children["home"]
        self.assertIsInstance(home, VFSDirectory)
        assert isinstance(home, VFSDirectory)
        self.assertIn("readme.txt", home.children)


class TestResolvePath(unittest.TestCase):
    def test_root(self) -> None:
        vfs = create_default_vfs()
        node = resolve_path(vfs.root, vfs.root, "/")
        self.assertIs(node, vfs.root)

    def test_nested(self) -> None:
        vfs = create_default_vfs()
        node = resolve_path(vfs.root, vfs.root, "/home")
        self.assertIsInstance(node, VFSDirectory)
        assert node is not None
        self.assertEqual(node.name, "home")

    def test_nonexistent(self) -> None:
        vfs = create_default_vfs()
        node = resolve_path(vfs.root, vfs.root, "/nonexistent")
        self.assertIsNone(node)


if __name__ == "__main__":
    unittest.main()
