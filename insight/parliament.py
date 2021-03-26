class Member:
    """
    Represents a Member of Parliament (MP).
    Has mp_id, first name, last name, email address, physical (mailing) address, party_id (represent party), path to
    their picture (photo_path), phone number, area (constituency) and a current flag (indicates if they are the active
    MP for the constituency).
   """

    def __init__(self, mp_id: int or str, first_name: str, last_name: str, email: str, address: str,
                 party_id: int or str, photo_path: str, phone_num: str, area: str, current: int or str):
        """
        Constructs a new Member Object with the given details.
        :param mp_id: The MP's id.
        :param first_name: The MP's first name.
        :param last_name: The MP's last name.
        :param email: The email address of the MP.
        :param address: The physical (mailing) address of the MP.
        :param party_id: The id of the party which they are a part of.
        :param photo_path: A path to the MP's photo.
        :param phone_num: The MP's phone number.
        :param area: The area (constituency) which the MP represents.
        :param current: A flag indicating if the MP is active or not. Possible values: 0 --> inactive, 1 --> active.
        """
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
        Creates and returns a dictionary representation of the current Member of Parliament (MP).
        :return: A dictionary containing the attributes of the current Member object.
        """
        return vars(self)

    def __str__(self) -> str:
        """
        Creates and returns a string representation of the current Member object. The string contains the
        email, id, address, party id, photo path, phone number and area of the MP.
        :return: A string (str) containing the Member's information.
        """
        mp_str = f"id: {self.mp_id}, last name: {self.last_name}, first name: {self.first_name}, email: {self.email}," \
                 f" address: {self.address}, party id: {self.party_id}, photo path: {self.photo_path}, phone number:" \
                 f" {self.phone_num}, area: {self.area}, current: {self.current}"
        return mp_str


class Bill:
    """
    Represents a Bill entity.
    Has id, title, description, date added to the database (or last updated), expiration date, status, a short
    description and a link to the bill's page on the https://bills.parliament.uk/.
    """

    def __init__(self, bill_id: int or str, title: str, desc: str or None, date_added: str, expiration_date: str,
                 status: str, short_desc: str = None, link: str = "https://bills.parliament.uk/"):
        """
        Constructs a new Bill Object with the given details. Optional parameters: short_desc and link.
        :param bill_id: The id of the bill.
        :param title: The title of the bill.
        :param desc: The scraped description of the bill.
        :param date_added: The date the bill was added to the database (or last updated).
        :param expiration_date: The date the bill is set to expire.
        :param status: The status of the bill. The bill's passage, can be: House of Commons, House of Lords or Final
        Stages.
        :param short_desc: A short description of the Bill. Defaults to None. If not given one, the description (desc)
        will be used to generate a short version.
        :param link: The bill's page on the https://bills.parliament.uk/. Contains more details for the Bill. Defaults
        to the general parliament website, if not given one.
        """
        self.id = bill_id
        self.title = title
        self.desc = desc
        self.date_added = date_added
        self.expiration_date = expiration_date
        self.status = status
        if not short_desc and self.desc:  # If no short description provided use self.desc
            short_desc = self.desc[:30]
        self.short_desc = short_desc
        self.link = link

    def prepare(self, additional_values: dict = None) -> dict:
        """
        Prepares bill to be sent to front-end, adding any extra fields that are expected (such as user likes/dislikes).
        :param additional_values: Extra key-value pairs to add to result
        :return: Bill in dict form, with extra fields.
        """
        bill_dict = self.to_dict()  # Get the dictionary representation of the Bill object
        if additional_values:  # Check if extra values are given
            for key in additional_values:
                bill_dict[key] = additional_values[key]  # Add the extra values to the dictionary
        return bill_dict  # Return the final version of the bill

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
