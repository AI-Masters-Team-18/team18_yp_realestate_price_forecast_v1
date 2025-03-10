# OBSOLETE - не используется тк решили перейти к парсингу M2.ru
# import pprint
# import requests
# import sys
# import urllib.request
# import ssl
# from bs4 import BeautifulSoup
# import re
# import random
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# import time
# from random import randint
# from fake_useragent.fake import UserAgent
# import undetected_chromedriver as uc

# # proxies = {
# # 'http': proxy,
# # 'https': proxy
# # }

# def proxy_request(url): #функция для запроса через прокси сервис
#     #инициализируем переменные для прокси-сервиса
#     host = 'brd.superproxy.io'
#     port = 33335
#     token = 'ed8a08ff-f504-4e51-8566-297b9fc2934d'
#     API_token = token
#     headers = {
#         "Content-Type": "application/json",
#         "Authorization": f"Bearer {API_token}"
#     }
#     username = 'brd-customer-hl_37518e03-zone-web_unlocker1'
#     password = 'azj2p3inpfgy'
#     cert_path = './New_SSL_certifcate/BrightData_SSL_certificate.crt'
#     context = ssl.create_default_context(cafile=cert_path)
#     proxy = f'{username}:{password}@{host}:{port}'
#     try:
#         opener = urllib.request.build_opener( #настраиваем через opener проброс запросов через прокси
#             urllib.request.ProxyHandler(
#                 {'http': 'http://' + proxy,
#                 'https': 'https://' + proxy}),
#             urllib.request.HTTPSHandler(context=context)) #прокси-пул сервис требует SSL-сертификат, поэтому указываем контекст
#         with opener.open(url) as response: #открываем страницу
#             html = response.read().decode('utf-8')
#         return html
#     except Exception as e:
#         print(f"Error parsing {url}: {e}")
#         return None

# def selenium_request(url,user_agent=None): #функция для запроса через selenium
#     if not user_agent:
#         user_agent = UserAgent()
#     proxy_list = [ #используем публично доступные прокси, тк в сервисе bright data закончился бесплатный триал
#     "194.28.194.146:1080",
#     "213.132.76.9:8081",
#     "185.46.97.75:1080",
#     "212.55.99.157:1080",
#     "178.178.6.143:1080",
#     "194.190.169.197:3701"
#     ]
#     options = Options()
#     options.add_argument("--headless")  # запуск без интерфейса
#     options.add_argument("--disable-gpu") # запуск без GPU, тк не показывается интерфейс
#     options.add_argument("--no-sandbox") # отключение sandbox помогает избежать проблем с правами доступа и конфликтов в окружении
#     options.add_argument(f"user-agent={user_agent.random}")
#     options.add_argument("--disable-blink-features=AutomationControlled") #для обхода защиты от ботов
#     options.add_argument("accept-language=en-US,en;q=0.9")
#     options.add_argument("referer=https://www.cian.ru/")
#     options.add_argument("accept=text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8")

#     #driver = uc.Chrome(options=options)
#     # options.add_argument(f'--proxy-server={random.choice(proxy_list)}') #выбираем случайный публичный прокси из списка
#     driver = webdriver.Chrome(options=options) #инициализируем драйвер
#     # Устанавливаем ожидания
#     driver.set_page_load_timeout(30)  # Таймаут загрузки страницы
#     driver.implicitly_wait(10)        # Неявное ожидание для поиска элементов
#     try:
#         driver.get(url)
#     except Exception as e:
#         print(f"Error parsing {url}: {e}")
#         return None
#     html_code = driver.page_source
#     if not html_code:
#         print(f"Failed to get page {url}")
#         return
#     if 'Ошибка - ЦианКажется' in html_code:
#         try:
#             time.sleep(randint(2, 5))
#             driver.get(url)
#         except Exception as e:
#             print(f"Error parsing {url}: {e}")
#             return None
#     soup = BeautifulSoup(html_code, "html.parser")
#     # Проверка на CAPTCHA
#     if soup.find("div", {"class": "g-recaptcha"}):
#         print("Google reCAPTCHA detected")
#     elif soup.find("div", {"class": "h-captcha"}):
#         print("hCaptcha detected")
#     elif "cf-challenge" in html_code:
#         print("Cloudflare CAPTCHA detected")
#     # else:
#     #     print("No CAPTCHA detected or different CAPTCHA type")
#     # address = soup.find('address')
#     # print(address)
#     driver.quit()
#     #time.sleep(randint(2, 5))
#     return html_code

# def extract_numbers(text): #для случаев, когда нужно достать целое 1 число
#     return ''.join(re.findall(r'\d+', text))

# def extract_numbers_list(text): #для случаев, когда нужно достать несколько/десятичные числа
#     return [float(text_number.replace(",", ".")) for text_number in re.findall(r'\d+,\d+|\d+', text)]

# def parse_page(row, user_agent): #функция для парсинга страницы
#     page_data={}
#     url = row['url'] # извлекаем url из поданного на вход df
#     df_input_underground = None
#     if row['underground']: # извлекаем метро из поданного на вход df
#         df_input_underground = row['underground'] # извлекаем метро, ниже будем сравнивать с тем, что нашли на странице
#     #html_text = proxy_request(url) #получаем html страницы через запрос в пул прокси-серверов
#     html_text = selenium_request(url, user_agent) #получаем html страницы через selenium
#     if not html_text or html_text == None:
#         print(f"Failed to get page {url}")
#         return page_data
#     detailed_page_soup = BeautifulSoup(html_text, 'html.parser')
#     print(f'Получено {detailed_page_soup.get_text()[:100]}')  # проверяем, что получили страницу
#     spans = detailed_page_soup.select("span") #ищем все теги span
#     #сохраняем адрес
#     try:
#         if detailed_page_soup.find('div',{'data-name':'Geo'}):
#             found_geo = detailed_page_soup.find('div',{'data-name':'Geo'})
#             if found_geo:
#                 print("found_geo")
#                 address_tag = found_geo.find('span',{'itemprop': 'name'})
#                 page_data['address'] = address_tag['content'] if address_tag else None
#             else:
#                 print("Geo element not found.")
#     except Exception as e:
#         print(f"Error parsing address data / url {url} {html_text[:100]}: {e}")
#     #сохраняем минуты до метро
#     try:
#         if df_input_underground: #если в исходной строке есть метро
#             #если есть гео информация и есть список метро
#             if found_geo and found_geo.find('ul', {'data-name':'UndergroundList'}).find_all('a',{'class':'a10a3f92e9--underground_link--VnUVj'}):
#                 underground_tags = found_geo.find('ul', {'data-name':'UndergroundList'}).find_all('a',{'class':'a10a3f92e9--underground_link--VnUVj'})
#                 for item in underground_tags:
#                     #если метро совпадает с тем, что в исходной строке, которую подали на вход и если иконка пешехода
#                     if item.text == df_input_underground and item.parent.find('path',{'d': lambda x: x and x.startswith('M8.67')}):
#                         mins = extract_numbers(item.parent.find('span',{'class':'a10a3f92e9--underground_time--YvrcI'}).text)
#                         page_data['mins_to_underground'] = mins
#                         break
#                     else:
#                         page_data['mins_to_underground'] = None
#     except Exception as e:
#         print(f"Error parsing underground data/ url {url}: {e}")
#     try:
#         transport_accessibility = detailed_page_soup.find('div', {'data-name':'TransportAccessibilityEntry'})
#         if transport_accessibility:
#             page_data['transport_accessibility_score'] = extract_numbers_list(transport_accessibility.text)[0]
#     except Exception as e:
#         print(f"Error parsing transport accessibility data: {e}")
#     try:
#         offers_list = detailed_page_soup.find_all('div', {'data-name': 'OfferSummaryInfoItem'})
#         for item in offers_list:
#             try:
#                 offer_details = item.find_all('p') #ищем все теги p
#                 if offer_details[0].text == "Высота потолков":
#                     page_data['ceiling_height_m'] = extract_numbers(offer_details[1].text)
#                 if offer_details[0].text == "Отделка":
#                     page_data['renovation_type'] = offer_details[1].text
#                 if offer_details[0].text == "Парковка":
#                     page_data['parking'] = offer_details[1].text
#                 if offer_details[0].text == "Тип дома":
#                     page_data['house_material_type'] = offer_details[1].text
#                 if offer_details[0].text == "Тип жилья":
#                     page_data['housing_type'] = offer_details[1].text
#                 if offer_details[0].text == "Вид из окон":
#                     page_data['view'] = offer_details[1].text
#                 if offer_details[0].text == "Санузел":
#                     page_data['bathroom_type'] = offer_details[1].text
#                 if offer_details[0].text == "Ремонт":
#                     page_data['renovation_type'] = offer_details[1].text
#             except Exception as e:
#                 print(f"Error parsing offer details for item / url {url}: {e}")
#     except Exception as e:
#         print(f"Error parsing offer summary info: {e}")
#     try:
#         for index, span in enumerate(spans):
#             try:
#                 if span.text.strip() == "Цена за метр":
#                     page_data["price_per_meter"] = extract_numbers(spans[index + 1].text)
#                 if span.text.strip() == "Условия сделки":
#                     page_data["deal_conditions"] = spans[index + 1].text
#                 if span.text.strip() == "Ипотека":
#                     page_data["mortgage_availability"] = spans[index + 1].text
#                 if span.text.strip() == "Год сдачи":
#                     page_data["construction_year"] = int(spans[index + 1].text)
#                 if span.text.strip() == "Дом":
#                     page_data["house_commisioned"] = spans[index + 1].text
#                 if span.text.strip() == "Жилая площадь":
#                     page_data["living_area"] = extract_numbers_list(spans[index + 1].text)[0]
#                 if span.text.strip() == "Площадь кухни":
#                     page_data["kitchen_area"] = extract_numbers_list(spans[index + 1].text)[0]
#                 if span.text.strip() == "Отделка":
#                     page_data["renovation_type"] = spans[index + 1].text
#                 if span.text.strip() == "Тип жилья":
#                     page_data["housing_type"] = spans[index + 1].text
#                 if span.text == "Тип дома":
#                     page_data["house_material_type"] = spans[index + 1].text
#             except Exception as e:
#                 print(f"Error parsing span data for span / url {url}: {e}")
#     except Exception as e:
#         print(f"Error parsing spans: {e}")
#     return page_data
