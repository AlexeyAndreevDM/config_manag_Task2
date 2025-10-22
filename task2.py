import argparse
import sys
import os
import xml.etree.ElementTree as ET


def parse_config(config_path: str):
    # Проверяем, существует ли файл конфигурации
    if not os.path.isfile(config_path):
        print(f"Ошибка: файл конфигурации не найден: {config_path}", file=sys.stderr)
        sys.exit(1)

    # Парсим XML и ловим ошибки формата
    try:
        tree = ET.parse(config_path)
    except ET.ParseError as e:
        print(f"Ошибка: недопустимый XML в файле конфигурации: {e}", file=sys.stderr)
        sys.exit(1)

    root = tree.getroot() # корень xml файла

    # Вспомогательная функция: извлечь непустой текст из обязательного тега
    def get_required_text(tag: str) -> str:
        elem = root.find(tag)
        if elem is None:
            print(f"Ошибка: отсутствует обязательный параметр конфигурации: <{tag}>", file=sys.stderr)
            sys.exit(1)
        text = elem.text
        if text is None or text.strip() == "":
            print(f"Ошибка: параметр конфигурации <{tag}> пуст или содержит только пробелы", file=sys.stderr)
            sys.exit(1)
        return text.strip()

    # Читаем три обязательных параметра из XML
    package_name = get_required_text("package_name")
    repository = get_required_text("repository")
    mode = get_required_text("mode")

    # Возвращаем конфигурацию как словарь
    return {
        "package_name": package_name,
        "repository": repository,
        "mode": mode,
    }


def parse_cargo_toml_for_dependencies(cargo_toml_path: str) -> list[str]:
    # Убеждаемся,что Cargo.toml существует
    if not os.path.isfile(cargo_toml_path):
        sys.exit(1)

    dependencies = []          # Список имён зависимостей
    in_dependencies = False    # находимся ли мы внутри секции dependencies

    # Читаем файл построчно
    with open(cargo_toml_path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            # Пропускаем пустые строки и комментарии
            if not stripped or stripped.startswith("#"):
                continue

            # Начало секции зависимостей
            if stripped == "[dependencies]":
                in_dependencies = True
                continue

            # Вход в другую секцию — выходим из режима зависимостей
            if stripped.startswith("[") and stripped != "[dependencies]":
                in_dependencies = False
                continue

            # Извлекаем имя зависимости из строки вида "name = ..."
            if in_dependencies and "=" in stripped:
                dep_name = stripped.split("=", 1)[0].strip()
                if dep_name:
                    dependencies.append(dep_name)

    return dependencies


# Настраиваем парсер аргументов командной строки
parser = argparse.ArgumentParser(description="Визуализатор графа зависимостей пакетов (Этап 2)")
parser.add_argument("--config", required=True, help="Путь к XML-файлу конфигурации")
args = parser.parse_args()

# Загружаем конфигурацию из XML
config = parse_config(args.config)
package_name = config["package_name"]
repository = config["repository"]
mode = config["mode"]

# Проверяем, что режим — только "local"
if mode != "local":
    print("Ошибка: на этапе 2 поддерживается только режим 'local'. Укажите <mode>local</mode> в конфигурации.", file=sys.stderr)
    sys.exit(1)

# Сначала ищем Cargo.toml в подкаталоге с именем пакета
cargo_path = os.path.join(repository, package_name, "Cargo.toml")
if not os.path.isfile(cargo_path):
    # Если не найден — пробуем в корне репозитория
    cargo_path = os.path.join(repository, "Cargo.toml")
    if not os.path.isfile(cargo_path):
        # Если и там нет — ошибка
        print(
            f"Ошибка: не удалось найти файл Cargo.toml для пакета '{package_name}'. "
            f"Проверьте наличие файла по одному из путей:\n"
            f"  {os.path.join(repository, package_name, 'Cargo.toml')}\n"
            f"  {os.path.join(repository, 'Cargo.toml')}",
            file=sys.stderr
        )
        sys.exit(1)

# Получаем список прямых зависимостей
dependencies = parse_cargo_toml_for_dependencies(cargo_path)

# Выводим каждую зависимость - требование 2 этапа
for dep in dependencies:
    print(dep)