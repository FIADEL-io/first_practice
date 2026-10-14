import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional, Tuple


@dataclass
class VFSNode:
    name: str
    permissions: str = "rw-r--r--"


@dataclass
class VFSFile(VFSNode):
    content: str = ""


@dataclass
class VFSDirectory(VFSNode):
    children: Dict[str, "VFSNode"] = field(default_factory=dict)


class VFS:
    def __init__(self, source_path: Optional[Path] = None) -> None:
        self.root = VFSDirectory(name="/")
        self.source_path = source_path


def find_or_create_parent(
    root: VFSDirectory,
    parts: Tuple[str, ...],
) -> Optional[VFSDirectory]:
    current = root
    for part in parts:
        if part not in current.children:
            current.children[part] = VFSDirectory(name=part)
        child = current.children[part]
        if not isinstance(child, VFSDirectory):
            return None
        current = child
    return current


def add_node(parent: VFSDirectory, name: str, is_file: bool) -> None:
    if is_file:
        parent.children[name] = VFSFile(name=name)
    elif name not in parent.children:
        parent.children[name] = VFSDirectory(name=name)


def load_vfs_from_directory(directory: Path) -> VFS:
    if not directory.exists():
        raise FileNotFoundError(f"VFS source not found: {directory}")
    if not directory.is_dir():
        raise ValueError(f"Not a directory: {directory}")
    vfs = VFS(source_path=directory.resolve())
    for item in directory.rglob("*"):
        relative = item.relative_to(directory)
        parts = relative.parts
        parent = find_or_create_parent(vfs.root, parts[:-1])
        if parent is None:
            continue
        add_node(parent, parts[-1], item.is_file())
    return vfs


def create_default_vfs() -> VFS:
    vfs = VFS()
    home = VFSDirectory(name="home")
    readme = VFSFile(name="readme.txt", content="Default VFS")
    home.children["readme.txt"] = readme
    vfs.root.children["home"] = home
    return vfs


def clear_physical_directory(directory: Path) -> None:
    if directory.exists():
        for item in directory.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()


def resolve_path(
    root: VFSDirectory,
    current_dir: VFSDirectory,
    path_str: str,
) -> Optional[VFSNode]:
    if not path_str:
        return current_dir
    if path_str.startswith("/"):
        node: VFSNode = root
        parts = path_str.strip("/").split("/")
    else:
        node = current_dir
        parts = path_str.split("/")
    for part in parts:
        if part == "" or part == ".":
            continue
        if part == "..":
            return None
        if not isinstance(node, VFSDirectory):
            return None
        if part not in node.children:
            return None
        node = node.children[part]
    return node


def get_current_dir_from_root(
    root: VFSDirectory,
    cwd_path: str,
) -> VFSDirectory:
    if cwd_path == "/" or cwd_path == "":
        return root
    parts = cwd_path.strip("/").split("/")
    current: VFSDirectory = root
    for part in parts:
        child = current.children.get(part)
        if not isinstance(child, VFSDirectory):
            return root
        current = child
    return current
