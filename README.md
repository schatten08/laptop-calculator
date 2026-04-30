# Laptop Purchase Calculator

A Streamlit-based web application designed to automate and calculate quarterly laptop procurement plans for multiple branch offices.

## Features
* **Multiple Input Modes**: 
  * Interactive Table (Copy-paste directly from Excel).
  * CSV Template Upload (with strict column validation).
  * Manual Form Input.
* **Advanced Allocation Math**: Uses the **Hare-Niemeyer method (Largest Remainder Method)** to distribute different laptop models proportionally based on historical purchases. This prevents off-by-one rounding errors.
* **Dynamic Buffer Reserve**: Add a percentage-based safety stock buffer for sudden breakages or unforeseen hiring.
* **State Management**: Seamlessly switches between input modes without losing entered data using Streamlit Session State.
* **Export Options**: Download the final computed purchase plan as:
  * Excel (`.xlsx`)
  * PDF Document (`.pdf`)
  * CSV Data (`.csv`)
* **Custom UI**: Clean corporate interface with Streamlit default branding hidden.

## Installation
1. Clone the repository.
2. Install the required Python packages (Python 3.9+ recommended):
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application locally:
   ```bash
   streamlit run app.py
   ```

## Usage / Business Logic
1. **New Hires**: Number of planned new employees.
2. **Replacements**: Number of outdated laptops needing replacement.
3. **Past [Model]**: Historical purchases from the previous quarter. Used to calculate the percentage distribution ratio among different models.
4. **Stock [Model]**: Current available stock. Subtracted from the final gross need to determine the actual purchase quantity.

## Technology Stack
* [Streamlit](https://streamlit.io/) - Frontend application framework
* [Pandas](https://pandas.pydata.org/) - Data manipulation and analysis
* [OpenPyXL](https://openpyxl.readthedocs.io/) - Excel file generation
* [ReportLab](https://www.reportlab.com/) - PDF document generation