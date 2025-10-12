import subprocess
import os

test_cases = [
    ("Тест 1: Успешная загрузка конфигурации", "config_corr.xml"),
    ("Тест 2: Отсутствует обязательный параметр <repository>", "config_missing_rep.xml"),
    ("Тест 3: Пустое значение в <package_name>", "config_missing_packnm.xml"),
    ("Тест 4: Некорректный XML - синтаксическая ошибка", "config_invalid_xml.xml"),
    ("Тест 5: Несуществующий файл конфигурации", "nonexistent_config.xml"),
]

for desc, config_file in test_cases:
    print(f"\n{desc}")
    result = subprocess.run(["python", "task2.py", "--config", config_file])
    print()