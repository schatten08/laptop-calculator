# Copilot Instructions for Laptop Purchase Calculator

## 1. Project Context
This is a Streamlit-based web application (`app.py`) for automating quarterly laptop procurement plans across 5 branch offices (Bishkek, Astana, Karaganda, Almaty, Tashkent).
The application relies heavily on data manipulation using `pandas` and exports reports using `openpyxl` and `reportlab`.

## 2. Architecture & State Management Rules
* **Streamlit Top-to-Bottom Execution:** Always account for Streamlit's rerun behavior. Never store user inputs in simple variables if they need to persist across UI changes.
* **Session State:** Always use `st.session_state.app_df` as the single source of truth for the central dataframe. Ensure bidirectional sync between UI forms and uploaded files.

## 3. Mathematical & Business Logic Constraints
* **The Rounding Paradox:** NEVER use the standard `round()` function when dividing overall laptop needs into model proportions. 
* **Hare-Niemeyer Method:** ALWAYS use the Largest Remainder Method (Hare-Niemeyer) mathematically to enforce that the sum of allocated laptops exactly matches the total required headcount without off-by-one errors.
* **Buffer Reservations:** Always apply the percentage buffer using `math.ceil()` to ensure at least 1 physical laptop is reserved if the fraction > 0.
* **Stock Subtraction:** Final purchase formula must strictly be `max(0, need_with_reserve - current_stock)`.

## 4. Code Style & Output Preferences
* Write all variable names, UI labels, and data outputs in **English**.
* Write all code comments and architectural explanations to the user in **Russian**.
* When suggesting edits, provide concise replacements rather than rewriting the entire file.
* Always handle file uploads (CSV/Excel) with a `try-except` block and validate that the columns match exactly.