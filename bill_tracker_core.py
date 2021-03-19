# from passlib.hash import sha256_crypt  # Uses SHA256 for storing the password. We could implement our own later
import datetime
import random
import string

# Configuration constants
CONFIG = {
    # Image Directory, for storing icons
    "img_dir": "res/img/",

    # Default image name
    "default_img": "no_photo.jpg",

    # External resources path
    "external_res_path": "/res/",

    # Invalid image name
    "invalid_img": "invalid_photo.jpg",

    # File extensions for valid images
    "valid_img_extensions": {
        "png", "PNG",
        "jpg", "jpeg", "JPG"
    },

    # Length of short description when it must be generated from the (long) description
    "short_desc_default_length": 20,

    # Default URL for bills
    "default_url": "https://www.youtube.com/watch?v=hXIArhNhD0g"
}


# Returns the URL for the given filename
def get_img_url(filename):
    return CONFIG["external_res_path"] + filename


# Generate a hash for the given password.
def hash_password(password):
    # Module not imported, so just return password for now
    # todo: Change this when user accounts are implemented
    return password

    # return sha256_crypt.hash(password)


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

    def verify_password(self, password):
        """
        Given a password, check if it is correct.
        :param password: The (hashed) password to check.
        :return: True if it is correct, False otherwise
        """
        return password == self.password_hash

    def to_dict(self):
        """
        Creates and returns a dictionary representation of the current User object.
        :return: A dictionary containing the attributes of the current User.
        """
        return vars(self)


class Bill:
    """
    Represents a bill entry.
    Has title, desc, date added, expiration, status, short_desc, photo and link.
    """

    def __init__(self, id, title, desc, date_added, expiration, status,
                 short_desc=None, photo=CONFIG["default_img"], link=CONFIG["default_url"]):
        self.link = link
        self.status = status
        self.expiration = expiration
        self.date_added = date_added
        self.desc = desc
        self.title = title
        self.id = id

        # Generate short desc from long desc if one isn't given
        if short_desc is None:
            # Length of this is dictated by CONFIG
            self.short_desc = desc[:CONFIG["short_desc_default_length"]]
        else:
            self.short_desc = short_desc

        # Check if img extension is valid
        # todo: Is there a better way of checking extension? Should we even be
        #  checking the extension here? Might be better to check filetype at upload.
        if photo.split(".")[-1] in CONFIG["valid_img_extensions"]:
            self.img_url = get_img_url(photo)
        else:
            # Use default invalid image if the image is the wrong file type
            self.img_url = get_img_url(CONFIG["invalid_img"])

    # Return self as key-value pair dict
    def to_dict(self):
        return vars(self)
