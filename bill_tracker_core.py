
class User(object):
    """
    Represents a User entity.
    Has an email, password, email address, notification, session token and postcode.
    """
    def __init__(self, email, password, notification_token, postcode, session_token):
        self.email = email
        self.password_hash = password
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


class ParliamentMember:
    def __init__(self, mp_id, first_name, last_name, email, address, party_id, photo_path, phone_num, area, current):
        self.mp_id = mp_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.address = address
        self.party_id = party_id
        self.photo_path = photo_path
        self.phone_num = phone_num
        self.area = area
        self.current = current

    def to_dict(self) -> dict:
        """
        Creates and returns a dictionary representation of the current ParliamentMember (MP) object.
        :return: A dictionary containing the attributes of the current ParliamentMember.
        """
        return vars(self)

    def __str__(self) -> str:
        """
        Creates and returns a string representation of the current ParliamentMember object. The string contains the
        email, id, address, party id, photo path, phone number and area of the MP.
        :return: A string (str) containing the ParliamentMember's information.
        """
        mp_str = f"id: {self.mp_id}, last name: {self.last_name}, first name: {self.first_name}, email: {self.email}," \
                 f" address: {self.address}, party id: {self.party_id}, photo path: {self.photo_path}, phone number:" \
                 f" {self.phone_num}, area: {self.area}, current: {self.current}"
        return mp_str


class Bill:
    """
    Represents a bill entry.
    Has title, desc, date added, expiration, status, short_desc and link.
    """
    def __init__(self, bill_id: int or str, title: str, desc: str, date_added: str, expiration_date: str, status: str,
                 short_desc: str = None, link: str = "https://bills.parliament.uk/"):
        """
        Creates a representation of a Bill.
        :param bill_id: The id of the bill.
        :param title: The title of the bill.
        :param desc: The scraped description of the bill.
        :param date_added: The date the bill was added to the database (or last updated).
        :param expiration_date: The date the bill is set to expire.
        :param status: The status of the bill. The bill's passage, can be: House of Commons, House of Lords or Final
        Stages.
        :param short_desc: A short description of the Bill. Defaults to None. If not given one, the description (desc)
        will be used to generate a short version.
        :param link: The bill's page on the https://bills.parliament.uk/. Contains more details for the Bill.
        """
        self.id = bill_id
        self.title = title
        self.desc = desc
        self.date_added = date_added
        self.expiration_date = expiration_date
        self.status = status
        if not short_desc:  # If no short description provided use self.desc
            short_desc = self.desc[:30] if self.desc else None
        self.short_desc = short_desc
        self.link = link

    def __str__(self) -> str:
        """
        Creates and returns a string representation of the current Bill object. The string contains the
        id, title, description, date added, expiration, status, a short description and a link to the bill.
        :return: A string (str) containing the Bill's information.
        """
        bill_str = f"id: {self.id}, title: {self.title}, description: {self.desc}, date added: {self.date_added}, " \
                   f"expiration: {self.expiration_date}, status: {self.status}, short description: {self.short_desc}," \
                   f" link: {self.link}"
        return bill_str

    def to_dict(self) -> dict:
        """
        Creates and returns a dictionary representation of the current Bill object.
        :return: A dictionary containing the attributes of the current Bill.
        """
        return vars(self)
