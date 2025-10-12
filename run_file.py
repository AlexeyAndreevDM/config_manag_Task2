import subprocess
import os

# Убедимся, что main.py находится в той же папке
if not os.path.exists("task2.py"):
    print("Ошибка: main.py не найден в текущей директории!")
    exit(1)

test_cases = [
    ("Тест 1: Успешная загрузка конфигурации\n", "config_corr.xml"),
    ("Тест 2: Отсутствует обязательный параметр <repository>\n", "config_missing_rep.xml"),
    ("Тест 3: Пустое значение в <package_name>\n", "config_missing_packnm.xml"),
    ("Тест 4: Некорректный XML - синтаксическая ошибка\n", "config_missing_mode.xml"),
    ("Тест 5: Несуществующий файл конфигурации\n", "nonexistent_config.xml"),
]

for desc, config_file in test_cases:
    print(f"\n{desc}")
    result = subprocess.run(["python", "task2.py", "--config", config_file])
    print(f"Код возврата: {result.returncode}")
    print()