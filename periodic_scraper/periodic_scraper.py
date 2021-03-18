# WARNING - importing parlpy after mysql.connector results in error with urllib, relating to SSL certs
# todo: fix this

from parlpy.bills.bill_list_fetcher import BillsOverview
import parlpy.mps.mp_fetcher as mf

import mysql.connector
from mysql.connector.constants import ClientFlag

import pandas as pd


# clear all rows and reset increment
def clear_table(conn, cursor, table_name):
    cursor.execute(f"DELETE FROM bills_app_db.{table_name}")
    cursor.execute(f"ALTER TABLE bills_app_db.{table_name} AUTO_INCREMENT = 1")
    conn.commit()


def insert_all_bill_overview_data(conn, cursor, bill_data):
    for b in bill_data.itertuples():
        # this code gets govt provided bill detail path, could be used as unique id?
        # bill_detail_path_number = int(getattr(b, "bill_detail_path").rsplit("/")[-1])
        # print("int bill id: {}".format(bill_detail_path_number))

        bill_name = getattr(b, "bill_title")
        command_string = "INSERT INTO bills_app_db.Bills (title) VALUES (\"{0}\")".format(bill_name)
        cursor.execute(command_string)

    conn.commit()

def print_all_rows_of_table(cursor, table_name):
    cursor.execute(f"SELECT * FROM bills_app_db.{table_name}")
    print("all items in table:")
    for x in cursor:
        print(x)

sql_config = {
    "user": "root",
    "password": "",
    "host": "35.223.77.43",
    "client_flags": [ClientFlag.SSL],
    "ssl_ca": "certs/server-ca.pem",
    "ssl_cert": "certs/client-cert.pem",
    "ssl_key": "certs/client-key.pem"
}

def get_names_from_full_name(name_display):
    name_words = name_display.split(" ")

    # if there are three words the first is likely a title
    if len(name_words) == 3:
        first_name = name_words[1]
        second_name = name_words[2]
    elif len(name_words) == 2:
        first_name = name_words[0]
        second_name = name_words[1]
    else:
        first_name = "unknown_first_name"
        second_name = "unknown_second_name"

    return first_name, second_name

def put_mp_data_in_db(cursor, conn, first_name, second_name, member_id, party_id):
    insert_command_string = f"INSERT INTO bills_app_db.MP (firstName, lastName, partyID) VALUES (\"{first_name}\",\"{second_name}\",{party_id})"

    print(f"insert command string")
    print(insert_command_string)

    cursor.execute(insert_command_string)



# ('mpID', b'int(11)', 'NO', 'PRI', None, 'auto_increment')
# ('firstName', b'text', 'YES', '', None, '')
# ('lastName', b'text', 'YES', '', None, '')
# ('email', b'text', 'YES', '', None, '')
# ('mpAddress', b'text', 'YES', '', None, '')
# ('partyID', b'int(11)', 'NO', 'MUL', None, '')
# ('photoPath', b'text', 'YES', '', None, '')
# ('phoneNum', b'text', 'YES', '', None, '')
# ('area', b'text', 'YES', '', None, '')
def insert_mp_data(conn, cursor):
    mp_fetcher = mf.MPOverview()

    mp_fetcher.get_all_members(params={"IsCurrentMember": True, "House": "Commons", "skip": 620})
    current_mp_data = mp_fetcher.mp_overview_data
    pd.set_option("display.max_columns", len(current_mp_data.columns))

    print(current_mp_data)

    clear_table(conn, cursor, "MP")

    for (index,
        name_display,
        name_full_title,
        name_address_as,
        name_list_as,
        member_id,
        gender,
        party_id,
        last_updated) in current_mp_data.itertuples():
        first_name, second_name = get_names_from_full_name(name_display)
        put_mp_data_in_db(cursor, conn, first_name, second_name, member_id, party_id)
        #print(name_display, member_id, party_id)

    conn.commit()




def insert_bills_data(conn, cursor):
    bills_this_session = BillsOverview()
    bills_this_session.update_all_bills_in_session()

    # clear the table and insert everything back in
    clear_table(conn, cursor, "Bills")
    insert_all_bill_overview_data(conn, cursor, bills_this_session.bills_overview_data)

    print_all_rows_of_table(cursor, "Bills")

def insert_and_update_data():
    conn = mysql.connector.connect(**sql_config)
    cursor = conn.cursor()

    insert_mp_data(conn, cursor)

    cursor.close()
    conn.close()

insert_and_update_data()
