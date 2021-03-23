# WARNING - importing parlpy after mysql.connector results in error with urllib, relating to SSL secrets
# todo: fix this

import parlpy.bills.bill_list_fetcher as blf
import parlpy.bills.bill_details_iterator as bdi
import parlpy.mps.mp_fetcher as mf
import parlpy.mps.parties_fetcher as pf
import db_interactions as db_agent

import mysql.connector
from mysql.connector.constants import ClientFlag

import pandas as pd
import os
import datetime
import pickle

import secret_manager as sm
import google.cloud.logging
import logging

#db_agent = None


# clear all rows and reset increment
def clear_table(conn, cursor, table_name):
    #cursor.execute(f"DELETE FROM {db_name}.{table_name}")
    #cursor.execute(f"ALTER TABLE {db_name}.{table_name} AUTO_INCREMENT = 1")
    #conn.commit()
    db_agent.interact(f"DELETE FROM {db_name}.{table_name}")
    db_agent.interact(f"ALTER TABLE {db_name}.{table_name} AUTO_INCREMENT = 1")


def clear_all_4_tables(conn, cursor):
    clear_table(conn, cursor, "MPVotes")
    clear_table(conn, cursor, "Bills")
    clear_table(conn, cursor, "MP")
    clear_table(conn, cursor, "Party")




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


def execute_insert_mp_data_in_db(conn, cursor, first_name, second_name, constituency, member_id, party_id, active):
    if active == True:
        current = 1
    else:
        current = 0
    insert_command_string = f"INSERT INTO MP (mpID, firstName, lastName, partyID, area, current) VALUES (\"{member_id}\",\"{first_name}\",\"{second_name}\",{party_id},\"{constituency}\",\"{current}\")"

    print(f"mp insert command string")
    print(insert_command_string)

    #cursor.execute(insert_command_string)
    db_agent.interact(insert_command_string)


# there are missing entries as package does not get dead members, but dead members ids may be refd in votes data
def insert_dead_mp_placeholder(conn, cursor):
    upper_limit_estimate = 6000
    for i in range(upper_limit_estimate):
        print(f"checking mpID {i} in table")
        if not is_in_field(conn, cursor, "MP", "mpID", i, "int"):
            print(f"mpID {i} not in table")
            execute_insert_mp_data_in_db(conn, cursor, "missing_first_name", "missing_second_name", "unknown", i, 0, False)
            #conn.commit()


# assumes table is empty
def insert_mp_data(conn, cursor):
    mp_fetcher = mf.MPOverview()

    mp_fetcher.get_all_members(params={"House": "Commons"})
    all_mp_data = mp_fetcher.mp_overview_data

    for mp in all_mp_data.itertuples():
        first_name, second_name = get_names_from_full_name(mp.name_display)

        print(f"{mp.name_display} is {mp.current_member} active")
        execute_insert_mp_data_in_db(conn, cursor, first_name, second_name, mp.constituency, mp.member_id, mp.party_id, active=mp.current_member)

    #conn.commit()


def is_in_field(conn, cursor, table, field, val, type):
    if type == "string":
        #cursor.execute(f"SELECT * FROM {db_name}.{table} WHERE {field} = \"{val}\"")
        cursor = db_agent.select(f"SELECT * FROM {db_name}.{table} WHERE {field} = \"{val}\"")
    elif type == "int":
        #cursor.execute(f"SELECT * FROM {db_name}.{table} WHERE {field} = {val}")
        cursor = db_agent.select(f"SELECT * FROM {db_name}.{table} WHERE {field} = {val}")
    else:
        raise ValueError("unrecog type")

    count = 0
    for row in cursor:
        count+=1

    if count > 0:
        return True
    else:
        return False


def execute_update_mp_data_in_db(cursor, conn, first_name, second_name, email, constituency, member_id, party_id, active):
    if active == True:
        current = 1
    else:
        current = 0
    update_command_string = f"UPDATE {db_name}.MP " \
                            f"SET mpID = \"{member_id}\", " \
                            f"firstName = \"{first_name}\", " \
                            f"lastName = \"{second_name}\", " \
                            f"email = \"{email}\", " \
                            f"partyID = {party_id}, " \
                            f"area = \"{constituency}\", " \
                            f"current = {current} " \
                            f"WHERE mpID = {member_id}"

    print(f"mp update command string")
    print(update_command_string)

    #cursor.execute(update_command_string)
    db_agent.interact(update_command_string)


# does not assume table is empty
def upsert_mp_data(conn, cursor):
    mp_fetcher = mf.MPOverview()

    # todo: uncomment and delete below
    mp_fetcher.get_all_members(params={"House": "Commons"})
    all_mp_data = mp_fetcher.mp_overview_data

    for mp in all_mp_data.itertuples():
        first_name, second_name = get_names_from_full_name(mp.name_display)
        print(mp)
        if is_in_field(conn, cursor, "MP", "mpID", mp.member_id, "int"):
            execute_update_mp_data_in_db(cursor, conn, first_name, second_name, mp.email, mp.constituency, mp.member_id, mp.party_id, active=mp.current_member)
        else:
            #execute_insert_mp_data_in_db(cursor, conn, first_name, second_name, mp.email, mp.constituency, mp.member_id, mp.party_id, active=mp.current_member)
            print("should not be the case")

    #conn.commit()


def execute_insert_party_data(cursor, party_id, party_name):
    insert_command_string = f"INSERT INTO {db_name}.Party (partyID, partyName) VALUES (\"{party_id}\",\"{party_name}\")"

    print(f"party insert command string")
    print(insert_command_string)

    #cursor.execute(insert_command_string)
    db_agent.interact(insert_command_string)


# insert all party data and execute
def insert_party_data(conn, cursor):
    party_details_list = pf.get_all_parties()
    max_id_in_use = 0
    for i in party_details_list:
        if i.party_id > max_id_in_use:
            max_id_in_use = i.party_id
    total_parties_ids_upper_estimate = 4000 + max_id_in_use

    party_details_dict = {}
    for p in party_details_list:
        party_details_dict[p.party_id] = p.party_name

    for i in range(total_parties_ids_upper_estimate):
        if i in party_details_dict.keys():
            execute_insert_party_data(cursor, i, party_details_dict[i])
        else:
            execute_insert_party_data(cursor, i, "unknown")

    #conn.commit()


def execute_update_party_data(cursor, party_id, party_name):
    update_command_string = f"UPDATE {db_name}.Party SET partyName = \"{party_name}\" WHERE partyID = {party_id}"

    #cursor.execute(update_command_string)
    db_agent.interact(update_command_string)


def upsert_party_data(conn, cursor):
    party_details_list = pf.get_all_parties()

    for party in party_details_list:
        if is_in_field(conn,cursor,"Party","partyID",party.party_id,"int"):
            print(f"party {party.party_name} is already in")
            execute_update_party_data(cursor, party.party_id, party.party_name)
        else:
            print(f"party {party.party_name} is not already in")
            execute_insert_party_data(cursor, party.party_id, party.party_name)

    #conn.commit()


# return the billID for the passed bill
# todo: this needs to be more sophisticated, does not account for cases where the title is the same
def bill_id_in_bills_table(conn, cursor, bill):
    bill_id = None

    #cursor.execute(f"SELECT billID FROM {db_name}.Bills WHERE titleStripped = \"{bill.title_stripped}\"")
    cursor = db_agent.select(f"SELECT billID FROM {db_name}.Bills WHERE titleStripped = \"{bill.title_stripped}\"")

    count = 0
    for row in cursor:
        bill_id = row[0]

        count+=1
        if count > 2:
            raise Exception("billID must be unique, duplicates found")

    return bill_id


def get_sessions_string(sessions):
    sessions_string = ""
    for s in sessions:
        sessions_string += (s + ",")
    sessions_string = sessions_string[:-1]

    return sessions_string


def execute_insert_new_bill_into_bills_table(conn, cursor, bill):
    sessions_string = get_sessions_string(bill.sessions)

    summary_sanitised = bill.summary.replace("\"", "")

    insertion_command_string \
        = f"INSERT INTO {db_name}.Bills (titleStripped, billOrAct, shortDesc, sessions, link) " \
          f"VALUES (\"{bill.title_stripped}\",\"{bill.title_postfix}\",\"{summary_sanitised}\",\"{sessions_string}\",\"{bill.url}\")"
    #cursor.execute(insertion_command_string)
    db_agent.interact(insertion_command_string)

    # todo: remove?
    #conn.commit()


def execute_update_bill(conn, cursor, bill):
    sessions_string = get_sessions_string(bill.sessions)

    update_command_string = f"UPDATE {db_name}.Bills " \
                            f"SET " \
                            f"billOrAct = \"{bill.title_postfix}\", " \
                            f"shortDesc = \"{bill.summary}\", " \
                            f"sessions = \"{sessions_string}\", " \
                            f"link = \"{bill.url}\" " \
                            f"WHERE titleStripped = \"{bill.title_stripped}\""
    print(f"update command string {update_command_string}")
    #cursor.execute(update_command_string)
    cursor = db_agent.interact(update_command_string)

def division_in_mpvotes_table(conn, cursor, division_name):
    count_command_string = f"SELECT COUNT(*) FROM {db_name}.MPVotes WHERE title = \"{division_name}\""
    #cursor.execute(count_command_string)
    cursor = db_agent.select(count_command_string)
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

    insert_command_string = f"INSERT INTO {db_name}.MPVotes (positive, billID, mpID, stage, title)" \
                            f"VALUES (\"{positive}\",\"{bill_id}\",\"{mp_id}\",\"{stage}\",\"{division_title}\")"
    #print(f"insert_command_string {insert_command_string}")
    #cursor.execute(insert_command_string)
    db_agent.interact(insert_command_string)


def put_bill_and_division_data_in_db(conn, cursor, bills_overview):
    for bill in bdi.get_bill_details(bills_overview):
        # get the billID from DB
        bill_id = bill_id_in_bills_table(conn, cursor, bill)
        # if there is no billID, then the bill is not in the table, hence we need to insert the bill
        if bill_id is None:
            print(f"bill {bill.title_stripped} not yet in Bills table")
            execute_insert_new_bill_into_bills_table(conn, cursor, bill)
            bill_id = bill_id_in_bills_table(conn, cursor, bill)
        else:
            print(f"bill {bill.title_stripped} already in Bills table")
            execute_update_bill(conn, cursor, bill)
        # todo: otherwise, modify the row to put in the data which may have changed (we dont know what has changed, so
        #  insert all of it
        #conn.commit()

        for division in bill.divisions_list:
            division_title = division.division_name
            division_stage = division.division_stage
            # only insert if we haven't already inserted the results
            if not division_in_mpvotes_table(conn, cursor, division.division_name):
                print(f"division {division_title} not yet in MPVotes table")
                for no in division.noes:
                    execute_insert_new_vote_into_mpvotes_table(cursor, division_title, division_stage, bill_id, no, aye=False)
                for aye in division.ayes:
                    execute_insert_new_vote_into_mpvotes_table(cursor, division_title, division_stage, bill_id, aye, aye=True)
            else:
                print(f"division {division_title} already in MPVotes table")

            #conn.commit()


def insert_bills_and_divisions_data(conn, cursor, fresh=False, session="2019-21"):
    if fresh == True:
        os.remove("datetime_last_scraped.p")
        clear_table(conn, cursor, "MPVotes")
        clear_table(conn, cursor, "Bills")


    bills_overview = blf.BillsOverview()
    bills_overview.get_changed_bills_in_session(session_name=session)
    print("new bills_overview.bills_overview_data")
    print(bills_overview.bills_overview_data)
    print("bills overview object obtained, scraping complete")
    print(f"item counts: {bills_overview.bills_overview_data.count()}")

    pd.set_option('display.max_columns', 20)
    print(bills_overview.bills_overview_data)

    # insert everything back in
    put_bill_and_division_data_in_db(conn, cursor, bills_overview)

    #conn.commit()


# wipes tables in order, inserts all data back in
# takes ~2hrs
def reload_all_tables(conn, cursor):
    clear_all_4_tables(conn, cursor)
    insert_party_data(conn, cursor)
    insert_mp_data(conn, cursor)
    insert_dead_mp_placeholder(conn, cursor)
    insert_bills_and_divisions_data(conn, cursor, fresh=True, session="All")


def mock_datetime_pickle():
    pass


def db_describe_table(table_name):
    description = db_agent.select(f"DESCRIBE {table_name}")
    print(f"{table_name} table structure")
    for x in description:
        print(x)


def print_all_rows_of_table(table_name):
    rows = db_agent.select(f"SELECT * FROM {table_name}")
    print(f"all items in table {table_name}:")
    for x in rows:
        print(x)


sql_config = {}

db_name = ""



# by default assumes running on app engine
def insert_and_update_data(completely_fresh=False, day_frequency_for_party_and_mp_data=7, allow_party_and_mp_upsert=True, run_on_app_engine=True):
    global db_name
    #global db_agent
    db_name = "bill_data"

    conn = None
    cursor = None

    bills_overview = blf.BillsOverview()

    mock_datetime = datetime.datetime(2021, 3, 20, 12, 0, 0)
    print(f"datatime to pickle: {mock_datetime}")
    bills_overview.mock_datetime_last_scraped(mock_datetime)

    read_datetime = pickle.load( open( "datetime_last_scraped.p", "rb" ) )
    print(f"read datetime: {read_datetime}")

    """
    if completely_fresh:
        reload_all_tables(conn, cursor)
    else:
        # update MPs and parties ~every 5 days by default
        if datetime.datetime.now().day % day_frequency_for_party_and_mp_data == 0 and allow_party_and_mp_upsert:
            upsert_party_data(conn, cursor)
            upsert_mp_data(conn, cursor)
            print("finished updating MP and Party table")
        else:
            print("not a designated day to update MP and Party, or updating these has been disabled by parameter")

        # todo in final version the session_name must be "All" - but check the script works on Google cloud first
        insert_bills_and_divisions_data(conn, cursor, fresh=False, session="All")
    """


"""
if __name__ == "__main__":
    insert_and_update_data(run_on_app_engine=False, allow_party_and_mp_upsert=False)
    """



