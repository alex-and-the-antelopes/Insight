import parlpy.bills.bill_list_fetcher as blf
import parlpy.bills.bill_details_iterator as bdi
import parlpy.mps.mp_fetcher as mf
import parlpy.mps.parties_fetcher as pf
import db_interactions as db_agent

import os
import datetime

import gcsfs


# clear all rows and reset increment
def clear_table(table_name):
    db_agent.interact(f"DELETE FROM {db_name}.{table_name}")
    db_agent.interact(f"ALTER TABLE {db_name}.{table_name} AUTO_INCREMENT = 1")


def clear_all_4_tables():
    clear_table("MPVotes")
    clear_table("Bills")
    clear_table("MP")
    clear_table("Party")


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


def execute_insert_mp_data_in_db(first_name, second_name, email, constituency, member_id, party_id, active):
    if active == True:
        current = 1
    else:
        current = 0
    insert_command_string = f"INSERT INTO MP (mpID, firstName, lastName, email, partyID, area, current) VALUES (\"{member_id}\",\"{first_name}\",\"{second_name}\",\"{email}\",{party_id},\"{constituency}\",\"{current}\")"

    print(f"mp insert command string")
    print(insert_command_string)

    db_agent.interact(insert_command_string)


# there are missing entries as package does not get dead members, but dead members ids may be refd in votes data
def insert_dead_mp_placeholder():
    upper_limit_estimate = 6000
    for i in range(upper_limit_estimate):
        print(f"checking mpID {i} in table")
        if not is_in_field("MP", "mpID", i, "int"):
            print(f"mpID {i} not in table")
            execute_insert_mp_data_in_db("missing_first_name", "missing_second_name", "unknown", "unknown", i, 0, False)


# assumes table is empty
def insert_mp_data():
    mp_fetcher = mf.MPOverview()

    mp_fetcher.get_all_members(params={"House": "Commons"})
    all_mp_data = mp_fetcher.mp_overview_data

    for mp in all_mp_data.itertuples():
        first_name, second_name = get_names_from_full_name(mp.name_display)

        print(f"{mp.name_display} is {mp.current_member} active")
        execute_insert_mp_data_in_db(first_name, second_name, mp.email, mp.constituency, mp.member_id, mp.party_id, mp.current_member)


def is_in_field(table, field, val, type):
    if type == "string":
        count_from_interaction = db_agent.select(f"SELECT COUNT(*) FROM {db_name}.{table} WHERE {field} = \"{val}\"")
    elif type == "int":
        count_from_interaction = db_agent.select(f"SELECT COUNT(*) FROM {db_name}.{table} WHERE {field} = {val}")
    else:
        raise ValueError("unrecog type")

    print(f"count from interact {count_from_interaction}")

    count = extract_first_string_from_db_interaction(count_from_interaction)
    count = int(count)

    print(f"count {count}")

    if count > 0:
        return True
    else:
        return False


def execute_update_mp_data_in_db(first_name, second_name, email, constituency, member_id, party_id, active):
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

    db_agent.interact(update_command_string)


# does not assume table is empty
def upsert_mp_data():
    print("in upsert_mp_data")
    mp_fetcher = mf.MPOverview()
    print("created MPOverview obj")

    # todo: uncomment and delete below
    mp_fetcher.get_all_members(params={"House": "Commons"})
    all_mp_data = mp_fetcher.mp_overview_data
    print("fetched all mp data")

    for mp in all_mp_data.itertuples():
        first_name, second_name = get_names_from_full_name(mp.name_display)
        print(f"checking if mp {mp.name_display}")
        if is_in_field("MP", "mpID", mp.member_id, "int"):
            print(f"mp {mp.name_display} already in MP")
            execute_update_mp_data_in_db(first_name, second_name, mp.email, mp.constituency, mp.member_id, mp.party_id, mp.current_member)
        else:
            print(f"mp {mp.name_display} not yet in MP")
            execute_insert_mp_data_in_db(first_name, second_name, mp.email, mp.constituency, mp.member_id, mp.party_id, mp.current_member)

    print("finished inserting mp data")


def execute_insert_party_data(party_id, party_name):
    insert_command_string = f"INSERT INTO {db_name}.Party (partyID, partyName) VALUES (\"{party_id}\",\"{party_name}\")"

    print(f"party insert command string")
    print(insert_command_string)

    db_agent.interact(insert_command_string)


# insert all party data and execute
def insert_party_data():
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
            execute_insert_party_data(i, party_details_dict[i])
        else:
            execute_insert_party_data(i, "unknown")


def execute_update_party_data(party_id, party_name):
    update_command_string = f"UPDATE {db_name}.Party SET partyName = \"{party_name}\" WHERE partyID = {party_id}"

    db_agent.interact(update_command_string)


def upsert_party_data():
    party_details_list = pf.get_all_parties()

    for party in party_details_list:
        if is_in_field("Party","partyID",party.party_id,"int"):
            print(f"party {party.party_name} is already in")
            execute_update_party_data(party.party_id, party.party_name)
        else:
            print(f"party {party.party_name} is not already in")
            execute_insert_party_data(party.party_id, party.party_name)


# gets xyz from string of form "[(xyz,...)]"
def extract_first_string_from_db_interaction(interaction_string):
    # remove opening 2 brackets
    extracted_result = interaction_string[2:]
    # remove closing 2 brackets
    extracted_result = extracted_result[:-2]
    extracted_result = extracted_result.split(",", maxsplit=1)[0]

    return extracted_result

# return the billID for the passed bill
# todo: this needs to be more sophisticated, does not account for cases where the title is the same
def bill_id_in_bills_table(bill):
    bill_id = None

    count_command_string = f"SELECT COUNT(*) FROM {db_name}.Bills WHERE titleStripped = \"{bill.title_stripped}\""
    count_from_interaction = db_agent.select(count_command_string)

    print(f"type count from interaction: {type(count_from_interaction)}")
    print(f"count from interaction: {count_from_interaction}")

    # remove opening 2 brackets
    count = extract_first_string_from_db_interaction(count_from_interaction)
    count = int(count)

    print(f"type count: {type(count)}")
    print(f"count: {count}")

    if count != 0:
        if count > 1:
            raise Exception("billID must be unique, duplicates found")

        select_bill_id_string = f"SELECT billID FROM {db_name}.Bills WHERE titleStripped = \"{bill.title_stripped}\""
        bill_id_from_interaction = db_agent.select(select_bill_id_string)
        print(f"type bill id interaction: {type(bill_id_from_interaction)}")
        print(f"bill id interaction: {bill_id_from_interaction}")

        bill_id = extract_first_string_from_db_interaction(bill_id_from_interaction)
        bill_id = int(bill_id)

        print(f"bill_id: {bill_id}")
        print(f"bill_id type: {type(bill_id)}")
    else:
        return None

    return bill_id


def division_in_mpvotes_table(division_name):
    count_command_string = f"SELECT COUNT(*) FROM {db_name}.MPVotes WHERE title = \"{division_name}\""

    count_from_interaction = db_agent.select(count_command_string)
    count = extract_first_string_from_db_interaction(count_from_interaction)
    count = int(count)

    if count > 0:
        return True
    else:
        return False

def get_sessions_string(sessions):
    sessions_string = ""
    for s in sessions:
        sessions_string += (s + ",")
    sessions_string = sessions_string[:-1]

    return sessions_string


def execute_insert_new_bill_into_bills_table(bill):
    sessions_string = get_sessions_string(bill.sessions)

    summary_sanitised = bill.summary.replace("\"", "")

    insertion_command_string \
        = f"INSERT INTO {db_name}.Bills (titleStripped, billOrAct, dateAdded, shortDesc, sessions, link) " \
          f"VALUES (\"{bill.title_stripped}\",\"{bill.title_postfix}\",\"{bill.last_updated.isoformat()}\",\"{summary_sanitised}\",\"{sessions_string}\",\"{bill.url}\")"

    db_agent.interact(insertion_command_string)


def execute_update_bill(bill):
    sessions_string = get_sessions_string(bill.sessions)

    datetime_iso_string = bill.last_updated.isoformat()
    print(f"dattime iso: {datetime_iso_string}")

    update_command_string = f"UPDATE {db_name}.Bills " \
                            f"SET " \
                            f"billOrAct = \"{bill.title_postfix}\", " \
                            f"dateAdded = \"{datetime_iso_string}\", " \
                            f"shortDesc = \"{bill.summary}\", " \
                            f"sessions = \"{sessions_string}\", " \
                            f"link = \"{bill.url}\" " \
                            f"WHERE titleStripped = \'{bill.title_stripped}\'"
    print(f"update command string {update_command_string}")
    row_used = db_agent.select(f"SELECT * FROM {db_name}.Bills WHERE titleStripped = \"{bill.title_stripped}\"")
    print(f"row used: {row_used}")

    db_agent.interact(update_command_string)


def execute_insert_new_vote_into_mpvotes_table(division_title, stage, bill_id, mp_id, aye=True):
    if aye == True:
        positive = 1
    else:
        positive = 0

    insert_command_string = f"INSERT INTO {db_name}.MPVotes (positive, billID, mpID, stage, title)" \
                            f"VALUES (\"{positive}\",\"{bill_id}\",\"{mp_id}\",\"{stage}\",\"{division_title}\")"

    db_agent.interact(insert_command_string)


def put_bill_and_division_data_in_db(bills_overview):
    for bill in bdi.get_bill_details(bills_overview):
        # get the billID from DB
        bill_id = bill_id_in_bills_table(bill)
        # if there is no billID, then the bill is not in the table, hence we need to insert the bill
        if bill_id is None:
            print(f"bill {bill.title_stripped} not yet in Bills table")
            execute_insert_new_bill_into_bills_table(bill)
            bill_id = bill_id_in_bills_table(bill)
        else:
            print(f"bill {bill.title_stripped} already in Bills table")
            row_before_op = db_agent.select(f"SELECT * FROM {db_name}.Bills WHERE titleStripped = \"{bill.title_stripped}\"")
            print(f"row before: {row_before_op}")
            execute_update_bill(bill)
            row_after_op = db_agent.select(
                f"SELECT * FROM {db_name}.Bills WHERE titleStripped = \"{bill.title_stripped}\"")
            print(f"row after: {row_after_op}")

        for division in bill.divisions_list:
            division_title = division.division_name
            division_stage = division.division_stage
            # only insert if we haven't already inserted the results
            if not division_in_mpvotes_table(division.division_name):
                print(f"division {division_title} not yet in MPVotes table")
                for no in division.noes:
                    execute_insert_new_vote_into_mpvotes_table(division_title, division_stage, bill_id, no, aye=False)
                for aye in division.ayes:
                    execute_insert_new_vote_into_mpvotes_table(division_title, division_stage, bill_id, aye, aye=True)
            else:
                print(f"division {division_title} already in MPVotes table")


def upsert_bills_and_divisions_data(fresh=False, session="2019-21"):
    if fresh == True:
        os.remove("datetime_last_scraped.p")
        clear_table("MPVotes")
        clear_table("Bills")


    bills_overview = blf.BillsOverview(run_on_app_engine=True, project_name="bills-app-305000", debug=True)
    bills_overview.get_changed_bills_in_session(session_name=session)

    filename = datetime.datetime.now().isoformat() + "_bills_overview"
    write_to_log_file(bills_overview.bills_overview_data.to_string(), filename)

    # insert everything back in
    put_bill_and_division_data_in_db(bills_overview)


# wipes tables in order, inserts all data back in
# takes ~2hrs
def reload_all_tables():
    clear_all_4_tables()
    insert_party_data()
    insert_mp_data()
    insert_dead_mp_placeholder()
    upsert_bills_and_divisions_data(fresh=True, session="All")


def db_describe_table(table_name):
    description = db_agent.select(f"DESCRIBE {table_name}")
    print(f"{table_name} table structure")
    print(description)


def print_all_rows_of_table(table_name):
    rows = db_agent.select(f"SELECT * FROM {table_name}")
    print(f"all items in table {table_name}:")
    print(rows)


sql_config = {}

db_name = ""


def write_to_log_file(message, log_filename):
    fs = gcsfs.GCSFileSystem(project="bills-app-305000")
    encoded_message = str.encode(message)
    with fs.open("bills-app-305000.appspot.com" + "/" + log_filename, "wb") as handle:
        handle.write(encoded_message)


# by default assumes running on app engine
def insert_and_update_data(completely_fresh=False, day_frequency_for_party_and_mp_data=7, allow_party_and_mp_upsert=True, run_on_app_engine=True, project_name="bills-app-305000"):
    global db_name
    db_name = "bill_app_db"

    bills_overview = blf.BillsOverview(run_on_app_engine=True,project_name="bills-app-305000")
    mock_datetime = datetime.datetime(2021, 3, 20, 12, 0, 0, 0)
    bills_overview.reset_datetime_last_scraped()
    bills_overview.mock_datetime_last_scraped(mock_datetime)

    if completely_fresh:
        reload_all_tables()
    else:
        # update MPs and parties ~every 5 days by default
        # this is not possible from google app engine as app engine times out

        if datetime.datetime.now().day % day_frequency_for_party_and_mp_data == 0 and allow_party_and_mp_upsert:
            upsert_party_data()
            upsert_mp_data()
            print("finished updating MP and Party table")
        else:
            print("not a designated day to update MP and Party, or updating these has been disabled by parameter")


        upsert_bills_and_divisions_data(fresh=False, session="All")

        # todo in final version the session_name must be "All" - but check the script works on Google cloud first

        print("finished inserting bills and divisions data")



if __name__ == "__main__":
    insert_and_update_data(run_on_app_engine=False, allow_party_and_mp_upsert=False)




