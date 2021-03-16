import mysql.connector
from mysql.connector.constants import ClientFlag


def print_tables_in_db(cursor):
    cursor.execute("SHOW tables IN bills_app_db")
    for x in cursor:
        print(x)


def print_table_structure(cursor, table_name):
    cursor.execute(f"DESCRIBE bills_app_db.{table_name}")
    print(f"{table_name} table structure")
    for x in cursor:
        print(x)


def print_all_rows_of_table(cursor, table_name):
    cursor.execute(f"SELECT * FROM bills_app_db.{table_name}")
    print(f"all items in table {table_name}:")
    for x in cursor:
        print(x)


sql_config = {
    "user": "root",
    "password": "",
    "host": "35.223.77.43",
    "client_flags": [ClientFlag.SSL],
    "ssl_ca": "../certs/server-ca.pem",
    "ssl_cert": "../certs/client-cert.pem",
    "ssl_key": "../certs/client-key.pem"
}


def investigate_db():
    conn = mysql.connector.connect(**sql_config)
    cursor = conn.cursor()

    #print_tables_in_db(cursor)

    print_table_structure(cursor, "MPVotes")

    #print_all_rows_of_bills_table(cursor)

    cursor.close()
    conn.close()

investigate_db()