import mysql.connector
from mysql.connector.constants import ClientFlag

public_ip = "35.190.194.63"

with open("../secrets/user_pass", 'r') as reader:
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

db_name = "bill_app_db"


def print_tables_in_db(cursor):
    cursor.execute(f"SHOW tables IN {db_name}")
    for x in cursor:
        print(x)


def print_table_structure(cursor, table_name):
    cursor.execute(f"DESCRIBE {db_name}.{table_name}")
    print(f"{table_name} table structure")
    for x in cursor:
        print(x)


def print_all_rows_of_table(cursor, table_name):
    cursor.execute(f"SELECT * FROM {db_name}.{table_name}")
    print(f"all items in table {table_name}:")
    for x in cursor:
        print(x)


def investigate_db():
    conn = mysql.connector.connect(**sql_config)
    cursor = conn.cursor()

    print_tables_in_db(cursor)

    print_table_structure(cursor, "Party")
    print_table_structure(cursor, "MP")
    print_table_structure(cursor, "Bills")
    print_table_structure(cursor, "MPVotes")

    #print_all_rows_of_table(cursor, "Party")
    print_all_rows_of_table(cursor, "MP")
    #print_all_rows_of_table(cursor, "Bills")
    #print_all_rows_of_table(cursor, "MPVotes")

    cursor.close()
    conn.close()

investigate_db()