class User:
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