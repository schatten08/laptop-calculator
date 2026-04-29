import streamlit as st
import pandas as pd
import math

st.set_page_config(page_title="Laptop Purchase Calculator", layout="wide")

# --- Скрываем стандартный брендинг Streamlit (гамбургер-меню и подвал) ---
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

# Константы локаций и моделей
LOCATIONS = ["Bishkek", "Astana", "Karaganda", "Almaty", "Tashkent"]
MODELS = ["Apple MacBook Pro 14", "HP EliteBook 8 G1i 16", "HP EliteBook 8 G1i 14"]

# Данные по умолчанию
default_hiring = [31, 100, 10, 35, 83]
default_replacements = [20, 30, 7, 27, 30]

past_data = {
    "Bishkek": [19, 15, 0], "Astana": [0, 40, 0], "Karaganda": [0, 24, 0], "Almaty": [0, 40, 0], "Tashkent": [0, 40, 0]
}

stock_data = {
    "Bishkek": [38, 21, 10], "Astana": [36, 20, 13], "Karaganda": [31, 17, 6], "Almaty": [108, 35, 11], "Tashkent": [89, 102, 26]
}

# Подготовка дефолтного датафрейма для табличного вода
default_df_data = []
for i, loc in enumerate(LOCATIONS):
    default_df_data.append({
        "Location": loc, "New Hires": default_hiring[i], "Replacements": default_replacements[i],
        f"Past | {MODELS[0]}": past_data[loc][0], f"Past | {MODELS[1]}": past_data[loc][1], f"Past | {MODELS[2]}": past_data[loc][2],
        f"Stock | {MODELS[0]}": stock_data[loc][0], f"Stock | {MODELS[1]}": stock_data[loc][1], f"Stock | {MODELS[2]}": stock_data[loc][2],
    })
default_df = pd.DataFrame(default_df_data)

APP_VERSION = "1.1" # 🚀 Меняйте эту цифру при каждом обновлении структуры колонок

# Используем Session State для сохранения данных между вкладками с проверкой версии
if "app_version" not in st.session_state or st.session_state.app_version != APP_VERSION:
    st.session_state.clear() # Полностью уничтожаем закэшированные (старые) значения пользователя
    st.session_state.app_version = APP_VERSION
    st.session_state.app_df = default_df.copy()
    st.toast("🔄 The app has been successfully updated to the latest version!", icon="🎉")
elif "app_df" not in st.session_state:
    st.session_state.app_df = default_df.copy()

st.sidebar.header("⚙️ Configuration")
input_mode = st.sidebar.radio("Choose Input Method:", ["Interactive Table (Paste from Excel)", "Upload CSV File", "Manual Forms"])

st.sidebar.header("📦 Buffer Reserve")
reserve_percent = st.sidebar.slider("Additional Reserve (%) for Quarter Needs", min_value=0, max_value=30, value=10, step=1)
st.sidebar.markdown("Provides a buffer in case of sudden breakages or unforeseen hiring.")

st.header("1. Input Data")

with st.expander("ℹ️ Column Definitions (How calculations work)"):
    st.markdown("""
    * **New Hires**: Planned number of new employees for the quarter.
    * **Replacements**: Number of old or broken laptops that need to be replaced.
    * **Past [Model]**: Number of laptops purchased in the *previous* quarter. This determines the **proportion (ratio)** of each model for the new purchases.
    * **Stock [Model]**: Current available stock in the office. These items will be subtracted from the final purchase amount.
    """)

hiring_data = {}
replacement_data = {}
past_inputs = {loc: [] for loc in LOCATIONS}
stock_inputs = {loc: [] for loc in LOCATIONS}

if input_mode == "Interactive Table (Paste from Excel)":
    st.markdown("You can **copy and paste** data directly from Excel into this table. Edit any cell as needed.")
    
    # Редактируем состояние
    edited_df = st.data_editor(st.session_state.app_df, use_container_width=True, hide_index=True)
    st.session_state.app_df = edited_df
    
    # Парсим результаты из таблицы
    for _, row in edited_df.iterrows():
        loc = row["Location"]
        if loc in LOCATIONS:
            hiring_data[loc] = int(row["New Hires"])
            replacement_data[loc] = int(row["Replacements"])
            past_inputs[loc] = [int(row[f"Past | {MODELS[0]}"]), int(row[f"Past | {MODELS[1]}"]), int(row[f"Past | {MODELS[2]}"])]
            stock_inputs[loc] = [int(row[f"Stock | {MODELS[0]}"]), int(row[f"Stock | {MODELS[1]}"]), int(row[f"Stock | {MODELS[2]}"])]

elif input_mode == "Upload CSV File":
    st.markdown("Download the template, fill it in Excel, and upload it back here.")
    template_csv = default_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV Template", data=template_csv, file_name="template.csv", mime="text/csv")
    
    uploaded_file = st.file_uploader("Upload filled CSV here", type=["csv"])
    if uploaded_file is not None:
        try:
            uploaded_df = pd.read_csv(uploaded_file)
            
            # Проверка, что файл не сломан (Валидация колонок)
            expected_cols = list(default_df.columns)
            if not all(col in uploaded_df.columns for col in expected_cols):
                st.error("Error: Uploaded file is missing required columns. Please use the downloaded template.")
            else:
                st.session_state.app_df = uploaded_df  # Сохраняем в состояние
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
        # Запасной вариант пока нет файла (берем из состояния)
        for _, row in st.session_state.app_df.iterrows():
            loc = row["Location"]
            hiring_data[loc], replacement_data[loc] = int(row["New Hires"]), int(row["Replacements"])
            past_inputs[loc] = [int(row[f"Past | {MODELS[0]}"]), int(row[f"Past | {MODELS[1]}"]), int(row[f"Past | {MODELS[2]}"])]
            stock_inputs[loc] = [int(row[f"Stock | {MODELS[0]}"]), int(row[f"Stock | {MODELS[1]}"]), int(row[f"Stock | {MODELS[2]}"])]

else:
    # Исходный ручной ввод
    cols = st.columns(len(LOCATIONS))
    for i, loc in enumerate(LOCATIONS):
        # Получаем сохраненные значения из df_state
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
                
    # Сохраняем новые цифры обратно в состояние
    for loc in LOCATIONS:
        st.session_state.app_df.loc[st.session_state.app_df["Location"] == loc, "New Hires"] = hiring_data[loc]
        st.session_state.app_df.loc[st.session_state.app_df["Location"] == loc, "Replacements"] = replacement_data[loc]
        for j, model in enumerate(MODELS):
            st.session_state.app_df.loc[st.session_state.app_df["Location"] == loc, f"Past | {model}"] = past_inputs[loc][j]
            st.session_state.app_df.loc[st.session_state.app_df["Location"] == loc, f"Stock | {model}"] = stock_inputs[loc][j]

st.header("2. Calculation & Results")

if st.button("Calculate Purchases", type="primary"):
    results = []
    total_buy = 0
    
    for loc in LOCATIONS:
        total_need = hiring_data[loc] + replacement_data[loc]
        
        # Вычисляем распределение (доли) на основе введенных прошлых закупок
        total_past = sum(past_inputs[loc])
        if total_past == 0:
            dist = [1.0 / len(MODELS)] * len(MODELS) # Равными долями по 33.3%
        else:
            dist = [past_inputs[loc][j] / total_past for j in range(len(MODELS))]
        
        # --- Метод максимального остатка (Hare-Niemeyer) ---
        exact_needs = [total_need * d for d in dist]
        base_needs = [math.floor(n) for n in exact_needs]
        remainders = [(exact_needs[j] - base_needs[j], j) for j in range(len(MODELS))]
        
        # Распределяем остатки
        remainder_to_distribute = total_need - sum(base_needs)
        remainders.sort(key=lambda x: x[0], reverse=True)
        for i in range(remainder_to_distribute):
            base_needs[remainders[i][1]] += 1

        for j, model in enumerate(MODELS):
            # Базовая потребность по модели (с правильным округлением Хэра-Нимейера)
            base_need_model = base_needs[j]
            # Потребность с учетом резерва (округляем вверх, чтобы всегда был запас)
            need_with_reserve = math.ceil(base_need_model * (1 + reserve_percent / 100))
            
            stock = stock_inputs[loc][j]
            buy = max(0, need_with_reserve - stock)
            
            results.append({
                "Location": loc,
                "Model": model,
                "Base Need": base_need_model,
                "Need with Reserve": need_with_reserve,
                "Stock Balance": stock,
                "Quantity to Purchase": buy
            })
            total_buy += buy
            
    df = pd.DataFrame(results)
    
    st.header("Final Purchase Plan")
    
    # Визуальное группирование по городам для отображения на сайте
    df_display = df.set_index(["Location", "Model"])
    st.dataframe(df_display, use_container_width=True)
    
    # Красивая метрика
    st.metric(label="Total Laptops to Purchase 💻", value=f"{total_buy} pcs.")
    st.divider()
    
    # Кнопки экспорта
    import io
    
    # Excel
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Purchase Plan')
    
    # PDF
    from reportlab.lib.pagesizes import letter, landscape
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=landscape(letter))
    elements = []
    
    styles = getSampleStyleSheet()
    elements.append(Paragraph(f"Quarterly Purchase Plan (Total: {total_buy} pcs.)", styles['Title']))
    elements.append(Spacer(1, 12))
    
    pdf_data = [df.columns.values.tolist()] + df.values.tolist()
    t = Table(pdf_data)
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
    doc.build(elements)
    
    # CSV
    csv = df.to_csv(index=False).encode('utf-8')
    
    # Располагаем три кнопки скачивания в ряд
    st.markdown("### Export Results")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button("📥 Excel (.xlsx)", data=buffer.getvalue(), file_name='laptop_plan.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', use_container_width=True)
    with col2:
        st.download_button("📥 PDF Document", data=pdf_buffer.getvalue(), file_name='laptop_plan.pdf', mime='application/pdf', use_container_width=True)
    with col3:
        st.download_button("📥 CSV Data", data=csv, file_name='laptop_plan.csv', mime='text/csv', use_container_width=True)
