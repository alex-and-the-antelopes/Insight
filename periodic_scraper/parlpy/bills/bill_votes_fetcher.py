"""
Robert Chambers 2021
"""

import requests
import datetime
import json

# get Response object from API, queried about divisions on a stripped title (title without the act/bill postfix)
def fetch_votes(
        bill_title_stripped: str,
        start_datetime: datetime.date,
        end_datetime: datetime.date = None) -> requests.models.Response:
    votes_endpoint = 'https://commonsvotes-api.parliament.uk/data/divisions.json/search'

    votes_parameters = {'queryParameters.searchTerm': bill_title_stripped,
                        'queryParameters.startDate': start_datetime.isoformat(),
                        }

    # add end time in order to narrow results, unless end_datetime None, which is the case for the current session only
    print(f"end_datetime {end_datetime}")
    if end_datetime is not None:
        votes_parameters['queryParameters.endDate'] = end_datetime.isoformat()

    r = requests.get(votes_endpoint, params=votes_parameters)

    return r

# get a list of divisionIDs
# note that the earliest *bill* division provided by the system is 2016-03-09
# the earliest session with bill divisions recorded by the system is 2015-16
def get_division_ids(bill_title_stripped: str,
        start_datetime: datetime.date,
        end_datetime: datetime.date = None
                     ) -> list:



    division_response = fetch_votes(bill_title_stripped, start_datetime, end_datetime)
    division_obj = json.loads(division_response.text)

    division_ids = []

    for d in division_obj:
        division_ids.append(d["DivisionId"])

    return division_ids

# return response for specific division by ID
def fetch_division_values(division_id):
    specific_division_endpoint = f"https://commonsvotes-api.parliament.uk/data/division/{division_id}.json"

    response = requests.get(specific_division_endpoint)

    return response

# second/third reading /: indicates the division is not the second or third reading, but is on amendments relating
# todo: better checking of title to determine what stage the division is for
def determine_division_stage(division_title):
    # even though "<nth> reading" may be in title, it may be referring to amendments
    if "second reading" in division_title.lower() \
            and "second reading:" not in division_title.lower() \
            and "second reading " not in division_title.lower() \
            and "amendment" not in division_title.lower() \
            and "amdt" not in division_title.lower():
        division_stage = "Second Reading"
    elif "third reading" in division_title.lower() \
            and "third reading:" not in division_title.lower() \
            and "third reading " not in division_title.lower() \
            and "amendment" not in division_title.lower() \
            and "amdt" not in division_title.lower():
        division_stage = "Third Reading"
    else:
        division_stage = "Amendments"

    return division_stage

# build and return a DivisionInformation object with title, stage, ayes list and noes list
def get_division_values(division_id):
    response = fetch_division_values(division_id)
    specific_division_obj = json.loads(response.text)

    division_title = specific_division_obj["Title"]

    ayes_data = specific_division_obj["Ayes"]
    ayes_ids = [a["MemberId"] for a in ayes_data]

    noes_data = specific_division_obj["Noes"]
    noes_ids = [n["MemberId"] for n in noes_data]

    division_stage = determine_division_stage(division_title)

    division_values = DivisionInformation(division_title, division_stage, ayes_ids, noes_ids)

    return division_values

class DivisionInformation():
    def __init__(self, division_name="", division_stage="", ayes=[], noes=[]):
        self.division_name = division_name
        # may be "Second Reading", "Third Reading", "Amendments"
        self.division_stage = division_stage
        # list of MP ids for the ayes
        self.ayes = ayes
        # list of MP ids for the noes
        self.noes = noes

# checks that a division is on a bill and not some other matter
# results for eg "finance" also returns results for divisions with "finances"
def check_division_is_on_bill(bill_title_stripped, division_name):
    bill_title_stripped_words = bill_title_stripped.split(' ')

    # check the division is on a bill and not some other matter
    if ("Bill") not in division_name:
        return False

    # check the division title contains all words in bill title
    for w in bill_title_stripped_words:
        if (w + ' ') not in division_name:
            return False

    return True

# return a list of DivisionInformation objects
def get_divisions_information(bill_title_stripped: str,
        start_datetime: datetime.date,
        end_datetime: datetime.date = None,
        skip_old_bills = True):
    # we know that the earliest division is 2016-3-9
    delta = None
    if end_datetime is not None:
        lower_limit_date = datetime.date(2016,3,9)
        delta = end_datetime - lower_limit_date

    if skip_old_bills and delta is not None and delta.total_seconds() < 0:
        return []

    division_ids = get_division_ids(bill_title_stripped, start_datetime, end_datetime)

    division_information_list = []

    for id in division_ids:
        division_information = get_division_values(id)

        # only add if all words in bill_title_stripped appear in division name

        # only add if division is on a bill
        if check_division_is_on_bill(bill_title_stripped, division_information.division_name):
            division_information_list.append(division_information)

    return division_information_list