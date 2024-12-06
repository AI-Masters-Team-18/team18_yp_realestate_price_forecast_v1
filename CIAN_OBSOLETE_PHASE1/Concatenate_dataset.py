# OBSOLETE - не используется тк решили перейти к парсингу M2.ru
# Description: Сергей собрал в отдельный файл квартиры, по метражу и количеству комнат
# Здесь реализовал скрипт для объединения нескольких csv файлов в один для объединенного датафрейма
import os
import pandas as pd
import sys

# Укажите директорию, где находятся ваши csv файлы
general_directory = '/Users/terrylimax/Desktop/Filtered data/'

# Создадим пустой DataFrame
combined_csv = pd.DataFrame()
print(sys.version)
# Пройдем по всем файлам в директории
for dirpath, dirnames, filenames in os.walk(general_directory): # Используем os.walk, чтобы получить доступ к поддиректориям
    for filename in filenames:
        if filename.endswith(".csv"):
            file_path = os.path.join(dirpath, filename) # Получим путь к файлу
            df = pd.read_csv(file_path, sep=';') # Прочитаем файл
            combined_csv = pd.concat([combined_csv, df], ignore_index=True) # Объединим его с общим DataFrame

# Сохраним итоговый CSV
combined_csv.to_csv("united_filtered.csv", index=False, sep=';')