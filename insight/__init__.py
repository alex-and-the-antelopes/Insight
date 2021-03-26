from util.database import is_new_address, fetch_user


class User:
    @staticmethod
    def verify_email_and_session_token(email_address: str, session_token: str) -> bool:
        """
        Verify the user using their email and token. Checks if the email address is used, and verifies the token.
        :param email_address: The email address of the user.
        :param session_token: The session token of the user.
        :return: True if the user was verified, False otherwise.
        """
        if is_new_address(email_address):  # Check if the email corresponds to a User
            return False
        user = fetch_user(email_address)  # Get the user form the database using their email
        if user and user.verify_token(session_token):
            return True  # Login successful
        return False  # Tokens do not match

    """
    Represents a User entity.
    Has an email address, password hash, email address, notification, session token and postcode.
    """
    def __init__(self, email: str, password_hash: str, notification_token: str, postcode: str, session_token: str):
        """
        Constructs a new User Object with the given details.
        :param email: The User's email address.
        :param password_hash: The User's hashed password.
        :param notification_token: The User's (ExponentPushToken) notification token. Unique to each User and device.
        :param postcode: The User's postcode.
        :param session_token: The User's unique session token.
        """
        self.email = email
        self.password_hash = password_hash
        self.notification_token = notification_token
        self.postcode = postcode
        self.session_token = session_token

    def update_postcode(self, postcode: str) -> None:
        """
        Updates the user's postcode.
        :param postcode: The postcode to be changed.
        :return: None.
        """
        self.postcode = postcode
        return

    def verify_password(self, password: str) -> bool:
        """
        Given a password, check if it is correct.
        :param password: The (hashed) password to check.
        :return: True if it is correct, False otherwise.
        """
        return password == self.password_hash

    def verify_token(self, token: str) -> bool:
        """
        Given a token, check if it is correct.
        :param token: The (hashed) password to check.
        :return: True if it is correct, False otherwise.
        """
        return token == self.session_token

    def to_dict(self) -> dict:
        """
        Creates and returns a dictionary representation of the current User object.
        :return: A dictionary containing the attributes of the current User.
        """
        return vars(self)

    def __str__(self) -> str:
        """
        Creates and returns a string representation of the current User object. The string contains the email, password
        hash, postcode, notification and session token of the User.
        :return: A string (str) containing the User's information.
        """
        user_str = f"email: {self.email}, postcode: {self.postcode}, session token: {self.session_token}, " \
                   f"password hash: {self.password_hash}, notification token: {self.notification_token}"
        return user_str


def filter_votes(bill_votes: list) -> list:
    """
    Cleans the given list of bill votes to only include relevant bill votes. Filters out amendments and deprecated
    readings.
    :param bill_votes: The list of bill votes to clean/filter.
    :return: The filtered list of bill votes.
    """
    clean_votes = []
    prev_id = '-1'  # Used to filter out deprecated bills from the final list
    for bill in bill_votes:
        if "amendments" in bill[2]:  # Ignore amendments
            continue
        if prev_id == bill[0]:
            clean_votes.pop()  # If bill id appears twice, remove the deprecated version
        clean_votes.append(bill)  # Add the bill to the cleaned list
        prev_id = bill[0]  # Update the previous id for next iteration
    return clean_votes