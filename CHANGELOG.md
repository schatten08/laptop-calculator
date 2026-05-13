# Changelog

All notable changes to the Laptop Purchase Calculator will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.5.1] - 2026-05-13
### Changed
* **Project Structure**: Refactored the project structure by moving `app.py` into a dedicated `src/` directory and cleaning up `__pycache__` artifacts to maintain a clean repository root.

## [1.5.0] - 2026-05-12
### Added
* **New Equipment Model**: Added `Apple MacBook Air` to the tracking system. The core application logic was refactored to dynamically generate columns based on the the `MODELS` array length, rather than hardcoding exactly 3 models.
* **Cache Busting**: Bumped `APP_VERSION` to `1.5` to clear outdated session states and seamlessly integrate the new model columns without triggering `KeyError`.

## [1.4.0] - 2026-04-30
### Added
* **Developer Experience (DX)**: Implemented professional VS Code workspace settings in `.vscode/settings.json`, including structure auto-formatting on save, trailing space cleanup, bracket pair colorization, and basic Pylance type checking.
* **Feedback Form**: Added an interactive form (`st.form`) inside the sidebar allowing users to submit text comments, rate the application, and trigger celebration animations upon successful submission.

### Changed
* **Interactive Table & Inputs**: Refactored the core application constants to natively sort locations alphabetically across all manual input forms and the interactive tables. Data arrays were converted to strict dictionary mappings to prevent indexing errors.
* **Cache Busting**: Bumped `APP_VERSION` to `1.4` to seamlessly apply the new alphabetical sorting layout and clear outdated session configurations.

## [1.3.0] - 2026-04-30
### Added
* **Custom Theming**: Added `.streamlit/config.toml` to force a professional Dark Mode UI baseline across all browsers, regardless of the user's OS settings. Replaced Streamlit's default red error-like highlight color with a calming corporate blue (`#1f77b4`).
* **Native Excel Upload & Templates**: Transitioned from `.csv` to `.xlsx` for the required template download to prevent delimiter and UTF-8 encoding issues for end-users. The file uploader now natively parses both Excel and CSV formats.
* **Bidirectional Data Sync**: Data uploaded via Excel now automatically and accurately pre-fills the input values in the "Manual Forms" and "Interactive Table" views thanks to the central Session State architecture.
* **AI Instruction Rules**: Updated `.github/copilot-instructions.md` to strictly enforce Conventional Commits, automated git push prompts, and structured Changelog maintenance moving forward.

### Changed
* **UI Improvements**: Separated the final purchase plan table into distinct visual blocks by location.
* **Data Sorting**: Locations and models are now sorted alphabetically natively within the UI and the generated Excel/PDF export documents for better readability.

### Removed
* **CSV Export**: Removed the CSV export button to declutter the user interface, as Excel and PDF formats fully cover business reporting needs.

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
