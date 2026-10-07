import os
import re
import sys
from typing import Callable
from config import AppConfig, parse_args
from script_runner import run_script

DEFAULT_VFS_NAME = "default_vfs"
PROMPT_TEMPLATE = "[{vfs_name}]$ "
ENV_VAR_PATTERN = re.compile(
    r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)"
)
ERROR_UNKNOWN_COMMAND = 127
EXIT_CODE_SUCCESS = 0

CommandHandler = Callable[[list[str]], int]


def expand_env_vars(text: str) -> str:

    def replacer(match: re.Match) -> str:
        var_name = match.group(1) or match.group(2)
        return os.environ.get(var_name, "")

    return ENV_VAR_PATTERN.sub(replacer, text)


def parse_command(line: str) -> tuple[str, list[str]]:
    parts = line.split()
    if not parts:
        return "", []
    return parts[0], parts[1:]


def cmd_ls(args: list[str]) -> int:
    print(f"ls called with args: {args}")
    return 0


def cmd_cd(args: list[str]) -> int:
    print(f"cd called with args: {args}")
    return 0


def cmd_exit(args: list[str]) -> int:
    return EXIT_CODE_SUCCESS


COMMANDS: dict[str, CommandHandler] = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "exit": cmd_exit,
}


def execute_command(command: str, args: list[str]) -> int:
    handler = COMMANDS.get(command)
    if handler is None:
        print(f"error: unknown command '{command}'")
        return ERROR_UNKNOWN_COMMAND
    return handler(args)


def print_debug_info(config: AppConfig) -> None:
    print("=== Debug: Configuration ===")
    print(f"vfs_path:    {config.vfs_path}")
    print(f"script_path: {config.script_path}")
    print("============================")


def main() -> int:
    config = parse_args()
    print_debug_info(config)

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
