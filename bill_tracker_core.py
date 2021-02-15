# from passlib.hash import sha256_crypt  # Uses SHA256 for storing the password. We could implement our own later

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
    return CONFIG["public_res_dir"] + filename


# Generate a hash for the given password.
def hash_password(password):
    # Module not imported, so just return password for now
    # todo: Change this when user accounts are implemented
    return password

    # return sha256_crypt.hash(password)


class User(object):
    """
    Represents a User entity.
    Has username, password. (Other Details could include: email address and more personal data)
    """

    def __init__(self, username, password):
        self.username = username
        # Hash password and save it
        self.password_hash = hash_password(password)

    # Given a password, hashes it and see if it is correct
    def verify_password(self, password):
        return hash_password(password) == self.password_hash
        # return sha256_crypt.verify(password, self.password_hash)  # True if they match, False otherwise

    # Return self as key-value pairs in dict
    def to_dict(self):
        return vars(self)


class Bill:
    """
    Represents a bill entry.
    Has title, desc, date added, expiration, status, short_desc, photo and link.
    """

    def __init__(self, title, desc, date_added, expiration, status,
                 short_desc=None, photo=CONFIG["default_img"], link=CONFIG["default_url"]):
        self.link = link
        self.status = status
        self.expiration = expiration
        self.date_added = date_added
        self.desc = desc
        self.title = title

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


# todo: Move this to actual unit test file
if __name__ == "__main__":
    user = User("sg2295", "password")
    print(user.username)
    print(user.password_hash)
    wrong_password = "pass"
    print("Testing the wrong password, passwords match:", user.verify_password(wrong_password))
    correct_password = "password"
    print("Testing the correct password, passwords match:", user.verify_password(correct_password))
