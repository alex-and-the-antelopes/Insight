import requests


def get_constituencies_from_post_code(pc: str) -> [dict]:
    """
    Utility function to get constituency data for a given post code. Uses the government's API.
    The more precise the postcode, the better.
    :param pc: Post code
    :return: List of constituencies.
    """
    params = {
        "searchText": pc
    }

    url = "https://members-api.parliament.uk/api/Location/Constituency/Search"

    response = requests.get(url, params=params)

    results = [
        item["value"]
        for item in response.json()["items"]
    ]

    return results
