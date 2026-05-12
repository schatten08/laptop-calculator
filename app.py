# --- ИМПОРТ БИБЛИОТЕК ---
import streamlit as st
import pandas as pd
import math
import requests

# Настройка страницы (должна быть первой командой Streamlit)
# layout="wide" расширяет контент на весь экран
st.set_page_config(page_title="Laptop Purchase Calculator", layout="wide")

# --- Скрываем стандартный брендинг Streamlit (гамбургер-меню и подвал) ---
# Это придает приложению вид корпоративного white-label продукта
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            [data-testid="stToolbar"] {visibility: hidden !important;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title("Laptop Purchase Calculator")

# --- БАЗОВЫЕ КОНСТАНТЫ И ДЕФОЛТНЫЕ ДАННЫЕ ---
# Сортируем локации по алфавиту для всех таблиц и форм
LOCATIONS = sorted(["Bishkek", "Astana", "Karaganda", "Almaty", "Tashkent"])
MODELS = ["Apple MacBook Pro 14", "HP EliteBook 8 G1i 16", "HP EliteBook 8 G1i 14"]

# Стартовые значения для найма сотрудников и замены сломанных устройств
default_hiring = {"Bishkek": 31, "Astana": 100, "Karaganda": 10, "Almaty": 35, "Tashkent": 83}
default_replacements = {"Bishkek": 20, "Astana": 30, "Karaganda": 7, "Almaty": 27, "Tashkent": 30}

# Доли для вычисления будущих закупок (история прошлого квартала)
past_data = {
    "Bishkek": [19, 15, 0], "Astana": [0, 40, 0], "Karaganda": [0, 24, 0], "Almaty": [0, 40, 0], "Tashkent": [0, 40, 0]
}

# Текущие запасы (бутиковый инвентарь или остатки на складе)
stock_data = {
    "Bishkek": [38, 21, 10], "Astana": [36, 20, 13], "Karaganda": [31, 17, 6], "Almaty": [108, 35, 11], "Tashkent": [89, 102, 26]
}

# --- ПОДГОТОВКА СТРУКТУРЫ ДАННЫХ ---
# Формируем матрицу (DataFrame) со всеми данными с аккуратными заголовками (разделитель "|")
# Этот шаблон используется и для таблицы, и для CSV файла
default_df_data = []
for loc in LOCATIONS:
    default_df_data.append({
        "Location": loc, "New Hires": default_hiring[loc], "Replacements": default_replacements[loc],
        f"Past | {MODELS[0]}": past_data[loc][0], f"Past | {MODELS[1]}": past_data[loc][1], f"Past | {MODELS[2]}": past_data[loc][2],
        f"Stock | {MODELS[0]}": stock_data[loc][0], f"Stock | {MODELS[1]}": stock_data[loc][1], f"Stock | {MODELS[2]}": stock_data[loc][2],
    })
default_df = pd.DataFrame(default_df_data)

APP_VERSION = "1.4" # 🚀 Контроль версий: меняем цифру чтобы сбросить кэш и применить алфавитную сортировку

# --- УПРАВЛЕНИЕ СОСТОЯНИЕМ (Session State) ---
# Это позволяет не терять данные пользователя (Memory), когда он переключается между
# разными кнопками/таблицами или открывает раздвижные блоки и меняет ползунки на странице.
if "app_version" not in st.session_state or st.session_state.app_version != APP_VERSION:
    # 🌟 Если версия кэша устарела: чистим его начисто, чтобы избежать ошибки KeyError
    st.session_state.clear()
    st.session_state.app_version = APP_VERSION
    st.session_state.app_df = default_df.copy()
    st.toast("🔄 The app has been successfully updated to the latest version!", icon="🎉")
elif "app_df" not in st.session_state:
    st.session_state.app_df = default_df.copy() # Если кэш пустой - загружаем дефолтный шаблон

# --- ПАНЕЛЬ НАСТРОЕК (Sidebar) ---
input_mode = st.sidebar.radio("Choose Input Method:", ["Interactive Table (Paste from Excel)", "Upload File (Excel / CSV)", "Manual Forms"])

st.sidebar.header("📦 Buffer Reserve")
reserve_percent = st.sidebar.slider("Additional Reserve (%) for Quarter Needs", min_value=0, max_value=30, value=10, step=1)
st.sidebar.markdown("Provides a buffer in case of sudden breakages or unforeseen hiring.")

st.sidebar.divider()

# --- ФОРМА ОБРАТНОЙ СВЯЗИ (Feedback Form) ---
st.sidebar.header("💬 Feedback")
with st.sidebar.form(key="feedback_form"):
    feedback_text = st.text_area("Tell us how to improve the app:", placeholder="e.g. Can we add Dell laptops?")
    rating = st.slider("Rate the app:", 1, 5, 5)
    submit_feed = st.form_submit_button("Send Feedback")

    if submit_feed:
        if feedback_text.strip():
            # Получаем секретные ключи из менеджера секретов Streamlit
            bot_token = st.secrets.get("TELEGRAM_BOT_TOKEN", "")
            chat_id = st.secrets.get("TELEGRAM_CHAT_ID", "")

            if bot_token and chat_id:
                # Формируем сообщение и отправляем запрос к API Telegram
                msg = f"💡 **Новый фидбек из приложения!**\n\n⭐ Оценка: {rating}/5\n💬 Текст: {feedback_text.strip()}"
                url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                payload = {"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"}

                try:
                    requests.post(url, json=payload, timeout=5)
                    st.success("✅ Thank you for your feedback! We'll review it soon.")
                except Exception as e:
                    st.error("Failed to send feedback. Please try again later.")
            else:
                st.warning("⚠️ Telegram secrets are not configured. Feedback wasn't sent.")
        else:
            st.error("Please enter some text before submitting.")

st.header("1. Input Data")

with st.expander("ℹ️ Column Definitions (How calculations work)"):
    st.markdown("""
    * **New Hires**: Planned number of new employees for the quarter.
    * **Replacements**: Number of old or broken laptops that need to be replaced.
    * **Past [Model]**: Number of laptops purchased in the *previous* quarter. This determines the **proportion (ratio)** of each model for the new purchases.
    * **Stock [Model]**: Current available stock in the office. These items will be subtracted from the final purchase amount.
    """)

# --- СБОР И АНАЛИЗ ДАННЫХ СО СТРАНИЦЫ ---
hiring_data = {}         # Очередь на найм по городам
replacement_data = {}    # Реплейсмент по городам
past_inputs = {loc: [] for loc in LOCATIONS}   # Прошлые показатели (матричные доли)
stock_inputs = {loc: [] for loc in LOCATIONS}  # Остатки на складе (буфер для вычета)

# --- ИНТЕРФЕЙС РОУТИНГА ---
# Логика изменяется в зависимости от выбора флажка в меню (Radio button)
if input_mode == "Interactive Table (Paste from Excel)":
    st.markdown("You can **copy and paste** data directly from Excel into this table. Edit any cell as needed.")

    # 📝 Выводим редактор таблиц (st.data_editor) и привязываем его к сохраненному состоянию (app_df)
    edited_df = st.data_editor(st.session_state.app_df, use_container_width=True, hide_index=True)
    st.session_state.app_df = edited_df

    # Пробегаем по строкам отредактированной таблицы и складываем данные в словари-переменные
    for _, row in edited_df.iterrows():
        loc = row["Location"]
        if loc in LOCATIONS:
            hiring_data[loc] = int(row["New Hires"])
            replacement_data[loc] = int(row["Replacements"])
            past_inputs[loc] = [int(row[f"Past | {MODELS[0]}"]), int(row[f"Past | {MODELS[1]}"]), int(row[f"Past | {MODELS[2]}"])]
            stock_inputs[loc] = [int(row[f"Stock | {MODELS[0]}"]), int(row[f"Stock | {MODELS[1]}"]), int(row[f"Stock | {MODELS[2]}"])]

elif input_mode == "Upload File (Excel / CSV)":
    st.markdown("Download the Excel template, fill it, and upload it back here. (Both `.xlsx` and `.csv` are supported).")

    # Конвертируем дефолтную таблицу (pd.DataFrame) в Excel для скачивания (это удобнее для юзеров)
    import io
    template_buffer = io.BytesIO()
    with pd.ExcelWriter(template_buffer, engine='openpyxl') as writer:
        default_df.to_excel(writer, index=False, sheet_name='Template')

    st.download_button("📥 Download Excel Template", data=template_buffer.getvalue(), file_name="template.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # Виджет загрузки (Drag and drop). Разрешаем и Excel и CSV форматы
    uploaded_file = st.file_uploader("Upload filled file here", type=["xlsx", "csv"])

    # --- ВАЛИДАЦИЯ ФАЙЛА И ОБРАБОТКА ОШИБОК (Try-Except) ---
    if uploaded_file is not None:
        try:
            # Читаем файл в зависимости от его расширения
            if uploaded_file.name.endswith('.csv'):
                uploaded_df = pd.read_csv(uploaded_file)
            else:
                uploaded_df = pd.read_excel(uploaded_file, engine='openpyxl')

            # Проверки: сравниваем колонки загруженного файла с 'expected_cols'
            expected_cols = list(default_df.columns)
            if not all(col in uploaded_df.columns for col in expected_cols):
                st.error("Error: Uploaded file is missing required columns. Please use the downloaded template.")
            else:
                # Если файл верен, парсим его данные в наши словари
                st.session_state.app_df = uploaded_df
                st.dataframe(uploaded_df, use_container_width=True)
                for _, row in uploaded_df.iterrows():
                    loc = row["Location"]
                    if loc in LOCATIONS:
                        hiring_data[loc] = int(row["New Hires"])
                        replacement_data[loc] = int(row["Replacements"])
                        past_inputs[loc] = [int(row[f"Past | {MODELS[0]}"]), int(row[f"Past | {MODELS[1]}"]), int(row[f"Past | {MODELS[2]}"])]
                        stock_inputs[loc] = [int(row[f"Stock | {MODELS[0]}"]), int(row[f"Stock | {MODELS[1]}"]), int(row[f"Stock | {MODELS[2]}"])]
        except Exception as e:
            st.error(f"Error reading file: {e}. Please ensure it matches the template.")
    else:
        st.warning("Awaiting file upload... Using previously saved or default values in the meantime.")
        # Пока пользователь не загрузил файл (или загрузил битый),
        # приложение берет резервные данные из памяти Streamlit (Session state).
        for _, row in st.session_state.app_df.iterrows():
            loc = row["Location"]
            hiring_data[loc], replacement_data[loc] = int(row["New Hires"]), int(row["Replacements"])
            past_inputs[loc] = [int(row[f"Past | {MODELS[0]}"]), int(row[f"Past | {MODELS[1]}"]), int(row[f"Past | {MODELS[2]}"])]
            stock_inputs[loc] = [int(row[f"Stock | {MODELS[0]}"]), int(row[f"Stock | {MODELS[1]}"]), int(row[f"Stock | {MODELS[2]}"])]

else:
    # Если выбран режим "Manual Forms", выводим поля ввода (инпуты) столбцами (по 5 столбцов - один на офис)
    # Формируем 5 столбцов `st.columns` для найма/реплейсов
    cols = st.columns(len(LOCATIONS))
    for i, loc in enumerate(LOCATIONS):
        # Подгружаем кэшированные стейты для данного города `loc` из `app_df`
        saved_row = st.session_state.app_df.loc[st.session_state.app_df["Location"] == loc]
        with cols[i]:
            st.subheader(loc)
            hiring_data[loc] = st.number_input(f"New Hires ({loc})", min_value=0, value=int(saved_row["New Hires"].values[0]))
            replacement_data[loc] = st.number_input(f"Replacements ({loc})", min_value=0, value=int(saved_row["Replacements"].values[0]))

    st.markdown("### Previous Quarter Purchases")
    cols_past = st.columns(len(LOCATIONS))
    for i, loc in enumerate(LOCATIONS):
        saved_row = st.session_state.app_df.loc[st.session_state.app_df["Location"] == loc]
        with cols_past[i]:
            for j, model in enumerate(MODELS):
                val = st.number_input(f"{model} (Past {loc})", min_value=0, value=int(saved_row[f"Past | {model}"].values[0]))
                past_inputs[loc].append(val)

    st.markdown("### Stock Balance")
    cols_stock = st.columns(len(LOCATIONS))
    for i, loc in enumerate(LOCATIONS):
        saved_row = st.session_state.app_df.loc[st.session_state.app_df["Location"] == loc]
        with cols_stock[i]:
            for j, model in enumerate(MODELS):
                val = st.number_input(f"{model} (Stock {loc})", min_value=0, value=int(saved_row[f"Stock | {model}"].values[0]))
                stock_inputs[loc].append(val)

    # СОХРАНЕНИЕ ДАННЫХ ОБРАТНО В SESSION STATE
    # Каждый раз когда меняются ручные инпуты, мы перезаписываем dataframe стейт.
    # Это позволяет пользователю сменить вкладку на "Intrereactive table", и увидеть там свои ручные цифры
    for loc in LOCATIONS:
        st.session_state.app_df.loc[st.session_state.app_df["Location"] == loc, "New Hires"] = hiring_data[loc]
        st.session_state.app_df.loc[st.session_state.app_df["Location"] == loc, "Replacements"] = replacement_data[loc]
        for j, model in enumerate(MODELS):
            st.session_state.app_df.loc[st.session_state.app_df["Location"] == loc, f"Past | {model}"] = past_inputs[loc][j]
            st.session_state.app_df.loc[st.session_state.app_df["Location"] == loc, f"Stock | {model}"] = stock_inputs[loc][j]

st.header("2. Calculation & Results")

# --- ВЫПОЛНЕНИЕ РАСЧЕТА ЗАДАЧИ ---
# Запуск кнопки инициирует алгоритмическое вычисление закупок
if st.button("Calculate Purchases", type="primary"):
    results = [] # Сюда складываем рассчитанную информацию для итоговой таблицы
    total_buy = 0

    for loc in LOCATIONS:
        # Для начала подсчитаем сколько человек в городе вообще нуждаются в ноутбуке
        total_need = hiring_data[loc] + replacement_data[loc]

        # Получаем сумму всех купленных ноутов филиала за прошлый квартал.
        # Например 10 Macbook + 20 HP = 30(sum)
        total_past = sum(past_inputs[loc])
        if total_past == 0:
            # Если филиал новый (никто ничего не закупал), устанавливаем дефолтные ровные доли (напр: 33.3% / 33.3% / 33.3%)
            dist = [1.0 / len(MODELS)] * len(MODELS)
        else:
            # Иначе высчитываем процентную долю каждой модели (например 10 / 30 = 33% для макбуков, 20 / 30 = 66% для HP)
            dist = [past_inputs[loc][j] / total_past for j in range(len(MODELS))]

        # --- АЛГОРИТМ РАСПРЕДЕЛЕНИЯ: Метод максимального остатка (Hare-Niemeyer Algorithm) ---
        # 1. Мы умножаем потребность (Total_need=5 чел) на (долю=33% Macbook). Это даст 1.65 макбуков.
        exact_needs = [total_need * d for d in dist]
        # 2. Мы берем только целую часть потребности. Было 1.65 - стало `math.floor` 1.
        base_needs = [math.floor(n) for n in exact_needs]
        # 3. Высчитываем дробный остаток для каждой модели: 1.65 - 1 = 0.65. Эту цифру запоминаем.
        remainders = [(exact_needs[j] - base_needs[j], j) for j in range(len(MODELS))]

        # 4. Вычисляем сколько "потерянных" ноутбуков нам нужно вернуть. (total_need - сумма округленных ноутбуков)
        remainder_to_distribute = total_need - sum(base_needs)

        # 5. Сортируем остатки убыванию. Тот, у кого дробная часть выше всего (например 0.9 против 0.1),
        # тот и получает право забрать +1 потерянный целый ноут. Это гарантирует, что total == total_need.
        remainders.sort(key=lambda x: x[0], reverse=True)
        for i in range(remainder_to_distribute):
            base_needs[remainders[i][1]] += 1

        for j, model in enumerate(MODELS):
            # Базовая потребность по модели (с правильным округлением квотирования Хэра-Нимейера)
            base_need_model = base_needs[j]

            # --- ЛОГИКА РЕЗЕРВАЦИИ / БУФЕРА ---
            # Допустим, нам нужно заказать 5 Macbooks. Буфер (slider) равен 10%.
            # 5 * 10% = 0.5 резервного ноутбука (всего 5.5). Мы округляем 5.5 вверх(math.ceil), получая итоговую цель = 6.
            # Это дает гарантию что непредвиденная поломка будет покрыта.
            need_with_reserve = math.ceil(base_need_model * (1 + reserve_percent / 100))

            stock = stock_inputs[loc][j]
            # Закупка - это формула (total_need_with_buffer - текущий_остаток).
            # Если остатков больше чем надо резервировать, `max(0, -x)` выведет чистый 0 (избавляя нас от отрицательных цифр)
            buy = max(0, need_with_reserve - stock)

            results.append({
                "Location": loc,
                "Model": model,
                "Total Need (incl. Reserve)": need_with_reserve,
                "Stock Balance": stock,
                "Quantity to Purchase": buy
            })
            total_buy += buy

    df = pd.DataFrame(results)
    # Сортируем таблицу по алфавиту для консистентности (как в UI, так и в экспортированных Excel/PDF)
    df = df.sort_values(by=["Location", "Model"])

    # --- БЛОК ВИЗУАЛЬНОГО ВЫВОДА ---
    st.header("Final Purchase Plan")

    # Визуальное разделение таблиц по локациям для лучшей читаемости (сортировка по алфавиту)
    for loc, group_df in df.groupby("Location"):
        st.write(f"##### 📍 {loc}")
        # Убираем колонку Location (она теперь в заголовке) и ставим Model как индекс
        loc_df = group_df.drop(columns=["Location"]).set_index("Model")
        st.dataframe(loc_df, use_container_width=True)

    # Красивая метрика (KPI) с итоговой штучной закупкой
    st.metric(label="Total Laptops to Purchase 💻", value=f"{total_buy} pcs.")
    st.info(f"💡 The *Total Need* and final purchase quantity already include the **{reserve_percent}%** buffer reserve.")
    st.divider()

    # --- БЛОК ЭКСПОРТА ФАЙЛОВ ---
    import io

    # 1. EXCEL (.xlsx)
    # Пишем в виртуальный буфер памяти (BytesIO) чтобы не засорять диск сервера мусорными файлами
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Purchase Plan')

    # 2. PDF
    # Создаем холст ReportLab в формате Letter и альбомной ориентации (landscape),
    # чтобы колонки таблицы не обрезались по ширине.
    from reportlab.lib.pagesizes import letter, landscape
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet

    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=landscape(letter))
    elements = []

    # Стилизуем заголовок "Quarterly Purchase Plan (Total: 400 pcs.)"
    styles = getSampleStyleSheet()
    elements.append(Paragraph(f"Quarterly Purchase Plan (Total: {total_buy} pcs.)", styles['Title']))
    elements.append(Spacer(1, 12))

    # Переводим датафрейм Pandas в список списков (list of lists) для генерации таблицы ReportLab
    pdf_data = [df.columns.values.tolist()] + df.values.tolist()
    t = Table(pdf_data)

    # Стилизация таблицы PDF: Серая заголовочная шапка, белые буквы и черная сетка границ
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(t)
    doc.build(elements) # Генерируем файл

    # Располагаем две кнопки скачивания в ряд (Excel и PDF)
    st.markdown("### Export Results")
    col1, col2 = st.columns(2)
    with col1:
        st.download_button("📥 Download Excel (.xlsx)", data=buffer.getvalue(), file_name='laptop_plan.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', use_container_width=True)
    with col2:
        st.download_button("📥 Download PDF", data=pdf_buffer.getvalue(), file_name='laptop_plan.pdf', mime='application/pdf', use_container_width=True)
