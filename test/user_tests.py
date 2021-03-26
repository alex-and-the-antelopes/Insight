import unittest
from insight import User


class UserTestCases(unittest.TestCase):
    """
    Tests for User. Covered functions:
    > verify_password
    > to_dict
    """
    def test_verify_password(self):
        """
        Test the verify_password() in User.
        """
        #  email, password, notification_token, postcode, session_token:
        user = User("email@email.com", "hashed_pass", "ExpoPushToken[1CAd241Xs]", "BA27AY", "AhfO3sd")
        # Check for actual value:
        self.assertTrue(user.verify_password("hashed_pass"))
        # Check for wrong values:
        self.assertFalse(user.verify_password("Pass"))
        self.assertFalse(user.verify_password(""))
        # Checking Wrong Types:
        self.assertFalse(user.verify_password(None))
        self.assertFalse(user.verify_password(("pass", "pass")))
        self.assertFalse(user.verify_password(13.012))

    def test_verify_token(self):
        """
        Test the verify_token() in User.
        """
        #  email, password, notification_token, postcode, session_token):
        user = User("email@email.com", "hashed_pass", "ExpoPushToken[1CAd241Xs]", "BA27AY", "AhfO3sd")
        # Check for actual value:
        self.assertTrue(user.verify_token("AhfO3sd"))
        # Check for wrong values:
        self.assertFalse(user.verify_token("ahfO3sd"))
        self.assertFalse(user.verify_token(""))
        # Checking Wrong Types:
        self.assertFalse(user.verify_token(None))
        self.assertFalse(user.verify_token(("AhfO3sd", "AhfO3sd")))
        self.assertFalse(user.verify_token(13.012))
