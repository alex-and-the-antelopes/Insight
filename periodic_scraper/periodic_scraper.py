# WARNING - importing parlpy after mysql.connector results in error with urllib, relating to SSL secrets
# todo: fix this

import parlpy.bills.bill_list_fetcher as blf
import parlpy.bills.bill_details_iterator as bdi
import parlpy.mps.mp_fetcher as mf
import parlpy.mps.parties_fetcher as pf

import mysql.connector
from mysql.connector.constants import ClientFlag

import pandas as pd

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


# clear all rows and reset increment
def clear_table(conn, cursor, table_name):
    cursor.execute(f"DELETE FROM bills_app_db.{table_name}")
    cursor.execute(f"ALTER TABLE bills_app_db.{table_name} AUTO_INCREMENT = 1")
    conn.commit()


def print_all_rows_of_table(cursor, table_name):
    cursor.execute(f"SELECT * FROM bills_app_db.{table_name}")
    print("all items in table:")
    for x in cursor:
        print(x)


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


def execute_mp_data_in_db(cursor, conn, first_name, second_name, member_id, party_id):
    insert_command_string = f"INSERT INTO bills_app_db.MP (firstName, lastName, partyID) VALUES (\"{first_name}\",\"{second_name}\",{party_id})"

    print(f"mp insert command string")
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
        print("here")
        execute_mp_data_in_db(cursor, conn, first_name, second_name, member_id, party_id)
        #print(name_display, member_id, party_id)

    conn.commit()


def execute_party_data_in_db(cursor, party_id, party_name):
    insert_command_string = f"INSERT INTO bills_app_db.Party (partyID, partyName) VALUES (\"{party_id}\",\"{party_name}\")"

    print(f"party insert command string")
    print(insert_command_string)

    cursor.execute(insert_command_string)


# clear table, execute insertions and commit Party data
# todo: write update functionality rather than delete -> add
def insert_party_data(conn, cursor):
    clear_table(conn, cursor, "Party")

    party_details_list = pf.get_all_parties()

    for p in party_details_list:
        execute_party_data_in_db(cursor, p.party_id, p.party_name)

    conn.commit()


def execute_bill_data_in_db(conn, cursor, bills_overview):
    for b in bdi.get_bill_details(bills_overview):
        print(b.title_stripped)
        #command_string = "INSERT INTO bills_app_db.Bills (title) VALUES (\"{0}\")".format(bill_name)
        #cursor.execute(command_string)

    #conn.commit()


def insert_bills_data(conn, cursor):
    bills_overview = blf.BillsOverview()
    bills_overview.update_all_bills_in_session(session_name="2019-21")

    # insert everything back in
    execute_bill_data_in_db(conn, cursor, bills_overview)

    conn.commit()

    #print_all_rows_of_table(cursor, "Bills")


def insert_and_update_data():
    conn = mysql.connector.connect(**sql_config)
    cursor = conn.cursor()
    #clear_table(conn, cursor, "Party")

    # todo: only run this infrequently
    # clear the tables in order according to foreign key constraints, then add all values back in
    if True:
        clear_table(conn, cursor, "MP")
        clear_table(conn, cursor, "Party")
        insert_party_data(conn, cursor)
        insert_mp_data(conn, cursor)

    insert_bills_data(conn, cursor)

    cursor.close()
    conn.close()


insert_and_update_data()
