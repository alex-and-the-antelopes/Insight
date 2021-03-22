import requests
import json

class PartyInformation():
    def __init__(self, party_name: str, party_id: int):
        self.party_name = party_name
        self.party_id = party_id

def get_all_parties():
    commons_parties_endpoint = "https://members-api.parliament.uk/api/Parties/GetActive/Commons"

    r = requests.get(commons_parties_endpoint)
    parties_object = json.loads(r.text)

    parties_items_object = parties_object["items"]

    # list holding PartiesInformation objects
    parties_list = []
    for p in parties_items_object:
        party_id = p["value"]["id"]
        party_name = p["value"]["name"]

        party_obj = PartyInformation(party_name, party_id)
        parties_list.append(party_obj)

    return parties_list
