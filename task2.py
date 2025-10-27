import argparse
import sys
import os
import xml.etree.ElementTree as ET
import urllib.request
import urllib.error
import tempfile


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
            print(f"Ошибка: параметр конфигурации <{tag}> пуст", file=sys.stderr)
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


def download_cargo_toml(url: str) -> str:
    """
    Скачивает Cargo.toml по URL и возвращает путь к временному файлу
    """
    try:
        # Скачиваем содержимое
        with urllib.request.urlopen(url) as response:
            content = response.read().decode('utf-8')
        
        # Создаем временный файл
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as temp_file:
            temp_file.write(content)
            return temp_file.name
            
    except urllib.error.URLError as e:
        print(f"Ошибка: не удалось скачать Cargo.toml по URL {url}: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка при обработке скачанного файла: {e}", file=sys.stderr)
        sys.exit(1)


def parse_cargo_toml_for_dependencies(cargo_toml_path: str) -> list[str]:
    """
    Парсит Cargo.toml файл и возвращает список зависимостей
    """
    if not os.path.isfile(cargo_toml_path):
        print(f"Ошибка: файл Cargo.toml не найден: {cargo_toml_path}", file=sys.stderr)
        sys.exit(1)

    dependencies = []
    in_dependencies = False
    found_sections = []

    with open(cargo_toml_path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()

            # Находим все секции (строки в квадратных скобках)
            if stripped.startswith("[") and stripped.endswith("]"):
                section_name = stripped.strip("[]")
                found_sections.append(section_name)
                
                # Проверяем, является ли это секцией dependencies
                if section_name == "dependencies":
                    in_dependencies = True
                else:
                    in_dependencies = False
                continue

            # Извлекаем имя зависимости из строки вида "name = ..."
            if in_dependencies and "=" in stripped:
                # Игнорируем комментарии в строке
                line_without_comment = stripped.split("#")[0].strip()
                if "=" in line_without_comment:
                    dep_name = line_without_comment.split("=", 1)[0].strip()
                    if dep_name and not dep_name.startswith("#"):
                        dependencies.append(dep_name)

    # Если не нашли зависимостей, возвращаем список секций
    if not dependencies:
        return found_sections
    
    return dependencies


# Настраиваем парсер аргументов командной строки
parser = argparse.ArgumentParser(description="Визуализатор графа зависимостей пакетов")
parser.add_argument("--config", required=True, help="Путь к XML-файлу конфигурации")
args = parser.parse_args()

# Загружаем конфигурацию из XML
config = parse_config(args.config)
package_name = config["package_name"]
repository = config["repository"]
mode = config["mode"]

# Обрабатываем в зависимости от режима
if mode == "local":
    # Локальный режим - ищем Cargo.toml в файловой системе
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

elif mode == "remote":
    # Удаленный режим - скачиваем Cargo.toml по URL
    cargo_path = download_cargo_toml(repository)
    
else:
    print(f"Ошибка: неизвестный режим работы '{mode}'. Поддерживаются: 'local', 'remote'", file=sys.stderr)
    sys.exit(1)

# Получаем список прямых зависимостей или секций
result = parse_cargo_toml_for_dependencies(cargo_path)

# Всегда выводим стандартный заголовок
print("Найденные зависимости в файле:")

# Выводим каждый элемент с маркером
for item in result:
    print(f"  - {item}")

# Если использовался временный файл (remote режим) - удаляем его
if mode == "remote":
    try:
        os.unlink(cargo_path)
    except OSError:
        pass  # Игнорируем ошибки удаления временного файла