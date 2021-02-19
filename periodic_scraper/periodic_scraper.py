# WARNING - importing parlpy after mysql.connector results in error with urllib, relating to SSL certs
# todo: fix this

from parlpy.bills.bill_list_fetcher import BillsOverview

import mysql.connector
from mysql.connector.constants import ClientFlag

from collections import namedtuple

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

# clear all rows and reset increment
def clear_bills_table(cursor):
    cursor.execute("DELETE FROM bills_app_db.Bills")
    cursor.execute("ALTER TABLE bills_app_db.Bills AUTO_INCREMENT = 1")
    conn.commit()

def insert_all_bill_overview_data(cursor, bill_data):
    for b in bill_data.itertuples():
        # this code gets govt provided bill detail path, could be used as unique id?
        # bill_detail_path_number = int(getattr(b, "bill_detail_path").rsplit("/")[-1])
        # print("int bill id: {}".format(bill_detail_path_number))

        bill_name = getattr(b, "bill_title")
        command_string = "INSERT INTO bills_app_db.Bills (title) VALUES (\"{0}\")".format(bill_name)
        cursor.execute(command_string)

    conn.commit()

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
print_bills_table_structure(cursor)

bills_this_session = BillsOverview()
bills_this_session.update_all_bills_in_session()

clear_bills_table(cursor)

insert_all_bill_overview_data(cursor, bills_this_session.bills_overview_data)

print_all_rows_of_bills_table(cursor)

cursor.close()
conn.close()
