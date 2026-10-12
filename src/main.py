import os
import re
import sys
from typing import Callable, List, Optional, Tuple

from config import AppConfig, parse_args
from script_runner import run_script
from vfs import (
    VFS,
    VFSDirectory,
    clear_physical_directory,
    create_default_vfs,
    get_current_dir_from_root,
    load_vfs_from_directory,
    resolve_path,
)

DEFAULT_VFS_NAME = "default_vfs"
PROMPT_TEMPLATE = "[{vfs_name}]$ "
ENV_VAR_PATTERN = re.compile(
    r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)"
)
ERROR_UNKNOWN_COMMAND = 127
ERROR_INVALID_ARGUMENT = 1
EXIT_CODE_SUCCESS = 0

CommandHandler = Callable[[List[str], "Context"], int]


class Context:
    def __init__(self, vfs: VFS) -> None:
        self.vfs = vfs
        self.cwd: str = "/"


def expand_env_vars(text: str) -> str:
    def replacer(match: re.Match) -> str:
        var_name = match.group(1) or match.group(2)
        return os.environ.get(var_name, "")

    return ENV_VAR_PATTERN.sub(replacer, text)


def parse_command(line: str) -> Tuple[str, List[str]]:
    parts = line.split()
    if not parts:
        return "", []
    return parts[0], parts[1:]


def cmd_ls(args: List[str], ctx: Context) -> int:
    if args:
        target_path = args[0]
    else:
        target_path = ctx.cwd

    node = resolve_path(
        ctx.vfs.root,
        get_current_dir_from_root(ctx.vfs.root, ctx.cwd),
        target_path,
    )

    if node is None:
        print(f"error: no such directory: {target_path}")
        return ERROR_INVALID_ARGUMENT

    if not isinstance(node, VFSDirectory):
        print(f"error: not a directory: {target_path}")
        return ERROR_INVALID_ARGUMENT

    for name in sorted(node.children.keys()):
        child = node.children[name]
        suffix = "/" if isinstance(child, VFSDirectory) else ""
        print(f"{name}{suffix}")

    return 0


def cmd_cd(args: List[str], ctx: Context) -> int:
    if not args:
        ctx.cwd = "/"
        return 0

    target_path = args[0]
    current_dir = get_current_dir_from_root(ctx.vfs.root, ctx.cwd)
    node = resolve_path(ctx.vfs.root, current_dir, target_path)

    if node is None:
        print(f"error: no such directory: {target_path}")
        return ERROR_INVALID_ARGUMENT

    if not isinstance(node, VFSDirectory):
        print(f"error: not a directory: {target_path}")
        return ERROR_INVALID_ARGUMENT

    if target_path.startswith("/"):
        ctx.cwd = "/" + "/".join(target_path.strip("/").split("/"))
    else:
        if ctx.cwd == "/":
            ctx.cwd = "/" + target_path
        else:
            ctx.cwd = ctx.cwd + "/" + target_path

    ctx.cwd = ctx.cwd.replace("//", "/")
    return 0


def cmd_pwd(args: List[str], ctx: Context) -> int:
    print(ctx.cwd)
    return 0


def cmd_vfs_init(args: List[str], ctx: Context) -> int:
    if ctx.vfs.source_path:
        clear_physical_directory(ctx.vfs.source_path)

    default_vfs = create_default_vfs()
    ctx.vfs.root = default_vfs.root
    ctx.cwd = "/"
    print("VFS reinitialized to default")
    return 0


def cmd_exit(args: List[str], ctx: Context) -> int:
    return EXIT_CODE_SUCCESS


COMMANDS: dict[str, CommandHandler] = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "pwd": cmd_pwd,
    "vfs-init": cmd_vfs_init,
    "exit": cmd_exit,
}

_global_context: Optional[Context] = None


def execute_command(
    command: str,
    args: List[str],
    ctx: Optional[Context] = None,
) -> int:
    handler = COMMANDS.get(command)
    if handler is None:
        print(f"error: unknown command '{command}'")
        return ERROR_UNKNOWN_COMMAND

    if ctx is None:
        ctx = _global_context
    if ctx is None:
        print("error: no VFS context initialized")
        return ERROR_INVALID_ARGUMENT

    return handler(args, ctx)


def print_debug_info(config: AppConfig) -> None:
    print("=== Debug: Configuration ===")
    print(f"vfs_path:    {config.vfs_path}")
    print(f"script_path: {config.script_path}")
    print("============================")


def main() -> int:
    global _global_context

    config = parse_args()
    print_debug_info(config)

    try:
        vfs = load_vfs_from_directory(config.vfs_path)
    except (FileNotFoundError, ValueError, PermissionError) as exc:
        print(f"error: failed to load VFS: {exc}")
        return 1

    _global_context = Context(vfs)

    prompt = PROMPT_TEMPLATE.format(vfs_name=DEFAULT_VFS_NAME)

    if config.script_path is not None:
        script_result = run_script(
            script_path=config.script_path,
            execute_command=execute_command,
            parse_command=parse_command,
            expand_env_vars=expand_env_vars,
        )
        if script_result != 0:
            return script_result

    while True:
        try:
            line = input(prompt)
        except EOFError:
            print()
            return EXIT_CODE_SUCCESS

        line = expand_env_vars(line.strip())
        if not line:
            continue

        command, args = parse_command(line)
        if command == "exit":
            return EXIT_CODE_SUCCESS

        execute_command(command, args)


if __name__ == "__main__":
    sys.exit(main())
