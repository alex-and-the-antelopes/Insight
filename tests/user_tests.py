import unittest
from bill_tracker_core import User
from bill_tracker_core import hash_password


class UserTestCases(unittest.TestCase):
    """
    Tests for User. Covered functions:
    > verify_password
    > to_dict
    Depend on/Affected by:
    > hash_password
    """

    def test_username(self):
        """
        Check that username is correct
        Could remove (I realized this wasn't needed too late)
        """
        user = User("admin", "pass", "notification token")
        # Check for actual value:
        self.assertEqual("admin", user.email)
        # Check for wrong values:
        self.assertNotEqual("Admin", user.email)
        self.assertNotEqual("", user.email)
        # Checking Wrong Types:
        self.assertNotEqual(None, user.email)
        self.assertNotEqual(("admin", "admin"), user.email)
        self.assertNotEqual(13.012, user.email)

    def test_verify_password(self):
        """
        Test the verify_password() in User
        """
        user = User("admin", "pass", "notification token")
        # Check for actual value:
        self.assertTrue(user.verify_password("pass"))
        # Check for wrong values:
        self.assertFalse(user.verify_password("Pass"))
        self.assertFalse(user.verify_password(""))
        # Checking Wrong Types:
        self.assertFalse(user.verify_password(None))
        self.assertFalse(user.verify_password(("pass", "pass")))
        self.assertFalse(user.verify_password(13.012))

    def test_to_dict(self):
        """
        Test the to_dict() in User
        """
        user = User("admin", "pass", "n token")
        user_dict = user.to_dict()
        # Check for actual value:
        self.assertEqual({'username': 'admin', 'password_hash': hash_password("pass"), 'notification_token': "n token"}, user_dict)
        # Check for wrong value:
        self.assertNotEqual({'username': 'admin', 'password_hash': hash_password("Pass"), 'notification_token': "n token"}, user_dict)  # Correct name, wrong pass, correct token
        self.assertNotEqual({'username': 'Admin', 'password_hash': hash_password("pass"), 'notification_token': "n token"}, user_dict)  # Wrong name, correct pass, correct token
        self.assertNotEqual({'username': 'admin', 'password_hash': hash_password("pass"), 'notification_token': "N token"}, user_dict)  # Correct name, correct pass, wrong token
        self.assertNotEqual({'username': 'Admin', 'password_hash': hash_password("Pass"), 'notification_token': "N token"}, user_dict)  # All wrong values
        # Check Wrong Types:
        # Partially wrong types:
        self.assertNotEqual({'username': None, 'password_hash': hash_password("pass"), 'notification_token': "n token"}, user_dict)  # None name
        self.assertNotEqual({'username': "admin", 'password_hash': hash_password(None), 'notification_token': "n token"}, user_dict)  # None pass
        self.assertNotEqual({'username': "admin", 'password_hash': hash_password("pass"), 'notification_token': None}, user_dict)  # None token
        self.assertNotEqual({'username': None, 'password_hash': hash_password(None), 'notification_token':None}, user_dict)  # None all
        # Fully wrong types:
        self.assertNotEqual("user", user_dict)
        self.assertNotEqual(None, user_dict)
        self.assertNotEqual(13.012, user_dict)


if __name__ == '__main__':
    unittest.main()
