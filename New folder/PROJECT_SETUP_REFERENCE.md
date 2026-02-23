# Kenan Account Retrieval - Project Setup Reference

## Project Overview
A Streamlit-based UI application for retrieving account IDs from multiple Kenan DB environments using customizable filters.

## Technology Stack
- **Frontend/Backend**: Python 3.14 with Streamlit
- **Database**: Oracle (multiple environments and customer DBs)
- **DB Connectivity**: pyodbc with Oracle ODBC Driver (OraClient12Home1)

## Project Structure
```
.
├── frontend/
│   ├── app.py              # Main Streamlit application
│   └── db_config.py        # Database configuration for all environments
├── logs/
│   └── account_search.log  # Application and connection logs
└── README.md               # Setup and usage instructions
```

## Features Implemented
1. **Multi-Environment Support**: IT, ST, UAT, System test, AM
2. **Customer DB Selection**: Server IDs 3-8 mapped to Customer DB1-6
3. **Search Filters**:
   - Account Type: TV, BB, HW, MA, BBH
   - Payment Type: Any, CDC, RID, Postal
   - In Collection: Any, Yes, No
   - Active Date: Date picker
   - Open Invoice: Any, Yes, No
   - Component ID: Optional text input
4. **Connection Testing**: Test button to verify DB connectivity before running queries
5. **Logging**: All searches and connection attempts logged to logs/account_search.log

## Database Configuration

### File: frontend/db_config.py
Structure for each environment:
```python
db_config = {
    "IT": {
        "customer": [
            {"host": "hostname", "port": 1521, "service_name": "service", "user": "username", "password": "password"},
            # ... 6 customer DBs total (indices 0-5)
        ]
    },
    # ... other environments
}
```

### Customer Server ID Mapping
- Server ID 3 → Customer DB1 (index 0)
- Server ID 4 → Customer DB2 (index 1)
- Server ID 5 → Customer DB3 (index 2)
- Server ID 6 → Customer DB4 (index 3)
- Server ID 7 → Customer DB5 (index 4)
- Server ID 8 → Customer DB6 (index 5)

## Connection Details
- **ODBC Driver**: Oracle in OraClient12Home1
- **Connection String Format**: 
  ```
  DRIVER={Oracle in OraClient12Home1};
  DBQ=host:port/service_name;
  UID=user;PWD=password
  ```

## Setup Steps Completed
1. Created Python virtual environment (.venv)
2. Installed required packages: streamlit, pyodbc
3. Created frontend directory structure
4. Implemented db_config.py for environment-specific DB connections
5. Built Streamlit UI with all required filters
6. Added Test Connection functionality
7. Implemented logging framework
8. Configured Oracle ODBC connectivity

## Running the Application
```powershell
& "C:/Users/ranganathans/OneDrive - Sky/SkyIT-Billing/Docs/automation/New folder/.venv/Scripts/python.exe" -m streamlit run frontend/app.py
```

Or from project folder with activated venv:
```powershell
streamlit run frontend/app.py
```

## Troubleshooting Steps Taken
1. **Node.js not available**: Switched from React to Python/Streamlit
2. **ODBC Driver not found**: Identified available drivers using `pyodbc.drivers()`
3. **Invalid credentials**: Added logging to trace connection details
4. **Module not found**: Installed pyodbc in correct Python environment

## Next Steps (Pending)
1. ✅ Test DB connections across all environments
2. ⏳ Integrate actual SQL query (user to provide)
3. ⏳ Display real account ID results from query
4. ⏳ Additional error handling and validation
5. ⏳ UI enhancements as needed

## Key Files

### frontend/app.py
Main application with:
- Filter definitions and UI elements
- Environment and Customer Server ID selection
- Test Connection button logic
- Search button logic (placeholder for SQL query)
- Logging configuration

### frontend/db_config.py
Database connection configurations for all environments and customer DBs

### logs/account_search.log
Contains:
- Connection test attempts (with host, port, service, user)
- Search operations (with all filter values)
- Errors and failures

## Important Notes
- Passwords are NOT logged for security
- Component ID filter is optional
- Connection string uses direct host/port/service instead of DSN
- Each environment has 6 customer databases configured
- Removed unused "environments" dictionary from app.py for cleaner code

## Security Considerations
- Database credentials stored in db_config.py (consider encrypting in production)
- Log files do not contain passwords
- ODBC connection uses standard authentication

---
*Last Updated: February 20, 2026*
