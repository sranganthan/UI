# Account Retrieval UI Project

This project provides a modern UI for retrieving account IDs from multiple Kenan DB environments using various filters. It consists of a frontend (React) and a backend (Node.js/Express) for extensibility and easy environment configuration.

## Features
- Filter by Account Type, Payment Type, In Collection, Active Date, Open Invoice, and Component ID
- Connects to multiple Kenan DB environments
- Runs user-provided SQL queries based on filters
- Displays account IDs in the UI

## Structure
- `frontend/` - React UI
- `backend/` - Node.js/Express API

## Setup and Usage Instructions

### 1. Prerequisites
- Python 3.14 (already installed)
- No admin rights required

### 2. Create and Activate Virtual Environment (if not already active)
Open PowerShell in your project folder and run:

```
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install Required Python Packages

```
pip install streamlit
```

### 4. Run the Streamlit App

```
& "C:/Users/ranganathans/OneDrive - Sky/SkyIT-Billing/Docs/automation/New folder/.venv/Scripts/python.exe" -m streamlit run frontend/app.py
```

Or, if your terminal is already in the project folder and the venv is activated:

```
streamlit run frontend/app.py
```

### 5. Using the Tool
- The app will open in your browser.
- Select or enter filter values (Account Type, Payment Type, In Collection, Active Date, Open Invoice, Component ID).
- Click the **Search** button.
- Results (Account IDs) will be displayed below the button.

### 6. Customizing SQL Query
- The current app uses a placeholder for the SQL query.
- To connect to your Kenan DB and run your SQL, update the logic inside the `if st.button("Search"):` block in `frontend/app.py`.
- You may need to install additional Python packages for database connectivity (e.g., `pyodbc`, `cx_Oracle`, etc.).

### 7. Stopping the App
- Press `Ctrl+C` in the terminal to stop the Streamlit server.

---

*Replace this README with more details as the project evolves.*
