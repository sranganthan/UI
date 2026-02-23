# DB configuration for each environment and DB type
# Use direct connection string for Oracle (no DSN required)
# Example for Oracle:
# 'oracle': {
#     'host': 'your_host',
#     'port': 1521,
#     'service_name': 'your_service',
#     'user': 'your_user',
#     'password': 'your_password'
# }

db_config = {
    "System test": {
        "customer": [
            {"host": "colkfxdb-scan", "port": 3525, "service_name": "COKCU1", "user": "arbor", "password": "Performance123"},
            {"host": "colkfxdb-scan", "port": 3525, "service_name": "COKCU2", "user": "arbor", "password": "Performance123"},
            {"host": "colkfxdb-scan", "port": 3525, "service_name": "COKCU3", "user": "arbor", "password": "Performance123"},
            {"host": "colkfxdb-scan", "port": 3525, "service_name": "COKCU4", "user": "arbor", "password": "Performance123"},
            {"host": "colkfxdb-scan", "port": 3525, "service_name": "COKCU5", "user": "arbor", "password": "Performance123"},
            {"host": "colkfxdb-scan", "port": 3525, "service_name": "COKCU6", "user": "arbor", "password": "Performance123"},
           # ... add more as needed ...
        ]
    },
   
     "ST": {
        "customer": [
            {"host": "colkfxmdb-scan", "port": 3525, "service_name": "BBKCU1", "user": "arbor", "password": "Delphix123"},
            {"host": "colkfxmdb-scan", "port": 3525, "service_name": "BBKCU2", "user": "arbor", "password": "Delphix123"},
            {"host": "colkfxmdb-scan", "port": 3525, "service_name": "BBKCU3", "user": "arbor", "password": "Delphix123"},
            {"host": "colkfxmdb-scan", "port": 3525, "service_name": "BBKCU4", "user": "arbor", "password": "Delphix123"},
            {"host": "colkfxmdb-scan", "port": 3525, "service_name": "BBKCU5", "user": "arbor", "password": "Delphix123"},
            {"host": "colkfxmdb-scan", "port": 3525, "service_name": "BBKCU6", "user": "arbor", "password": "Delphix123"},
           # ... add more as needed ...
        ]
    },
    "IT": {
        "customer": [
            {"host": "colkfx28db1", "port": 4521, "service_name": "C28KCU1", "user": "arbor", "password": "Arb03fx2019"},
            {"host": "colkfx28db1", "port": 4521, "service_name": "C28KCU2", "user": "arbor", "password": "Arb03fx2019"},
            {"host": "colkfx28db1", "port": 4521, "service_name": "C28KCU3", "user": "arbor", "password": "Arb03fx2019"},
            {"host": "colkfx28db1", "port": 4521, "service_name": "C28KCU4", "user": "arbor", "password": "Arb03fx2019"},
            {"host": "colkfx28db1", "port": 4521, "service_name": "C28KCU5", "user": "arbor", "password": "Arb03fx2019"},
            {"host": "colkfx28db1", "port": 4521, "service_name": "C28KCU6", "user": "arbor", "password": "Arb03fx2019"},
           # ... add more as needed ...
        ]
    },
    "AM": {
        "customer": [
            {"host": "colkfxamdb-scan", "port": 2525, "service_name": "AMKCU1", "user": "arbor", "password": "Performance123"},
            {"host": "colkfxamdb-scan", "port": 2525, "service_name": "AMKCU2", "user": "arbor", "password": "Performance123"},
            {"host": "colkfxamdb-scan", "port": 2525, "service_name": "AMKCU3", "user": "arbor", "password": "Performance123"},
            {"host": "colkfxamdb-scan", "port": 2525, "service_name": "AMKCU4", "user": "arbor", "password": "Performance123"},
            {"host": "colkfxamdb-scan", "port": 2525, "service_name": "AMKCU5", "user": "arbor", "password": "Performance123"},
            {"host": "colkfxamdb-scan", "port": 2525, "service_name": "AMKCU6", "user": "arbor", "password": "Performance123"},
           # ... add more as needed ...
        ]
    },
    "UAT": {
        "customer": [
            {"host": "e2ebbkfxmdb1", "port": 3521, "service_name": "E2EKCU1", "user": "arbor", "password": "Delphix123"},
            {"host": "e2ebbkfxmdb1", "port": 3521, "service_name": "E2EKCU2", "user": "arbor", "password": "Delphix123"},
            {"host": "e2ebbkfxmdb1", "port": 3521, "service_name": "E2EKCU3", "user": "arbor", "password": "Delphix123"},
            {"host": "e2ebbkfxmdb1", "port": 3521, "service_name": "E2EKCU4", "user": "arbor", "password": "Delphix123"},
            {"host": "e2ebbkfxmdb1", "port": 3521, "service_name": "E2EKCU5", "user": "arbor", "password": "Delphix123"},
            {"host": "e2ebbkfxmdb1", "port": 3521, "service_name": "E2EKCU6", "user": "arbor", "password": "Delphix123"},
           # ... add more as needed ...
        ]
    },
}
