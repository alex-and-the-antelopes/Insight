import requests


def is_valid_postcode(postcode: str) -> bool:
    """
    Checks if the given postcode is a valid postcode using the https://api.postcodes.io/ API.
    :param postcode: The postcode to evaluate.
    :return: True if the postcode is valid, False otherwise.
    """
    # Use the postcode.io API to validate postcodes
    url = f"https://api.postcodes.io/postcodes/{postcode}/validate"
    response = requests.get(url).json()

    # Request was processed properly
    if response['status'] == 200:
        # Get the API's evaluation
        return response['result']

    # API refused to evaluate the request (typeError)
    return False


def strip_text(text: str) -> str:
    """
    Finds and removes the escape characters in the given string. Checks for linux and windows escape characters.
    :param text: The string to be parsed.
    :return: The parsed string.
    """
    if "\r" in text:
        text = text.replace("\r", "")  # Remove linux next line char
    if "\n" in text:
        text = text.replace("\n", "")  # Remove mac & windows next line char
    return text