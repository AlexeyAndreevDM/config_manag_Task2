import argparse
import sys
import os
import xml.etree.ElementTree as ET


def parse_config(config_path: str):
    # Проверяем, существует ли указанный файл конфигурации
    if not os.path.isfile(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    # Парсим XML-файл и обрабатываем ошибки формата
    try:
        tree = ET.parse(config_path)
    except ET.ParseError as e:
        raise ValueError(f"Invalid XML in configuration file: {e}")

    root = tree.getroot()

    # Вспомогательная функция для извлечения обязательного текстового значения из XML-тега
    def get_required_text(tag: str) -> str:
        elem = root.find(tag)
        if elem is None:
            raise ValueError(f"Missing required configuration parameter: <{tag}>")
        text = elem.text
        if text is None or text.strip() == "":
            raise ValueError(f"Configuration parameter <{tag}> is empty or whitespace-only")
        return text.strip()

    # Извлекаем обязательные параметры конфигурации
    package_name = get_required_text("package_name")
    repository = get_required_text("repository")
    mode = get_required_text("mode")

    # Возвращаем конфигурацию в виде словаря
    return {
        "package_name": package_name,
        "repository": repository,
        "mode": mode,
    }


# Настраиваем парсер аргументов командной строки
parser = argparse.ArgumentParser(description="Package dependency graph visualizer (Stage 1 prototype)")
parser.add_argument(
    "--config",
    required=True,
    help="Path to the XML configuration file"
)
args = parser.parse_args()

# Загружаем и выводим конфигурацию или обрабатываем ошибки
try:
    config = parse_config(args.config)
    for key, value in config.items():
        print(f"{key}={value}")
except (FileNotFoundError, ValueError) as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)