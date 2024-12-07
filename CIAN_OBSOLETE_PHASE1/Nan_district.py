# OBSOLETE - не используется тк решили перейти к парсингу M2.ru
# Игорь реализовывл геокодер для заполнения пропусков в столбце "district" на основе значения "residential_complex"
import requests
import json
from bs4 import BeautifulSoup

# Вписывается ваш токен для api запросов Я.карт
TOKEN = 'a1c084ab-2715-4b05-8180-2be2f2cdec86'

# Функция find_district(x) находит "district" по значению "residential_complex", где x - значение "residential_complex"


def find_district(x):
    url = f"https://geocode-maps.yandex.ru/1.x/?geocode={x}&format=json&apikey={TOKEN}"
    response = requests.get(url)

    tree = BeautifulSoup(response.content, 'html.parser')
    formatted_html = tree.prettify()
    data = json.loads(formatted_html)
    data_list = data["response"]["GeoObjectCollection"]["featureMember"][0][
        "GeoObject"]["metaDataProperty"]["GeocoderMetaData"]["Address"]['Components']
    for i in data_list:
        if 'район' in (i['name']):
            i_name = i['name'].replace('район', '')
            return i_name.strip()


# Применение функции  find_district(x) для df
# df['district_Nan'] = df['residential_complex'].apply(
#     lambda x: find_district(x))
# df['district'].fillna(df['district_Nan'], inplace=True)

# del df['district_Nan']

# # Выводим результат
# df.head()
