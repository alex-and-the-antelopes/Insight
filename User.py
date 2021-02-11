from passlib.hash import sha256_crypt  # Uses SHA256 for storing the password. We could implement our own later


class User:
    """
    Represents a User entity.
    Has username, password. (Other Details could include: email address and more personal data)
    """
    def __init__(self, username, password):
        self.username = username
        self.password_hash = sha256_crypt.hash(password)  # get hash password

    # Given a password, hashes it and see if it is correct
    def verify_password(self, password):
        return sha256_crypt.verify(password, self.password_hash)  # True if they match, False otherwise


if __name__ == "__main__":
    user = User("sg2295", "password")
    print(user.username)
    print(user.password_hash)
    wrong_password = "pass"
    print("Testing the wrong password, passwords match:", user.verify_password(wrong_password))
    correct_password = "password"
    print("Testing the correct password, passwords match:", user.verify_password(correct_password))