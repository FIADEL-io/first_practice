from pathlib import Path
from typing import Callable


def run_script(
    script_path: Path,
    execute_command: Callable[[str, list[str]], int],
    parse_command: Callable[[str], tuple[str, list[str]]],
    expand_env_vars: Callable[[str], str],
) -> int:
    if not script_path.exists():
        print(f"error: script not found: {script_path}")
        return 1

    with script_path.open("r", encoding="utf-8") as file:
        for line_number, raw_line in enumerate(file, start=1):
            line = raw_line.strip()

            # Пропускаем пустые строки и комментарии
            if not line or line.startswith("#"):
                continue

            # Имитация диалога: выводим ввод
            print(f"[script:{line_number}]$ {line}")

            # Раскрываем переменные окружения
            expanded = expand_env_vars(line)
            command, args = parse_command(expanded)

            # Выполняем команду
            return_code = execute_command(command, args)

            # ВАЖНО для варианта 11: остановка при первой ошибке
            if return_code != 0:
                print(
                    f"error: script stopped at line {line_number}: "
                    f"command '{command}' returned code {return_code}"
                )
                return return_code

    return 0
