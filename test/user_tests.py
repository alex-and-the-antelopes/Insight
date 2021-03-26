import unittest
from insight import User


class UserTestCases(unittest.TestCase):
    """
    Tests for User. Covered functions:
    > verify_password
    > to_dict
    Depend on/Affected by:
    > hash_password
    """
    def test_verify_password(self):
        """
        Test the verify_password() in User
        """
        #  email, password, notification_token, postcode, session_token):
        user = User("email@email.com", "hashed_pass", "ExpoPushToken[XXXXXXX]", "BA27AY", "AhfO3sd")
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
        Test the verify_token() in User
        """
        #  email, password, notification_token, postcode, session_token):
        user = User("email@email.com", "hashed_pass", "ExpoPushToken[XXXXXXX]", "BA27AY", "AhfO3sd")
        # Check for actual value:
        self.assertTrue(user.verify_token("AhfO3sd"))
        # Check for wrong values:
        self.assertFalse(user.verify_token("ahfO3sd"))
        self.assertFalse(user.verify_token(""))
        # Checking Wrong Types:
        self.assertFalse(user.verify_token(None))
        self.assertFalse(user.verify_token(("AhfO3sd", "AhfO3sd")))
        self.assertFalse(user.verify_token(13.012))

    def test_to_dict(self):
        """
        Test the to_dict() in User todo fix to_dict tests
        """
        user = User("admin", "pass", "n token")
        user_dict = user.to_dict()
        # Check for actual value:
        self.assertEqual({'username': 'admin', 'password_hash': "password_hash", 'notification_token': "n token"}, user_dict)
        # Check for wrong value:
        self.assertNotEqual({'username': 'admin', 'password_hash': "password_hash", 'notification_token': "n token"}, user_dict)  # Correct name, wrong pass, correct token
        self.assertNotEqual({'username': 'Admin', 'password_hash': "password_hash", 'notification_token': "n token"}, user_dict)  # Wrong name, correct pass, correct token
        self.assertNotEqual({'username': 'admin', 'password_hash': "password_hash", 'notification_token': "N token"}, user_dict)  # Correct name, correct pass, wrong token
        self.assertNotEqual({'username': 'Admin', 'password_hash': "password_hash", 'notification_token': "N token"}, user_dict)  # All wrong values
        # Check Wrong Types:
        # Partially wrong types:
        self.assertNotEqual({'username': None, 'password_hash': "password_hash", 'notification_token': "n token"}, user_dict)  # None name
        self.assertNotEqual({'username': "admin", 'password_hash': None, 'notification_token': "n token"}, user_dict)  # None pass
        self.assertNotEqual({'username': "admin", 'password_hash': "password_hash", 'notification_token': None}, user_dict)  # None token
        self.assertNotEqual({'username': None, 'password_hash': None, 'notification_token':None}, user_dict)  # None all
        # Fully wrong types:
        self.assertNotEqual("user", user_dict)
        self.assertNotEqual(None, user_dict)
        self.assertNotEqual(13.012, user_dict)


if __name__ == '__main__':
    unittest.main()
