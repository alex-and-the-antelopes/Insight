import datetime
import time
import pandas as pd
import requests
import json


def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=2)
    print(text)


# def underscore_to_camelcase(name: str) -> str:
#     parts = [part[0].upper() + part[1:].lower() for part in name.split("_")]
#     camel = "".join(parts)
#     return camel[0].lower() + camel[1:]


class MPOverview:
    # Parameters for getting alive MPs
    current_mp_params = {
        "IsCurrentMember": True,
        "House": "Commons",
    }

    def __init__(self):
        """
        Overview class for members.
        """
        self.last_updated = None

        self.api_url = "https://members-api.parliament.uk/api/"

        self.max_take = 20

        self.columns = [
            # Display Name
            "name_display",
            # Full Title
            "name_full_title",
            # Name to address member by
            "name_address_as",
            # Name to list member by
            "name_list_as",
            # email for MP
            "email",
            # Member ID (for further information)
            "member_id",
            # whether the MP is a current member
            "current_member",
            # Gender
            "gender",
            # Party that the member belongs to
            "party_id",
            # Constituency of member
            "constituency",
            # Time this information was retrieved
            "last_updated"
        ]
        self.mp_overview_data = pd.DataFrame([], columns=self.columns)


    def __get_email(self, mp_id):
        contact_details_endpoint = f"https://members-api.parliament.uk/api/Members/{mp_id}/Contact"
        response = requests.get(contact_details_endpoint)

        # get the MP's parliamentary email
        email_address = "none_given"
        for contact in response.json()["value"]:
            if contact["type"] == "Parliamentary":
                if "email" in contact.keys():
                    email_address = contact["email"]

        return email_address


    def __add_member_to_data_from_api_response(self, response: requests.Response, only_get_current_members_emails: bool) -> None:
        """
        Adds members from a response to the data
        :param response: Response to add
        """
        # jprint(response.json())
        for item in response.json()["items"]:
            value_obj = item["value"]
            # Don't include dead people
            if value_obj["latestHouseMembership"]["membershipEndReason"] == "Death":
                continue

            if value_obj["latestHouseMembership"]["membershipStatus"] is not None:
                current_member = True
            else:
                current_member = False

            # if only_get_current_members_emails is false, always get the MP's/former MP's email
            if current_member or only_get_current_members_emails == False:
                email = self.__get_email(value_obj["id"])
            else:
                email = "not_current_member"

            values = {
                "name_display": value_obj["nameDisplayAs"],
                "name_full_title": value_obj["nameFullTitle"],
                "name_address_as": value_obj["nameAddressAs"],
                "name_list_as": value_obj["nameListAs"],
                "email": email,
                "member_id": value_obj["id"],
                "current_member": current_member,
                "gender": value_obj["gender"],
                "party_id": value_obj["latestParty"]["id"],
                "constituency": value_obj["latestHouseMembership"]["membershipFrom"],
                "last_updated": datetime.datetime.now(),
            }

            self.mp_overview_data = self.mp_overview_data.append(values, ignore_index=True)

    def get_all_members(self,
                        params: dict,
                        fetch_delay: int = 0,
                        limit: int = None,
                        only_get_current_members_emails: bool = True,
                        verbose: bool = False) -> None:
        """
        Get all members that fit the criteria stated in params and save in self.mp_overview_data
        :param params: dictionary of parameters to pass
        :param fetch_delay: Time (seconds) between fetching each 'page'
        :param limit: Limit of number of members to retrieve.
        :param only_get_current_members_emails: default true if we only want emails for current members (recommended)
        :param verbose: Enable verbose mode
        """
        take = self.max_take
        skip = params.get("skip", 0)
        count = 0
        while True:
            # Get next response
            response = self.__fetch_members(params=params)

            n_items = len(response.json()["items"])

            if response.status_code != 200:
                print(f"Received status code {response.status_code}, terminating...")
                break

            if n_items == 0:
                break

            count += n_items
            # Save response to dataframe
            self.__add_member_to_data_from_api_response(response, only_get_current_members_emails)

            # Calculate next skip
            skip += take

            # Respect limit, if it's set
            if limit is not None and count >= limit:
                if verbose:
                    jprint(response.json())
                    print(f"Limit {limit} reached.")

                break

            # Delay if set
            if verbose:
                # Print response
                jprint(response.json())
                # Wait fetch_delay seconds
                print(f"Waiting {fetch_delay}s... ")
                time.sleep(fetch_delay)
                print("Getting...")
            else:
                time.sleep(fetch_delay)

            params["skip"] = skip

        now = datetime.datetime.now()
        if verbose:
            print(f"{count} members retrieved.")
            print(f"Setting last_updated to {now}.")
            print(f"Updating finished.\n")
        self.last_updated = now

    def get_active_MPs(self, fetch_delay: int = 0, limit: int = None, verbose: bool = False):
        """
        Get all active MPs in parliament.
        Wrapper for get_all_members. Uses the MPOverview.current_mp_params dict.
        :param fetch_delay: Time (seconds) between fetching each 'page'
        :param limit: Limit of number of members to retrieve.
        :param verbose: Enable verbose mode
        :return:
        """

        return self.get_all_members(self.current_mp_params, fetch_delay, limit, verbose)

    def __fetch_members(self, params: dict = None) -> requests.Response:
        """

        :param params:
        :return:
        """
        if params is None:
            params = {}

        path = "Members/Search"

        response = requests.get(self.api_url + path, params=params)

        return response
