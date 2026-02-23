import streamlit as st
from datetime import date
import logging
import os
from db_config import db_config

# Setup logging
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, "account_search.log")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)


# Add Invoice button to redirect to Invoicing UI
st.markdown('<a href="https://accountsui.streamlit.app/" target="_blank"><button style="background-color:#4CAF50;color:white;padding:10px 24px;border:none;border-radius:4px;cursor:pointer;">Invoice</button></a>', unsafe_allow_html=True)

st.title("Kenan Account Retrieval")

# Filters
account_types = ["TV", "BB", "HW", "MA", "BBH"]
payment_types = ["Any", "CDC", "RID", "Postal"]

account_type = st.selectbox("Account Type", account_types)
payment_type = st.selectbox("Payment Type", payment_types)
in_collection = st.selectbox("In Collection", ["Any", "Yes", "No"])
active_date = st.date_input("Active Date", value=date.today())
open_invoice = st.selectbox("Open Invoice", ["Any", "Yes", "No"])
component_id = st.text_input("Component ID (optional)")

env_options = list(db_config.keys())
environment = st.selectbox("Environment", env_options)

customer_server_ids = [3, 4, 5, 6, 7, 8]
server_id_to_index = {3: 0, 4: 1, 5: 2, 6: 3, 7: 4, 8: 5}
customer_server_id = st.selectbox("Customer Server ID", customer_server_ids)

if st.button("Test Connection"):
    try:
        import pyodbc
        env_conf = db_config[environment]
        cust_db_index = server_id_to_index[customer_server_id]
        db_conf = env_conf["customer"][cust_db_index]
        conn_str = (
            f"DRIVER={{Oracle in OraClient12Home1}};"
            f"DBQ={db_conf['host']}:{db_conf['port']}/{db_conf['service_name']};"
            f"UID={db_conf['user']};PWD={db_conf['password']}"
        )
        # Log connection details (excluding password)
        logging.info(f"Testing connection: env={environment}, DB{cust_db_index+1}, host={db_conf['host']}, port={db_conf['port']}, service={db_conf['service_name']}, user={db_conf['user']}")
        conn = pyodbc.connect(conn_str)
        conn.close()
        st.success(f"Connection to {environment} Customer DB{cust_db_index+1} successful!")
    except Exception as e:
        st.error(f"Connection test failed: {e}")
        logging.error(f"Connection test failed for env={environment}, DB{cust_db_index+1}: {e}")

if st.button("Search"):
    try:
        import pyodbc
        env_conf = db_config[environment]
        cust_db_index = server_id_to_index[customer_server_id]
        db_conf = env_conf["customer"][cust_db_index]
        # Use direct Oracle connection string
        conn_str = (
            f"DRIVER={{Oracle in OraClient12Home1}};"
            f"DBQ={db_conf['host']}:{db_conf['port']}/{db_conf['service_name']};"
            f"UID={db_conf['user']};PWD={db_conf['password']}"
        )
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        # Build SQL query with optional component_id
        # sql = f"SELECT account_id FROM accounts WHERE ..."
        # if component_id:
        #     sql += f" AND component_id = '{component_id}'"
        # cursor.execute(sql)
        # results = [row[0] for row in cursor.fetchall()]
        st.success(f"Connected to {environment} Customer DB{cust_db_index+1}!")
        st.write(["AccountID1", "AccountID2"])
        logging.info(f"Search successful in {environment} Customer DB{cust_db_index+1} for filters: AccountType={account_type}, PaymentType={payment_type}, InCollection={in_collection}, ActiveDate={active_date}, OpenInvoice={open_invoice}, ComponentID={component_id if component_id else 'N/A'}, CustomerServerID={customer_server_id}")
        cursor.close()
        conn.close()
    except Exception as e:
        st.error(f"DB connection failed: {e}")
        logging.error(f"DB connection/search failed in {environment} Customer DB{customer_server_id}: {e}")

        st.warning("Could not retrieve data. Please check your connection or try a different environment.")
