# WARNING - importing parlpy after mysql.connector results in error with urllib, relating to SSL certs
# todo: fix this

from parlpy.bills.bill_list_fetcher import BillsOverview

import mysql.connector
from mysql.connector.constants import ClientFlag

# todo: put these in utility file for investigating database
def print_tables_in_db(cursor):
    cursor.execute("SHOW tables IN bills_app_db")
    for x in cursor:
        print(x)

def print_bills_table_structure(cursor):
    cursor.execute("DESCRIBE bills_app_db.Bills")
    print("Bills table structure")
    for x in cursor:
        print(x)

def print_all_rows_of_bills_table(cursor):
    cursor.execute("SELECT * FROM bills_app_db.Bills")
    print("all items in table:")
    for x in cursor:
        print(x)

sql_config = {
    "user": "root",
    "password": "",
    "host": "35.223.77.43",
    "client_flags": [ClientFlag.SSL],
    "ssl_ca": "/home/r/PycharmProjects/BillTracker/periodic_scraper/certs/server-ca.pem",
    "ssl_cert": "/home/r/PycharmProjects/BillTracker/periodic_scraper/certs/client-cert.pem",
    "ssl_key": "/home/r/PycharmProjects/BillTracker/periodic_scraper/certs/client-key.pem"
}


conn = mysql.connector.connect(**sql_config)

cursor = conn.cursor()

# list_tables_in_db(cursor)
#print_bills_table_structure(cursor)

cursor.execute("INSERT INTO bills_app_db.Bills (billID) VALUES (334)")
conn.commit()

print_all_rows_of_bills_table(cursor)

cursor.close()
conn.close()

#bills_this_session = BillsOverview()
#bills_this_session.update_all_bills_in_session()

#print(bills_this_session.bills_overview_data)

#print(bills_this_session.bills_overview_data.iloc[0])
