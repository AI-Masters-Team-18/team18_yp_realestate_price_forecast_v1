import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import json
import requests
from backend.models import SetModelRequest
import plotly.graph_objects as go

sys.path.append(str(Path(__file__).resolve().parent.parent))


def main():
    st.sidebar.header("Загрузить файл")
    uploaded_file = st.sidebar.file_uploader("Выберите файл", type=["xlsx"])

    if uploaded_file is not None:
        try:
            st.header("Датасет")
            df_filtered = pd.read_excel(uploaded_file)

        except Exception as err:
            st.error(err)
            return

        st.dataframe(df_filtered.head())

        st.header("EDA")

        if st.checkbox("Показать информацию о датасете"):
            st.subheader("Информация о датасете")
            st.text(f"Размер: {df_filtered.shape}")
            st.text("Типы данных:")
            st.write(df_filtered.dtypes)

        if st.checkbox("Показать пропущенные значения"):
            st.subheader("Пропущенные значения")
            st.write(df_filtered.isnull().sum())

        if st.checkbox("Показать описательные статистики"):
            st.subheader("Описательные статистики")
            st.write(df_filtered.describe())

        columns_to_drop = [
            "ссылка",
            "Санузел",
            "Кол-во санузлов",
            "описание",
            "Временная эпоха",
            "Отопление",
            "Балкон/лоджия",
            "Серия дома",
            "Кондиционер",
            "Кухонная мебель",
            "Холодильник",
            "Хорошая школа",
            "Фитнес клуб",
            "Детский сад",
            "Посудомойка",
            "Интернет",
            "Телевизор",
            "Торговый центр",
            "Хорошие школы",
            "Стиральная машина",
            "Source_File",
            "Sheet_Name",
            "адрес",
            "Лифт",
            "Парковка",
            "Парк или зона отдыха",
            "Консьерж",
            "Вид из окна",
            "Территория",
            "Реновация",
            "Мебель",
            "Вид из окон",
        ]
        df_filtered = df_filtered.drop(columns=[col for col in columns_to_drop if col in df_filtered.columns])
        st.write(f"Столбцы: {columns_to_drop} мало влияют на стоимость квартиры, удалим их")

        initial_size = df_filtered.shape[0]
        df_filtered = df_filtered.drop_duplicates()
        final_size = df_filtered.shape[0]
        st.write(f"Удалим {initial_size - final_size} повторяющихся значений")

        st.subheader("Поиск пропущенных значений")
        st.subheader("Пункт 1")
        columns_to_clean = [
            "до центра",
            "Площадь квартиры",
            "Жилая площадь",
            "Высота потолков",
            "цена",
            "Площадь кухни",
        ]
        st.write(
            f"Преобразуем значения столбцов {columns_to_clean} в числовой формат (float64), заменим запятые на точки, некорректные значения преобразуем в NaN, а затем заполним их медианой соответствующего столбца"
        )
        for column in columns_to_clean:
            df_filtered[column] = (
                df_filtered[column]
                .astype(str)
                .str.strip()
                .str.replace(",", ".", regex=False)
                .str.extract(r"(-?\d+\.?\d*)")[0]
            )
            df_filtered[column] = pd.to_numeric(df_filtered[column], errors="coerce")
            if not df_filtered[column].isna().all():
                df_filtered[column] = df_filtered[column].fillna(df_filtered[column].median())

        st.subheader("Пункт 2")
        st.write(
            "Преобразуем значения столбцов ['Этаж', 'Этажей в доме'] в целочисленный формат (int), некорректные значения заменим на NaN, а затем заполним их медианой соответствующего столбца."
        )
        df_filtered[["Этаж", "Этажей в доме"]] = df_filtered[["Этаж", "Этажей в доме"]].apply(
            lambda col: pd.to_numeric(col, errors="coerce").fillna(col.median()).astype(int)
        )

        st.subheader("Пункт 3")
        st.write(
            "Мы заметили, что значения в столбце Срок сдачи представляют собой строки, содержащие информацию о квартале и годе, например, '4\xa0кв.\xa02025\xa0г.', или только год, например, '2025\xa0г.'. Также встречаются значения nan и 'Неизвестно'. Однако для анализа нас интересует только год. Поэтому мы извлекли год из строк, заменили 'Неизвестно' на NaN, а некорректные значения преобразовали в 0, после чего перевели данные в целочисленный формат."
        )
        df_filtered["Срок сдачи"] = (
            df_filtered["Срок сдачи"]
            .str.replace("\xa0", " ")
            .replace("Неизвестно", np.nan)
            .str.extract(r"(\d{4})")
            .fillna(0)
            .astype(int)
        )

        st.subheader("Пункт 4")
        st.write(
            "Преобразуем значения столбца Год постройки в целочисленный формат (int), некорректные значения заменим на 0, чтобы обеспечить консистентность данных для дальнейшего анализа."
        )
        df_filtered["Год постройки"] = df_filtered["Год постройки"].fillna(0).astype(int)

        st.subheader("Пункт 5")
        st.write(
            "Объединим столбцы Год постройки и Срок сдачи в один столбец Год постройки, подставляя значения из Срок сдачи, если данные в Год постройки отсутствуют. Это упростит структуру данных и устранит дублирование."
        )
        df_filtered["Год постройки"] = df_filtered["Год постройки"].where(
            df_filtered["Год постройки"] > 0, df_filtered["Срок сдачи"]
        )
        df_filtered = df_filtered.drop(columns=["Срок сдачи"])

        st.subheader("Пункт 6")
        st.write(
            "Посмотрим на столбец Тип жилья. В нём содержатся значения: [nan, 'апартаменты']. Если тип жилья не указан (NaN), будем считать его квартирой. Заменим NaN на квартира."
        )
        st.write(df_filtered["Тип жилья"].unique())
        df_filtered["Тип жилья"] = df_filtered["Тип жилья"].fillna("квартира")

        st.subheader("Пункт 7")
        st.write(
            "Посчитаем количество строк, где хотя бы один из столбцов: станция1, станция2 или станция3 имеет значение NaN."
        )
        st.write(df_filtered[["станция1", "станция2", "станция3"]].isna().any(axis=1).sum())
        st.write(
            "Удалим эти строки, поскольку отсутствие данных о станциях может указывать на то, что квартиры находятся за пределами города."
        )
        df_filtered = df_filtered.dropna(subset=["станция1", "станция2", "станция3"], how="any")
        st.write(
            "Преобразуем значения столбцов время_до_станции1, пешком1, время_до_станции2, пешком2, время_до_станции3, пешком3 в целочисленный формат (int)."
        )
        columns_to_convert = [
            "время_до_станции1",
            "пешком1",
            "время_до_станции2",
            "пешком2",
            "время_до_станции3",
            "пешком3",
        ]

        df_filtered[columns_to_convert] = df_filtered[columns_to_convert].astype(int)
        st.write(
            'Оставим только ближайшую станцию метро. Определим минимальное время из столбцов время_до_станции1, время_до_станции2, время_до_станции3. Сохраним её название, время и признак "пешком". Удалим данные о других станциях.'
        )
        time_columns = [f"время_до_станции{i}" for i in range(1, 4)]
        station_columns = [f"станция{i}" for i in range(1, 4)]
        walk_columns = [f"пешком{i}" for i in range(1, 4)]

        min_indices = df_filtered[time_columns].idxmin(axis=1).str.extract(r"(\d)")[0].astype(int) - 1

        df_filtered["станция"] = df_filtered[station_columns].to_numpy()[range(len(df_filtered)), min_indices]
        df_filtered["время"] = df_filtered[time_columns].to_numpy()[range(len(df_filtered)), min_indices]
        df_filtered["пешком"] = df_filtered[walk_columns].to_numpy()[range(len(df_filtered)), min_indices]

        df_filtered.drop(columns=station_columns + time_columns + walk_columns, inplace=True)

        st.subheader("Пункт 8")
        st.write(
            "Для категориальных данных в столбце Материал стен заполним пропуски наиболее часто встречающимся значением (модой)."
        )
        st.write(df_filtered["Материал стен"].unique())
        df_filtered["Материал стен"] = df_filtered["Материал стен"].fillna(df_filtered["Материал стен"].mode()[0])

        st.subheader("Пункт 9")
        st.write("Проверим уникальные значения в столбцах Отделка и Ремонт ")
        st.write(df_filtered["Отделка"].unique())
        st.write(df_filtered["Ремонт"].unique())
        st.write("Приведём значения в столбце Отделка к единому формату")
        df_filtered["Отделка"] = df_filtered["Отделка"].replace(
            {
                "без отделки": "Без отделки",
                "чистовая": "Чистовая отделка",
                "предчистовая": "Предчистовая отделка",
            }
        )
        st.write("Заполним пропуски в столбце Ремонт значениями из столбца Отделка, если они отсутствуют")
        df_filtered["Ремонт"] = df_filtered["Ремонт"].fillna(df_filtered["Отделка"])
        st.write("Удалим столбец Отделка")
        df_filtered = df_filtered.drop(columns=["Отделка"])
        st.write(
            "Для категориальных данных в столбце Ремонт заполним пропуски наиболее часто встречающимся значением (модой)."
        )
        df_filtered["Ремонт"] = df_filtered["Ремонт"].fillna(df_filtered["Ремонт"].mode()[0])

        st.subheader("Вывод")
        st.write(
            "Таким образом, в нашем датасете больше не осталось пропущенных значений. Однако стоит обратить внимание на столбец Год постройки, где значения NaN были заменены на 0. В результате, около 38% квартир не имеют указания года постройки. Для дальнейшего анализа и обучения модели стоит рассмотреть возможность удаления таких данных или заполнения их медианным значением."
        )
        st.write(df_filtered.isna().sum())

        st.subheader("Валидация значений")
        st.write(
            "Выполним валидацию значений в числовых столбцах DataFrame, подсчитывая количество отрицательных значений в каждом из них."
        )
        numeric_columns = df_filtered.select_dtypes(include=["int64", "float64"]).columns

        data = [
            {
                "Название": column,
                "Кол-во отрицательных значений": (df_filtered[column] < 0).sum(),
            }
            for column in numeric_columns
        ]
        st.write(pd.DataFrame(data))
        st.write("Удалим строки, содержащие отрицательные значения в числовых столбцах.")
        df_filtered = df_filtered[(df_filtered[numeric_columns] >= 0).all(axis=1)]
        st.subheader("Изучение поведения каждого признака")
        st.write("Переименуем колонки")
        df_filtered.rename(
            columns={
                "до центра": "Расстояние до центра",
                "комнат": "Кол-во комнат",
                "Площадь квартиры": "Общая площадь",
                "Этажей в доме": "Кол-во этажей в доме",
                "цена": "Цена",
                "Жилая площадь": "Жилая площадь",
                "Высота потолков": "Высота потолков",
                "Материал стен": "Материал стен",
                "Этаж": "Этаж",
                "Ремонт": "Ремонт",
                "Год постройки": "Год постройки",
                "Тип жилья": "Тип жилья",
                "Площадь кухни": "Площадь кухни",
                "станция": "Станция",
                "время": "Время",
                "пешком": "Пешком",
            },
            inplace=True,
        )

        df_filtered

        st.write("Функция для визуализации распределений и boxplot числовых признаков")

        def plot_feature_distributions(data, features):
            for feature in features:
                fig, axes = plt.subplots(1, 2, figsize=(12, 6))
                sns.histplot(
                    data[feature],
                    bins=30,
                    kde=True,
                    ax=axes[0],
                    color="skyblue",
                    edgecolor="black",
                )
                axes[0].set_title(f"Распределение '{feature}'", fontsize=14)
                axes[0].set_xlabel(feature, fontsize=12)
                axes[0].set_ylabel("Частота", fontsize=12)
                axes[0].grid(visible=True, linestyle="--", alpha=0.6)
                sns.boxplot(y=data[feature], ax=axes[1], color="lightgreen", width=0.5)
                axes[1].set_title(f"Boxplot '{feature}'", fontsize=14)
                axes[1].set_ylabel(feature, fontsize=12)
                axes[1].grid(visible=True, linestyle="--", alpha=0.6)
                plt.tight_layout()
                st.pyplot(fig)

        numerical_features = df_filtered.select_dtypes(include=["int64", "float64"]).columns.tolist()
        st.write("Числовые признаки:", numerical_features)

        if numerical_features:
            st.write("Распределения числовых признаков:")
            plot_feature_distributions(df_filtered, numerical_features)

        st.subheader("Общие выводы по всем графикам")
        st.markdown(
            """
        1. **Расстояние до центра**:
           - **Гистограмма**: Наблюдается высокая концентрация значений в диапазоне **0–15 км**, но есть значительное количество выбросов на больших расстояниях до **30 км**.
           - **Boxplot**: Указывает на наличие выбросов, особенно в верхнем диапазоне значений (дальние расстояния).

        2. **Общая площадь**:
           - **Гистограмма**: Распределение сильно скошено вправо, большинство значений лежит в диапазоне **20–200 м²**.
           - **Boxplot**: Множество выбросов с общей площадью более **200 м²**, что требует дополнительной проверки.

        3. **Жилая площадь**:
           - **Гистограмма**: Основная часть значений сосредоточена в диапазоне **10–50 м²**.
           - **Boxplot**: Наблюдается множество выбросов, особенно в верхнем диапазоне (свыше **100 м²**).

        4. **Этаж**:
           - **Гистограмма**: Большинство объектов находится на **1–20 этажах**, с постепенным убыванием частоты.
           - **Boxplot**: Имеются выбросы для высотных зданий, особенно этажи **50+**.

        5. **Год постройки**:
           - **Гистограмма**: Два пика — **до 2000 года** и в районе **новостроек (после 2000)**.
           - **Boxplot**: Из-за распределения во времени выбросы не видны, но имеются значения, которые можно считать аномалиями.

        6. **Высота потолков**:
           - **Гистограмма**: Большинство значений сконцентрированы в районе **2–3 метров**, но есть экстремальные выбросы.
           - **Boxplot**: Явные выбросы выше **4 метров**, включая аномалии с **50+ метров**, что требует анализа.

        7. **Цена**:
           - **Гистограмма**: Основная масса значений сосредоточена на низких ценах, с редкими высокими выбросами.
           - **Boxplot**: Много выбросов, особенно в верхнем диапазоне, где цена достигает **сверхвысоких значений**.

        8. **Количество этажей в доме**:
           - **Гистограмма**: Большинство зданий имеет **5–20 этажей**, с отдельными пиками в районе **20+ этажей**.
           - **Boxplot**: Наблюдаются выбросы, связанные с высотными зданиями (**60+ этажей**).

        9. **Площадь кухни**:
           - **Гистограмма**: Большинство значений находится в диапазоне **5–15 м²**, с выбросами вплоть до **140 м²**.
           - **Boxplot**: Явные выбросы превышают нормальные значения (более **20 м²**).

        10. **Время**:
            - **Гистограмма**: Основная масса данных сосредоточена в диапазоне **10–30 единиц**, с плавным убыванием частоты.
            - **Boxplot**: Значения **40+** можно считать выбросами.

        11. **Пешком**:
            - **Гистограмма**: Бинарное распределение с двумя четкими значениями **0** и **1**.
            - **Boxplot**: Значение **1** преобладает, а **0** можно считать редким выбросом.')
            """
        )

        st.subheader("Функция для визуализации взаимосвязи числовых признаков с целевой переменной")

        def plot_feature_price_relationships(data, features, target):
            features = [feature for feature in features if feature != target]

            for feature in features:
                fig, ax = plt.subplots(figsize=(8, 6))  # Создаем фигуру и ось
                sns.scatterplot(
                    x=data[feature],
                    y=data[target],
                    color="cornflowerblue",
                    edgecolor="black",
                    alpha=0.7,
                    ax=ax,
                )
                ax.set_title(f"Взаимосвязь '{feature}' с '{target}'", fontsize=14)
                ax.set_xlabel(feature, fontsize=12)
                ax.set_ylabel(target, fontsize=12)
                ax.grid(visible=True, linestyle="--", alpha=0.6)

                # Отображаем график через Streamlit
                st.pyplot(fig)

        plot_feature_price_relationships(df_filtered, numerical_features, "Цена")

        st.subheader("Общие выводы по всем диаграммам рассеивания:")
        st.markdown(
            """

        1. **Взаимосвязь "Расстояние до центра" с "Ценой"**:
           - Объекты, расположенные **ближе к центру** (меньшие значения расстояния), имеют более **высокие цены**.
           - С увеличением расстояния от центра цены значительно снижаются.
           - Наблюдаются **выбросы** с аномально высокими значениями цены, независимо от расстояния.

        2. **Взаимосвязь "Общая площадь" с "Ценой"**:
           - Прямая зависимость: **большая площадь** объекта приводит к более высокой цене.
           - Основная масса объектов сосредоточена в диапазоне небольшой площади и низких цен.
           - **Выбросы** присутствуют среди объектов с большими площадями и высокими ценами.

        3. **Взаимосвязь "Жилая площадь" с "Ценой"**:
           - Аналогично общей площади: объекты с **большей жилой площадью** имеют тенденцию к более высоким ценам.
           - Большая часть точек сосредоточена на **малых значениях площади и цен**, с некоторыми выбросами.

        4. **Взаимосвязь "Этаж" с "Ценой"**:
           - Наибольшие цены наблюдаются на **низких этажах**.
           - С увеличением этажа цена имеет тенденцию к стабилизации на более низком уровне.
           - Наблюдаются **выбросы** с высокой стоимостью, преимущественно на низких этажах.

        5. **Взаимосвязь "Год постройки" с "Ценой"**:
           - Объекты - новостройки имеют более **высокие цены**.

        6. **Взаимосвязь "Высота потолков" с "Ценой"**:
           - В диапазоне **стандартной высоты потолков** (около 2.5-4 м) цены распределены равномерно.
           - Аномально высокие значения высоты потолков (до 400) сопровождаются выбросами по цене, что вероятно связано с ошибками в данных.

        7. **Взаимосвязь "Количество этажей в доме" с "Ценой"**:
           - В домах с **малым количеством этажей** цены имеют более широкий диапазон и включают высокие значения.
           - С увеличением количества этажей цены стабилизируются на низком уровне.
           - Наблюдаются выбросы с высокой стоимостью, сосредоточенные среди малых значений этажности.

        8. **Взаимосвязь "Площадь кухни" с "Ценой"**:
           - Прямая зависимость: большая **площадь кухни** коррелирует с более высокими ценами.
           - Основная масса объектов с малой площадью кухни имеет низкую стоимость.
           - Наличие выбросов с аномально высокими значениями требует проверки.

        9. **Взаимосвязь "Время" с "Ценой"**:
           - Основное количество объектов сосредоточено при малых значениях "Времени".

        10. **Взаимосвязь "Пешком" с "Ценой"**:
            - Объекты с **пешей доступностью** (значение "1") имеют больший разброс и высокие цены.
            - Объекты без пешей доступности ("0") имеют более низкие и стабилизированные цены.

        ---

        ### Итоговые выводы:
        - **Основные факторы**, влияющие на цену, включают **площадь** (общая, жилая, кухня), **этаж**, **высоту потолков** и **пешую доступность**.
        - **Удалённость от центра** является значимым фактором: **чем ближе к центру**, тем выше цена.
        - **Современные объекты** имеют преимущественно высокие цены.
        - Наблюдается **множество выбросов** во всех метриках, что требует дополнительного анализа для проверки достоверности данных.
        """
        )
        st.subheader("Попарные распределения признаков")
        pairplot = sns.pairplot(df_filtered, diag_kind="kde", plot_kws={"alpha": 0.6})
        pairplot.fig.suptitle("Попарные распределения признаков", y=1.02, fontsize=16)
        st.pyplot(pairplot.fig)

        URL = "http://127.0.0.1:8000"  # для вызова FastAPI

        # Создаем модель
        st.header("Создать новую модель")
        with st.form("create_model"):
            new_model_id = st.text_input("Введите ID новой модели", value="model_X")
            submitted = st.form_submit_button("Создать модель")
            if submitted:
                payload = {"model_id": new_model_id}
                resp = requests.post(f"{URL}/models/create", json=payload)
                if resp.status_code == 200:
                    st.success(resp.json()["message"])
                else:
                    st.error(resp.text)
        # Обучаем модель
        st.header("Выбираем модель и обучаем")
        # получаем список созданных моделей
        try:
            resp_models = requests.get(f"{URL}/models")
            resp_models.raise_for_status()
            models_data = resp_models.json().get("models", [])
            if not models_data:
                st.warning("Модели не найдены")
            else:
                for m in models_data:
                    try:
                        # Показываем детали модели, включая коэффициенты с гиперпараметрами, если модели уже были обучены
                        resp_model = requests.get(f"{URL}/models/{m['model_id']}")
                        resp_model.raise_for_status()
                        model_data = resp_model.json()
                        st.write(
                            f"**{m['model_id']}**  Active={m['is_active']}  | {m['description']} | {model_data['detailed_info']}"
                        )
                    except requests.exceptions.RequestException as e:
                        st.warning(f"Не удалось получить данные для модели {m['model_id']}: {e}")
        except requests.exceptions.RequestException as e:
            st.error(f"Ошибка при получении списка моделей: {e}")
            models_data = []
        except Exception as e:
            st.error(f"Ошибка: {e}")

        # Выбор модели
        if models_data:
            model_options = [m["model_id"] for m in models_data]
            model_id = st.selectbox("Выберите модель", model_options)
            if model_id:
                st.write(f"Выбрана модель: {model_id}. Введите гиперпараметры модели")
                alpha_input = st.number_input("alpha", value=1.0)
                max_iter_input = st.number_input("max_iter", value=1000)

            # обучаем выбранную модель
            if st.button("Обучить модель") and alpha_input and max_iter_input:
                if not model_id:
                    st.error("Выбор ID модели обязателен")
                elif not uploaded_file:
                    st.error("Загрузите файл с данными")
                else:
                    # перед обучением, сначала нужно сделать ее активной
                    try:
                        request_body = SetModelRequest(
                            model_id=model_id
                        ).dict()  # преобразуем в dict, чтобы requests смог преобразовать
                        response = requests.post(f"{URL}/models/set", json=request_body)
                        response.raise_for_status()
                        if response.status_code == 200:
                            response_data = response.json()
                            if response_data.get("status") == "OK":
                                st.success(
                                    response_data.get("message")
                                )  # показываем пользователю успешное сообщение от сервера
                    except requests.exceptions.HTTPError as e:
                        st.error(f"Ошибка при попытке установке модели: {e.response.status_code} - {e.response.text}")
                        return
                    except requests.exceptions.RequestException as e:
                        st.error(f"Ошибка при попытке установке модели: {e}")
                        return
                    # потом обучаем модель
                    try:
                        request_data_fit = {
                            "model_id": model_id,
                            "hyperparams": {
                                "alpha": alpha_input,
                                "max_iter": max_iter_input,
                            },
                            "dataframe": df_filtered.to_dict(orient="records"),
                        }
                        response = requests.post(f"{URL}/fit", json=request_data_fit)
                        response.raise_for_status()
                        if response.status_code == 201:
                            st.success("Модель начала обучаться!")
                            st.json(response.json())
                    except requests.exceptions.HTTPError as e:
                        st.error(f"Ошибка сервера: {e.response.status_code} - {e.response.text}")
                        return
                    except requests.exceptions.RequestException as e:
                        st.error(f"Ошибка клиента при запросе: {e}")
                        return
                    except json.JSONDecodeError:
                        st.error("Ошибка при загрузке гиперпараметров")
                        return
                    except Exception as err:
                        st.error(f"Ошибка: {str(err)}")
                        return
                # показываем детали обученной модели и кривую обучения
                st.subheader("Детали обученной модели")
                try:
                    # показываем на клиенте детали обученной модели
                    resp_model = requests.get(f"{URL}/models/{model_id}")
                    resp_model.raise_for_status()
                    model_data = resp_model.json()
                    if model_data:
                        st.write(f"Детали обученной модели: {model_data}")
                    else:
                        st.warning("Данные модели не найдены")
                    # показываем кривую обучения
                    hyperparams = {model_data.get("alpha"), model_data.get("max_iter")}
                    model_id = model_data.get("model_id")
                    request_structure = {
                        "model_id": model_id,
                        "hyperparams": hyperparams,
                        "dataframe": df_filtered.to_dict(orient="records"),
                    }
                    response = requests.post(f"{URL}/plot_learning_curve", json=request_structure)
                    response.raise_for_status()
                    if response.status_code == 200:
                        st.write("Кривая обучения")
                        train_sizes = response.json().get("train_sizes")
                        train_scores_mean = response.json().get("train_scores_mean")
                        test_scores_mean = response.json().get("test_scores_mean")

                        fig = go.Figure()
                        fig.add_trace(
                            go.Scatter(
                                x=train_sizes,
                                y=train_scores_mean,
                                mode="lines+markers",
                                name="Training Error",
                                line=dict(color="blue"),
                            )
                        )
                        fig.add_trace(
                            go.Scatter(
                                x=train_sizes,
                                y=test_scores_mean,
                                mode="lines+markers",
                                name="Cross-validation Error",
                                line=dict(color="red"),
                            )
                        )

                        fig.update_layout(
                            title="Кривая обучения для Ridge регрессии",
                            xaxis_title="Объем обучающей выборки",
                            yaxis_title="Ошибка (MSE)",
                            legend=dict(
                                x=0,
                                y=1,
                                bgcolor="rgba(255, 255, 255, 0)",
                                bordercolor="rgba(0, 0, 0, 0)",
                            ),
                            template="plotly_white",
                        )
                        st.plotly_chart(fig)
                except requests.exceptions.HTTPError as e:
                    st.error(f"Ошибка сервера: {e.response.status_code} - {e.response.text}")
                    return
                except requests.exceptions.RequestException as e:
                    st.error(f"Ошибка при получении информации о модели: {e}")
                    return
                except Exception as e:
                    st.error(f"Ошибка: {e}")
                    return


if __name__ == "__main__":
    main()
