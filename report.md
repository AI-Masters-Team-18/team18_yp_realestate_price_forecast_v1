# Документация проекта

## 1. Структура проекта
Проект состоит из следующих основных модулей:
- **Streamlit интерфейс (`app.py`)**:
  - Отвечает за обработку данных и предоставление графического интерфейса для пользователя.
- **Взаимодействие с FastAPI**:
  - Приложение интегрируется с сервером, реализующим REST API для обучения и управления моделями машинного обучения.
- **Обработка данных**:
  - Осуществляется предобработка данных, включая фильтрацию, преобразование форматов, удаление выбросов и заполнение пропусков.

## 2. Функционал приложения
Приложение предоставляет следующие возможности:
1. **Загрузка данных**:
   - Пользователь загружает данные в формате `.xlsx`.
2. **Анализ данных (EDA)**:
   - Отображение структуры и набора данных.
   - Визуализация распределений числовых данных.
   - Анализ пропущенных значений, выбросов, а также взаимосвязи признаков с целевой переменной.
3. **Обработка данных**:
   - Удаление нерелевантных колонок.
   - Замена пропусков медианными значениями.
   - Преобразование строковых значений в числовой формат.
4. **Модели машинного обучения**:
   - Создание новых моделей.
   - Обучение модели с указанными гиперпараметрами.
   - Визуализация кривой обучения модели.

## 3. Инструкция по использованию

1. **Запуск приложения**:
   - Запуск осуществляется командой:
     ```
     streamlit run app.py
     ```

2. **Загрузка данных**:
   - В боковой панели нажмите на кнопку "Загрузить файл" и выберите файл `.xlsx`.

3. **Анализ данных**:
   - Ознакомьтесь с EDA.
   - Убедитесь, что данные корректно предобработаны.

4. **Создание модели**:
   - Введите уникальный ID для новой модели в разделе "Создать новую модель".
   - Нажмите "Создать модель".

5. **Обучение модели**:
   - Выберите модель из доступного списка.
   - Укажите гиперпараметры.
   - Нажмите "Обучить модель", чтобы запустить процесс обучения.

6. **Визуализация результатов**:
   - После завершения обучения проверьте параметры модели, график обучения, а также метрики.


## 3. Описание модулей

### **Модуль `main.py`**

Модуль `main.py` реализует основной функционал веб-приложения. Он отвечает за работу с REST API, управление моделями машинного обучения, загрузку данных и выполнение предсказаний.

#### Основные компоненты:
- **Эндпоинты API**:
  - `/models`: Возвращает список всех моделей.
  - `/models/create`: Создает новую модель.
  - `/models/set`: Устанавливает активную модель.
  - `/fit`: Запускает процесс обучения модели.
  - `/models/{mid}`: Получает детальную информацию о модели.
  - `/predict`: Выполняет предсказание с использованием модели.
  - `/upload-dataset`: Загружает CSV файл с данными.
  - `/eda`: Выполняет разведочный анализ данных.
  - `/learning-curve`: Вычисляет метрики обучения 


- **Логирование**:

Логирование настраивается через модуль **`logging_config.py`**, обеспечивая удобный вывод информации о запросах, ошибках и статусах задач.

- **Хранение данных**:

Файлы данных загружаются в директорию `/app/data`, а модели хранятся в глобальном словаре **`MODELS`**.

- **Обучение**:

Для обучения используется функция **`train_pipeline`** из модуля **`train_process.py`**, что позволяет реализовать сквозной процесс обучения с настройкой гиперпараметров.

---

### **Модуль `models.py`**

Модуль `models.py` содержит модели Pydantic для валидации данных API, таких как информация о моделях, запросы на обучение и предсказания.

#### Основные компоненты:
- **Модели Pydantic**:
  - `ModelInfo`: Информация о модели.
  - `ModelListResponse`: Список моделей.
  - `SetModelRequest`: Запрос на установку модели.
  - `FitRequest`: Запрос на обучение модели.
  - `LearningCurveResponse`: Ответ с метриками кривой обучения.
  - `PredictRequest`: Запрос на предсказание.
  - `PredictResponse`: Ответ с результатами предсказания.
  - `CreateModelRequest`: Запрос на создание модели.
  - `CreateModelResponse`: Ответ после создания модели.
  - `UploadDatasetResponse`: Ответ после загрузки данных.
  - `EDAResponse`: Ответ с результатами анализа данных.

---

### **Модуль `logging_config.py`**

Модуль `logging_config.py` отвечает за настройку логирования в приложении. Он настраивает два обработчика: консольный и файловый, с ротацией логов.

#### Основные компоненты:
- **Переменные**:
  - `LOG_DIR`: Путь к директории для хранения логов.
  - `LOG_FILE`: Имя файла для записи логов.
- **Функция `setup_logging()`**:
  - Настроена для записи логов в файл с ежедневной ротацией и отображения логов в консоли.

---

### **Модуль `train_process.py`**

Модуль `train_process.py` обеспечивает создание и обучение моделей машинного обучения, включая этапы предобработки данных и тренировки моделей.

#### Основные компоненты:
- **Класс `RoomTransformer`**: Преобразует данные о количестве комнат.
- **Функция `build_pipeline`**: Строит пайплайн для предобработки и обучения модели.
- **Функция `train_pipeline`**: Загружает данные, обучает модель и оценивает её производительность.

## 4. Dockerfile

Этот `Dockerfile` используется для создания Docker-образа приложения. 

###  Подробное описание:

1. **`FROM python:3.9-slim`**  
   Указывает базовый образ для контейнера. Используется минималистичный образ Python версии 3.9 (`slim` - легковесная версия, подходящая для сокращения размера конечного образа).

2. **`WORKDIR /app`**  
   Устанавливает рабочую директорию контейнера. Все последующие команды будут выполняться внутри этой директории.

3. **`COPY requirements.txt /app/`**  
   Копирует файл `requirements.txt` из локальной файловой системы в директорию `/app` контейнера.

4. **`RUN pip install --no-cache-dir -r requirements.txt`**  
   Устанавливает зависимости Python, указанные в файле `requirements.txt`. Флаг `--no-cache-dir` предотвращает сохранение временных файлов, что снижает размер образа.

5. **`COPY . /app`**  
   Копирует все файлы и директории из текущей директории на хосте в директорию `/app` внутри контейнера.

6. **`EXPOSE 8000`**  
   Указывает, что приложение будет прослушивать порт `8000` внутри контейнера. Это нужно для взаимодействия с приложением из вне контейнера.

7. **`CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]`** 

   Определяет команду, которая будет выполняться при запуске контейнера. Здесь запускается сервер Uvicorn, используя модуль `main` и приложение `app`:
   - `--host 0.0.0.0`: позволяет принимать подключения со всех IP-адресов.
   - `--port 8000`: указывает порт, на котором будет запущен сервер.

---

### Инструкция по использованию

1. **Создание Docker-образа**  
   ```
   docker build -t my-python-app
   ```

2. **Запуск контейнера** 

Производится на основе созданного образа
```
docker run -p 8000:8000 my-python-app
```
3. **Ссылка на приложение**

После запуска приложение будет доступно по адресу:
http://localhost:8000