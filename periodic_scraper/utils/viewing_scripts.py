def print_tables_in_db(cursor):
    cursor.execute("SHOW tables IN bills_app_db")
    for x in cursor:
        print(x)


def print_table_structure(cursor, table_name):
    cursor.execute(f"DESCRIBE bills_app_db.{table_name}")
    print("Bills table structure")
    for x in cursor:
        print(x)


def print_all_rows_of_bills_table(cursor):
    cursor.execute("SELECT * FROM bills_app_db.Bills")
    print("all items in table:")
    for x in cursor:
        print(x)