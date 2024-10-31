import pprint
import requests  
import sys
import urllib.request
import ssl
from bs4 import BeautifulSoup
import re

host = 'brd.superproxy.io'
port = 33335
API_token = 'ed8a08ff-f504-4e51-8566-297b9fc2934d'
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_token}"
}
username = 'brd-customer-hl_37518e03-zone-web_unlocker1'
password = 'azj2p3inpfgy'
cert_path = './New_SSL_certifcate/BrightData_SSL_certificate.crt'
context = ssl.create_default_context(cafile=cert_path) 

proxy = f'{username}:{password}@{host}:{port}'
proxies = {
'http': proxy,
'https': proxy
}

def proxy_request(url): #функция для запроса через прокси сервис
    opener = urllib.request.build_opener( #настраиваем через opener проброс запросов через прокси
        urllib.request.ProxyHandler(
            {'http': 'http://' + proxy,
            'https': 'https://' + proxy}),
        urllib.request.HTTPSHandler(context=context)) #прокси-пул сервис требует SSL-сертификат, поэтому указываем контекст
    
    with opener.open(url) as response: #открываем страницу
        html = response.read().decode('utf-8')

    return html

def extract_numbers(text): #для случаев, когда нужно достать целое 1 число
    return ''.join(re.findall(r'\d+', text))

def extract_numbers_list(text): #для случаев, когда нужно достать несколько/десятичные числа
    return [float(text_number.replace(",", ".")) for text_number in re.findall(r'\d+,\d+|\d+', text)]

def parse_page(row):
    url = row['url'] # извлекаем url из поданного на вход df
    df_input_underground = row['underground'] # извлекаем метро, ниже будем сравнивать с тем, что нашли на странице
    
    html_text = proxy_request(url) #получаем html страницы
    
    detailed_page_soup = BeautifulSoup(html_text, 'html.parser')
    spans = detailed_page_soup.select("span") #ищем все теги span
    page_data={}

    found_geo = detailed_page_soup.find('div', {'data-name': 'Geo'})
    # print(found_geo)
    address = found_geo.find('address')
    if address:
        address_container = address.find('div', {'data-name': 'AddressContainer'})
        
    if address_container:
        address_items = address_container.find_all('a', {'data-name': 'AddressItem'})
        if address_items[2]:
            page_data["area"] = address_items[2].text.split()[1] # убираем р-н, сохраняем название района
        if address_items[3]: #если есть улица
            page_data["street"] = address_items[3].text #сохраняем название улицы

    if address.find('ul', {'data-name': 'UndergroundList'}): #находим на детальной странице метро
        underground_list = address.find('ul', {'data-name': 'UndergroundList'})
        for item in underground_list:
            underground_found = item.find('a',{'class':'a10a3f92e9--underground_link--VnUVj'}).text
            if underground_found == df_input_underground: #если метро совпадает с тем, что в исходной строке, которую подали на вход 
                mins = extract_numbers(item.find('span',{'class':'a10a3f92e9--underground_time--YvrcI'}).text)
                page_data['mins_to_underground'] = mins
            #при такой обработке есть вероятность, что модель будет относиться ко всем стилям передвижения одинаково, 
            #поэтому если будет указано только (10 мин на машине), формат хранения данных в датафрейме будет считываться как пешком до метро
                
    
    transport_accessibility = detailed_page_soup.find('div', {'data-name':'TransportAccessibilityEntry'})
    if transport_accessibility:
        page_data['transport_accessibility_score'] = extract_numbers_list(transport_accessibility.text)[0]


    offers_list = detailed_page_soup.find_all('div', {'data-name': 'OfferSummaryInfoItem'})
    for item in offers_list:
        offer_details = item.find_all('p') #ищем все теги p
        
        if offer_details[0].text == "Высота потолков":
            page_data['ceiling_height_m'] = extract_numbers(offer_details[1].text)

        if offer_details[0].text == "Отделка":
            page_data['renovation_type'] = offer_details[1].text

        if offer_details[0].text == "Парковка":
            page_data['parking'] = offer_details[1].text

        if offer_details[0].text == "Тип дома":
            page_data['house_material_type'] = offer_details[1].text
        
        if offer_details[0].text == "Тип жилья":
            page_data['housing_type'] = offer_details[1].text

        if offer_details[0].text == "Вид из окон":
            page_data['view'] = offer_details[1].text
        
        if offer_details[0].text == "Санузел":
            page_data['bathroom_type'] = offer_details[1].text
        
        if offer_details[0].text == "Ремонт":
            page_data['renovation_type'] = offer_details[1].text
    

    for index, span in enumerate(spans):
        if span.text.strip() == "Цена за метр":
            page_data["price_per_meter"] = extract_numbers(spans[index + 1].text)
        
        if span.text.strip() == "Условия сделки":
            page_data["deal_conditions"] = spans[index + 1].text

        if span.text.strip() == "Ипотека":
            page_data["mortgage_availability"] = spans[index + 1].text

        if span.text.strip() == "Год сдачи":
            page_data["construction_year"] = int(spans[index + 1].text)
        
        if span.text.strip() == "Дом":
            page_data["house_commisioned"] = spans[index + 1].text
        
        if span.text.strip() == "Жилая площадь":
            page_data["living_area"] = extract_numbers_list(spans[index + 1].text)[0]
        
        if span.text.strip() == "Площадь кухни":
            page_data["kitchen_area"] = extract_numbers_list(spans[index + 1].text)[0]

        if span.text.strip() == "Отделка":
            page_data["finishing_type"] = spans[index + 1].text

        if span.text.strip() == "Тип жилья":
            page_data["housing_type"] = spans[index + 1].text
            
        if span.text == "Тип дома":
            page_data["house_material_type"] = spans[index + 1].text
    
    return page_data