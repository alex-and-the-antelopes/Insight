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

with open("secrets/mastergk_pass", 'r') as reader:
    password = reader.read()

sql_config = {
    "user": "mastergk",
    "password": password,
    "host": public_ip,
    "client_flags": [ClientFlag.SSL],
    "ssl_ca": "secrets/server-ca.pem",
    "ssl_cert": "secrets/client-cert.pem",
    "ssl_key": "secrets/client-key.pem"
}


# clear all rows and reset increment
def clear_table(conn, cursor, table_name):
    cursor.execute(f"DELETE FROM bill_app_db.{table_name}")
    cursor.execute(f"ALTER TABLE bill_app_db.{table_name} AUTO_INCREMENT = 1")
    conn.commit()


def print_all_rows_of_table(cursor, table_name):
    cursor.execute(f"SELECT * FROM bill_app_db.{table_name}")
    print(f"all items in table: {table_name}")
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
    insert_command_string = f"INSERT INTO bill_app_db.MP (mpID, firstName, lastName, partyID) VALUES (\"{member_id}\",\"{first_name}\",\"{second_name}\",{party_id})"

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

    mp_fetcher.get_all_members(params={"House": "Commons"})
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
    insert_command_string = f"INSERT INTO bill_app_db.Party (partyID, partyName) VALUES (\"{party_id}\",\"{party_name}\")"

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


def bill_id_in_bills_table(conn, cursor, bill):
    bill_id = None

    cursor.execute(f"SELECT billID FROM bill_app_db.Bills WHERE titleStripped = \"{bill.title_stripped}\"")

    count = 0
    for row in cursor:
        bill_id = row[0]

        count+=1
        if count > 2:
            raise Exception("billID must be unique, duplicates found")

    return bill_id


def insert_new_bill_into_bills_table(conn, cursor, bill):
    insertion_command_string \
        = f"INSERT INTO bill_app_db.Bills (titleStripped, billOrAct, shortDesc, link) " \
          f"VALUES (\"{bill.title_stripped}\",\"{bill.title_postfix}\",\"{bill.summary}\",\"{bill.url}\")"
    cursor.execute(insertion_command_string)
    conn.commit()


def division_in_mpvotes_table(conn, cursor, division_name):
    count_command_string = f"SELECT COUNT(*) FROM bill_app_db.MPVotes WHERE title = \"{division_name}\""
    cursor.execute(count_command_string)
    for c in cursor:
        print(f"type count[0] {type(c[0])}")
        count = c[0]

    if count > 0:
        return True
    else:
        return False


def execute_insert_new_vote_into_mpvotes_table(cursor, division_title, stage, bill_id, mp_id, aye=True):
    if aye == True:
        positive = 1
    else:
        positive = 0

    insert_command_string = f"INSERT INTO bill_app_db.MPVotes (positive, billID, mpID, stage, title)" \
                            f"VALUES (\"{positive}\",\"{bill_id}\",\"{mp_id}\",\"{stage}\",\"{division_title}\")"
    cursor.execute(insert_command_string)



def execute_bill_data_in_db(conn, cursor, bills_overview):
    for bill in bdi.get_bill_details(bills_overview):
        # get the billID from DB
        bill_id = bill_id_in_bills_table(conn, cursor, bill)
        # if there is no billID, then the bill is not in the table, hence we need to insert the bill
        if bill_id is None:
            insert_new_bill_into_bills_table(conn, cursor, bill)
            bill_id = bill_id_in_bills_table(conn, cursor, bill)
        # todo: otherwise, modify the row to put in the data which may have changed (we dont know what has changed, so
        #  insert all of it
        else:
            pass

        for division in bill.divisions_list:
            division_title = division.division_name
            division_stage = division.division_stage
            # only insert if we haven't already inserted the results
            if not division_in_mpvotes_table(conn, cursor, division.division_name):
                print(f"division {division_title} not in MPVotes table")
                for no in division.noes:
                    execute_insert_new_vote_into_mpvotes_table(cursor, division_title, division_stage, bill_id, no, aye=False)
                for aye in division.ayes:
                    execute_insert_new_vote_into_mpvotes_table(cursor, division_title, division_stage, bill_id, aye, aye=True)
                conn.commit()


def insert_bills_and_divisions_data(conn, cursor):
    bills_overview = blf.BillsOverview()
    # todo in final version the session_name must be "All" - but check the script works on Google cloud first
    bills_overview.update_all_bills_in_session(session_name="2019-21")
    print("bills overview object obtained, scraping complete")
    print(f"{bills_overview.bills_overview_data.count()} items")

    # insert everything back in
    execute_bill_data_in_db(conn, cursor, bills_overview)

    conn.commit()


def refresh_mp_and_party_tables(conn, cursor):
    clear_table(conn, cursor, "MP")
    clear_table(conn, cursor, "Party")
    insert_party_data(conn, cursor)
    insert_missing_party_data(conn, cursor)
    insert_mp_data(conn, cursor)


# function called by cron, I need to split functionality into different functions
def insert_and_update_data():
    conn = mysql.connector.connect(**sql_config)
    cursor = conn.cursor(buffered=True)

    # todo: only run this infrequently
    # clear the tables in order according to foreign key constraints, then add all values back in
    # commented out - data currently in db, working on inserting bill and division data
    refresh_mp_and_party_tables(conn, cursor)
    print("finished updating MP and Party table")

    print_all_rows_of_table(cursor, "MP")
    print_all_rows_of_table(cursor, "Party")

    insert_bills_and_divisions_data(conn, cursor)

    cursor.close()
    conn.close()


insert_and_update_data()
