import mysql.connector
from mysql.connector.constants import ClientFlag

public_ip = "35.190.194.63"

with open("../secrets/mastergk_pass", 'r') as reader:
    password = reader.read()

sql_config = {
    "user": "mastergk",
    "password": password,
    "host": public_ip,
    "client_flags": [ClientFlag.SSL],
    "ssl_ca": "../secrets/server-ca.pem",
    "ssl_cert": "../secrets/client-cert.pem",
    "ssl_key": "../secrets/client-key.pem"
}


def print_tables_in_db(cursor):
    cursor.execute("SHOW tables IN bill_app_db")
    for x in cursor:
        print(x)


def print_table_structure(cursor, table_name):
    cursor.execute(f"DESCRIBE bill_app_db.{table_name}")
    print(f"{table_name} table structure")
    for x in cursor:
        print(x)


def print_all_rows_of_table(cursor, table_name):
    cursor.execute(f"SELECT * FROM bill_app_db.{table_name}")
    print(f"all items in table {table_name}:")
    for x in cursor:
        print(x)


def investigate_db():
    conn = mysql.connector.connect(**sql_config)
    cursor = conn.cursor()

    print_tables_in_db(cursor)

    print_table_structure(cursor, "MPVotes")

    #print_all_rows_of_table(cursor, "MP")

    cursor.close()
    conn.close()

investigate_db()