import streamlit as st
import pandas as pd
import math

st.set_page_config(page_title="Laptop Purchase Calculator", layout="wide")

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
        f"Past {MODELS[0]}": past_data[loc][0], f"Past {MODELS[1]}": past_data[loc][1], f"Past {MODELS[2]}": past_data[loc][2],
        f"Stock {MODELS[0]}": stock_data[loc][0], f"Stock {MODELS[1]}": stock_data[loc][1], f"Stock {MODELS[2]}": stock_data[loc][2],
    })
default_df = pd.DataFrame(default_df_data)

st.header("1. Input Data")

# Выбор формата ввода
input_mode = st.radio("Choose Input Method:", ["Interactive Table (Paste from Excel)", "Upload CSV File", "Manual Forms"])

hiring_data = {}
replacement_data = {}
past_inputs = {loc: [] for loc in LOCATIONS}
stock_inputs = {loc: [] for loc in LOCATIONS}

if input_mode == "Interactive Table (Paste from Excel)":
    st.markdown("You can **copy and paste** data directly from Excel into this table. Edit any cell as needed.")
    edited_df = st.data_editor(default_df, use_container_width=True, hide_index=True)
    
    # Парсим результаты из таблицы
    for _, row in edited_df.iterrows():
        loc = row["Location"]
        if loc in LOCATIONS:
            hiring_data[loc] = int(row["New Hires"])
            replacement_data[loc] = int(row["Replacements"])
            past_inputs[loc] = [int(row[f"Past {MODELS[0]}"]), int(row[f"Past {MODELS[1]}"]), int(row[f"Past {MODELS[2]}"])]
            stock_inputs[loc] = [int(row[f"Stock {MODELS[0]}"]), int(row[f"Stock {MODELS[1]}"]), int(row[f"Stock {MODELS[2]}"])]

elif input_mode == "Upload CSV File":
    st.markdown("Download the template, fill it in Excel, and upload it back here.")
    template_csv = default_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV Template", data=template_csv, file_name="template.csv", mime="text/csv")
    
    uploaded_file = st.file_uploader("Upload filled CSV here", type=["csv"])
    if uploaded_file is not None:
        try:
            uploaded_df = pd.read_csv(uploaded_file)
            st.dataframe(uploaded_df, use_container_width=True)
            for _, row in uploaded_df.iterrows():
                loc = row["Location"]
                if loc in LOCATIONS:
                    hiring_data[loc] = int(row["New Hires"])
                    replacement_data[loc] = int(row["Replacements"])
                    past_inputs[loc] = [int(row[f"Past {MODELS[0]}"]), int(row[f"Past {MODELS[1]}"]), int(row[f"Past {MODELS[2]}"])]
                    stock_inputs[loc] = [int(row[f"Stock {MODELS[0]}"]), int(row[f"Stock {MODELS[1]}"]), int(row[f"Stock {MODELS[2]}"])]
        except Exception as e:
            st.error(f"Error reading file: {e}. Please ensure it matches the template.")
    else:
        st.warning("Awaiting file upload... Using default values in the meantime.")
        # Запасной вариант пока нет файла
        for _, row in default_df.iterrows():
            loc = row["Location"]
            hiring_data[loc], replacement_data[loc] = int(row["New Hires"]), int(row["Replacements"])
            past_inputs[loc] = [int(row[f"Past {MODELS[0]}"]), int(row[f"Past {MODELS[1]}"]), int(row[f"Past {MODELS[2]}"])]
            stock_inputs[loc] = [int(row[f"Stock {MODELS[0]}"]), int(row[f"Stock {MODELS[1]}"]), int(row[f"Stock {MODELS[2]}"])]

else:
    # Исходный ручной ввод
    cols = st.columns(len(LOCATIONS))
    for i, loc in enumerate(LOCATIONS):
        with cols[i]:
            st.subheader(loc)
            hiring_data[loc] = st.number_input(f"New Hires ({loc})", min_value=0, value=default_hiring[i])
            replacement_data[loc] = st.number_input(f"Replacements ({loc})", min_value=0, value=default_replacements[i])
    
    st.markdown("### Previous Quarter Purchases")
    cols_past = st.columns(len(LOCATIONS))
    for i, loc in enumerate(LOCATIONS):
        with cols_past[i]:
            for j, model in enumerate(MODELS):
                val = st.number_input(f"{model} (Past {loc})", min_value=0, value=past_data[loc][j])
                past_inputs[loc].append(val)
                
    st.markdown("### Stock Balance")
    cols_stock = st.columns(len(LOCATIONS))
    for i, loc in enumerate(LOCATIONS):
        with cols_stock[i]:
            for j, model in enumerate(MODELS):
                val = st.number_input(f"{model} (Stock {loc})", min_value=0, value=stock_data[loc][j])
                stock_inputs[loc].append(val)

st.header("2. Buffer Stock")
reserve_percent = st.slider("Additional Reserve (%) for Quarter Needs", min_value=0, max_value=30, value=10, step=1)
st.markdown("Provides a buffer in case of sudden breakages or unforeseen hiring.")

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
        
        for j, model in enumerate(MODELS):
            # Базовая потребность по модели
            base_need_model = round(total_need * dist[j])
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
    
    st.header("Final Purchase Table")
    
    # Визуальное группирование по городам для отображения на сайте
    # Это объединит ячейки с названиями городов в визуальные блоки
    df_display = df.set_index(["Location", "Model"])
    st.table(df_display)
    
    st.success(f"Total number of laptops to purchase: **{total_buy} pcs.**")
    
    # Кнопка для скачивания CSV (оставляем обычный плоский df для удобства Excel)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Table as CSV (for Excel)",
        data=csv,
        file_name='laptop_purchase_plan.csv',
        mime='text/csv',
    )
