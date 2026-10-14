import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional


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


def load_vfs_from_directory(directory: Path) -> VFS:
    if not directory.exists():
        raise FileNotFoundError(f"VFS source not found: {directory}")
    if not directory.is_dir():
        raise ValueError(f"Not a directory: {directory}")

    vfs = VFS(source_path=directory.resolve())

    for item in directory.rglob("*"):
        relative = item.relative_to(directory)
        parts = relative.parts
        current: VFSDirectory = vfs.root
        for part in parts[:-1]:
            if part not in current.children:
                current.children[part] = VFSDirectory(name=part)
            child = current.children[part]
            if not isinstance(child, VFSDirectory):
                break
            current = child
        else:
            name = parts[-1]
            if item.is_file():
                current.children[name] = VFSFile(name=name)
            elif item.is_dir():
                if name not in current.children:
                    current.children[name] = VFSDirectory(name=name)

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
