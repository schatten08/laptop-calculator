# Changelog

All notable changes to the Laptop Purchase Calculator will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-04-29
### Added
* **Excel Export**: Added `openpyxl` engine to generate full `.xlsx` purchase plans directly in the browser memory.
* **PDF Export**: Implemented `reportlab` to generate cleanly formatted, corporate-styled PDF reports (in horizontal landscape orientation).
* Visual column separators (`|`) in data tables to improve readability (e.g., `Past | Apple MacBook Pro 14`).
* Custom CSS injection to hide default Streamlit branding (header, hamburger menu, footer).
* UI component updates: moved configuration to the left sidebar, upgraded to full `st.dataframe` for responsive viewing, and added `st.metric` for the total purchase number.
* Added an `st.info` tooltip explaining the reserve inclusion below the metric.
* Added cache versioning (`APP_VERSION`) to automatically clear user caches and prevent `KeyError` crashes when column names change.

### Changed
* Simplified the final results table by removing the intermediate "Base Need" column. Now directly shows "Total Need (incl. Reserve)".

## [1.1.0] - 2026-04-29
### Added
* **Session State Management**: Data persistence across different input tabs (Interactive Table, CSV, Manual). Data is no longer lost when seamlessly switching views (`st.session_state.app_df`).
* **CSV Validation**: Uploaded CSV files are now strictly validated against expected columns to prevent application crashes and Tracebacks.
* Tooltips and an expander "ℹ️ Column Definitions" providing transparent instructions on how calculations work to the end user.

### Fixed
* **The Rounding Paradox**: Replaced standard `round()` allocation with the **Hare-Niemeyer (Largest Remainder)** algorithm to ensure the calculated laptop count perfectly matches the total headcount requirement without the ±1 discrepancies (giving exactly what is required).

## [1.0.0] - 2026-04-28
### Added
* Initial functional release of the Streamlit Calculator application.
* Basic arithmetic calculation logic for Bishkek, Astana, Karaganda, Almaty, and Tashkent branch offices.
* Basic input support for Apple MacBook Pro 14, HP EliteBook 8 G1i 16, and HP EliteBook 8 G1i 14 models.
* Dynamic basic CSV template generation and file upload.