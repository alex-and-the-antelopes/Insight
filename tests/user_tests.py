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
        user = User("admin", "pass")
        # Check for actual value:
        self.assertEqual("admin", user.username)
        # Check for wrong values:
        self.assertNotEqual("Admin", user.username)
        self.assertNotEqual("", user.username)
        # Checking Wrong Types:
        self.assertNotEqual(None, user.username)
        self.assertNotEqual(("admin", "admin"), user.username)
        self.assertNotEqual(13.012, user.username)

    def test_verify_password(self):
        """
        Test the verify_password() in User
        """
        user = User("admin", "pass")
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
        user = User("admin", "pass")
        # Check for actual value:
        self.assertEqual({'username': 'admin', 'password_hash': hash_password("pass")}, user.to_dict())
        # Check for wrong value:
        self.assertNotEqual({'username': 'admin', 'password_hash': hash_password("Pass")}, user.to_dict())  # Correct name, wrong pass
        self.assertNotEqual({'username': 'Admin', 'password_hash': hash_password("pass")}, user.to_dict())  # Wrong name, correct pass
        self.assertNotEqual({'username': 'Admin', 'password_hash': hash_password("Pass")}, user.to_dict())  # Both wrong values
        # Check Wrong Types:
        # Partially wrong types:
        self.assertNotEqual({'username': None, 'password_hash': hash_password("Pass")}, user.to_dict())  # None name
        self.assertNotEqual({'username': "admin", 'password_hash': hash_password(None)}, user.to_dict())  # None pass
        self.assertNotEqual({'username': None, 'password_hash': hash_password(None)}, user.to_dict())  # Both None
        # Fully wrong types:
        self.assertNotEqual("user", user.to_dict())
        self.assertNotEqual(None, user.to_dict())
        self.assertNotEqual(13.012, user.to_dict())

# Check for hashed passwords etc
# make sure it runs normally
# think about corner cases/edge cases
# this will run on the pipeline


if __name__ == '__main__':
    unittest.main()
